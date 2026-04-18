import streamlit as st
from lib.auth import require_login
from lib.db import query
from lib.scoring import calcular_puntos_usuario
from lib.deadline import is_locked

st.title("🏆 Ranking")

require_login()

if not is_locked():
    st.info("El ranking completo se activa cuando cierre el prode. Por ahora podés ver tu posición estimada.")

users = query("users", columns="id,nombre")
if not users:
    st.warning("No hay usuarios cargados.")
    st.stop()

resultados = []
with st.spinner("Calculando puntajes..."):
    for user in users:
        try:
            desglose = calcular_puntos_usuario(user["id"])
            resultados.append({
                "nombre": user["nombre"],
                "total": desglose["total"],
                "grupos_resultado": desglose["grupos_resultado"],
                "grupos_clasificados": desglose["grupos_clasificados"],
                "eliminatorias": desglose["eliminatorias"],
            })
        except Exception:
            resultados.append({"nombre": user["nombre"], "total": 0,
                               "grupos_resultado": 0, "grupos_clasificados": 0, "eliminatorias": 0})

resultados.sort(key=lambda x: x["total"], reverse=True)

for i, r in enumerate(resultados, 1):
    medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}."
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 2])
        col1.markdown(f"**{medal}**")
        col2.markdown(f"**{r['nombre']}**")
        col3.metric("Total", r["total"])
        col4.metric("Grupos", r["grupos_resultado"] + r["grupos_clasificados"])
        col5.metric("Elim.", r["eliminatorias"])
