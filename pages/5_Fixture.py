import streamlit as st
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from lib.constants import NOMBRES_FASE, EQUIPOS_POR_GRUPO
from lib.flags import flag_img
from lib.data import load_fixture, load_teams

st.title("📅 Fixture")

fixture_raw = load_fixture()
teams = load_teams()

tz_bsas  = st.session_state.get("tz_bsas", False)
offset   = timedelta(hours=-3) if tz_bsas else timedelta(0)
tz_label = "BA" if tz_bsas else "UTC"
today    = (datetime.now(timezone.utc) + offset).date()

FASES_ORDER = ["grupos", "16vos", "8vos", "cuartos", "semi", "tercer_puesto", "final"]

MESES = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
         7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}
DIAS  = {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}


def parse_dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


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


def is_arg(fix):
    return fix.get("local") == "ARG" or fix.get("visitante") == "ARG"


def match_card(fix, show_date=False, idx=0):
    loc_id = fix.get("local")
    vis_id = fix.get("visitante")
    dt     = parse_dt(fix["fecha"])
    hora   = (dt + offset).strftime("%H:%M")
    ciudad = fix["ciudad"]

    if loc_id and vis_id:
        loc_t = teams.get(loc_id)
        vis_t = teams.get(vis_id)
        loc_str = f"{flag_img(loc_t)}<b>{loc_id}</b>" if loc_t else f"<b>{loc_id}</b>"
        vis_str = f"{flag_img(vis_t)}<b>{vis_id}</b>" if vis_t else f"<b>{vis_id}</b>"
    else:
        loc_str = f"<b>{fmt_ph(fix.get('ph_local', ''))}</b>"
        vis_str = f"<b>{fmt_ph(fix.get('ph_visitante', ''))}</b>"

    row_bg   = "#1A1F2E" if idx % 2 == 0 else "transparent"
    bg       = row_bg
    color    = "inherit"
    badge    = ""

    if show_date:
        dt_local  = dt + offset
        meta = f"{DIAS[dt_local.weekday()]} {dt_local.day} {MESES[dt_local.month]} · {hora} {tz_label} · {ciudad}"
    else:
        meta = f"{hora} {tz_label} · {ciudad}"

    st.markdown(f"""
<div style="padding:7px 10px;margin:3px 0;border-radius:5px;background:{bg};color:{color}">
  <div>{loc_str} &nbsp;vs&nbsp; {vis_str}{badge}</div>
  <div style="font-size:0.78em;opacity:0.7;margin-top:3px">{meta}</div>
</div>""", unsafe_allow_html=True)


tab1, tab2 = st.tabs(["📆 Por Fecha", "⚽ Por Grupos"])

# ── Tab 1: cronológico ─────────────────────────────────────────────────────────
with tab1:
    by_date = defaultdict(list)
    for fix in fixture_raw:
        d = (parse_dt(fix["fecha"]) + offset).date()
        by_date[d].append(fix)

    for date in sorted(by_date.keys()):
        partidos = sorted(by_date[date], key=lambda f: f["fecha"])
        dia_str  = f"{DIAS[date.weekday()]} {date.day} de {MESES[date.month]}"
        tiene_arg = any(is_arg(f) for f in partidos)

        if date == today:
            st.markdown(f"### 📍 HOY — {dia_str}")
        else:
            label = dia_str
            st.markdown(f"### {label}")

        for idx, fix in enumerate(partidos):
            match_card(fix, idx=idx)

# ── Tab 2: por grupos y fase ───────────────────────────────────────────────────
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
                nombres_equipos = " / ".join(teams[e]["nombre"] for e in EQUIPOS_POR_GRUPO[grupo])
                label = f"Grupo {grupo}  ·  {nombres_equipos}"
                with st.expander(label, expanded=False):
                    for idx, fix in enumerate(partidos_grupo):
                        match_card(fix, show_date=True, idx=idx)
        else:
            for idx, fix in enumerate(sorted(partidos_fase, key=lambda f: f["fecha"])):
                match_card(fix, show_date=True, idx=idx)

        st.divider()
