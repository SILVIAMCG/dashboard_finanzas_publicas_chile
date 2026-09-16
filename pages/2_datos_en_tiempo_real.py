import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date

import altair as alt
import streamlit as st

from scripts.remuneraciones import equivalente_sueldo
from scripts.operaciones import CLASIFICACIONES, KPI, obtener_valores, obtener_valores_grupo
from utils import aplicar_estilos

st.set_page_config(page_title="Datos en tiempo real | Finanzas Chile", page_icon="🔴", layout="wide")
aplicar_estilos()

st.title("🔴 Datos en tiempo real")
st.caption("Consultas en vivo a la API del Banco Central de Chile")

# ── Buscador de sueldo equivalente ──────────────────────────────────────────

st.header("💰 Calculadora de sueldo equivalente")

OPCIONES_INDICE = {
    "IPC (poder adquisitivo)": "ipc",
    "Índice nominal de remuneraciones": "nominal",
    "Índice real de remuneraciones": "real",
}

col1, col2, col3 = st.columns(3)
with col1:
    sueldo = st.number_input("Sueldo actual (CLP)", min_value=0, value=600_000, step=10_000)
with col2:
    anio_objetivo = st.number_input(
        "Año objetivo", min_value=1990, max_value=date.today().year, value=2015, step=1
    )
with col3:
    etiqueta_indice = st.selectbox("Índice a usar", list(OPCIONES_INDICE.keys()))
    indice = OPCIONES_INDICE[etiqueta_indice]


@st.cache_data(ttl=3600, show_spinner="Consultando API del Banco Central...")
def _calcular_equivalente(sueldo, anio, indice):
    return equivalente_sueldo(sueldo, anio, indice)


if sueldo > 0:
    try:
        equivalente = _calcular_equivalente(sueldo, anio_objetivo, indice)
        st.metric(f"Equivalente en {anio_objetivo}", f"${equivalente:,.0f}")
    except ValueError as e:
        st.error(str(e))

#Buscador de indicadores clave
st.header("📈 Buscador de indicadores clave")

anio_kpi = st.number_input(
    "Año", min_value=1990, max_value=date.today().year, value=date.today().year, step=1, key="anio_kpi"
)


@st.cache_data(ttl=3600, show_spinner="Consultando API del Banco Central...")
def _obtener_valores_grupo(grupo, anio):
    return obtener_valores_grupo(grupo, anio)


def _etiqueta(texto: str) -> str:
    return texto.replace("_", " ").capitalize()


def _grafico_barras_kpi(totales) -> alt.Chart:
    datos = totales.round(0).astype(int).rename_axis("Item").reset_index(name="Total anual")
    return (
        alt.Chart(datos)
        .mark_bar(color="#4C78A8")
        .encode(
            x=alt.X("Total anual:Q", title="Total anual (CLP)", axis=alt.Axis(format=",d")),
            y=alt.Y(
                "Item:N",
                title=None,
                sort="-x",
                axis=alt.Axis(labelColor="#1f2937", labelFontWeight="bold", labelAlign="right", labelLimit=250),
            ),
            tooltip=[alt.Tooltip("Item:N", title="Item"), alt.Tooltip("Total anual:Q", format=",d")],
        )
    )


columnas_kpi = st.columns(len(KPI))
for columna, (nombre_grupo, items_grupo) in zip(columnas_kpi, KPI.items()):
    with columna:
        try:
            df_grupo = _obtener_valores_grupo(items_grupo, anio_kpi)
            totales = df_grupo.sum().rename("Total anual")
            totales.index = [_etiqueta(item) for item in totales.index]
            st.subheader(_etiqueta(nombre_grupo))
            st.altair_chart(_grafico_barras_kpi(totales), use_container_width=True)
        except ValueError as e:
            st.error(str(e))

# ── Buscador de operaciones ─────────────────────────────────────────────────

st.header("📊 Buscador de operaciones")

col1, col2, col3 = st.columns(3)
with col1:
    clasificacion = st.selectbox("Clasificación", list(CLASIFICACIONES.keys()), format_func=_etiqueta)
with col2:
    item = st.selectbox("Item", list(CLASIFICACIONES[clasificacion].keys()), format_func=_etiqueta)
with col3:
    anio_operacion = st.number_input(
        "Año", min_value=1990, max_value=date.today().year, value=date.today().year, step=1, key="anio_operacion"
    )


@st.cache_data(ttl=3600, show_spinner="Consultando API del Banco Central...")
def _obtener_valores(item, anio):
    return obtener_valores(item, anio, CLASIFICACIONES)


def _grafico_lineas_operacion(df, columna_valor: str) -> alt.Chart:
    datos = df.round(0).reset_index()
    columna_fecha = datos.columns[0]
    return (
        alt.Chart(datos)
        .mark_line(color="#4C78A8", point=True)
        .encode(
            x=alt.X(
                f"{columna_fecha}:T",
                timeUnit="yearmonth",
                title=None,
                axis=alt.Axis(format="%b %Y", tickCount="month", labelColor="#1f2937", labelFontWeight="bold"),
            ),
            y=alt.Y(
                f"{columna_valor}:Q",
                title="Valor (CLP)",
                axis=alt.Axis(format=",d", labelColor="#1f2937", labelFontWeight="bold"),
            ),
            tooltip=[
                alt.Tooltip(f"{columna_fecha}:T", title="Fecha", format="%b %Y"),
                alt.Tooltip(f"{columna_valor}:Q", format=",d"),
            ],
        )
    )


try:
    df = _obtener_valores(item, anio_operacion)
    st.altair_chart(_grafico_lineas_operacion(df, item), use_container_width=True)
    st.dataframe(df.round(0).astype(int), use_container_width=True)
except ValueError as e:
    st.error(str(e))

