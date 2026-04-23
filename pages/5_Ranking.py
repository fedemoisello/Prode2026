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
        except Exception as e:
            st.warning(f"Error calculando puntos de {user['nombre']}: {e}")
            resultados.append({"nombre": user["nombre"], "total": 0,
                               "grupos_resultado": 0, "grupos_clasificados": 0, "eliminatorias": 0})

resultados.sort(key=lambda x: x["total"], reverse=True)

rows_html = ""
for i, r in enumerate(resultados, 1):
    medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}."
    bg = "#1A1F2E" if i % 2 == 0 else "transparent"
    grupos_pts = r["grupos_resultado"] + r["grupos_clasificados"]
    rows_html += f"""<tr style="background:{bg}">
        <td style="padding:8px 6px;text-align:center">{medal}</td>
        <td style="padding:8px 6px"><b>{r['nombre']}</b></td>
        <td style="padding:8px 6px;text-align:center">{grupos_pts}</td>
        <td style="padding:8px 6px;text-align:center">{r['eliminatorias']}</td>
        <td style="padding:8px 6px;text-align:center"><b>{r['total']}</b></td>
    </tr>"""

st.markdown(f"""
<table style="width:100%;border-collapse:collapse;font-family:inherit">
<thead><tr style="opacity:0.5;font-size:0.82em;border-bottom:1px solid #444">
    <th style="padding:6px;text-align:center">Pos.</th>
    <th style="padding:6px;text-align:left">Nombre</th>
    <th style="padding:6px;text-align:center">Grupos</th>
    <th style="padding:6px;text-align:center">Elim.</th>
    <th style="padding:6px;text-align:center">Total</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
""", unsafe_allow_html=True)
