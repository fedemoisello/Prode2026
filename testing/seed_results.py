"""
Carga resultados ficticios para los 72 partidos de grupos.
Uso: py -3 testing/seed_results.py
Deshacer: py -3 testing/clear_results.py
"""
import json, os, pathlib, random, sys
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("ERROR: py -3 -m pip install -r requirements.txt")
    sys.exit(1)

random.seed(42)

ROOT = pathlib.Path(__file__).parent.parent
fixture = json.loads((ROOT / "data/fixture.json").read_text(encoding="utf-8"))
grupos = [f for f in fixture if f["fase"] == "grupos"]

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

rows = []
for m in grupos:
    gl = random.randint(0, 3)
    gv = random.randint(0, 3)
    ganador = m["local"] if gl > gv else (m["visitante"] if gv > gl else None)
    rows.append({
        "partido_id": m["id"],
        "goles_local": gl,
        "goles_visitante": gv,
        "ganador": ganador,
        "finalizado": True,
    })

sb.table("results").upsert(rows).execute()
print(f"✅ {len(rows)} resultados de grupos cargados (seed=42).")
