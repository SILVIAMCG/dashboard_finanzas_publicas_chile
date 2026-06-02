import pandas as pd
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cargar(nombre):
    return pd.read_csv(os.path.join(BASE, "data", "processed_data", nombre))


def balance_trimestral(ingresos=None, gastos=None):
    """
    Retorna un DataFrame con ingresos, gastos y balance por periodo y fuente.

    Si no se pasan los DataFrames los carga desde los CSV procesados.
    """
    if ingresos is None:
        ingresos = cargar("ingresos_largo.csv")
    if gastos is None:
        gastos = cargar("gastos_largo.csv")

    total_ing = (
        ingresos[ingresos["categoria"] == "INGRESOS"]
        .set_index(["periodo", "año", "trimestre", "fuente"])["valor"]
        .rename("ingresos")
    )
    total_gas = (
        gastos[gastos["categoria"] == "GASTOS"]
        .set_index(["periodo", "año", "trimestre", "fuente"])["valor"]
        .rename("gastos")
    )

    df = pd.concat([total_ing, total_gas], axis=1)
    df["balance"] = df["ingresos"] - df["gastos"]
    return df.reset_index().sort_values(["fuente", "año", "trimestre"])


def balance_anual(df_trimestral=None):
    """
    Agrega el balance trimestral a nivel anual por fuente.

    Acepta el resultado de balance_trimestral() o lo calcula internamente.
    """
    if df_trimestral is None:
        df_trimestral = balance_trimestral()

    return (
        df_trimestral.groupby(["año", "fuente"])[["ingresos", "gastos", "balance"]]
        .sum()
        .reset_index()
    )


def totales_trimestral(ingresos=None, gastos=None, anf=None):
    """
    Calcula TOTAL_INGRESOS, TOTAL_GASTOS y PRESTAMO_NETO por periodo y fuente.

    Fórmulas (equivalentes a las del Excel):
        TOTAL_INGRESOS = INGRESOS + venta_activos_fisicos
        TOTAL_GASTOS   = GASTOS + ADQUISICION_NETA_ANF + venta_activos_fisicos
        PRESTAMO_NETO  = TOTAL_INGRESOS - TOTAL_GASTOS

    Si no se pasan los DataFrames los carga desde los CSV procesados.
    """
    if ingresos is None:
        ingresos = cargar("ingresos_largo.csv")
    if gastos is None:
        gastos = cargar("gastos_largo.csv")
    if anf is None:
        anf = cargar("anf_largo.csv")

    idx = ["periodo", "año", "trimestre", "fuente"]

    ing = (
        ingresos[ingresos["categoria"] == "INGRESOS"]
        .set_index(idx)["valor"].rename("INGRESOS")
    )
    gas = (
        gastos[gastos["categoria"] == "GASTOS"]
        .set_index(idx)["valor"].rename("GASTOS")
    )
    anf_neta = (
        anf[anf["categoria"] == "ADQUISICION_NETA_ANF"]
        .set_index(idx)["valor"].rename("ADQUISICION_NETA_ANF")
    )
    venta = (
        anf[anf["categoria"] == "venta_activos_fisicos"]
        .set_index(idx)["valor"].rename("venta_activos_fisicos")
    )

    df = pd.concat([ing, gas, anf_neta, venta], axis=1)
    df["TOTAL_INGRESOS"] = df["INGRESOS"] + df["venta_activos_fisicos"]
    df["TOTAL_GASTOS"]   = df["GASTOS"] + df["ADQUISICION_NETA_ANF"] + df["venta_activos_fisicos"]
    df["PRESTAMO_NETO"]  = df["TOTAL_INGRESOS"] - df["TOTAL_GASTOS"]

    return df[["TOTAL_INGRESOS", "TOTAL_GASTOS", "PRESTAMO_NETO"]].reset_index().sort_values(["fuente", "año", "trimestre"])


def totales_anual(df_trimestral=None):
    """
    Agrega TOTAL_INGRESOS, TOTAL_GASTOS y PRESTAMO_NETO a nivel anual por fuente.

    Acepta el resultado de totales_trimestral() o lo calcula internamente.
    """
    if df_trimestral is None:
        df_trimestral = totales_trimestral()

    return (
        df_trimestral.groupby(["año", "fuente"])[["TOTAL_INGRESOS", "TOTAL_GASTOS", "PRESTAMO_NETO"]]
        .sum()
        .reset_index()
    )


def financiamiento_trimestral(af=None, pasivos=None):
    """
    Calcula FINANCIAMIENTO = ADQUISICION_NETA_AF - PASIVOS_NETOS_INCURRIDOS
    por periodo y fuente.

    Es una identidad contable GFS equivalente a PRESTAMO_NETO (bajo la línea).
    Si no se pasan los DataFrames los carga desde los CSV procesados.
    """
    if af is None:
        af = cargar("af_largo.csv")
    if pasivos is None:
        pasivos = cargar("pasivos_netos.csv")

    idx = ["periodo", "año", "trimestre", "fuente"]

    af_neta = (
        af[af["categoria"] == "ADQUISICION_NETA_AF"]
        .set_index(idx)["valor"].rename("ADQUISICION_NETA_AF")
    )
    pas_netos = (
        pasivos[pasivos["categoria"] == "PASIVOS_NETOS_INCURRIDOS"]
        .set_index(idx)["valor"].rename("PASIVOS_NETOS_INCURRIDOS")
    )

    df = pd.concat([af_neta, pas_netos], axis=1)
    df["FINANCIAMIENTO"] = df["ADQUISICION_NETA_AF"] - df["PASIVOS_NETOS_INCURRIDOS"]

    return df.reset_index().sort_values(["fuente", "año", "trimestre"])


def financiamiento_anual(df_trimestral=None):
    """
    Agrega FINANCIAMIENTO a nivel anual por fuente.

    Acepta el resultado de financiamiento_trimestral() o lo calcula internamente.
    """
    if df_trimestral is None:
        df_trimestral = financiamiento_trimestral()

    return (
        df_trimestral.groupby(["año", "fuente"])[["ADQUISICION_NETA_AF", "PASIVOS_NETOS_INCURRIDOS", "FINANCIAMIENTO"]]
        .sum()
        .reset_index()
    )


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.float_format", "{:,.2f}".format)

    trim = balance_trimestral()
    print("=== Balance trimestral (millones de pesos) ===\n")
    print(trim.to_string(index=False))

    print("\n--- Resumen anual por fuente ---")
    print(balance_anual(trim).to_string(index=False))

    print("\n\n=== Totales y préstamo neto trimestral ===\n")
    tot = totales_trimestral()
    print(tot.to_string(index=False))

    print("\n--- Totales anuales por fuente ---")
    print(totales_anual(tot).to_string(index=False))

    print("\n\n=== Financiamiento trimestral ===\n")
    fin = financiamiento_trimestral()
    print(fin.to_string(index=False))

    print("\n--- Financiamiento anual por fuente ---")
    print(financiamiento_anual(fin).to_string(index=False))
