from datetime import datetime, timezone
from lib.db import get_config


def get_deadline() -> datetime:
    val = get_config("deadline_utc")
    return datetime.fromisoformat(val.replace("Z", "+00:00"))


def is_locked() -> bool:
    return datetime.now(timezone.utc) >= get_deadline()


def assert_not_locked():
    if is_locked():
        raise PermissionError("Prode bloqueado — el torneo ya comenzó.")


def tiempo_restante() -> str:
    deadline = get_deadline()
    now = datetime.now(timezone.utc)
    if now >= deadline:
        return "Prode cerrado"
    delta = deadline - now
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes = rem // 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours}h {minutes}m"
