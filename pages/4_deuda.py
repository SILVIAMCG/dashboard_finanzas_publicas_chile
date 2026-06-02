import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.calculos import financiamiento_trimestral, cargar
from utils import aplicar_estilos

st.set_page_config(page_title="Deuda | Finanzas Chile", page_icon="🏦", layout="wide")
aplicar_estilos()

# ── Datos ─────────────────────────────────────────────────────────────────────

@st.cache_data
def cargar_datos():
    fin   = financiamiento_trimestral()
    pasiv = cargar("pasivos_netos.csv")
    ipc   = cargar("ipc_trimestral.csv")

    pasiv = pasiv.merge(ipc, on=["año", "trimestre"], how="left")
    fin   = fin.merge(ipc, on=["año", "trimestre"], how="left")
    return fin, pasiv


fin_raw, pasiv_raw = cargar_datos()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filtros")

    fuente = st.selectbox("Nivel de gobierno", ["Gobierno Central", "Gobierno General"])
    modo = st.radio(
        "Valores",
        ["Nominales", "Reales (pesos 2023)"],
        help="Reales ajusta por inflación usando el IPC base 2023.",
    )

    st.divider()
    st.caption("Fuente: Ministerio de Hacienda · Elaboración propia")

# ── Preparar datos ────────────────────────────────────────────────────────────

fin   = fin_raw[fin_raw["fuente"] == fuente].copy()
pasiv = pasiv_raw[pasiv_raw["fuente"] == fuente].copy()

cols_fin   = ["ADQUISICION_NETA_AF", "PASIVOS_NETOS_INCURRIDOS", "FINANCIAMIENTO"]
cols_pasiv = ["valor"]

if modo == "Reales (pesos 2023)":
    for c in cols_fin:
        fin[c] = fin[c] / (fin["indice"] / 100)
    pasiv["valor"] = pasiv["valor"] / (pasiv["indice"] / 100)

ESCALA = 1_000_000
UNIDAD = "Billones de pesos"
fin["periodo_str"] = fin["año"].astype(str) + "-Q" + fin["trimestre"].astype(str)

# ── Título ────────────────────────────────────────────────────────────────────

st.title("🏦 Deuda y Financiamiento")
st.caption(f"{fuente} · {modo}")

# ── KPIs último trimestre ─────────────────────────────────────────────────────

ultimo = fin.sort_values(["año", "trimestre"]).iloc[-1]
penultimo = fin.sort_values(["año", "trimestre"]).iloc[-2]

k1, k2, k3 = st.columns(3)

def delta(actual, anterior):
    if anterior == 0: return None
    return f"{(actual - anterior) / abs(anterior) * 100:+.1f}%"

k1.metric(
    "Financiamiento",
    f"${ultimo['FINANCIAMIENTO']/ESCALA:,.2f}B",
    delta(ultimo["FINANCIAMIENTO"], penultimo["FINANCIAMIENTO"]),
    help="Déficit (–) o Superávit (+) del período",
)
k2.metric(
    "Adquisición Neta de Activos Financieros",
    f"${ultimo['ADQUISICION_NETA_AF']/ESCALA:,.2f}B",
    delta(ultimo["ADQUISICION_NETA_AF"], penultimo["ADQUISICION_NETA_AF"]),
    help="Cambio neto en activos financieros del Estado",
)
k3.metric(
    "Pasivos Netos Incurridos",
    f"${ultimo['PASIVOS_NETOS_INCURRIDOS']/ESCALA:,.2f}B",
    delta(ultimo["PASIVOS_NETOS_INCURRIDOS"], penultimo["PASIVOS_NETOS_INCURRIDOS"]),
    delta_color="inverse",
    help="Nueva deuda neta contraída en el período",
)

ultimo_periodo = f"{int(ultimo['año'])}-Q{int(ultimo['trimestre'])}"
st.caption(f"Último período disponible: {ultimo_periodo}")

st.divider()

# ── Financiamiento trimestral ─────────────────────────────────────────────────

st.subheader("Financiamiento trimestral: ¿cuánto se endeudó o ahorró el Estado?")

fig = go.Figure()

superavit = fin["FINANCIAMIENTO"].clip(lower=0) / ESCALA
deficit   = fin["FINANCIAMIENTO"].clip(upper=0) / ESCALA

fig.add_scatter(
    x=fin["periodo_str"], y=superavit,
    fill="tozeroy", fillcolor="rgba(21,101,192,0.2)",
    line=dict(width=0), showlegend=False, hoverinfo="skip",
)
fig.add_scatter(
    x=fin["periodo_str"], y=deficit,
    fill="tozeroy", fillcolor="rgba(198,40,40,0.2)",
    line=dict(width=0), showlegend=False, hoverinfo="skip",
)
fig.add_scatter(
    name="Financiamiento",
    x=fin["periodo_str"],
    y=fin["FINANCIAMIENTO"] / ESCALA,
    mode="lines+markers",
    line=dict(color="#37474F", width=2),
    marker=dict(
        color=["#1565C0" if v >= 0 else "#C62828" for v in fin["FINANCIAMIENTO"]],
        size=7,
    ),
    hovertemplate="%{x}<br>$%{y:,.2f}B<extra></extra>",
)
fig.add_shape(
    type="line", xref="paper", yref="y",
    x0=0, x1=1, y0=0, y1=0,
    line=dict(color="#90A4AE", width=1),
)

fig.update_layout(
    yaxis_title=UNIDAD,
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#EEEEEE", zeroline=False),
    xaxis=dict(tickangle=-45),
    margin=dict(t=20, b=60),
    height=380,
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True)
st.caption("🔵 Superávit (Estado financió a otros)  🔴 Déficit (Estado requirió financiamiento)")

# ── Endeudamiento externo vs interno ─────────────────────────────────────────

st.subheader("Endeudamiento neto: externo vs interno por año")

ext = pasiv[pasiv["categoria"] == "endeudamiento_externo_neto"]
int_ = pasiv[pasiv["categoria"] == "endeudamiento_interno_neto"]

ext_anual  = ext.groupby("año")["valor"].sum().reset_index()
int_anual  = int_.groupby("año")["valor"].sum().reset_index()

fig2 = go.Figure()
fig2.add_bar(
    name="Externo",
    x=ext_anual["año"].astype(str),
    y=ext_anual["valor"] / ESCALA,
    marker_color="#1565C0",
    hovertemplate="Externo %{x}: $%{y:,.2f}B<extra></extra>",
)
fig2.add_bar(
    name="Interno",
    x=int_anual["año"].astype(str),
    y=int_anual["valor"] / ESCALA,
    marker_color="#42A5F5",
    hovertemplate="Interno %{x}: $%{y:,.2f}B<extra></extra>",
)
fig2.add_shape(
    type="line", xref="paper", yref="y",
    x0=0, x1=1, y0=0, y1=0,
    line=dict(color="#90A4AE", width=1),
)

fig2.update_layout(
    barmode="group",
    yaxis_title=UNIDAD,
    legend=dict(orientation="h", y=1.08),
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#EEEEEE", zeroline=False),
    margin=dict(t=40, b=20),
    height=360,
)

st.plotly_chart(fig2, use_container_width=True)
st.caption(
    "Valores positivos = el Estado se endeudó (más deuda nueva que la que pagó).  "
    "Valores negativos = el Estado pagó más deuda de la que contrajo."
)

# ── Bono de reconocimiento ────────────────────────────────────────────────────

st.subheader("Bono de Reconocimiento")
st.caption(
    "Deuda del Estado con quienes cotizaron en el sistema antiguo de pensiones "
    "(INP/AFP) antes de 1981."
)

bono = pasiv[pasiv["categoria"] == "bono_de_reconocimiento"]
bono_anual = bono.groupby("año")["valor"].sum().reset_index()

fig3 = go.Figure()
fig3.add_bar(
    x=bono_anual["año"].astype(str),
    y=bono_anual["valor"] / ESCALA,
    marker_color="#78909C",
    hovertemplate="%{x}: $%{y:,.2f}B<extra></extra>",
)
fig3.update_layout(
    yaxis_title=UNIDAD,
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#EEEEEE"),
    margin=dict(t=20, b=20),
    height=280,
    showlegend=False,
)
st.plotly_chart(fig3, use_container_width=True)
