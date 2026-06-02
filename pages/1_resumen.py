import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.calculos import totales_trimestral, cargar
from utils import aplicar_estilos

st.set_page_config(page_title="Resumen | Finanzas Chile", page_icon="📊", layout="wide")

aplicar_estilos()

# ── Datos ────────────────────────────────────────────────────────────────────

@st.cache_data
def cargar_datos():
    tot = totales_trimestral()
    ipc = cargar("ipc_trimestral.csv")
    df = tot.merge(ipc, on=["año", "trimestre"], how="left")
    return df


df_raw = cargar_datos()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filtros")

    fuente = st.selectbox(
        "Nivel de gobierno",
        ["Gobierno Central", "Gobierno General"],
        help="Central incluye ministerios y servicios. General agrega municipalidades.",
    )

    año = st.selectbox("Año", sorted(df_raw["año"].unique(), reverse=True))

    modo = st.radio(
        "Valores",
        ["Nominales", "Reales (pesos 2023)"],
        help="Reales ajusta por inflación usando el IPC base 2023.",
    )

    st.divider()
    st.caption("Fuente: Ministerio de Hacienda · Elaboración propia")

# ── Preparar datos ────────────────────────────────────────────────────────────

df = df_raw[df_raw["fuente"] == fuente].copy()

# Ajuste real: dividir por (ipc/100) para expresar en pesos de 2023
cols_val = ["TOTAL_INGRESOS", "TOTAL_GASTOS", "PRESTAMO_NETO"]
if modo == "Reales (pesos 2023)":
    for c in cols_val:
        df[c] = df[c] / (df["indice"] / 100)

ESCALA = 1_000_000          # mostrar en billones
UNIDAD = "Billones de pesos"

def fmt(valor):
    """Formatea un valor en billones con 2 decimales."""
    return f"{valor / ESCALA:,.2f}"

def delta_pct(actual, anterior):
    if anterior == 0:
        return None
    return f"{(actual - anterior) / abs(anterior) * 100:+.1f}%"

# Año seleccionado y año anterior
año_sel  = df[df["año"] == año]
año_ant  = df[df["año"] == año - 1]

ing_sel  = año_sel["TOTAL_INGRESOS"].sum()
gas_sel  = año_sel["TOTAL_GASTOS"].sum()
bal_sel  = año_sel["PRESTAMO_NETO"].sum()

ing_ant  = año_ant["TOTAL_INGRESOS"].sum() if len(año_ant) else 0
gas_ant  = año_ant["TOTAL_GASTOS"].sum()   if len(año_ant) else 0

# ── KPIs ──────────────────────────────────────────────────────────────────────

st.title("📊 Resumen fiscal")
st.caption(f"{fuente} · {año} · {modo}")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Total Ingresos",
    f"${fmt(ing_sel)}B",
    delta_pct(ing_sel, ing_ant),
    help=UNIDAD,
)
k2.metric(
    "Total Gastos",
    f"${fmt(gas_sel)}B",
    delta_pct(gas_sel, gas_ant),
    delta_color="inverse",
    help=UNIDAD,
)

balance_label = "Superávit" if bal_sel >= 0 else "Déficit"
k3.metric(
    balance_label,
    f"${fmt(abs(bal_sel))}B",
    help=f"Préstamo neto / Endeudamiento neto · {UNIDAD}",
)

pct_bal = bal_sel / ing_sel * 100 if ing_sel else 0
k4.metric(
    "Balance s/ Ingresos",
    f"{pct_bal:+.1f}%",
    help="Balance como porcentaje de los ingresos totales del año",
)

st.divider()

# ── Gráfico trimestral ────────────────────────────────────────────────────────

st.subheader(f"Ingresos y gastos por trimestre — {año}")

df_año = año_sel.sort_values("trimestre")
trimestres = [f"T{t}" for t in df_año["trimestre"]]

colores_ing = "#1565C0"
colores_gas = ["#C62828" if p < 0 else "#E53935"
               for p in df_año["PRESTAMO_NETO"]]

fig = go.Figure()

fig.add_bar(
    name="Ingresos",
    x=trimestres,
    y=df_año["TOTAL_INGRESOS"] / ESCALA,
    marker_color=colores_ing,
    text=(df_año["TOTAL_INGRESOS"] / ESCALA).map(lambda v: f"${v:,.1f}B"),
    textposition="outside",
)
fig.add_bar(
    name="Gastos",
    x=trimestres,
    y=df_año["TOTAL_GASTOS"] / ESCALA,
    marker_color="#E53935",
    text=(df_año["TOTAL_GASTOS"] / ESCALA).map(lambda v: f"${v:,.1f}B"),
    textposition="outside",
)

fig.update_layout(
    barmode="group",
    yaxis_title=f"{UNIDAD}",
    legend=dict(orientation="h", y=1.08),
    margin=dict(t=40, b=20),
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#EEEEEE"),
    height=420,
)

st.plotly_chart(fig, use_container_width=True)

# ── Balance histórico ─────────────────────────────────────────────────────────

st.subheader("Balance anual histórico (2017 – 2025)")

# Este gráfico siempre muestra todos los años para dar contexto histórico completo
bal_anual = (
    df.groupby("año")["PRESTAMO_NETO"]
    .sum()
    .reset_index()
)
bal_anual["valor_B"] = bal_anual["PRESTAMO_NETO"] / ESCALA
bal_anual["superavit"] = bal_anual["valor_B"].clip(lower=0)
bal_anual["deficit"]   = bal_anual["valor_B"].clip(upper=0)

fig2 = go.Figure()

# Área rellena superávit (sobre 0)
fig2.add_scatter(
    x=bal_anual["año"], y=bal_anual["superavit"],
    fill="tozeroy", fillcolor="rgba(21,101,192,0.25)",
    line=dict(width=0), showlegend=False, hoverinfo="skip",
)
# Área rellena déficit (bajo 0)
fig2.add_scatter(
    x=bal_anual["año"], y=bal_anual["deficit"],
    fill="tozeroy", fillcolor="rgba(198,40,40,0.25)",
    line=dict(width=0), showlegend=False, hoverinfo="skip",
)
# Línea principal coloreada por signo
fig2.add_scatter(
    x=bal_anual["año"],
    y=bal_anual["valor_B"],
    mode="lines+markers+text",
    line=dict(color="#37474F", width=2),
    marker=dict(
        color=["#1565C0" if v >= 0 else "#C62828" for v in bal_anual["valor_B"]],
        size=10,
    ),
    text=bal_anual["valor_B"].map(lambda v: f"${v:,.1f}B"),
    textposition=[
        "top center" if v >= 0 else "bottom center"
        for v in bal_anual["valor_B"]
    ],
    textfont=dict(size=11),
    showlegend=False,
    hovertemplate="%{x}: $%{y:,.2f}B<extra></extra>",
)
# Línea de referencia en 0
fig2.add_hline(y=0, line_color="#90A4AE", line_width=1)

# Resaltar el año seleccionado con un marcador naranja encima
bal_año = bal_anual[bal_anual["año"] == año]
if not bal_año.empty:
    fig2.add_scatter(
        x=bal_año["año"],
        y=bal_año["valor_B"],
        mode="markers",
        marker=dict(color="#FFA000", size=14, symbol="diamond"),
        showlegend=False,
        hovertemplate=f"{año} (seleccionado): $%{{y:,.2f}}B<extra></extra>",
    )

fig2.update_layout(
    yaxis_title=f"{UNIDAD}",
    xaxis=dict(tickmode="linear", dtick=1),
    margin=dict(t=20, b=20),
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#EEEEEE", zeroline=False),
    height=380,
)

st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "🔵 Área azul = superávit  🔴 Área roja = déficit  "
    "🔶 Diamante naranja = año seleccionado en el filtro"
)
