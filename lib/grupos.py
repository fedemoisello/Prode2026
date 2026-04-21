"""
Calcula la tabla de posiciones de un grupo a partir de los resultados
(reales o predichos). Aplica criterios de desempate FIFA Art. 13.
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
    fair_play_pts: int = 0  # acumulado del grupo; más alto = mejor conducta

    @property
    def pts(self) -> int:
        return self.pg * 3 + self.pe

    @property
    def dg(self) -> int:
        return self.gf - self.gc


def _fp_partido(tarjetas: dict) -> int:
    """Convierte dict de tarjetas de un equipo en puntos fair play (negativo = peor)."""
    return -(
        tarjetas.get("amarillas", 0) * 1 +
        tarjetas.get("rojas_doble", 0) * 3 +
        tarjetas.get("rojas_directas", 0) * 4 +
        tarjetas.get("amarilla_roja", 0) * 5
    )


def calcular_tabla(
    equipos: list[str],
    partidos: list[dict],
    ranking_fifa: dict[str, int] | None = None,
) -> list[RowTabla]:
    """
    equipos: lista de 4 IDs de equipos del grupo
    partidos: lista de dicts con keys local, visitante, goles_local, goles_visitante.
              Opcionalmente: tarjetas = {equipo_id: {amarillas, rojas_doble, rojas_directas, amarilla_roja}}
    ranking_fifa: {equipo_id: posicion} — menor número = mejor ranking
    Devuelve lista de RowTabla ordenada por criterios FIFA Art. 13.
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

        # Fair play: acumular si el partido tiene datos de tarjetas
        for equipo, t in p.get("tarjetas", {}).items():
            if equipo in filas:
                filas[equipo].fair_play_pts += _fp_partido(t)

    tabla = list(filas.values())
    return _ordenar_fifa(tabla, partidos, ranking_fifa or {})


def _ordenar_fifa(
    tabla: list[RowTabla],
    partidos: list[dict],
    ranking_fifa: dict[str, int],
) -> list[RowTabla]:
    """Ordena por criterios FIFA Art. 13: pts → H2H (paso 1+2) → dg/gf/fp/ranking."""
    grupos_pts: dict[int, list[RowTabla]] = {}
    for r in tabla:
        grupos_pts.setdefault(r.pts, []).append(r)

    result = []
    for pts in sorted(grupos_pts.keys(), reverse=True):
        grupo = grupos_pts[pts]
        if len(grupo) == 1:
            result.extend(grupo)
        else:
            result.extend(_resolver_empate(grupo, partidos, profundidad=0, ranking_fifa=ranking_fifa))
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


def _resolver_empate(
    empatados: list[RowTabla],
    partidos: list[dict],
    profundidad: int,
    ranking_fifa: dict[str, int],
) -> list[RowTabla]:
    """
    Resuelve empate en puntos aplicando criterios FIFA Art. 13.
    Paso 1 (profundidad=0): H2H entre todos los empatados.
    Paso 2 (profundidad=1): H2H solo entre los que siguen igualados.
    Tras el paso 2: dg general → gf general → fair play → ranking FIFA.
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
            result.extend(_resolver_empate(subgrupo, partidos, profundidad=1, ranking_fifa=ranking_fifa))
        else:
            # Criterios d, e, f, g, h del Art. 13: general dg → gf → fair play → ranking FIFA
            subgrupo.sort(
                key=lambda r: (r.dg, r.gf, r.fair_play_pts, -ranking_fifa.get(r.equipo, 999)),
                reverse=True,
            )
            result.extend(subgrupo)
        i = j

    return result


def clasificados(tabla: list[RowTabla]) -> tuple[str, str, str]:
    """Devuelve (primero, segundo, tercero) de la tabla."""
    return tabla[0].equipo, tabla[1].equipo, tabla[2].equipo
