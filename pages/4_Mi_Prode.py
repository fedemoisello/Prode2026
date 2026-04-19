import streamlit as st
import json, pathlib
from lib.auth import require_login
from lib.db import query
from lib.grupos import calcular_tabla
from lib.constants import GRUPOS, PARTIDOS_POR_GRUPO, EQUIPOS_POR_GRUPO
from lib.flags import flag_img

st.title("📊 Mi Prode")

u = require_login()

fixture_raw = json.loads(pathlib.Path("data/fixture.json").read_text(encoding="utf-8"))
teams_raw = json.loads(pathlib.Path("data/teams.json").read_text(encoding="utf-8"))
fixture = {f["id"]: f for f in fixture_raw}
teams = {t["id"]: t for t in teams_raw}

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
            loc = teams[fix["local"]]
            vis = teams[fix["visitante"]]
            gl = pick.get("goles_local", "—")
            gv = pick.get("goles_visitante", "—")
            st.markdown(f"{flag_img(loc)}**{loc['nombre']}** {gl} - {gv} **{vis['nombre']}** {flag_img(vis)}", unsafe_allow_html=True)
            partidos.append({
                "local": fix["local"], "visitante": fix["visitante"],
                "goles_local": pick.get("goles_local"), "goles_visitante": pick.get("goles_visitante"),
            })
        tabla = calcular_tabla(equipos, partidos)
        st.divider()
        for i, row in enumerate(tabla):
            eq = teams[row.equipo]
            clasif = "🟢" if i < 2 else ("🟡" if i == 2 else "🔴")
            st.markdown(f"<small>{clasif} {flag_img(eq)}{eq['nombre']} — {row.pts}pts ({row.gf}-{row.gc})</small>", unsafe_allow_html=True)

st.subheader("Eliminatorias")
fases = ["16vos", "8vos", "cuartos", "semi", "tercer_puesto", "final"]
nombres_fase = {
    "16vos": "16avos", "8vos": "Octavos", "cuartos": "Cuartos",
    "semi": "Semis", "tercer_puesto": "3er Puesto", "final": "Final",
}
for fase in fases:
    partidos_fase = [f for f in fixture_raw if f["fase"] == fase]
    if not partidos_fase:
        continue
    st.markdown(f"**{nombres_fase[fase]}**")
    for fix in partidos_fase:
        pick = picks_e.get(fix["id"])
        if not pick:
            st.caption(f"Partido {fix['id']}: sin pronosticar")
            continue
        ganador = teams.get(pick.get("equipo_ganador"))
        gl = pick.get("goles_local", "—")
        gv = pick.get("goles_visitante", "—")
        gname = f"{ganador['flag']} {ganador['nombre']}" if ganador else "—"
        st.caption(f"Partido {fix['id']} · Ganador: {gname} · Score: {gl}-{gv}")
