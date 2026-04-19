"""
Calcula la tabla de posiciones de un grupo a partir de los resultados
(reales o predichos). Aplica criterios de desempate FIFA (hasta DFD).
"""
from dataclasses import dataclass, field


@dataclass
class RowTabla:
    equipo: str
    pj: int = 0
    pg: int = 0
    pe: int = 0
    pp: int = 0
    gf: int = 0
    gc: int = 0

    @property
    def pts(self) -> int:
        return self.pg * 3 + self.pe

    @property
    def dg(self) -> int:
        return self.gf - self.gc


def calcular_tabla(equipos: list[str], partidos: list[dict]) -> list[RowTabla]:
    """
    equipos: lista de 4 IDs de equipos del grupo
    partidos: lista de dicts con keys local, visitante, goles_local, goles_visitante
              Solo se incluyen partidos con ambos goles definidos (no None).
    Devuelve lista de RowTabla ordenada por criterios FIFA.
    """
    filas = {e: RowTabla(equipo=e) for e in equipos}

    for p in partidos:
        if p.get("goles_local") is None or p.get("goles_visitante") is None:
            continue
        gl, gv = p["goles_local"], p["goles_visitante"]
        loc, vis = p["local"], p["visitante"]
        if loc not in filas or vis not in filas:
            continue

        filas[loc].pj += 1
        filas[vis].pj += 1
        filas[loc].gf += gl
        filas[loc].gc += gv
        filas[vis].gf += gv
        filas[vis].gc += gl

        if gl > gv:
            filas[loc].pg += 1
            filas[vis].pp += 1
        elif gl < gv:
            filas[vis].pg += 1
            filas[loc].pp += 1
        else:
            filas[loc].pe += 1
            filas[vis].pe += 1

    tabla = list(filas.values())
    return _ordenar_fifa(tabla, partidos)


def _ordenar_fifa(tabla: list[RowTabla], partidos: list[dict]) -> list[RowTabla]:
    """Ordena por criterios FIFA 2026: pts → H2H → general (dg, gf)."""
    grupos_pts: dict[int, list[RowTabla]] = {}
    for r in tabla:
        grupos_pts.setdefault(r.pts, []).append(r)

    result = []
    for pts in sorted(grupos_pts.keys(), reverse=True):
        grupo = grupos_pts[pts]
        if len(grupo) == 1:
            result.extend(grupo)
        else:
            result.extend(_resolver_empate(grupo, partidos, profundidad=0))
    return result


def _h2h_stats(empatados: list[RowTabla], partidos: list[dict]) -> dict[str, dict]:
    equipos_set = {r.equipo for r in empatados}
    stats = {r.equipo: {"pts": 0, "dg": 0, "gf": 0} for r in empatados}
    for p in partidos:
        loc, vis = p.get("local"), p.get("visitante")
        gl, gv = p.get("goles_local"), p.get("goles_visitante")
        if gl is None or gv is None or loc not in equipos_set or vis not in equipos_set:
            continue
        stats[loc]["gf"] += gl
        stats[loc]["dg"] += gl - gv
        stats[vis]["gf"] += gv
        stats[vis]["dg"] += gv - gl
        if gl > gv:
            stats[loc]["pts"] += 3
        elif gl < gv:
            stats[vis]["pts"] += 3
        else:
            stats[loc]["pts"] += 1
            stats[vis]["pts"] += 1
    return stats


def _resolver_empate(empatados: list[RowTabla], partidos: list[dict], profundidad: int) -> list[RowTabla]:
    """
    Resuelve empate en puntos aplicando H2H (paso 1 y 2 FIFA).
    profundidad=0: primer pase H2H; profundidad=1: segundo pase H2H entre restantes.
    Si sigue empatado, aplica criterio general (dg, gf).
    """
    if len(empatados) == 1:
        return empatados

    h2h = _h2h_stats(empatados, partidos)

    def h2h_key(r: RowTabla):
        s = h2h[r.equipo]
        return (s["pts"], s["dg"], s["gf"])

    empatados.sort(key=h2h_key, reverse=True)

    result = []
    i = 0
    while i < len(empatados):
        j = i + 1
        while j < len(empatados) and h2h_key(empatados[j]) == h2h_key(empatados[i]):
            j += 1
        subgrupo = empatados[i:j]
        if len(subgrupo) == 1:
            result.extend(subgrupo)
        elif profundidad == 0:
            # Segundo pase H2H entre los que siguen empatados (FIFA paso 2)
            result.extend(_resolver_empate(subgrupo, partidos, profundidad=1))
        else:
            # Criterio general: dg y gf de toda la fase de grupos
            subgrupo.sort(key=lambda r: (r.dg, r.gf), reverse=True)
            result.extend(subgrupo)
        i = j

    return result


def clasificados(tabla: list[RowTabla]) -> tuple[str, str, str]:
    """Devuelve (primero, segundo, tercero) de la tabla."""
    return tabla[0].equipo, tabla[1].equipo, tabla[2].equipo
