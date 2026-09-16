import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils import aplicar_estilos

#streamlit run app.py

st.set_page_config(
    page_title="Finanzas Públicas Chile",
    page_icon="🇨🇱",
    layout="wide",
)

aplicar_estilos()

st.title("🇨🇱 Finanzas Públicas de Chile")
st.subheader("2017 – 2026 · Datos del Ministerio de Hacienda")

st.markdown("""
Este dashboard muestra cómo el Estado de Chile recauda y gasta sus recursos,
trimestre a trimestre. Incluye datos históricos desde 2017 a 2025 y datos en tiempo real hasta el 2026.

Los datos provienen del **Estado de Operaciones** publicado por el
Ministerio de Hacienda, e incluyen tanto el **Gobierno Central** como el
**Gobierno General** (que agrega municipalidades y otras entidades).

---

### ¿Qué puedes explorar?

| Página | Contenido |
|---|---|
| 📊 **Resumen** | Ingresos vs gastos del período, superávit o déficit |
| 🕒 **Datos en tiempo real** | Información actualizada sobre la situación financiera |
| 📈 **Ingresos y Gastos** | Evolución histórica, valores nominales y reales |
| 🧩 **Composición** | En qué se gasta y de dónde vienen los ingresos |
| 🏦 **Deuda** | Endeudamiento neto y financiamiento |

Usa el **menú lateral** para navegar entre páginas.

---
""")

st.info(
    "💡 Puedes ver los valores en **pesos corrientes** (nominales) "
    "o en **pesos de 2023** (reales, descontando la inflación) "
    "usando el selector disponible en cada página.",
    icon="💡",
)

with st.expander("ℹ️ Glosario básico"):
    st.markdown("""
- **Gobierno Central**: Ministerios, servicios públicos y Tesoro.
- **Gobierno General**: Gobierno Central + municipalidades + otras entidades públicas.
- **Superávit**: el gobierno recaudó más de lo que gastó.
- **Déficit**: el gobierno gastó más de lo que recaudó.
- **Valores reales**: cifras ajustadas por inflación (IPC base 2023 = 100),
  permiten comparar montos de distintos años como si fueran pesos del mismo valor.
- **Préstamo neto / Endeudamiento neto**: diferencia entre ingresos y gastos totales
  incluyendo inversiones. Si es negativo, el gobierno necesitó endeudarse o usar reservas.
""")
