"""
Crea los usuarios del prode con PIN hasheado.
Editá la lista USUARIOS antes de correr.
Uso: py -3 scripts/create_users.py
Genera users_pines.txt con los PINs en claro — guardalo en 1Password y borralo.
"""
import os, sys, pathlib, secrets
from dotenv import load_dotenv

load_dotenv()

try:
    import bcrypt
    from supabase import create_client
except ImportError:
    print("ERROR: py -3 -m pip install -r requirements.txt")
    sys.exit(1)

# ── Editá esta lista ───────────────────────────────────────────────────────────
USUARIOS = [
    "Bidi", "Matuno", "Pela", "Sebi", "Fla", "Bele", "Bosti",
    "Buga", "Conri", "Chapa", "Dalmi", "Gasti", "Juanpa",
    "Mike", "Wake", "Pola", "Fede",
]
ADMIN = "Fede"
# ─────────────────────────────────────────────────────────────────────────────

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
sb = create_client(url, key)


def gen_pin() -> str:
    return str(secrets.randbelow(9000) + 1000)  # 1000-9999


registros = []
pines = []
for nombre in USUARIOS:
    pin = gen_pin()
    pin_hash = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    registros.append({
        "nombre": nombre,
        "pin_hash": pin_hash,
        "is_admin": nombre == ADMIN,
    })
    pines.append(pin)
    print(f"  {nombre}: {pin}")

sb.table("users").upsert(registros, on_conflict="nombre").execute()

out = pathlib.Path("users_pines.txt")
out.write_text(
    "\n".join(f"{r['nombre']}: {p}" for r, p in zip(registros, pines)),
    encoding="utf-8"
)
print(f"\n✅ {len(registros)} usuarios creados/actualizados.")
print(f"⚠️  PINs guardados en {out.resolve()} — pasalos a 1Password y borrá el archivo.")
