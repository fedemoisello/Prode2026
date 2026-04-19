import json
import bcrypt
import streamlit as st
from datetime import datetime, timezone, timedelta
from lib.db import query, insert, update, get_client


SESSION_TTL_HOURS = 24 * 7  # 7 días
_COOKIE_NAME = "prode_session"
_COOKIE_MAX_AGE = 86400 * 7  # 7 días en segundos


def _cm():
    return st.session_state.get("_cm")


def hash_pin(pin: str) -> str:
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()


def check_pin(pin: str, hashed: str) -> bool:
    return bcrypt.checkpw(pin.encode(), hashed.encode())


def get_all_users() -> list[dict]:
    return query("users", columns="id,nombre,is_admin")


def login(nombre: str, pin: str) -> dict | None:
    sb = get_client()
    rows = sb.table("users").select("*").ilike("nombre", nombre).execute().data
    if not rows:
        return None
    user = rows[0]
    if not check_pin(pin, user["pin_hash"]):
        return None
    return user


def set_session(user: dict):
    login_at = datetime.now(timezone.utc).isoformat()
    data = {
        "id": user["id"],
        "nombre": user["nombre"],
        "is_admin": user.get("is_admin", False),
        "login_at": login_at,
    }
    st.session_state["user"] = data
    cm = _cm()
    if cm:
        try:
            cm.set(_COOKIE_NAME, json.dumps(data), max_age=_COOKIE_MAX_AGE)
        except Exception:
            pass


def get_session() -> dict | None:
    u = st.session_state.get("user")
    if u:
        login_at = datetime.fromisoformat(u["login_at"])
        if datetime.now(timezone.utc) - login_at > timedelta(hours=SESSION_TTL_HOURS):
            _clear_session_state()
            return None
        return u

    # Intentar restaurar desde cookie
    cm = _cm()
    if cm:
        try:
            raw = cm.get(_COOKIE_NAME)
            if raw:
                data = json.loads(raw)
                login_at = datetime.fromisoformat(data["login_at"])
                if datetime.now(timezone.utc) - login_at < timedelta(hours=SESSION_TTL_HOURS):
                    st.session_state["user"] = data
                    return data
                # Cookie expirada — borrarla
                cm.delete(_COOKIE_NAME)
        except Exception:
            pass
    return None


def clear_session():
    cm = _cm()
    if cm:
        try:
            cm.delete(_COOKIE_NAME)
        except Exception:
            pass
    _clear_session_state()


def _clear_session_state():
    st.session_state.pop("user", None)


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
