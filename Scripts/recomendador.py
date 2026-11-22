# Autor: Soriano Josue Lautaro
import pandas as pd
from pathlib import Path

# Ruta de la carpeta principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent



# 1. Carga del catalogo de carreras


df_carreras = pd.read_csv(
    BASE_DIR / "Datos" / "Procesados" / "catalogo_carreras_integrado.csv",
    encoding="utf-8-sig"
)


# 2. Definicion de variables


variables_intereses = [
    "interes_salud",
    "interes_tecnologia",
    "interes_educacion",
    "interes_arte",
    "interes_social",
    "interes_ambiente"
]

variables_fortalezas = [
    "fortaleza_matematica",
    "fortaleza_lengua",
    "fortaleza_biologia",
    "fortaleza_historia",
    "fortaleza_fisica",
    "fortaleza_tecnologia"
]



# 3. Matriz de afinidad


matriz_afinidad = {

    "AC01": {
        "nombre": "Ciencias Exactas y Naturales",
        "intereses": {
            "interes_ambiente": 0.5
        },
        "fortalezas": {
            "fortaleza_matematica": 1,
            "fortaleza_fisica": 1,
            "fortaleza_biologia": 0.5
        }
    },

    "AC02": {
        "nombre": "Salud y Ciencias de la Vida",
        "intereses": {
            "interes_salud": 1
        },
        "fortalezas": {
            "fortaleza_biologia": 1
        }
    },

    "AC03": {
        "nombre": "Tecnologia e Informatica",
        "intereses": {
            "interes_tecnologia": 1
        },
        "fortalezas": {
            "fortaleza_tecnologia": 1,
            "fortaleza_matematica": 0.5
        }
    },

    "AC04": {
        "nombre": "Ciencias Sociales y Humanas",
        "intereses": {
            "interes_social": 1
        },
        "fortalezas": {
            "fortaleza_lengua": 1,
            "fortaleza_historia": 1
        }
    },

    "AC05": {
        "nombre": "Educacion y Formacion Docente",
        "intereses": {
            "interes_educacion": 1,
            "interes_social": 0.5
        },
        "fortalezas": {
            "fortaleza_lengua": 1,
            "fortaleza_historia": 0.5
        }
    },

    "AC06": {
        "nombre": "Economia, Administracion y Negocios",
        "intereses": {
            "interes_social": 0.5
        },
        "fortalezas": {
            "fortaleza_matematica": 0.5,
            "fortaleza_lengua": 0.5
        }
    },

    "AC07": {
        "nombre": "Arte, Diseño y Comunicacion",
        "intereses": {
            "interes_arte": 1
        },
        "fortalezas": {}
    },

    "AC08": {
        "nombre": "Ambiente, Produccion y Ciencias Agropecuarias",
        "intereses": {
            "interes_ambiente": 1
        },
        "fortalezas": {
            "fortaleza_biologia": 1,
            "fortaleza_matematica": 0.5
        }
    }
}



# 4. Funciones de normalizacion


def convertir_interes(valor):
    return (valor / 5) * 100


def convertir_fortaleza(valor):
    return (valor / 10) * 100


def valor_clave(perfil, variable, funcion_conversion):

    if not variable or pd.isna(variable) or variable not in perfil.index:
        return None

    return funcion_conversion(perfil[variable])


def calcular_puntaje_carrera(perfil, oferta, area):

    interes = valor_clave(
        perfil,
        oferta.get("Interes_clave"),
        convertir_interes
    )

    fortaleza_clave = valor_clave(
        perfil,
        oferta.get("Fortaleza_clave"),
        convertir_fortaleza
    )

    interes_area = area["afinidad_intereses"]
    detalle_fortaleza = "neutro explícito 50"

    if pd.isna(interes):
        interes = interes_area

    if pd.notna(fortaleza_clave):

        peso = oferta.get("Peso_fortaleza", 1.0)

        if pd.isna(peso):
            peso = 1.0

        fortaleza = 50.0 + (fortaleza_clave - 50.0) * peso
        detalle_fortaleza = f"fortaleza ajustada (peso {peso:.1f})"

    else:

        fortaleza = 50.0

    neutro = 50.0

    if pd.notna(interes) and pd.notna(fortaleza):

        puntaje = interes * 0.60 + fortaleza * 0.40
        regla = f"60% interes + 40% {detalle_fortaleza}"

    elif pd.notna(interes):

        puntaje = interes * 0.60 + neutro * 0.40
        regla = f"60% interes + 40% {detalle_fortaleza}"

    elif pd.notna(fortaleza):

        puntaje = neutro * 0.60 + fortaleza * 0.40
        regla = f"60% neutro + 40% {detalle_fortaleza}"

    else:

        puntaje = area["afinidad_total"]
        regla = "afinidad del area"

    return pd.Series({
        "puntaje_interes": interes,
        "puntaje_fortaleza": fortaleza,
        "puntaje_carrera": puntaje,
        "regla_puntaje": regla
    })


def aplicar_columnas_visibles(ofertas):

    if "Institucion_normalizada" in ofertas.columns:
        ofertas["Institucion_original"] = ofertas["Institucion"]
        ofertas["Institucion"] = ofertas[
            "Institucion_normalizada"
        ].fillna(ofertas["Institucion"])

    if "Localidad_normalizada" in ofertas.columns:
        ofertas["Localidad_original"] = ofertas["Localidad"]
        ofertas["Localidad"] = ofertas[
            "Localidad_normalizada"
        ].fillna(ofertas["Localidad"])

    return ofertas



# 5. Calculo de afinidad por dimension


def calcular_afinidad_dimension(perfil, variables, funcion_conversion):

    suma_ponderada = 0
    suma_pesos = 0

    for variable, peso in variables.items():

        valor = perfil[variable]

        valor_porcentual = funcion_conversion(valor)

        suma_ponderada += valor_porcentual * peso
        suma_pesos += peso

    if suma_pesos == 0:
        return None

    return suma_ponderada / suma_pesos



# 6. Calculo de afinidad por area


def calcular_afinidad_area(perfil, area):

    datos_area = matriz_afinidad[area]

    afinidad_intereses = calcular_afinidad_dimension(
        perfil,
        datos_area["intereses"],
        convertir_interes
    )

    afinidad_fortalezas = calcular_afinidad_dimension(
        perfil,
        datos_area["fortalezas"],
        convertir_fortaleza
    )

    # Combinar intereses y fortalezas

    if afinidad_intereses is None:
        afinidad_intereses = 50.0

    if afinidad_fortalezas is None:
        afinidad_fortalezas = 50.0

    afinidad_total = (
        afinidad_intereses * 0.60 +
        afinidad_fortalezas * 0.40
    )

    return {
        "area": datos_area["nombre"],
        "afinidad_intereses": afinidad_intereses,
        "afinidad_fortalezas": afinidad_fortalezas,
        "afinidad_total": afinidad_total
    }



# 7. Calculo de todas las areas


def calcular_todas_las_areas(perfil):

    resultados = []

    for codigo_area in matriz_afinidad:

        resultado = calcular_afinidad_area(
            perfil,
            codigo_area
        )

        resultado["codigo_area"] = codigo_area

        resultados.append(resultado)

    df_resultados = pd.DataFrame(resultados)

    df_resultados = df_resultados.sort_values(
        by="afinidad_total",
        ascending=False
    )

    return df_resultados



# 8. Funcion principal del recomendador


def recomendar_perfil(perfil, cantidad_areas=3, ofertas_por_area=10):

    # Convertir las respuestas en una Serie de Pandas

    perfil = pd.Series(perfil).copy()

    # Comprobar que existan todas las variables

    variables_requeridas = (
        variables_intereses + variables_fortalezas
    )

    faltantes = [
        variable for variable in variables_requeridas
        if variable not in perfil.index
    ]

    if faltantes:
        raise ValueError(
            f"Faltan variables del perfil: {faltantes}"
        )

    # Validar las respuestas de intereses

    for variable in variables_intereses:

        valor = pd.to_numeric(
            perfil[variable],
            errors="coerce"
        )

        if pd.isna(valor) or not 1 <= valor <= 5:
            raise ValueError(
                f"{variable} debe tener un valor entre 1 y 5"
            )

        perfil[variable] = valor

    # Validar las respuestas de fortalezas

    for variable in variables_fortalezas:

        valor = pd.to_numeric(
            perfil[variable],
            errors="coerce"
        )

        if pd.isna(valor) or not 1 <= valor <= 10:
            raise ValueError(
                f"{variable} debe tener un valor entre 1 y 10"
            )

        perfil[variable] = valor

    # Calcular las afinidades de las ocho areas

    afinidades = calcular_todas_las_areas(perfil)

    puntajes_areas = []

    for _, area in afinidades.iterrows():

        ofertas_area = df_carreras[
            df_carreras["Codigo_area"] == area["codigo_area"]
        ]

        if ofertas_area.empty:

            puntajes_areas.append(area["afinidad_total"])
            continue

        puntajes = ofertas_area.apply(
            lambda fila: calcular_puntaje_carrera(
                perfil,
                fila,
                area
            )["puntaje_carrera"],
            axis=1
        )

        puntajes_areas.append(puntajes.max())

    afinidades["puntaje_mejor_carrera"] = puntajes_areas

    afinidades["puntaje_orden_area"] = afinidades[
        ["afinidad_total", "puntaje_mejor_carrera"]
    ].max(axis=1)

    afinidades = afinidades.sort_values(
        by="puntaje_orden_area",
        ascending=False
    )

    # Seleccionar las areas principales

    mejores_areas = afinidades.head(cantidad_areas)

    resultados_ofertas = []

    # Buscar las ofertas educativas de cada area

    for _, area in mejores_areas.iterrows():

        codigo = area["codigo_area"]

        ofertas = df_carreras[
            df_carreras["Codigo_area"] == codigo
        ].copy()

        if not ofertas.empty:

            puntajes = ofertas.apply(
                lambda fila: calcular_puntaje_carrera(
                    perfil,
                    fila,
                    area
                ),
                axis=1
            )

            ofertas = pd.concat([ofertas, puntajes], axis=1)

            ofertas = ofertas.sort_values(
                by=["puntaje_carrera", "Carrera"],
                ascending=[False, True]
            )

            if "Grupo_oferta" in ofertas.columns:
                ofertas = ofertas.drop_duplicates(
                    subset=["Grupo_oferta"],
                    keep="first"
                )

            ofertas = ofertas.head(ofertas_por_area)

        # Asociar la afinidad a cada oferta

        ofertas["codigo_area_recomendacion"] = codigo

        ofertas["afinidad_total"] = area["afinidad_total"]

        resultados_ofertas.append(ofertas)

    # Unificar las ofertas encontradas

    if resultados_ofertas:

        ofertas_finales = pd.concat(
            resultados_ofertas,
            ignore_index=True
        )

        if (
            "Categorias_relacionadas" not in ofertas_finales.columns
            and "Grupo_oferta" in ofertas_finales.columns
        ):
            categorias_por_grupo = df_carreras.groupby("Grupo_oferta")["Categoria"].apply(
                lambda valores: " | ".join(sorted(set(valores.dropna())))
            )
            ofertas_finales["Categorias_relacionadas"] = ofertas_finales[
                "Grupo_oferta"
            ].map(categorias_por_grupo)

    else:

        ofertas_finales = pd.DataFrame()

    ofertas_finales = aplicar_columnas_visibles(ofertas_finales)

    # Devolver areas y ofertas por separado

    return {
        "areas": mejores_areas.reset_index(drop=True),
        "ofertas": ofertas_finales
    }



# 9. PRUEBAS DEL RECOMENDADOR


if __name__ == "__main__":

    print("=" * 60)
    print("PRUEBAS DEL SISTEMA RECOMENDADOR")
    print("=" * 60)


    # 9.1 Prueba con perfil sintetico


    df_perfiles = pd.read_csv(
        BASE_DIR / "Datos" / "Sinteticos" / "perfiles_estudiantes_sinteticos.csv",
        encoding="utf-8-sig"
    )

    perfil_prueba = df_perfiles.iloc[0]

    resultado_sintetico = recomendar_perfil(perfil_prueba)

    print("\nRESULTADOS DEL PERFIL SINTETICO")

    print(
        resultado_sintetico["areas"][
            ["codigo_area", "area", "afinidad_total"]
        ].to_string(index=False)
    )

    print(
        "\nTotal de ofertas:",
        len(resultado_sintetico["ofertas"])
    )


    # 9.2 Prueba con perfil nuevo


    perfil_nuevo = {

        "interes_salud": 2,
        "interes_tecnologia": 5,
        "interes_educacion": 4,
        "interes_arte": 1,
        "interes_social": 3,
        "interes_ambiente": 4,

        "fortaleza_matematica": 9,
        "fortaleza_lengua": 8,
        "fortaleza_biologia": 4,
        "fortaleza_historia": 7,
        "fortaleza_fisica": 10,
        "fortaleza_tecnologia": 9
    }

    resultado_nuevo = recomendar_perfil(perfil_nuevo)

    print("\nRESULTADOS DEL PERFIL NUEVO")

    print(
        resultado_nuevo["areas"][
            ["codigo_area", "area", "afinidad_total"]
        ].to_string(index=False)
    )

    print(
        "\nTotal de ofertas:",
        len(resultado_nuevo["ofertas"])
    )

    print("\nPRUEBAS FINALIZADAS")
