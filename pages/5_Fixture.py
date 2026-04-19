import streamlit as st
import json, pathlib
from collections import defaultdict
from datetime import datetime, timedelta, timezone

st.title("📅 Fixture")

fixture_raw = json.loads(pathlib.Path("data/fixture.json").read_text(encoding="utf-8"))
teams_raw   = json.loads(pathlib.Path("data/teams.json").read_text(encoding="utf-8"))
teams = {t["id"]: t for t in teams_raw}

tz_bsas  = st.session_state.get("tz_bsas", False)
offset   = timedelta(hours=-3) if tz_bsas else timedelta(0)
tz_label = "BA" if tz_bsas else "UTC"
today    = (datetime.now(timezone.utc) + offset).date()

NOMBRES_FASE = {
    "grupos":        "Fase de Grupos",
    "16vos":         "16avos de Final",
    "8vos":          "Octavos de Final",
    "cuartos":       "Cuartos de Final",
    "semi":          "Semifinales",
    "tercer_puesto": "Tercer Puesto",
    "final":         "Final",
}
FASES_ORDER = ["grupos", "16vos", "8vos", "cuartos", "semi", "tercer_puesto", "final"]


def parse_dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fmt_hora(s):
    return (parse_dt(s) + offset).strftime("%H:%M")


def fmt_ph(ph):
    if not ph:
        return "Por definir"
    if ph.startswith("W"):
        return f"Gan. P{ph[1:]}"
    if ph.startswith("L"):
        return f"Per. P{ph[1:]}"
    if ph[0].isdigit():
        pos = {"1": "1°", "2": "2°", "3": "Mejor 3°"}.get(ph[0], ph[0])
        return f"{pos} Gr.{ph[1:]}"
    return ph


def team_html(team_id):
    t = teams.get(team_id)
    if not t:
        return team_id
    return f'<img src="https://flagcdn.com/w20/{t["iso2"]}.png" height="14" style="vertical-align:middle;margin-right:3px"><b>{t["nombre"]}</b>'


def is_arg(fix):
    return fix.get("local") == "ARG" or fix.get("visitante") == "ARG"


def match_card(fix, show_date=False):
    loc_id = fix.get("local")
    vis_id = fix.get("visitante")
    dt     = parse_dt(fix["fecha"])
    hora   = (dt + offset).strftime("%H:%M")
    ciudad = fix["ciudad"]

    if loc_id and vis_id:
        loc_str = team_html(loc_id)
        vis_str = team_html(vis_id)
    else:
        loc_str = f"<b>{fmt_ph(fix.get('ph_local', ''))}</b>"
        vis_str = f"<b>{fmt_ph(fix.get('ph_visitante', ''))}</b>"

    arg   = is_arg(fix)
    bg    = "#5DADE2" if arg else "transparent"
    color = "white"  if arg else "inherit"
    badge = " &nbsp;🔵⚪" if arg else ""

    if show_date:
        dt_local  = dt + offset
        fecha_str = f"{DIAS[dt_local.weekday()]} {dt_local.day} {MESES[dt_local.month]} · "
    else:
        fecha_str = ""

    st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:7px 10px;margin:3px 0;border-radius:5px;
            background:{bg};color:{color}">
  <span style="flex:1">{loc_str} &nbsp;vs&nbsp; {vis_str}{badge}</span>
  <span style="white-space:nowrap;margin-left:12px;font-size:0.82em;opacity:0.85">
    {fecha_str}{hora} {tz_label} · {ciudad}
  </span>
</div>""", unsafe_allow_html=True)


tab1, tab2 = st.tabs(["📆 Por Fecha", "🏆 Por Fase"])

# ── Tab 1: cronológico ─────────────────────────────────────────────────────────
with tab1:
    by_date = defaultdict(list)
    for fix in fixture_raw:
        d = (parse_dt(fix["fecha"]) + offset).date()
        by_date[d].append(fix)

    MESES = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
             7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}
    DIAS  = {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}

    for date in sorted(by_date.keys()):
        partidos = sorted(by_date[date], key=lambda f: f["fecha"])
        dia_str  = f"{DIAS[date.weekday()]} {date.day} de {MESES[date.month]}"
        tiene_arg = any(is_arg(f) for f in partidos)

        if date == today:
            st.markdown(f"### 📍 HOY — {dia_str}")
        else:
            label = f"{'🔵⚪ ' if tiene_arg else ''}{dia_str}"
            st.markdown(f"### {label}")

        for fix in partidos:
            match_card(fix)

# ── Tab 2: por fase ────────────────────────────────────────────────────────────
with tab2:
    for fase in FASES_ORDER:
        partidos_fase = [f for f in fixture_raw if f["fase"] == fase]
        if not partidos_fase:
            continue

        st.subheader(NOMBRES_FASE[fase])

        if fase == "grupos":
            grupos = sorted(set(f["grupo"] for f in partidos_fase))
            for grupo in grupos:
                partidos_grupo = sorted(
                    [f for f in partidos_fase if f["grupo"] == grupo],
                    key=lambda f: f["fecha"],
                )
                tiene_arg = any(is_arg(f) for f in partidos_grupo)
                label = f"Grupo {grupo}{'  🔵⚪' if tiene_arg else ''}"
                with st.expander(label, expanded=tiene_arg):
                    for fix in partidos_grupo:
                        match_card(fix, show_date=True)
        else:
            for fix in sorted(partidos_fase, key=lambda f: f["fecha"]):
                match_card(fix, show_date=True)

        st.divider()
