import streamlit as st
import json, pathlib
from lib.auth import require_login
from lib.deadline import assert_not_locked, is_locked
from lib.db import query, upsert
from lib.grupos import calcular_tabla, clasificados
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

# Calcular clasificados de cada grupo
primeros, segundos, terceros_por_grupo = {}, {}, {}
for grupo in GRUPOS:
    equipos = EQUIPOS_POR_GRUPO[grupo]
    partidos = []
    for pid in PARTIDOS_POR_GRUPO[grupo]:
        fix = fixture[pid]
        pick = picks_g.get(pid, {})
        partidos.append({
            "local": fix["equipo_local"], "visitante": fix["equipo_visitante"],
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

# Orden de fases para mostrar
FASES = [
    ("16vos", list(range(73, 89))),
    ("8vos",  list(range(89, 97))),
    ("cuartos", list(range(97, 101))),
    ("semi", [101, 102]),
    ("tercer_puesto", [103]),
    ("final", [104]),
]

NOMBRES_FASE = {
    "16vos": "16avos de Final", "8vos": "Octavos de Final",
    "cuartos": "Cuartos de Final", "semi": "Semifinales",
    "tercer_puesto": "Tercer Puesto", "final": "Final",
}

def equipo_label(eid):
    if not eid:
        return "Por definir"
    t = teams.get(eid)
    return f"{t['flag']} {t['nombre']}" if t else eid

# Construir quién ganó cada partido según picks
ganadores_picks = {}
for pid, pick in picks_e.items():
    ganadores_picks[pid] = pick.get("equipo_ganador")

nuevos_picks = {}

for fase, partido_ids in FASES:
    st.subheader(f"🏆 {NOMBRES_FASE[fase]}  (+{PUNTOS_GANADOR.get(fase, '?')} pts por ganador)")
    cols = st.columns(min(len(partido_ids), 4))

    for i, pid in enumerate(partido_ids):
        col = cols[i % len(cols)]
        fix = fixture.get(pid, {})

        # Determinar equipos del cruce
        if pid in cruces_16:
            loc_id = cruces_16[pid]["local"]
            vis_id = cruces_16[pid]["visitante"]
        else:
            # Propagar desde ganadores anteriores
            ph_l = fix.get("ph_local", "")
            ph_v = fix.get("ph_visitante", "")
            loc_id = ganadores_picks.get(int(ph_l[1:])) if ph_l.startswith("W") else None
            vis_id = ganadores_picks.get(int(ph_v[1:])) if ph_v.startswith("W") else None
            if fase == "tercer_puesto":
                src_l = int(ph_l[1:]) if ph_l.startswith("L") else None
                src_v = int(ph_v[1:]) if ph_v.startswith("L") else None
                all_semi = ganadores_picks.get(101), ganadores_picks.get(102)
                semi_equipos_l = {cruces_16.get(97, {}).get("local"), cruces_16.get(97, {}).get("visitante")} if ph_l == "L101" else {cruces_16.get(99, {}).get("local"), cruces_16.get(99, {}).get("visitante")}
                loc_id = None
                vis_id = None

        prev = picks_e.get(pid, {})
        prev_ganador = prev.get("equipo_ganador")
        prev_gl = prev.get("goles_local", 0)
        prev_gv = prev.get("goles_visitante", 0)

        with col:
            st.markdown(f"**Partido {pid}** · {fix.get('ciudad', '')}")
            opciones = [eid for eid in [loc_id, vis_id] if eid]
            etiquetas = [equipo_label(e) for e in opciones]

            if not opciones:
                st.caption("Equipos por definir según picks anteriores.")
                continue

            idx_prev = opciones.index(prev_ganador) if prev_ganador in opciones else 0
            ganador_sel = st.radio(
                "Ganador", etiquetas, index=idx_prev,
                key=f"e_{pid}_g", disabled=locked, horizontal=True,
            )
            ganador_id = opciones[etiquetas.index(ganador_sel)]

            col_gl, col_gv = st.columns(2)
            gl = col_gl.number_input(f"{equipo_label(loc_id)} goles", 0, 20, prev_gl,
                                     key=f"e_{pid}_l", disabled=locked)
            gv = col_gv.number_input(f"{equipo_label(vis_id)} goles", 0, 20, prev_gv,
                                     key=f"e_{pid}_v", disabled=locked)
            ganadores_picks[pid] = ganador_id
            nuevos_picks[pid] = {
                "equipo_ganador": ganador_id,
                "goles_local": gl,
                "goles_visitante": gv,
            }

if not locked and nuevos_picks:
    if st.button("💾 Guardar todas las eliminatorias"):
        try:
            assert_not_locked()
            rows = [
                {"user_id": u["id"], "partido_id": pid, **v}
                for pid, v in nuevos_picks.items()
            ]
            upsert("picks_eliminatorias", rows)
            st.success("Eliminatorias guardadas.")
            st.rerun()
        except PermissionError as e:
            st.error(str(e))
