import streamlit as st
from lib.auth import require_login
from lib.db import query
from lib.grupos import calcular_tabla
from lib.constants import GRUPOS, PARTIDOS_POR_GRUPO, EQUIPOS_POR_GRUPO, NOMBRES_FASE_CORTO
from lib.flags import flag_img
from lib.data import load_fixture, load_teams, load_ranking_fifa

st.title("📊 Mi Prode")

u = require_login()

fixture_raw = load_fixture()
fixture = {f["id"]: f for f in fixture_raw}
teams = load_teams()
ranking_fifa = load_ranking_fifa()

picks_g = {p["partido_id"]: p for p in query("picks_grupos", {"user_id": u["id"]})}
picks_e = {p["partido_id"]: p for p in query("picks_eliminatorias", {"user_id": u["id"]})}

st.subheader("Fase de Grupos")
for grupo in GRUPOS:
    partido_ids = PARTIDOS_POR_GRUPO[grupo]
    equipos = EQUIPOS_POR_GRUPO[grupo]
    with st.expander(f"Grupo {grupo}"):
        partidos = []
        for pid in partido_ids:
            fix = fixture[pid]
            pick = picks_g.get(pid, {})
            loc = teams.get(fix["local"], {})
            vis = teams.get(fix["visitante"], {})
            gl = pick.get("goles_local", "—")
            gv = pick.get("goles_visitante", "—")
            st.markdown(
                f"{flag_img(loc)}<b>{loc.get('nombre', fix['local'])}</b> {gl}"
                f" - {gv} <b>{vis.get('nombre', fix['visitante'])}</b>{flag_img(vis)}",
                unsafe_allow_html=True,
            )
            partidos.append({
                "local": fix["local"], "visitante": fix["visitante"],
                "goles_local": pick.get("goles_local"), "goles_visitante": pick.get("goles_visitante"),
            })
        tabla = calcular_tabla(equipos, partidos, ranking_fifa=ranking_fifa)
        st.divider()
        for i, row in enumerate(tabla):
            eq = teams[row.equipo]
            clasif = "🟢" if i < 2 else ("🟡" if i == 2 else "🔴")
            st.markdown(f"<small>{clasif} {flag_img(eq)}{eq['nombre']} — {row.pts}pts ({row.gf}-{row.gc})</small>", unsafe_allow_html=True)

st.subheader("Eliminatorias")
fases = ["16vos", "8vos", "cuartos", "semi", "tercer_puesto", "final"]
for fase in fases:
    partidos_fase = [f for f in fixture_raw if f["fase"] == fase]
    if not partidos_fase:
        continue
    st.markdown(f"**{NOMBRES_FASE_CORTO[fase]}**")
    for fix in partidos_fase:
        pick = picks_e.get(fix["id"])
        if not pick:
            st.caption(f"Partido {fix['id']}: sin pronosticar")
            continue
        ganador = teams.get(pick.get("equipo_ganador"))
        gl = pick.get("goles_local", "—")
        gv = pick.get("goles_visitante", "—")
        if ganador:
            gname_html = f"{flag_img(ganador)}<b>{ganador['nombre']}</b>"
        else:
            gname_html = "—"
        st.markdown(
            f"<small>Partido {fix['id']} · Ganador: {gname_html} · Score: {gl}-{gv}</small>",
            unsafe_allow_html=True,
        )
