"""
Construye el bracket de eliminación directa a partir de los picks del usuario.
Entrada: clasificados por grupo (1ro, 2do, 3ro) + asignación de terceros.
Salida: dict {partido_id: {local: equipo, visitante: equipo}}
"""
from lib.constants import (
    BRACKET_8VOS, BRACKET_CUARTOS, BRACKET_SEMIS, BRACKET_FINAL, BRACKET_TERCER
)


def build_16vos(
    primeros: dict[str, str],   # {grupo: equipo}
    segundos: dict[str, str],   # {grupo: equipo}
    asignacion_terceros: dict[int, str],  # {partido_id: equipo}
) -> dict[int, dict]:
    """Devuelve {partido_id: {local, visitante}} para partidos 73-88."""
    cruces = {}

    mapeo = {
        73: (segundos.get("A"), segundos.get("B")),
        74: (primeros.get("E"), asignacion_terceros.get(74)),
        75: (primeros.get("F"), segundos.get("C")),
        76: (primeros.get("C"), segundos.get("F")),
        77: (primeros.get("I"), asignacion_terceros.get(77)),
        78: (segundos.get("E"), segundos.get("I")),
        79: (primeros.get("A"), asignacion_terceros.get(79)),
        80: (primeros.get("L"), asignacion_terceros.get(80)),
        81: (primeros.get("D"), asignacion_terceros.get(81)),
        82: (primeros.get("G"), asignacion_terceros.get(82)),
        83: (segundos.get("K"), segundos.get("L")),
        84: (primeros.get("H"), segundos.get("J")),
        85: (primeros.get("B"), asignacion_terceros.get(85)),
        86: (primeros.get("J"), segundos.get("H")),
        87: (primeros.get("K"), asignacion_terceros.get(87)),
        88: (segundos.get("D"), segundos.get("G")),
    }

    for pid, (loc, vis) in mapeo.items():
        cruces[pid] = {"local": loc, "visitante": vis}

    return cruces


def propagar_bracket(ganadores: dict[int, str]) -> dict[int, dict]:
    """
    Dado un dict {partido_id: equipo_ganador} construye los cruces de
    8vos, cuartos, semis, final y tercer puesto.
    Devuelve {partido_id: {local, visitante}} para partidos 89-104.
    """
    cruces = {}

    for siguiente, (p1, p2) in {**BRACKET_8VOS, **BRACKET_CUARTOS, **BRACKET_SEMIS, **BRACKET_FINAL}.items():
        loc = ganadores.get(p1)
        vis = ganadores.get(p2)
        cruces[siguiente] = {"local": loc, "visitante": vis}

    for pid, (p1, p2) in BRACKET_TERCER.items():
        perdedores_conocidos = {
            k: v for k, v in ganadores.items()
        }
        cruces[pid] = {
            "local": None,
            "visitante": None,
        }

    return cruces
