import pandas as pd
import os

pd.set_option("future.no_silent_downcasting", True)

RENOMBRAR = {
    "ADQUISICIÓN NETA DE ACTIVOS FINANCIEROS": "ADQUISICION_NETA_AF",
}

PARAR_EN = "Caja"


def procesar_hoja_af(df, fuente):
    """
    Extrae la sección 'ADQUISICIÓN NETA DE ACTIVOS FINANCIEROS' de una hoja
    del Excel hasta el ítem 'Caja' (inclusive), excluyendo filas todo-cero.
    Retorna un DataFrame en formato largo.

    Parámetros
    ----------
    df : DataFrame leído sin encabezado (header=None)
    fuente : str  "Gobierno Central" o "Gobierno General"
    """
    # Fila 7 → trimestres (T1-T4)
    trimestres_row = df.iloc[7]

    # Año tomado del T1 de cada grupo para evitar el error del Excel donde
    # las columnas Q4 de 2024 y 2025 tienen el año 2023 en el encabezado.
    cols_datos: list = []
    año_actual = None
    for col in df.columns[1:]:
        trim_val = trimestres_row[col]
        if pd.isna(trim_val) or not str(trim_val).startswith("T"):
            continue
        num_trim = int(str(trim_val)[1])
        if num_trim == 1:
            año_actual = df.iloc[6, col]
        if año_actual is None or pd.isna(año_actual):
            continue
        periodo = f"{int(año_actual)}-Q{num_trim}"
        cols_datos.append((col, periodo, int(año_actual), num_trim))

    cols_solo = [c for c, *_ in cols_datos]

    # Localizar fila ADQUISICIÓN NETA DE ACTIVOS FINANCIEROS
    af_start = None
    for idx in range(len(df)):
        celda = df.iloc[idx, 0]
        if pd.notna(celda) and "ADQUISICI" in str(celda).upper() and "NO FINANCIERO" not in str(celda).upper():
            af_start = idx
            break

    if af_start is None:
        raise ValueError(f"No se encontró la sección AF en la fuente: {fuente}")

    # Recopilar filas desde af_start hasta PARAR_EN (inclusive)
    indices_af = []
    for idx in range(af_start, len(df)):
        celda = df.iloc[idx, 0]
        if pd.isna(celda) or str(celda).strip() == "":
            break
        indices_af.append(idx)
        if str(celda).strip() == PARAR_EN:
            break

    # Construir el DataFrame largo excluyendo filas todo-cero
    rows = []
    for idx in indices_af:
        fila = df.iloc[idx]
        nombre_original = str(fila[0]).strip().rstrip("0123456789").strip()
        categoria = RENOMBRAR.get(nombre_original, nombre_original)

        valores_fila = [fila[c] for c in cols_solo if pd.notna(fila[c])]
        if valores_fila and all(v == 0 for v in valores_fila):
            continue

        for col, periodo, año, trimestre in cols_datos:
            valor = fila[col]
            if pd.notna(valor):
                rows.append(
                    {
                        "categoria": categoria,
                        "periodo": periodo,
                        "valor": valor,
                        "año": año,
                        "trimestre": trimestre,
                        "fuente": fuente,
                    }
                )

    return pd.DataFrame(rows)


def main():
    ruta_excel = os.path.join("data", "raw_data", "finanzas_publicas_historico.xlsx")
    ruta_salida = os.path.join("data", "processed_data", "af_largo.csv")

    df_gc = pd.read_excel(ruta_excel, sheet_name=0, header=None)  # Serie_Trim_GC
    df_gg = pd.read_excel(ruta_excel, sheet_name=2, header=None)  # Serie_Trim_GG

    gc_largo = procesar_hoja_af(df_gc, "Gobierno Central")
    gg_largo = procesar_hoja_af(df_gg, "Gobierno General")

    df_final = pd.concat([gc_largo, gg_largo], ignore_index=True)

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    df_final.to_csv(ruta_salida, index=False, encoding="utf-8")

    print(f"Archivo guardado: {ruta_salida}")
    print(f"Total de registros: {len(df_final):,}")
    print(f"\nCategorías encontradas ({df_final['categoria'].nunique()}):")
    for cat in df_final["categoria"].unique():
        print(f"  - {cat}")
    print(f"\nRango temporal: {df_final['año'].min()} – {df_final['año'].max()}")
    print(f"Fuentes: {df_final['fuente'].unique().tolist()}")
    print("\nPrimeras 9 filas:")
    print(df_final.head(9).to_string(index=False))


if __name__ == "__main__":
    main()
