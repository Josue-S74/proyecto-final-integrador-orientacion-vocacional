# Autor: Soriano Josue Lautaro
from pathlib import Path

import pandas as pd

# 1. Rutas de los archivos

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_CATALOGO = BASE_DIR / "Datos" / "Procesados" / "catalogo_carreras_jujuy_limpio.csv"
RUTA_MAPEO = BASE_DIR / "Datos" / "Procesados" / "mapeo_carreras_areas.csv"
RUTA_PERFILES = BASE_DIR / "Datos" / "Sinteticos" / "perfiles_estudiantes_sinteticos.csv"
RUTA_INTEGRADO = BASE_DIR / "Datos" / "Procesados" / "catalogo_carreras_integrado.csv"

# 2. Carga de los Dataset

df_catalogo = pd.read_csv(RUTA_CATALOGO, encoding="utf-8-sig")
df_mapeo = pd.read_csv(RUTA_MAPEO, encoding="utf-8-sig")
df_perfiles = pd.read_csv(RUTA_PERFILES, encoding="utf-8-sig")

print("ARCHIVOS CARGADOS")
print("Catálogo:", df_catalogo.shape)
print("Mapeo:", df_mapeo.shape)
print("Perfiles:", df_perfiles.shape)

# 3. Comprobacion del mapeo

columnas_necesarias = [
    "Carrera",
    "Categoria",
    "Codigo_area",
    "Area_principal",
    "Subarea",
    "Criterio_asignacion",
    "Codigo_area_original",
    "Area_principal_original",
    "Es_profesorado",
    "Especialidad",
    "Codigo_area_especialidad",
    "Area_especialidad",
    "Fortaleza_clave",
    "Peso_fortaleza",
    "Interes_clave",
    "Criterio_especialidad"
]

faltantes = [
    columna for columna in columnas_necesarias
    if columna not in df_mapeo.columns
]

if faltantes:
    raise ValueError(f"Faltan columnas en el mapeo: {faltantes}")

# 4. Integracion del catalogo

df_integrado = df_catalogo.merge(
    df_mapeo[columnas_necesarias],
    on=["Carrera", "Categoria"],
    how="left",
    validate="many_to_one",
    indicator=True
)

# 5. validacion del resultado

sin_clasificar = df_integrado["_merge"] != "both"

print("\nRESULTADO DE LA INTEGRACIÓN")
print("Ofertas originales:", len(df_catalogo))
print("Ofertas integradas:", len(df_integrado))
print("Ofertas sin correspondencia:", sin_clasificar.sum())

if sin_clasificar.any():

    print("\nCARRERAS SIN CLASIFICACIÓN:")
    print(
        df_integrado.loc[
            sin_clasificar,
            ["Carrera", "Categoria"]
        ].to_string(index=False)
    )

else:


    # 6. Guardado del catalogo integrado

    df_integrado = df_integrado.drop(columns="_merge")

    clave_oferta = [
        "Carrera",
        "Institucion_normalizada",
        "Localidad_normalizada"
    ]

    grupos = df_integrado.groupby(clave_oferta, dropna=False)

    df_integrado["Grupo_oferta"] = grupos.ngroup() + 1
    df_integrado["Duplicado_probable"] = df_integrado.duplicated(clave_oferta, keep=False)
    df_integrado["Fuentes_relacionadas"] = grupos["Archivo_origen"].transform(
        lambda valores: " | ".join(sorted(set(valores.dropna())))
    )
    df_integrado["Categorias_relacionadas"] = grupos["Categoria"].transform(
        lambda valores: " | ".join(sorted(set(valores.dropna())))
    )

    df_integrado.to_csv(
        RUTA_INTEGRADO,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nCatálogo integrado guardado correctamente.")

# 7. Informacion de los perfiles sinteticos

print("\nPERFILES ESTUDIANTILES")
print("Cantidad de perfiles:", len(df_perfiles))
print("Cantidad de variables:", len(df_perfiles.columns))

if "perfil_id" in df_perfiles.columns:
    print("Identificadores únicos:", df_perfiles["perfil_id"].nunique())
else:
    print("No se encontró la columna perfil_id.")
