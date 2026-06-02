# 🇨🇱 Dashboard de Finanzas Públicas de Chile

Dashboard interactivo que muestra la evolución de los ingresos y gastos del Estado de Chile entre 2017 y 2025, construido con **Streamlit** y **Plotly**.

## 🔗 Demo

> _[Enlace al deploy en Streamlit Community Cloud]_

---

## 📊 ¿Qué muestra el dashboard?

| Página | Contenido |
|---|---|
| **Resumen** | KPIs fiscales del año seleccionado, balance trimestral y evolución histórica del superávit/déficit |
| **Ingresos y Gastos** | Línea histórica 2017–2025, variación anual y tabla resumen |
| **Composición** | Desagregación de gastos e ingresos por subcategoría, con gráfico de torta por año |
| **Deuda** | Financiamiento trimestral, endeudamiento externo vs interno y Bono de Reconocimiento |

Todas las páginas permiten alternar entre **valores nominales** y **valores reales (pesos de 2023)**, descontando inflación con el IPC del INE.

---

## 🗂️ Estructura del proyecto

```
dashboard_macroeconomia_chile/
│
├── app.py                        # Página de inicio
├── utils.py                      # Estilos CSS compartidos
├── requirements.txt
│
├── pages/
│   ├── 1_resumen.py
│   ├── 2_ingresos_gastos.py
│   ├── 3_composicion.py
│   └── 4_deuda.py
│
├── scripts/
│   ├── calculos.py               # Funciones reutilizables de cálculo
│   ├── procesar_ingresos.py      # Genera ingresos_largo.csv
│   ├── procesar_gastos.py        # Genera gastos_largo.csv
│   ├── procesar_anf.py           # Genera anf_largo.csv
│   ├── procesar_af.py            # Genera af_largo.csv
│   ├── procesar_pasivos.py       # Genera pasivos_netos.csv
│   └── procesar_ipc.py           # Genera ipc_trimestral.csv
│
├── data/
│   └── processed_data/           # CSV procesados (incluidos en el repo)
│       ├── ingresos_largo.csv
│       ├── gastos_largo.csv
│       ├── anf_largo.csv
│       ├── af_largo.csv
│       ├── pasivos_netos.csv
│       └── ipc_trimestral.csv
│
└── .streamlit/
    └── config.toml               # Tema visual
```

---

## 📦 Fuentes de datos

| Dataset | Fuente | Descripción |
|---|---|---|
| Estado de Operaciones | [Dipres - Ministerio de Hacienda](https://www.dipres.gob.cl) | Ingresos, gastos y financiamiento del Gobierno Central y General, trimestral 2017–2025 |
| IPC General | [INE Chile](https://www.ine.gob.cl) | Índice de Precios al Consumidor mensual, base 2023 = 100 |

Los archivos Excel originales **no se incluyen** en el repositorio. Los CSV en `data/processed_data/` son el resultado del pipeline de procesamiento.

---

## 🚀 Correr localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/dashboard_macroeconomia_chile.git
cd dashboard_macroeconomia_chile

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
streamlit run app.py
```

---

## 🔄 Actualizar los datos

Si tienes acceso a los archivos Excel originales, ejecuta los scripts en orden:

```bash
python scripts/procesar_ingresos.py
python scripts/procesar_gastos.py
python scripts/procesar_anf.py
python scripts/procesar_af.py
python scripts/procesar_pasivos.py
python scripts/procesar_ipc.py
```

Los CSV procesados se sobreescriben automáticamente en `data/processed_data/`.

---

## 🛠️ Stack

- [Streamlit](https://streamlit.io/) — framework del dashboard
- [Plotly](https://plotly.com/python/) — visualizaciones interactivas
- [Pandas](https://pandas.pydata.org/) — procesamiento de datos
