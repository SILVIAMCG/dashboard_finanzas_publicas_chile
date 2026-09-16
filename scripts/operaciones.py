import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from api.conect import siete
from api.data import operaciones_no_financieras, operaciones_financieras, gasto_corriente, gasto_de_capital

CLASIFICACIONES = {
    "operaciones_no_financieras": operaciones_no_financieras,
    "operaciones_financieras": operaciones_financieras,
}
KPI = {
    "gasto_corriente": gasto_corriente,
    "gasto_de_capital": gasto_de_capital
}
TODAS_LAS_SERIES = {**CLASIFICACIONES, **KPI}


def buscar_serie(item: str, fuentes: dict[str, dict[str, str]] | None = None) -> tuple[str, str]:
    """Busca `item` dentro de `fuentes` y devuelve (nombre_grupo, codigo_serie).

    Si no se especifica `fuentes`, busca en todas las series disponibles
    (CLASIFICACIONES y KPI). Para restringir la búsqueda a un solo grupo,
    pasar explícitamente CLASIFICACIONES o KPI (o cualquier subconjunto).
    """
    item = item.strip().lower()
    fuentes = fuentes if fuentes is not None else TODAS_LAS_SERIES
    for nombre_grupo, indicadores in fuentes.items():
        if item in indicadores:
            return nombre_grupo, indicadores[item]
    raise ValueError(f"Item '{item}' no encontrado en: {list(fuentes)}.")


def _rango_anio(anio: int) -> tuple[str, str]:
    return f"{anio}-01-01", f"{anio}-12-31"


def obtener_valores(item: str, anio: int, fuentes: dict[str, dict[str, str]] | None = None) -> pd.DataFrame:
    """Consulta la API del Banco Central y devuelve los valores del item para el año dado."""
    _, codigo = buscar_serie(item, fuentes)
    desde, hasta = _rango_anio(anio)
    return siete.cuadro(series=[codigo], desde=desde, hasta=hasta, nombres=[item])


def obtener_valores_grupo(grupo: dict[str, str], anio: int) -> pd.DataFrame:
    """Consulta en una sola llamada todos los items de un grupo (p. ej. un grupo de KPI) para el año dado."""
    desde, hasta = _rango_anio(anio)
    return siete.cuadro(series=list(grupo.values()), desde=desde, hasta=hasta, nombres=list(grupo.keys()))


if __name__ == "__main__":
    print(obtener_valores("ingresos", 2024))
