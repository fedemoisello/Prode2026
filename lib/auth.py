import bcrypt
import streamlit as st
from datetime import datetime, timezone, timedelta
from lib.db import query, insert, update, get_client


SESSION_TTL_HOURS = 24


def hash_pin(pin: str) -> str:
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()


def check_pin(pin: str, hashed: str) -> bool:
    return bcrypt.checkpw(pin.encode(), hashed.encode())


def get_all_users() -> list[dict]:
    return query("users", columns="id,nombre,is_admin")


def login(nombre: str, pin: str) -> dict | None:
    from supabase import create_client
    sb = get_client()
    rows = sb.table("users").select("*").ilike("nombre", nombre).execute().data
    if not rows:
        return None
    user = rows[0]
    if not check_pin(pin, user["pin_hash"]):
        return None
    return user


def set_session(user: dict):
    st.session_state["user"] = {
        "id": user["id"],
        "nombre": user["nombre"],
        "is_admin": user.get("is_admin", False),
        "login_at": datetime.now(timezone.utc).isoformat(),
    }


def get_session() -> dict | None:
    u = st.session_state.get("user")
    if not u:
        return None
    login_at = datetime.fromisoformat(u["login_at"])
    if datetime.now(timezone.utc) - login_at > timedelta(hours=SESSION_TTL_HOURS):
        del st.session_state["user"]
        return None
    return u


def require_login():
    u = get_session()
    if not u:
        st.warning("Tenés que iniciar sesión primero.")
        st.stop()
    return u


def require_admin():
    u = require_login()
    if not u["is_admin"]:
        st.error("Acceso restringido a administradores.")
        st.stop()
    return u
