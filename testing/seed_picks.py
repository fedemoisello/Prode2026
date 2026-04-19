"""
Crea TestBot1/2/3 en users y carga picks completos (72 grupos + 32 elim).
Uso: py -3 testing/seed_picks.py
Deshacer: py -3 testing/clear_picks.py
Logueo en la app: nombre=TestBot1, PIN=0001 (etc.)
"""
import json, os, pathlib, random, sys
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
    import bcrypt
except ImportError:
    print("ERROR: py -3 -m pip install -r requirements.txt")
    sys.exit(1)

random.seed(42)

ROOT = pathlib.Path(__file__).parent.parent
fixture = json.loads((ROOT / "data/fixture.json").read_text(encoding="utf-8"))
teams   = json.loads((ROOT / "data/teams.json").read_text(encoding="utf-8"))
team_ids = [t["id"] for t in teams]

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

BOTS = [
    {"nombre": "TestBot1", "pin": "0001"},
    {"nombre": "TestBot2", "pin": "0002"},
    {"nombre": "TestBot3", "pin": "0003"},
]

# Insertar o recuperar cada bot
for bot in BOTS:
    existing = sb.table("users").select("id").eq("nombre", bot["nombre"]).execute().data
    if existing:
        bot["id"] = existing[0]["id"]
        print(f"  {bot['nombre']} ya existe (id={bot['id']})")
    else:
        pin_hash = bcrypt.hashpw(bot["pin"].encode(), bcrypt.gensalt()).decode()
        result = sb.table("users").insert({
            "nombre": bot["nombre"],
            "pin_hash": pin_hash,
            "is_admin": False,
        }).execute()
        bot["id"] = result.data[0]["id"]
        print(f"  {bot['nombre']} creado (id={bot['id']})")

grupos_fx = [f for f in fixture if f["fase"] == "grupos"]
elim_fx   = [f for f in fixture if f["fase"] != "grupos"]

picks_g, picks_e = [], []
for bot in BOTS:
    for m in grupos_fx:
        picks_g.append({
            "user_id":        bot["id"],
            "partido_id":     m["id"],
            "goles_local":    random.randint(0, 3),
            "goles_visitante": random.randint(0, 3),
        })
    for m in elim_fx:
        picks_e.append({
            "user_id":         bot["id"],
            "partido_id":      m["id"],
            "equipo_ganador":  random.choice(team_ids),
            "goles_local":     random.randint(0, 3),
            "goles_visitante": random.randint(0, 3),
        })

sb.table("picks_grupos").upsert(picks_g).execute()
sb.table("picks_eliminatorias").upsert(picks_e).execute()

print(f"✅ {len(picks_g)} picks de grupos + {len(picks_e)} de eliminatorias cargados.")
print("   TestBot1 PIN: 0001 | TestBot2 PIN: 0002 | TestBot3 PIN: 0003")
