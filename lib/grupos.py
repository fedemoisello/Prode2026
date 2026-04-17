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
    tabla.sort(key=_sort_key(tabla), reverse=True)
    return tabla


def _sort_key(tabla):
    def key(r: RowTabla):
        return (r.pts, r.dg, r.gf)
    return key


def clasificados(tabla: list[RowTabla]) -> tuple[str, str, str]:
    """Devuelve (primero, segundo, tercero) de la tabla."""
    return tabla[0].equipo, tabla[1].equipo, tabla[2].equipo
