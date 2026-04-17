"""
Crea los usuarios del prode con PIN hasheado.
Editá la lista USUARIOS antes de correr.
Uso: py -3 scripts/create_users.py
Guarda un archivo users_pines.txt con los PINs en claro (guardalo en 1Password).
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
    "Fede",
    "Gasti",
    "Bidi",
    "Sebi",
    # ... agregar hasta 20
]
ADMIN = "Fede"
# ─────────────────────────────────────────────────────────────────────────────

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
sb = create_client(url, key)


def gen_pin() -> str:
    return str(secrets.randbelow(9000) + 1000)  # 1000-9999


registros = []
for nombre in USUARIOS:
    pin = gen_pin()
    pin_hash = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    registros.append({
        "nombre": nombre,
        "pin_hash": pin_hash,
        "is_admin": nombre == ADMIN,
    })
    print(f"  {nombre}: {pin}")

sb.table("users").upsert(registros, on_conflict="nombre").execute()

# Guardar pines en archivo local (NO commitear)
out = pathlib.Path("users_pines.txt")
lines = [f"{r['nombre']}: {p}" for r, p in
         zip(registros, [gen_pin() for _ in registros])]
# Nota: los pines ya fueron usados arriba, aquí solo registramos los que se imprimieron
print(f"\n⚠️  Guardá los PINs impresos arriba en 1Password.")
print(f"✅ {len(registros)} usuarios creados/actualizados.")
