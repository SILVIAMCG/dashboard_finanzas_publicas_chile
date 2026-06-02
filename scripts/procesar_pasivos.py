import pandas as pd
import os

pd.set_option("future.no_silent_downcasting", True)

# Solo se conservan las filas cuyo nombre original esté en este mapa.
RENOMBRAR = {
    "PASIVOS NETOS INCURRIDOS":  "PASIVOS_NETOS_INCURRIDOS",
    "Endeudamiento Externo Neto": "endeudamiento_externo_neto",
    "Endeudamiento Interno Neto": "endeudamiento_interno_neto",
    "Bono de Reconocimiento":     "bono_de_reconocimiento",
}


def procesar_hoja_pasivos(df, fuente):
    """
    Extrae la sección 'PASIVOS NETOS INCURRIDOS' de una hoja del Excel,
    conservando únicamente los ítems definidos en RENOMBRAR.
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

    # Localizar fila PASIVOS NETOS INCURRIDOS
    pasivos_start = None
    for idx in range(len(df)):
        celda = df.iloc[idx, 0]
        if pd.notna(celda) and str(celda).strip() == "PASIVOS NETOS INCURRIDOS":
            pasivos_start = idx
            break

    if pasivos_start is None:
        raise ValueError(f"No se encontró 'PASIVOS NETOS INCURRIDOS' en la fuente: {fuente}")

    # Recopilar filas hasta la primera celda vacía
    indices_seccion = []
    for idx in range(pasivos_start, len(df)):
        celda = df.iloc[idx, 0]
        if pd.isna(celda) or str(celda).strip() == "":
            break
        indices_seccion.append(idx)

    # Construir el DataFrame largo conservando solo los ítems del mapa
    rows = []
    for idx in indices_seccion:
        fila = df.iloc[idx]
        nombre_original = str(fila[0]).strip().rstrip("0123456789").strip()
        if nombre_original not in RENOMBRAR:
            continue
        categoria = RENOMBRAR[nombre_original]
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
    ruta_salida = os.path.join("data", "processed_data", "pasivos_netos.csv")

    df_gc = pd.read_excel(ruta_excel, sheet_name=0, header=None)  # Serie_Trim_GC
    df_gg = pd.read_excel(ruta_excel, sheet_name=2, header=None)  # Serie_Trim_GG

    gc_largo = procesar_hoja_pasivos(df_gc, "Gobierno Central")
    gg_largo = procesar_hoja_pasivos(df_gg, "Gobierno General")

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
    print("\nPrimeras 8 filas:")
    print(df_final.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
