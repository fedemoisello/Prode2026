"""
Calcula los puntos de un usuario dado sus picks y los resultados reales.
"""
from lib.constants import (
    PUNTOS_TENDENCIA, PUNTOS_GOL_EQUIPO, PUNTOS_RESULTADO_BONUS,
    PUNTOS_CLASIFICADO_12, PUNTOS_GANADOR,
)
from lib.grupos import calcular_tabla, clasificados
from lib.db import query
from lib.data import load_ranking_fifa


def _tendencia(gl, gv):
    if gl > gv: return "L"
    if gl < gv: return "V"
    return "E"


def puntos_partido_grupos(pred_gl, pred_gv, real_gl, real_gv) -> int:
    pts = 0
    if _tendencia(pred_gl, pred_gv) == _tendencia(real_gl, real_gv):
        pts += PUNTOS_TENDENCIA
    local_ok = (pred_gl == real_gl)
    visita_ok = (pred_gv == real_gv)
    if local_ok:
        pts += PUNTOS_GOL_EQUIPO
    if visita_ok:
        pts += PUNTOS_GOL_EQUIPO
    if local_ok and visita_ok and _tendencia(pred_gl, pred_gv) == _tendencia(real_gl, real_gv):
        pts += PUNTOS_RESULTADO_BONUS
    return pts


def puntos_partido_eliminatoria(
    pred_ganador, pred_gl, pred_gv,
    real_ganador, real_gl, real_gv,
    fase: str
) -> int:
    pts = 0
    if pred_ganador and pred_ganador == real_ganador:
        pts += PUNTOS_GANADOR.get(fase, 0)
    if pred_gl is not None and real_gl is not None and pred_gl == real_gl:
        pts += PUNTOS_GOL_EQUIPO
    if pred_gv is not None and real_gv is not None and pred_gv == real_gv:
        pts += PUNTOS_GOL_EQUIPO
    if (pred_gl is not None and pred_gv is not None
            and real_gl is not None and real_gv is not None
            and pred_gl == real_gl and pred_gv == real_gv):
        pts += PUNTOS_RESULTADO_BONUS
    return pts


def calcular_puntos_usuario(user_id: int) -> dict:
    """
    Calcula todos los puntos de un usuario.
    Solo cuenta partidos ya finalizados en la tabla results.
    """
    total = 0
    desglose = {"grupos_resultado": 0, "grupos_clasificados": 0, "eliminatorias": 0}

    ranking_fifa = load_ranking_fifa()
    picks_g = {p["partido_id"]: p for p in query("picks_grupos", {"user_id": user_id})}
    results  = {r["partido_id"]: r for r in query("results") if r.get("finalizado")}
    fixture_g = {f["id"]: f for f in query("fixture", {"fase": "grupos"})}

    # Puntos por resultado en grupos
    for pid, pick in picks_g.items():
        res = results.get(pid)
        if not res:
            continue
        pts = puntos_partido_grupos(
            pick["goles_local"], pick["goles_visitante"],
            res["goles_local"], res["goles_visitante"]
        )
        desglose["grupos_resultado"] += pts
        total += pts

    # Puntos por clasificados 1ro y 2do de grupo
    grupos_partidos = _agrupar_por_grupo(fixture_g)
    for grupo, partido_ids in grupos_partidos.items():
        equipos = list(
            {f["equipo_local"] for f in fixture_g.values() if f.get("grupo") == grupo} |
            {f["equipo_visitante"] for f in fixture_g.values() if f.get("grupo") == grupo}
        )
        partidos_pred = _build_partidos(partido_ids, picks_g, fixture_g)
        partidos_real = _build_partidos(partido_ids, results, fixture_g)

        if not all(p.get("goles_local") is not None for p in partidos_real):
            continue

        p1p, p2p, _ = clasificados(calcular_tabla(equipos, partidos_pred, ranking_fifa=ranking_fifa))
        p1r, p2r, _ = clasificados(calcular_tabla(equipos, partidos_real, ranking_fifa=ranking_fifa))

        if p1p == p1r:
            desglose["grupos_clasificados"] += PUNTOS_CLASIFICADO_12
            total += PUNTOS_CLASIFICADO_12
        if p2p == p2r:
            desglose["grupos_clasificados"] += PUNTOS_CLASIFICADO_12
            total += PUNTOS_CLASIFICADO_12

    # Puntos eliminatorias
    picks_e = {p["partido_id"]: p for p in query("picks_eliminatorias", {"user_id": user_id})}
    fixture_e = {f["id"]: f for f in query("fixture") if f["fase"] != "grupos"}

    for pid, pick in picks_e.items():
        res = results.get(pid)
        if not res:
            continue
        fix = fixture_e.get(pid)
        if not fix:
            continue
        pts = puntos_partido_eliminatoria(
            pick.get("equipo_ganador"), pick.get("goles_local"), pick.get("goles_visitante"),
            res.get("ganador"), res.get("goles_local"), res.get("goles_visitante"),
            fix["fase"]
        )
        desglose["eliminatorias"] += pts
        total += pts

    desglose["total"] = total
    return desglose


def _agrupar_por_grupo(fixture_g: dict) -> dict:
    from collections import defaultdict
    grupos = defaultdict(list)
    for pid, f in fixture_g.items():
        if f.get("grupo"):
            grupos[f["grupo"]].append(pid)
    return dict(grupos)


def _build_partidos(partido_ids, picks_or_results, fixture_g) -> list:
    partidos = []
    for pid in partido_ids:
        fix = fixture_g.get(pid)
        if not fix:
            continue
        row = picks_or_results.get(pid)
        loc_id = fix.get("equipo_local")
        vis_id = fix.get("equipo_visitante")
        p = {
            "local": loc_id,
            "visitante": vis_id,
            "goles_local": row.get("goles_local") if row else None,
            "goles_visitante": row.get("goles_visitante") if row else None,
        }
        # Incluir tarjetas solo cuando vienen de results (tienen las columnas de cards)
        if row and any(row.get(k) for k in ("amarillas_local", "amarillas_visitante",
                                             "rojas_doble_local", "rojas_directas_local")):
            p["tarjetas"] = {
                loc_id: {
                    "amarillas":       int(row.get("amarillas_local") or 0),
                    "rojas_doble":     int(row.get("rojas_doble_local") or 0),
                    "rojas_directas":  int(row.get("rojas_directas_local") or 0),
                },
                vis_id: {
                    "amarillas":       int(row.get("amarillas_visitante") or 0),
                    "rojas_doble":     int(row.get("rojas_doble_visitante") or 0),
                    "rojas_directas":  int(row.get("rojas_directas_visitante") or 0),
                },
            }
        partidos.append(p)
    return partidos
