import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from api.conect import siete
from api.data import indices_remuneraciones

INDICES_VALIDOS = list(indices_remuneraciones.keys())  # ["nominal", "real", "ipc"]


def _serie_completa(indice: str) -> pd.Series:
    """Descarga el histórico completo del índice indicado desde la API del Banco Central."""
    if indice not in indices_remuneraciones:
        raise ValueError(f"Índice '{indice}' no válido. Opciones: {INDICES_VALIDOS}")
    codigo = indices_remuneraciones[indice]
    df = siete.cuadro(series=[codigo], nombres=[indice])
    return df[indice].dropna()


def equivalente_sueldo(sueldo_actual: float, anio_objetivo: int, indice: str = "ipc") -> float:
    """Calcula a cuánto equivale `sueldo_actual` (a valores de hoy) en `anio_objetivo`.

    Usa como deflactor el índice indicado ("nominal", "real" o "ipc"), comparando el
    último valor disponible de la serie contra el promedio del año objetivo.
    """
    serie = _serie_completa(indice)

    valor_actual = serie.iloc[-1]
    valor_objetivo = serie[serie.index.year == anio_objetivo].mean()

    if pd.isna(valor_objetivo):
        raise ValueError(f"No hay datos de '{indice}' para el año {anio_objetivo}.")

    return sueldo_actual * (valor_objetivo / valor_actual)


if __name__ == "__main__":
    for indice in INDICES_VALIDOS:
        eq = equivalente_sueldo(600_000, 2015, indice)
        print(f"{indice}: $600.000 de hoy equivalen a ${eq:,.0f} en 2015")
