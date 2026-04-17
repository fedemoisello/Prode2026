"""
Inicializa la DB de Supabase con equipos y fixture.
Requiere SUPABASE_URL y SUPABASE_KEY en .env o variables de entorno.
Uso: py -3 scripts/seed_db.py
"""
import json, os, pathlib, sys
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("ERROR: instalá dependencias: py -3 -m pip install -r requirements.txt")
    sys.exit(1)

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
sb = create_client(url, key)

ROOT = pathlib.Path(__file__).parent.parent

# ── Teams ──────────────────────────────────────────────────────────────────────
teams = json.loads((ROOT / "data/teams.json").read_text(encoding="utf-8"))
rows_teams = [
    {"id": t["id"], "nombre": t["nombre"], "grupo": t["grupo"],
     "flag": t["flag"], "seed": t["seed"]}
    for t in teams
]
result = sb.table("teams").upsert(rows_teams).execute()
print(f"Teams insertados: {len(rows_teams)}")

# ── Fixture ────────────────────────────────────────────────────────────────────
fixture = json.loads((ROOT / "data/fixture.json").read_text(encoding="utf-8"))
rows_fixture = []
for f in fixture:
    row = {
        "id": f["id"],
        "fase": f["fase"],
        "grupo": f.get("grupo"),
        "fecha_hora": f["fecha"],
        "sede": f["sede"],
        "ciudad": f["ciudad"],
        "equipo_local": f.get("local"),
        "equipo_visitante": f.get("visitante"),
        "ph_local": f.get("ph_local"),
        "ph_visitante": f.get("ph_visitante"),
    }
    rows_fixture.append(row)

result = sb.table("fixture").upsert(rows_fixture).execute()
print(f"Fixture insertado: {len(rows_fixture)} partidos")
print("✅ Seed completo.")
