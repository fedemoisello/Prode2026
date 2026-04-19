import streamlit as st
from lib.auth import require_admin
from lib.db import query, upsert, update
from lib.data import load_fixture, load_teams

st.title("⚙️ Admin")

u = require_admin()

fixture_raw = load_fixture()
teams = load_teams()
fixture = {f["id"]: f for f in fixture_raw}

tab_results, tab_users = st.tabs(["Cargar resultados", "Usuarios"])

# ── Resultados reales ──────────────────────────────────────────────────────────
with tab_results:
    st.subheader("Cargar resultado real de un partido")
    results_db = {r["partido_id"]: r for r in query("results")}

    fases = ["grupos", "16vos", "8vos", "cuartos", "semi", "tercer_puesto", "final"]
    fase_sel = st.selectbox("Fase", fases)
    partidos_fase = [f for f in fixture_raw if f["fase"] == fase_sel]

    if not partidos_fase:
        st.info("No hay partidos para esta fase.")
    else:
        opciones = {f["id"]: f"P{f['id']} — {f.get('ciudad','')}" for f in partidos_fase}
        pid_sel = st.selectbox("Partido", list(opciones.keys()), format_func=lambda x: opciones[x])

        fix = fixture[pid_sel]
        res = results_db.get(pid_sel, {})

        if fix["fase"] == "grupos":
            loc = teams.get(fix.get("local"), {})
            vis = teams.get(fix.get("visitante"), {})
            c1, c2, c3 = st.columns(3)
            gl = c1.number_input(f"Goles {loc.get('nombre','Local')}", 0, 20,
                                 res.get("goles_local", 0), key="admin_gl")
            c2.markdown("**-**")
            gv = c3.number_input(f"Goles {vis.get('nombre','Visitante')}", 0, 20,
                                 res.get("goles_visitante", 0), key="admin_gv")
            finalizado = st.checkbox("Partido finalizado", res.get("finalizado", False))

            payload = {
                "partido_id": pid_sel,
                "goles_local": gl,
                "goles_visitante": gv,
                "finalizado": finalizado,
            }
        else:
            equipos_disponibles = list(teams.keys())
            ganador_prev = res.get("ganador")
            idx = equipos_disponibles.index(ganador_prev) if ganador_prev in equipos_disponibles else 0
            ganador = st.selectbox(
                "Equipo ganador", equipos_disponibles,
                format_func=lambda x: teams[x]["nombre"],
                index=idx,
            )
            c1, c2 = st.columns(2)
            gl = c1.number_input("Goles local (opcional)", 0, 20, res.get("goles_local", 0))
            gv = c2.number_input("Goles visitante (opcional)", 0, 20, res.get("goles_visitante", 0))
            finalizado = st.checkbox("Partido finalizado", res.get("finalizado", False))

            payload = {
                "partido_id": pid_sel,
                "ganador": ganador,
                "goles_local": gl,
                "goles_visitante": gv,
                "finalizado": finalizado,
            }

        # Confirmación de 2 pasos
        if st.button("Guardar resultado"):
            st.session_state["confirm_save"] = True

        if st.session_state.get("confirm_save"):
            st.warning("¿Confirmar? Esto sobreescribe el resultado existente.")
            col_yes, col_no = st.columns(2)
            if col_yes.button("Sí, guardar", type="primary"):
                upsert("results", payload)
                st.success("Guardado.")
                st.session_state["confirm_save"] = False
            if col_no.button("Cancelar"):
                st.session_state["confirm_save"] = False
                st.rerun()

# ── Usuarios ───────────────────────────────────────────────────────────────────
with tab_users:
    st.subheader("Estado de prodes")
    users = query("users", columns="id,nombre,is_admin,created_at")
    for user in users:
        pg = len(query("picks_grupos", {"user_id": user["id"]}))
        pe = len(query("picks_eliminatorias", {"user_id": user["id"]}))
        icon = "✅" if pg == 72 and pe == 32 else ("⚠️" if pg > 0 else "❌")
        st.markdown(f"{icon} **{user['nombre']}** — Grupos: {pg}/72 · Elim: {pe}/32")
