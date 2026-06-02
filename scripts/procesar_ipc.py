import pandas as pd
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def procesar_ipc():
    """
    Lee el IPC mensual, filtra 2017-2025, promedia por trimestre y
    reindexiza a base 2023 = 100.

    Retorna un DataFrame con columnas: indice, año, trimestre.
    """
    ruta = os.path.join(BASE, "data", "raw_data", "ipc_general_new.xlsx")

    df = pd.read_excel(ruta, sheet_name=0, header=0)
    df.columns = ["periodo", "indice"]
    df["periodo"] = pd.to_datetime(df["periodo"])
    df["año"] = df["periodo"].dt.year
    df["trimestre"] = df["periodo"].dt.quarter

    # Filtrar 2017-2025
    df = df[df["año"].between(2017, 2025)].copy()

    # Promedio trimestral de los valores mensuales originales
    trim = (
        df.groupby(["año", "trimestre"])["indice"]
        .mean()
        .reset_index()
    )

    # Rebase: base 2023 = 100
    # El factor es el promedio de los 4 trimestres de 2023
    base_2023 = trim[trim["año"] == 2023]["indice"].mean()
    trim["indice"] = (trim["indice"] / base_2023 * 100).round(4)

    return trim[["indice", "año", "trimestre"]]


def main():
    ipc = procesar_ipc()
    print("IPC trimestral (base 2023 = 100)\n")
    print(ipc.to_string(index=False))

    ruta_salida = os.path.join(BASE, "data", "processed_data", "ipc_trimestral.csv")
    ipc.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"\nArchivo guardado: {ruta_salida}")


if __name__ == "__main__":
    main()
