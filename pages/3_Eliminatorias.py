import streamlit as st
import json, pathlib
from lib.auth import require_login
from lib.deadline import assert_not_locked, is_locked
from lib.db import query, upsert
from lib.grupos import calcular_tabla
from lib.terceros import mejores_terceros, asignar_terceros
from lib.bracket import build_16vos
from lib.constants import GRUPOS, PARTIDOS_POR_GRUPO, EQUIPOS_POR_GRUPO, PUNTOS_GANADOR

st.set_page_config(page_title="Eliminatorias · Prode 2026", page_icon="🎯", layout="wide")
st.title("🎯 Eliminatorias")

u = require_login()
locked = is_locked()

fixture_raw = json.loads(pathlib.Path("data/fixture.json").read_text(encoding="utf-8"))
teams_raw = json.loads(pathlib.Path("data/teams.json").read_text(encoding="utf-8"))
fixture = {f["id"]: f for f in fixture_raw}
teams = {t["id"]: t for t in teams_raw}

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
    tabla = calcular_tabla(equipos, partidos)
    primeros[grupo] = tabla[0].equipo
    segundos[grupo] = tabla[1].equipo
    terceros_por_grupo[grupo] = {
        "grupo": grupo, "equipo": tabla[2].equipo,
        "pts": tabla[2].pts, "dg": tabla[2].dg, "gf": tabla[2].gf,
    }

mejores = mejores_terceros(terceros_por_grupo)
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
    if not eid:
        return "Por definir"
    t = teams.get(eid)
    return f"{t['flag']} {t['nombre']}" if t else eid


FASES = [
    ("16vos",        list(range(73, 89))),
    ("8vos",         list(range(89, 97))),
    ("cuartos",      list(range(97, 101))),
    ("semi",         [101, 102]),
    ("tercer_puesto",[103]),
    ("final",        [104]),
]
NOMBRES_FASE = {
    "16vos": "16avos de Final", "8vos": "Octavos de Final",
    "cuartos": "Cuartos de Final", "semi": "Semifinales",
    "tercer_puesto": "Tercer Puesto", "final": "Final",
}

nuevos_picks: dict[int, dict] = {}

for fase, partido_ids in FASES:
    pts_label = PUNTOS_GANADOR.get(fase, "?")
    st.subheader(f"🏆 {NOMBRES_FASE[fase]}  (+{pts_label} pts por ganador)")
    cols = st.columns(min(len(partido_ids), 4))

    for i, pid in enumerate(partido_ids):
        col = cols[i % len(cols)]
        fix = fixture.get(pid, {})
        loc_id, vis_id = resolver_equipos(pid)

        prev = picks_e.get(pid, {})
        prev_ganador = prev.get("equipo_ganador")
        prev_gl = prev.get("goles_local", 0)
        prev_gv = prev.get("goles_visitante", 0)

        with col:
            st.markdown(f"**Partido {pid}** · {fix.get('ciudad', '')}")
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

            nuevos_picks[pid] = {"equipo_ganador": ganador_id, "goles_local": gl, "goles_visitante": gv}

if not locked and nuevos_picks:
    if st.button("💾 Guardar todas las eliminatorias"):
        try:
            assert_not_locked()
            rows = [{"user_id": u["id"], "partido_id": pid, **v} for pid, v in nuevos_picks.items()]
            upsert("picks_eliminatorias", rows)
            st.success("Eliminatorias guardadas.")
            st.rerun()
        except PermissionError as e:
            st.error(str(e))
