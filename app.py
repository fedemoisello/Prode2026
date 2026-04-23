import streamlit as st
import extra_streamlit_components as stx
from lib.auth import get_session

st.set_page_config(
    page_title="Prode Mundial 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CookieManager inicializado una sola vez por sesión
if "_cm" not in st.session_state:
    st.session_state["_cm"] = stx.CookieManager(key="prode_cm")

u = get_session()

with st.sidebar:
    col_lbl, col_tog = st.columns([5, 1])
    col_lbl.markdown(
        '<img src="https://flagcdn.com/w20/ar.png" height="14" '
        'style="vertical-align:middle;margin-right:5px">Hora Argentina',
        unsafe_allow_html=True,
    )
    col_tog.toggle("", key="tz_bsas", value=True, label_visibility="collapsed")

pages = [
    st.Page("pages/1_Inicio.py",       title="Inicio",            icon="🏠", default=True),
    st.Page("pages/2_Fase_Grupos.py",  title="Mis Grupos",        icon="✏️"),
    st.Page("pages/3_Eliminatorias.py",title="Mis Eliminatorias", icon="✏️"),
    st.Page("pages/4_Mi_Prode.py",     title="Ver mi Prode",      icon="👁"),
    st.Page("pages/5_Fixture.py",      title="Fixture",           icon="📅"),
    st.Page("pages/5_Ranking.py",      title="Ranking",           icon="🏆"),
]
if u and u.get("is_admin"):
    pages.append(st.Page("pages/6_Admin.py", title="Admin", icon="⚙️"))

pg = st.navigation(pages)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
body { font-family: 'Poppins', sans-serif !important; }

/* ─── SIDEBAR MOBILE ──────────────────────────────────── */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        width: 220px !important;
        min-width: 220px !important;
    }
}

/* ─── FLECHA DEL SIDEBAR (sidebar cerrado) ──────────────── */
[data-testid="collapsedControl"] {
    background: #27AE60 !important;
    background-color: #27AE60 !important;
    border-radius: 0 8px 8px 0 !important;
    width: 2rem !important;
    height: 3rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border: none !important;
}
[data-testid="collapsedControl"] button,
[data-testid="collapsedControl"] > *,
[data-testid="collapsedControl"] span {
    background: #27AE60 !important;
    background-color: #27AE60 !important;
    border: none !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="collapsedControl"] button svg {
    color: white !important;
    fill: white !important;
    width: 1.2rem !important;
    height: 1.2rem !important;
}
/* ─── FLECHA DEL SIDEBAR (sidebar abierto) ───────────────── */
[data-testid="stSidebarHeader"] button,
[data-testid="stSidebarHeader"] [data-testid="baseButton-headerNoPadding"] {
    background: #27AE60 !important;
    background-color: #27AE60 !important;
    border-radius: 8px !important;
    border: none !important;
}
[data-testid="stSidebarHeader"] button svg,
[data-testid="stSidebarHeader"] [data-testid="baseButton-headerNoPadding"] svg {
    color: white !important;
    fill: white !important;
}
</style>
""", unsafe_allow_html=True)

pg.run()
