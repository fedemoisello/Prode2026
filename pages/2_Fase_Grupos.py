import streamlit as st
from lib.auth import require_login
from lib.deadline import assert_not_locked, is_locked
from lib.db import query, upsert
from lib.grupos import calcular_tabla, clasificados
from lib.constants import GRUPOS, PARTIDOS_POR_GRUPO, EQUIPOS_POR_GRUPO
import json, pathlib

st.set_page_config(page_title="Fase de Grupos · Prode 2026", page_icon="⚽", layout="wide")
st.title("⚽ Fase de Grupos")

u = require_login()
locked = is_locked()

if locked:
    st.warning("🔒 El prode está cerrado. Solo podés ver tus picks.")

# Cargar fixture y picks existentes
fixture_raw = json.loads(pathlib.Path("data/fixture.json").read_text(encoding="utf-8"))
teams_raw = json.loads(pathlib.Path("data/teams.json").read_text(encoding="utf-8"))
fixture = {f["id"]: f for f in fixture_raw if f["fase"] == "grupos"}
teams = {t["id"]: t for t in teams_raw}

picks_existentes = {p["partido_id"]: p
                    for p in query("picks_grupos", {"user_id": u["id"]})}

for grupo in GRUPOS:
    partido_ids = PARTIDOS_POR_GRUPO[grupo]
    equipos = EQUIPOS_POR_GRUPO[grupo]

    with st.expander(f"Grupo {grupo}  ·  {' / '.join(teams[e]['nombre'] for e in equipos)}", expanded=False):

        # Tabla en vivo a partir de picks actuales en session_state
        partidos_para_tabla = []
        for pid in partido_ids:
            fix = fixture[pid]
            key_gl = f"g_{pid}_l"
            key_gv = f"g_{pid}_v"
            gl = st.session_state.get(key_gl, picks_existentes.get(pid, {}).get("goles_local"))
            gv = st.session_state.get(key_gv, picks_existentes.get(pid, {}).get("goles_visitante"))
            partidos_para_tabla.append({
                "local": fix["equipo_local"],
                "visitante": fix["equipo_visitante"],
                "goles_local": gl,
                "goles_visitante": gv,
            })

        tabla = calcular_tabla(equipos, partidos_para_tabla)
        col_tabla, col_partidos = st.columns([1, 2])

        with col_tabla:
            st.markdown("**Tabla**")
            for i, row in enumerate(tabla):
                eq = teams[row.equipo]
                clasif = "🟢" if i < 2 else ("🟡" if i == 2 else "🔴")
                st.markdown(f"{clasif} {eq['flag']} **{eq['nombre']}** — {row.pts}pts DG{row.dg:+d} ({row.gf}-{row.gc})")

        with col_partidos:
            st.markdown("**Resultados**")
            nuevos_picks = {}
            for pid in partido_ids:
                fix = fixture[pid]
                loc = teams[fix["equipo_local"]]
                vis = teams[fix["equipo_visitante"]]
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(fix["fecha"].replace("Z", "+00:00"))
                fecha_str = dt.strftime("%d/%m %H:%M") + " UTC"

                prev = picks_existentes.get(pid, {})
                default_l = prev.get("goles_local", 0)
                default_v = prev.get("goles_visitante", 0)

                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 3])
                c1.markdown(f"{loc['flag']} {loc['nombre']}")
                gl = c2.number_input("", min_value=0, max_value=20, value=default_l,
                                     key=f"g_{pid}_l", label_visibility="collapsed", disabled=locked)
                c3.markdown("<div style='text-align:center;padding-top:8px'>-</div>", unsafe_allow_html=True)
                gv = c4.number_input("", min_value=0, max_value=20, value=default_v,
                                     key=f"g_{pid}_v", label_visibility="collapsed", disabled=locked)
                c5.markdown(f"{vis['flag']} {vis['nombre']}")
                st.caption(f"📅 {fecha_str} · {fix['ciudad']}")
                nuevos_picks[pid] = {"goles_local": gl, "goles_visitante": gv}

        if not locked:
            if st.button(f"💾 Guardar Grupo {grupo}", key=f"save_{grupo}"):
                try:
                    assert_not_locked()
                    rows = [
                        {
                            "user_id": u["id"],
                            "partido_id": pid,
                            "goles_local": v["goles_local"],
                            "goles_visitante": v["goles_visitante"],
                        }
                        for pid, v in nuevos_picks.items()
                    ]
                    upsert("picks_grupos", rows)
                    st.success(f"Grupo {grupo} guardado.")
                    st.rerun()
                except PermissionError as e:
                    st.error(str(e))
