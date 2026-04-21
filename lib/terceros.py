"""
Asigna los 8 mejores terceros a los slots del bracket.
Cada slot solo acepta terceros de ciertos grupos (ver TERCEROS_VALIDOS).
Usamos backtracking para encontrar asignación válida.
"""
from lib.constants import TERCEROS_VALIDOS


def mejores_terceros(
    terceros_por_grupo: dict,
    ranking_fifa: dict[str, int] | None = None,
) -> list[dict]:
    """
    terceros_por_grupo: {grupo: {pts, dg, gf, fair_play_pts, equipo}}
    ranking_fifa: {equipo_id: posicion} — menor número = mejor ranking
    Devuelve lista de los 8 mejores terceros, ordenada de mejor a peor.
    Criterios FIFA Art. 13 (sección terceros): pts → dg → gf → fair play → ranking FIFA.
    """
    rf = ranking_fifa or {}
    candidatos = list(terceros_por_grupo.values())
    candidatos.sort(
        key=lambda x: (
            x["pts"],
            x["dg"],
            x["gf"],
            x.get("fair_play_pts", 0),
            -rf.get(x["equipo"], 999),
        ),
        reverse=True,
    )
    return candidatos[:8]


def asignar_terceros(mejores: list[dict]) -> dict[int, str]:
    """
    mejores: resultado de mejores_terceros() — lista de 8 dicts con 'grupo' y 'equipo'
    Devuelve {partido_id: equipo_id} para los 8 slots de 16vos.
    Usa backtracking para encontrar asignación válida según TERCEROS_VALIDOS.
    """
    slots = list(TERCEROS_VALIDOS.keys())  # [74, 77, 79, 80, 81, 82, 85, 87]
    grupos_disponibles = {t["grupo"] for t in mejores}
    equipo_por_grupo = {t["grupo"]: t["equipo"] for t in mejores}

    asignacion: dict[int, str] = {}
    grupos_usados: set[str] = set()

    def backtrack(idx: int) -> bool:
        if idx == len(slots):
            return True
        slot = slots[idx]
        candidatos = TERCEROS_VALIDOS[slot] & (grupos_disponibles - grupos_usados)
        for grupo in sorted(candidatos):
            asignacion[slot] = equipo_por_grupo[grupo]
            grupos_usados.add(grupo)
            if backtrack(idx + 1):
                return True
            del asignacion[slot]
            grupos_usados.discard(grupo)
        return False

    if not backtrack(0):
        # fallback: asignar en orden si no hay solución (no debería ocurrir)
        for i, slot in enumerate(slots):
            if i < len(mejores):
                asignacion[slot] = mejores[i]["equipo"]

    return asignacion
