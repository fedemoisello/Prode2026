import streamlit as st
from lib.auth import require_login
from lib.deadline import assert_not_locked, is_locked
from lib.db import query, upsert
from lib.grupos import calcular_tabla, clasificados
from lib.constants import GRUPOS, PARTIDOS_POR_GRUPO, EQUIPOS_POR_GRUPO
from lib.flags import flag_img, team_label
from lib.data import load_fixture, load_teams, load_ranking_fifa
from datetime import datetime, timedelta

st.title("⚽ Fase de Grupos")

u = require_login()
locked = is_locked()
tz_bsas = st.session_state.get("tz_bsas", False)

if locked:
    st.warning("🔒 El prode está cerrado. Solo podés ver tus picks.")

if "grupos_guardados" not in st.session_state:
    st.session_state["grupos_guardados"] = set()

# Cargar fixture y picks existentes
fixture = {f["id"]: f for f in load_fixture() if f["fase"] == "grupos"}
teams = load_teams()
ranking_fifa = load_ranking_fifa()

picks_existentes = {p["partido_id"]: p
                    for p in query("picks_grupos", {"user_id": u["id"]})}

for grupo in GRUPOS:
    partido_ids = PARTIDOS_POR_GRUPO[grupo]
    equipos = EQUIPOS_POR_GRUPO[grupo]

    group_complete = all(pid in picks_existentes for pid in partido_ids)
    title_icon = " ✅" if group_complete else ""
    expander_label = f"Grupo {grupo}{title_icon}  ·  {' / '.join(teams[e]['nombre'] for e in equipos)}"

    with st.expander(expander_label, expanded=False):

        if grupo in st.session_state["grupos_guardados"]:
            st.success(f"✅ Grupo {grupo} guardado correctamente.")

        # Tabla en vivo a partir de picks actuales en session_state
        partidos_para_tabla = []
        for pid in partido_ids:
            fix = fixture[pid]
            key_gl = f"g_{pid}_l"
            key_gv = f"g_{pid}_v"
            gl = st.session_state.get(key_gl, picks_existentes.get(pid, {}).get("goles_local"))
            gv = st.session_state.get(key_gv, picks_existentes.get(pid, {}).get("goles_visitante"))
            partidos_para_tabla.append({
                "local": fix["local"],
                "visitante": fix["visitante"],
                "goles_local": gl,
                "goles_visitante": gv,
            })

        tabla = calcular_tabla(equipos, partidos_para_tabla, ranking_fifa=ranking_fifa)

        st.markdown("**Resultados**")
        nuevos_picks = {}
        for idx, pid in enumerate(partido_ids):
            fix = fixture[pid]
            loc = teams[fix["local"]]
            vis = teams[fix["visitante"]]
            dt = datetime.fromisoformat(fix["fecha"].replace("Z", "+00:00"))
            if tz_bsas:
                dt_display = dt - timedelta(hours=3)
                fecha_str = dt_display.strftime("%d/%m %H:%M") + " (BA)"
            else:
                fecha_str = dt.strftime("%d/%m %H:%M") + " UTC"

            prev = picks_existentes.get(pid, {})
            default_l = prev.get("goles_local", 0)
            default_v = prev.get("goles_visitante", 0)

            if idx % 2 == 0:
                jornada_num = idx // 2 + 1
                st.markdown(f"""<div style="
                    background:#1A1F2E;border-radius:4px;
                    padding:4px 10px;margin:14px 0 2px 0;
                    font-size:0.72em;letter-spacing:0.09em;
                    text-transform:uppercase;font-weight:600;
                    color:rgba(255,255,255,0.45)
                ">Jornada {jornada_num}</div>""", unsafe_allow_html=True)

            with st.container(border=(idx % 2 == 0)):
                r1l, r1r = st.columns([3, 1])
                r1l.markdown(f"{flag_img(loc)}**{loc['nombre']}**", unsafe_allow_html=True)
                gl = r1r.number_input("Local", min_value=0, max_value=20, value=default_l,
                                      key=f"g_{pid}_l", label_visibility="collapsed", disabled=locked)
                r2l, r2r = st.columns([3, 1])
                r2l.markdown(f"{flag_img(vis)}**{vis['nombre']}**", unsafe_allow_html=True)
                gv = r2r.number_input("Visitante", min_value=0, max_value=20, value=default_v,
                                      key=f"g_{pid}_v", label_visibility="collapsed", disabled=locked)
                st.caption(f"📅 {fecha_str} · {fix['ciudad']}")
            nuevos_picks[pid] = {"goles_local": gl, "goles_visitante": gv}

        st.divider()
        st.markdown("**Tabla en base a tus resultados**")
        for i, row in enumerate(tabla):
            eq = teams[row.equipo]
            clasif = "🟢" if i < 2 else ("🟡" if i == 2 else "🔴")
            st.markdown(f"{clasif} {flag_img(eq)}**{eq['nombre']}** — {row.pts}pts DG{row.dg:+d} ({row.gf}-{row.gc})", unsafe_allow_html=True)

        if not locked:
            _, bcol = st.columns([3, 1])
            if bcol.button(f"💾 Guardar Grupo {grupo}", key=f"save_{grupo}", use_container_width=True):
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
                    st.session_state["grupos_guardados"].add(grupo)
                    st.rerun()
                except PermissionError as e:
                    st.error(str(e))

total_picks_g = len(query("picks_grupos", {"user_id": u["id"]}))
if total_picks_g >= 72:
    st.divider()
    if not locked:
        st.success("✅ Fase de grupos completa. ¡Ahora cargá las eliminatorias!")
        if st.button("Continuar a Mis Eliminatorias →", type="primary", use_container_width=True):
            st.switch_page("pages/3_Eliminatorias.py")
    else:
        st.success("✅ Fase de grupos completa.")
