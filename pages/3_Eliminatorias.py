import streamlit as st
from lib.auth import require_login
from lib.deadline import assert_not_locked, is_locked
from lib.db import query, upsert
from lib.grupos import calcular_tabla
from lib.terceros import mejores_terceros, asignar_terceros
from lib.bracket import build_16vos
from lib.constants import GRUPOS, PARTIDOS_POR_GRUPO, EQUIPOS_POR_GRUPO, PUNTOS_GANADOR, NOMBRES_FASE
from lib.flags import flag_img
from lib.data import load_fixture, load_teams, load_ranking_fifa

st.title("🎯 Eliminatorias")

u = require_login()
locked = is_locked()

fixture = {f["id"]: f for f in load_fixture()}
teams = load_teams()
ranking_fifa = load_ranking_fifa()

picks_g = {p["partido_id"]: p for p in query("picks_grupos", {"user_id": u["id"]})}
picks_e = {p["partido_id"]: p for p in query("picks_eliminatorias", {"user_id": u["id"]})}

if len(picks_g) < 72:
    st.warning("Completá primero la fase de grupos (necesitás los 72 resultados para calcular el bracket).")
    st.stop()

# Calcular clasificados de cada grupo a partir de los picks del usuario
primeros, segundos, terceros_por_grupo = {}, {}, {}
for grupo in GRUPOS:
    equipos = EQUIPOS_POR_GRUPO[grupo]
    partidos = []
    for pid in PARTIDOS_POR_GRUPO[grupo]:
        fix = fixture[pid]
        pick = picks_g.get(pid, {})
        partidos.append({
            "local": fix["local"], "visitante": fix["visitante"],
            "goles_local": pick.get("goles_local"), "goles_visitante": pick.get("goles_visitante"),
        })
    tabla = calcular_tabla(equipos, partidos, ranking_fifa=ranking_fifa)
    primeros[grupo] = tabla[0].equipo
    segundos[grupo] = tabla[1].equipo
    terceros_por_grupo[grupo] = {
        "grupo": grupo, "equipo": tabla[2].equipo,
        "pts": tabla[2].pts, "dg": tabla[2].dg, "gf": tabla[2].gf,
        "fair_play_pts": tabla[2].fair_play_pts,
    }

mejores = mejores_terceros(terceros_por_grupo, ranking_fifa=ranking_fifa)
asignacion = asignar_terceros(mejores)
cruces_16 = build_16vos(primeros, segundos, asignacion)

# ganadores_picks: {partido_id: equipo_id} según lo que el usuario ya pickó
ganadores_picks: dict[int, str] = {
    p["partido_id"]: p.get("equipo_ganador")
    for p in picks_e.values()
    if p.get("equipo_ganador")
} if picks_e else {}


def resolver_equipos(pid: int) -> tuple[str | None, str | None]:
    """Devuelve (local, visitante) para cualquier partido del bracket."""
    if pid in cruces_16:
        return cruces_16[pid]["local"], cruces_16[pid]["visitante"]
    fix = fixture.get(pid, {})
    ph_l = fix.get("ph_local", "")
    ph_v = fix.get("ph_visitante", "")

    def resolver_placeholder(ph: str) -> str | None:
        if ph.startswith("W"):
            return ganadores_picks.get(int(ph[1:]))
        if ph.startswith("L"):
            src = int(ph[1:])
            loc, vis = resolver_equipos(src)
            ganador = ganadores_picks.get(src)
            if ganador is None or loc is None or vis is None:
                return None
            return vis if ganador == loc else loc
        return None

    return resolver_placeholder(ph_l), resolver_placeholder(ph_v)


def equipo_label(eid: str | None) -> str:
    """Código de 3 letras para usar en radio/number_input (sin HTML)."""
    return eid if eid else "TBD"


def equipo_header(eid: str | None) -> str:
    """Bandera + código 3 letras para mostrar en markdown."""
    if not eid:
        return "TBD"
    t = teams.get(eid)
    if not t:
        return eid
    return f'{flag_img(t)}<b>{eid}</b>'


FASES = [
    ("16vos",        list(range(73, 89))),
    ("8vos",         list(range(89, 97))),
    ("cuartos",      list(range(97, 101))),
    ("semi",         [101, 102]),
    ("tercer_puesto",[103]),
    ("final",        [104]),
]

nuevos_picks: dict[int, dict] = {}
picks_invalidos: list[int] = []

for fase, partido_ids in FASES:
    pts_label = PUNTOS_GANADOR.get(fase, "?")
    st.subheader(f"🏆 {NOMBRES_FASE[fase]}  (+{pts_label} pts por ganador)")
    n_cols = 1 if len(partido_ids) == 1 else 2
    cols = st.columns(n_cols)

    for i, pid in enumerate(partido_ids):
        col = cols[i % n_cols]
        fix = fixture.get(pid, {})
        loc_id, vis_id = resolver_equipos(pid)

        prev = picks_e.get(pid, {})
        prev_ganador = prev.get("equipo_ganador")
        prev_gl = prev.get("goles_local", 0)
        prev_gv = prev.get("goles_visitante", 0)

        with col:
            with st.container(border=True):
                st.markdown(
                    f"{equipo_header(loc_id)} &nbsp;vs&nbsp; {equipo_header(vis_id)}"
                    f"<br><small style='opacity:.6'>{fix.get('ciudad','')}</small>",
                    unsafe_allow_html=True,
                )
                opciones = [eid for eid in [loc_id, vis_id] if eid]

                if not opciones:
                    st.caption("Equipos por definir según picks anteriores.")
                    continue

                etiquetas = [equipo_label(e) for e in opciones]
                idx_prev = opciones.index(prev_ganador) if prev_ganador in opciones else 0

                ganador_sel = st.radio(
                    "Ganador", etiquetas, index=idx_prev,
                    key=f"e_{pid}_g", disabled=locked, horizontal=True,
                )
                ganador_id = opciones[etiquetas.index(ganador_sel)]
                ganadores_picks[pid] = ganador_id  # propagar para partidos siguientes

                col_gl, col_gv = st.columns(2)
                gl = col_gl.number_input(f"{equipo_label(loc_id)} goles", 0, 20, prev_gl,
                                         key=f"e_{pid}_l", disabled=locked)
                gv = col_gv.number_input(f"{equipo_label(vis_id)} goles", 0, 20, prev_gv,
                                         key=f"e_{pid}_v", disabled=locked)

                # Validar consistencia goles vs ganador (solo cuando hay diferencia de goles)
                if gl != gv:
                    esperado = loc_id if gl > gv else vis_id
                    if ganador_id != esperado:
                        st.error(
                            f"Si {equipo_label(loc_id)} hace {gl} y {equipo_label(vis_id)} hace {gv}, "
                            f"no puede ganar {equipo_label(ganador_id)}."
                        )
                        picks_invalidos.append(pid)

                nuevos_picks[pid] = {"equipo_ganador": ganador_id, "goles_local": gl, "goles_visitante": gv}

if not locked and nuevos_picks:
    if picks_invalidos:
        st.error(f"Corregí los {len(picks_invalidos)} partido(s) con goles inconsistentes antes de guardar.")
    elif st.button("💾 Guardar todas las eliminatorias"):
        try:
            assert_not_locked()
            rows = [{"user_id": u["id"], "partido_id": pid, **v} for pid, v in nuevos_picks.items()]
            upsert("picks_eliminatorias", rows)
            st.success("Eliminatorias guardadas.")
            st.rerun()
        except PermissionError as e:
            st.error(str(e))
