"""
Borra todos los resultados de la tabla results.
Uso: py -3 testing/clear_results.py
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
sb.table("results").delete().neq("partido_id", 0).execute()
print("✅ Tabla results vaciada.")
