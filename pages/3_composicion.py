import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.calculos import cargar
from utils import aplicar_estilos

st.set_page_config(page_title="Composición | Finanzas Chile", page_icon="🧩", layout="wide")
aplicar_estilos()

# ── Etiquetas amigables ───────────────────────────────────────────────────────

NOMBRES_GASTOS = {
    "Personal":                                      "Personal",
    "Bienes y servicios de consumo y producción":    "Bienes y Servicios",
    "Intereses":                                     "Intereses de Deuda",
    "Subsidios y donaciones":                        "Subsidios y Donaciones",
    "Prestaciones previsionales":                    "Prestaciones Previsionales",
    "Otros":                                         "Otros Gastos",
}
NOMBRES_INGRESOS = {
    "Ingresos tributarios netos":   "Impuestos",
    "Traspasos Codelco":            "Traspasos Codelco",
    "Imposiciones previsionales":   "Cotizaciones Previsionales",
    "Donaciones":                   "Donaciones",
    "Rentas de la propiedad":       "Rentas de la Propiedad",
    "Ingresos de operación":        "Ingresos de Operación",
    "Otros ingresos":               "Otros Ingresos",
}

COLORES_GASTOS = [
    "#1565C0", "#1976D2", "#1E88E5", "#42A5F5",
    "#90CAF9", "#C62828",
]
COLORES_INGRESOS = [
    "#1B5E20", "#2E7D32", "#388E3C", "#43A047",
    "#66BB6A", "#A5D6A7", "#E8F5E9",
]

# ── Datos ─────────────────────────────────────────────────────────────────────

@st.cache_data
def cargar_datos():
    ing = cargar("ingresos_largo.csv")
    gas = cargar("gastos_largo.csv")
    ipc = cargar("ipc_trimestral.csv")
    return ing, gas, ipc


ing_raw, gas_raw, ipc = cargar_datos()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filtros")

    fuente = st.selectbox("Nivel de gobierno", ["Gobierno Central", "Gobierno General"])
    seccion = st.radio("Ver", ["Gastos", "Ingresos"])
    modo = st.radio(
        "Valores",
        ["Nominales", "Reales (pesos 2023)"],
        help="Reales ajusta por inflación usando el IPC base 2023.",
    )
    año_donut = st.selectbox("Año para el detalle", sorted(ing_raw["año"].unique(), reverse=True))

    st.divider()
    st.caption("Fuente: Ministerio de Hacienda · Elaboración propia")

# ── Preparar datos ────────────────────────────────────────────────────────────

if seccion == "Gastos":
    df_raw = gas_raw.copy()
    cat_total = "GASTOS"
    nombres = NOMBRES_GASTOS
    colores = COLORES_GASTOS
else:
    df_raw = ing_raw.copy()
    cat_total = "INGRESOS"
    nombres = NOMBRES_INGRESOS
    colores = COLORES_INGRESOS

df = df_raw[df_raw["fuente"] == fuente].copy()
df = df.merge(ipc, on=["año", "trimestre"], how="left")

if modo == "Reales (pesos 2023)":
    df["valor"] = df["valor"] / (df["indice"] / 100)

ESCALA = 1_000_000
UNIDAD = "Billones de pesos"

# Subcategorías (sin el total agregado)
df_sub = df[df["categoria"] != cat_total].copy()
df_sub["categoria"] = df_sub["categoria"].map(nombres).fillna(df_sub["categoria"])

# Agregar por año
anual = (
    df_sub.groupby(["año", "categoria"])["valor"]
    .sum()
    .reset_index()
)
anual["valor_B"] = anual["valor"] / ESCALA

# ── Título ────────────────────────────────────────────────────────────────────

st.title("🧩 Composición de " + seccion)
st.caption(f"{fuente} · {modo}")

# ── Gráfico barras apiladas ───────────────────────────────────────────────────

st.subheader(f"¿En qué se distribuyen los {seccion.lower()} cada año?")

categorias = anual["categoria"].unique().tolist()

fig = go.Figure()
for i, cat in enumerate(categorias):
    d = anual[anual["categoria"] == cat].sort_values("año")
    fig.add_bar(
        name=cat,
        x=d["año"].astype(str),
        y=d["valor_B"],
        marker_color=colores[i % len(colores)],
        hovertemplate=f"{cat}<br>%{{x}}: $%{{y:,.2f}}B<extra></extra>",
    )

fig.update_layout(
    barmode="stack",
    yaxis_title=UNIDAD,
    legend=dict(orientation="h", y=-0.25, font=dict(size=11)),
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#EEEEEE"),
    margin=dict(t=20, b=120),
    height=460,
)

st.plotly_chart(fig, use_container_width=True)

# ── Donut año seleccionado ────────────────────────────────────────────────────

st.subheader(f"Detalle {año_donut} — ¿qué porcentaje representa cada ítem?")

donut_data = anual[anual["año"] == año_donut].sort_values("valor_B", ascending=False)

col1, col2 = st.columns([1, 1])

with col1:
    fig2 = go.Figure(go.Pie(
        labels=donut_data["categoria"],
        values=donut_data["valor_B"],
        hole=0.45,
        marker_colors=colores,
        textinfo="label+percent",
        textfont=dict(size=12),
        hovertemplate="%{label}<br>$%{value:,.2f}B · %{percent}<extra></extra>",
    ))
    fig2.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=380,
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    total_año = donut_data["valor_B"].sum()
    st.markdown(f"**Total {seccion} {año_donut}: ${total_año:,.2f}B**")
    st.markdown("---")
    for _, row in donut_data.iterrows():
        pct = row["valor_B"] / total_año * 100
        st.markdown(f"**{row['categoria']}**")
        st.progress(int(pct), text=f"${row['valor_B']:,.2f}B · {pct:.1f}%")
        st.markdown("")
