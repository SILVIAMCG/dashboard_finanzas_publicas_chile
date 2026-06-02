import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.calculos import totales_trimestral, cargar
from utils import aplicar_estilos

st.set_page_config(page_title="Ingresos y Gastos | Finanzas Chile", page_icon="📈", layout="wide")
aplicar_estilos()

# ── Datos ─────────────────────────────────────────────────────────────────────

@st.cache_data
def cargar_datos():
    tot = totales_trimestral()
    ipc = cargar("ipc_trimestral.csv")
    return tot.merge(ipc, on=["año", "trimestre"], how="left")


df_raw = cargar_datos()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filtros")

    fuente = st.selectbox(
        "Nivel de gobierno",
        ["Gobierno Central", "Gobierno General"],
    )
    modo = st.radio(
        "Valores",
        ["Nominales", "Reales (pesos 2023)"],
        help="Reales ajusta por inflación usando el IPC base 2023.",
    )
    rango = st.slider(
        "Rango de años",
        min_value=2017, max_value=2025,
        value=(2017, 2025), step=1,
    )

    st.divider()
    st.caption("Fuente: Ministerio de Hacienda · Elaboración propia")

# ── Preparar datos ────────────────────────────────────────────────────────────

df = df_raw[
    (df_raw["fuente"] == fuente) &
    (df_raw["año"].between(*rango))
].copy()

if modo == "Reales (pesos 2023)":
    for c in ["TOTAL_INGRESOS", "TOTAL_GASTOS", "PRESTAMO_NETO"]:
        df[c] = df[c] / (df["indice"] / 100)

ESCALA = 1_000_000
UNIDAD = "Billones de pesos"
df["periodo_str"] = df["año"].astype(str) + "-Q" + df["trimestre"].astype(str)

# ── Título ────────────────────────────────────────────────────────────────────

st.title("📈 Evolución de Ingresos y Gastos")
st.caption(f"{fuente} · {rango[0]}–{rango[1]} · {modo}")

# ── Gráfico principal: líneas ─────────────────────────────────────────────────

st.subheader("Total ingresos vs total gastos por trimestre")

fig = go.Figure()

fig.add_scatter(
    name="Ingresos",
    x=df["periodo_str"],
    y=df["TOTAL_INGRESOS"] / ESCALA,
    mode="lines+markers",
    line=dict(color="#1565C0", width=2),
    marker=dict(size=5),
    hovertemplate="%{x}<br>Ingresos: $%{y:,.2f}B<extra></extra>",
)
fig.add_scatter(
    name="Gastos",
    x=df["periodo_str"],
    y=df["TOTAL_GASTOS"] / ESCALA,
    mode="lines+markers",
    line=dict(color="#C62828", width=2),
    marker=dict(size=5),
    hovertemplate="%{x}<br>Gastos: $%{y:,.2f}B<extra></extra>",
)

# Área entre curvas: verde cuando ingreso > gasto, rojo al revés
fig.add_scatter(
    name="Brecha (Ing > Gas)",
    x=df["periodo_str"],
    y=df["TOTAL_INGRESOS"] / ESCALA,
    fill=None, line=dict(width=0), showlegend=False, hoverinfo="skip",
)
fig.add_scatter(
    name="Superávit / Déficit",
    x=df["periodo_str"],
    y=df["TOTAL_GASTOS"] / ESCALA,
    fill="tonexty",
    fillcolor="rgba(198,40,40,0.12)",
    line=dict(width=0),
    showlegend=True,
    hoverinfo="skip",
)

fig.update_layout(
    yaxis_title=UNIDAD,
    legend=dict(orientation="h", y=1.1),
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#EEEEEE"),
    xaxis=dict(tickangle=-45),
    margin=dict(t=40, b=60),
    height=430,
)

st.plotly_chart(fig, use_container_width=True)

# ── Variación anual ───────────────────────────────────────────────────────────

st.subheader("Variación anual (respecto al mismo trimestre del año anterior)")

df_sorted = df.sort_values(["año", "trimestre"])
df_sorted["var_ing"] = df_sorted["TOTAL_INGRESOS"].pct_change(4) * 100
df_sorted["var_gas"] = df_sorted["TOTAL_GASTOS"].pct_change(4) * 100
df_var = df_sorted.dropna(subset=["var_ing"])

fig2 = go.Figure()
fig2.add_bar(
    name="Var. Ingresos",
    x=df_var["periodo_str"],
    y=df_var["var_ing"].round(1),
    marker_color="#1565C0",
    opacity=0.8,
    hovertemplate="%{x}<br>Ingresos: %{y:+.1f}%<extra></extra>",
)
fig2.add_bar(
    name="Var. Gastos",
    x=df_var["periodo_str"],
    y=df_var["var_gas"].round(1),
    marker_color="#E53935",
    opacity=0.8,
    hovertemplate="%{x}<br>Gastos: %{y:+.1f}%<extra></extra>",
)
fig2.add_hline(y=0, line_color="#90A4AE", line_width=1)

fig2.update_layout(
    barmode="group",
    yaxis_title="Variación % anual",
    legend=dict(orientation="h", y=1.1),
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#EEEEEE"),
    xaxis=dict(tickangle=-45),
    margin=dict(t=40, b=60),
    height=380,
)

st.plotly_chart(fig2, use_container_width=True)

# ── Tabla resumen anual ───────────────────────────────────────────────────────

with st.expander("Ver tabla resumen anual"):
    anual = (
        df.groupby("año")[["TOTAL_INGRESOS", "TOTAL_GASTOS", "PRESTAMO_NETO"]]
        .sum()
        .reset_index()
    )
    anual.columns = ["Año", "Total Ingresos", "Total Gastos", "Balance"]
    for col in ["Total Ingresos", "Total Gastos", "Balance"]:
        anual[col] = (anual[col] / ESCALA).map(lambda v: f"${v:,.2f}B")
    st.dataframe(anual, use_container_width=True, hide_index=True)
