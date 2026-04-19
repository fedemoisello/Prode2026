"""
Borra TestBot1/2/3 y todos sus picks de la DB.
Uso: py -3 testing/clear_picks.py
"""
import os, sys
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("ERROR: py -3 -m pip install -r requirements.txt")
    sys.exit(1)

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

BOTS = ["TestBot1", "TestBot2", "TestBot3"]

for nombre in BOTS:
    result = sb.table("users").select("id").eq("nombre", nombre).execute().data
    if result:
        uid = result[0]["id"]
        sb.table("picks_grupos").delete().eq("user_id", uid).execute()
        sb.table("picks_eliminatorias").delete().eq("user_id", uid).execute()
        sb.table("users").delete().eq("id", uid).execute()
        print(f"  ✓ {nombre} eliminado (id={uid})")
    else:
        print(f"  – {nombre} no encontrado, nada que borrar")

print("✅ Limpieza completa.")
