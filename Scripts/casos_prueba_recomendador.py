from pathlib import Path

import pandas as pd

from recomendador import df_carreras, recomendar_perfil

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_RESULTADOS = BASE_DIR / "Resultados"

CASOS = [
    {
        "id": "caso_1",
        "nombre": "Interés educativo alto y fortaleza matemática alta",
        "perfil": {
            "interes_salud": 1,
            "interes_tecnologia": 2,
            "interes_educacion": 5,
            "interes_arte": 1,
            "interes_social": 3,
            "interes_ambiente": 1,
            "fortaleza_matematica": 10,
            "fortaleza_lengua": 5,
            "fortaleza_biologia": 3,
            "fortaleza_historia": 4,
            "fortaleza_fisica": 3,
            "fortaleza_tecnologia": 4,
        },
        "especialidades_esperadas": ["Matemática"],
    },
    {
        "id": "caso_2",
        "nombre": "Interés educativo alto y fortaleza física alta",
        "perfil": {
            "interes_salud": 2,
            "interes_tecnologia": 3,
            "interes_educacion": 5,
            "interes_arte": 1,
            "interes_social": 2,
            "interes_ambiente": 2,
            "fortaleza_matematica": 6,
            "fortaleza_lengua": 4,
            "fortaleza_biologia": 5,
            "fortaleza_historia": 3,
            "fortaleza_fisica": 10,
            "fortaleza_tecnologia": 5,
        },
        "especialidades_esperadas": ["Física"],
    },
    {
        "id": "caso_3",
        "nombre": "Interés educativo alto y fortaleza biológica alta",
        "perfil": {
            "interes_salud": 4,
            "interes_tecnologia": 1,
            "interes_educacion": 5,
            "interes_arte": 1,
            "interes_social": 2,
            "interes_ambiente": 3,
            "fortaleza_matematica": 4,
            "fortaleza_lengua": 4,
            "fortaleza_biologia": 10,
            "fortaleza_historia": 3,
            "fortaleza_fisica": 4,
            "fortaleza_tecnologia": 2,
        },
        "especialidades_esperadas": ["Biología"],
    },
    {
        "id": "caso_4",
        "nombre": "Interés educativo alto sin fortalezas académicas destacadas",
        "perfil": {
            "interes_salud": 2,
            "interes_tecnologia": 1,
            "interes_educacion": 5,
            "interes_arte": 2,
            "interes_social": 4,
            "interes_ambiente": 2,
            "fortaleza_matematica": 5,
            "fortaleza_lengua": 5,
            "fortaleza_biologia": 5,
            "fortaleza_historia": 5,
            "fortaleza_fisica": 5,
            "fortaleza_tecnologia": 5,
        },
        "especialidades_esperadas": [
            "Educación",
            "Educación Primaria",
        ],
        "top_n": 10,
        "homogeneo": True,
    },
    {
        "id": "caso_5",
        "nombre": "Interés tecnológico alto y fortaleza matemática alta",
        "perfil": {
            "interes_salud": 1,
            "interes_tecnologia": 5,
            "interes_educacion": 1,
            "interes_arte": 2,
            "interes_social": 1,
            "interes_ambiente": 2,
            "fortaleza_matematica": 10,
            "fortaleza_lengua": 3,
            "fortaleza_biologia": 3,
            "fortaleza_historia": 2,
            "fortaleza_fisica": 7,
            "fortaleza_tecnologia": 10,
        },
        "especialidades_esperadas": ["Informática"],
        "sin_profesorados": True,
    },
    {
        "id": "caso_6",
        "nombre": "Perfil educativo con matemática 8 y física 9",
        "perfil": {
            "interes_salud": 2,
            "interes_tecnologia": 3,
            "interes_educacion": 5,
            "interes_arte": 1,
            "interes_social": 3,
            "interes_ambiente": 2,
            "fortaleza_matematica": 8,
            "fortaleza_lengua": 4,
            "fortaleza_biologia": 4,
            "fortaleza_historia": 3,
            "fortaleza_fisica": 9,
            "fortaleza_tecnologia": 5,
        },
        "especialidades_esperadas": ["Física"],
    },
]

COLUMNAS_OFERTAS = [
    "codigo_area_recomendacion",
    "Carrera",
    "Categoria",
    "Especialidad",
    "Institucion",
    "Localidad",
    "Grupo_oferta",
    "Categorias_relacionadas",
    "Fuentes_relacionadas",
    "Fortaleza_clave",
    "Peso_fortaleza",
    "puntaje_interes",
    "puntaje_fortaleza",
    "puntaje_carrera",
    "regla_puntaje",
]


def verificar(caso, top):
    especialidades = set(top["Especialidad"].dropna())
    esperadas = set(caso["especialidades_esperadas"])
    excluidas = set(caso.get("especialidades_excluidas", []))
    faltantes = esperadas - especialidades

    if faltantes:
        return f"FALLA: faltan especialidades esperadas ({', '.join(sorted(faltantes))})"

    if excluidas and especialidades & excluidas:
        return "FALLA: aparece una especialidad no esperada"

    combinaciones_prohibidas = [
        ("Química", "fortaleza_fisica"),
        ("Deportes", "fortaleza_fisica"),
        ("Educación Física", "fortaleza_fisica"),
        ("Tecnología Industrial", "fortaleza_tecnologia"),
        ("Psicología", "fortaleza_biologia"),
        ("Comunicación", "fortaleza_lengua"),
    ]

    for especialidad, fortaleza in combinaciones_prohibidas:
        if (
            (top["Especialidad"] == especialidad)
            & (top["Fortaleza_clave"] == fortaleza)
        ).any():
            return f"FALLA: {especialidad} recibe {fortaleza}"

    if not top["puntaje_carrera"].is_monotonic_decreasing:
        return "FALLA: el orden no es descendente por puntaje"

    if "Grupo_oferta" in top.columns and top["Grupo_oferta"].duplicated().any():
        return "FALLA: se repite un Grupo_oferta"

    if caso.get("sin_profesorados") and top["Carrera"].str.contains(
        "profesor|prof\\.", case=False, regex=True, na=False
    ).any():
        return "FALLA: aparece un profesorado cuando no corresponde"

    if caso.get("homogeneo"):

        dispersion = top["puntaje_carrera"].max() - top["puntaje_carrera"].min()

        if dispersion > 20:
            return f"FALLA: puntajes no homogéneos (dispersión {dispersion:.1f})"

        return (
            f"OK: especialidad(es) {', '.join(sorted(esperadas))}; "
            f"dispersión {dispersion:.1f}"
        )

    return f"OK: especialidad(es) {', '.join(sorted(esperadas))}"


def verificar_fortalezas_y_correcciones():
    problemas = []
    catalogo = df_carreras

    combinaciones_prohibidas = [
        ("Química", "fortaleza_fisica"),
        ("Deportes", "fortaleza_fisica"),
        ("Educación Física", "fortaleza_fisica"),
        ("Tecnología Industrial", "fortaleza_tecnologia"),
        ("Psicología", "fortaleza_biologia"),
        ("Comunicación", "fortaleza_lengua"),
    ]

    for especialidad, fortaleza in combinaciones_prohibidas:
        if (
            (catalogo["Especialidad"] == especialidad)
            & (catalogo["Fortaleza_clave"] == fortaleza)
        ).any():
            problemas.append(f"{especialidad} recibe {fortaleza}")

    automotriz = catalogo["Carrera"].str.contains(
        r"mec[aá]nica automotriz", case=False, regex=True, na=False
    )
    if (automotriz & (catalogo["Especialidad"] != "Tecnología Industrial")).any():
        problemas.append("mecánica automotriz no es Tecnología Industrial")
    if (automotriz & (catalogo["Fortaleza_clave"] == "fortaleza_tecnologia")).any():
        problemas.append("mecánica automotriz recibe fortaleza_tecnologia")

    higiene = catalogo["Carrera"].str.contains("higiene", case=False, na=False)
    if (higiene & (catalogo["Especialidad"] != "Salud")).any():
        problemas.append("higiene y seguridad no está unificado en Salud")

    neuromotora = catalogo["Carrera"].str.contains(
        "Discapacidad Neuromotora", case=False, na=False
    )
    if (neuromotora & (catalogo["Especialidad"] != "Educación Especial")).any():
        problemas.append("discapacidad neuromotora no es Educación Especial")

    educacion_tecnologica = catalogo["Carrera"].str.contains(
        r"educ(?:aci[oó]n|\.)\s+tecnol", case=False, regex=True, na=False
    )
    if (
        educacion_tecnologica
        & (catalogo["Especialidad"] != "Educación Tecnológica")
    ).any():
        problemas.append("educación tecnológica no está unificada")

    relaciones_publicas = catalogo["Carrera"].str.contains(
        r"relaciones p[uú]blicas|protocolo", case=False, regex=True, na=False
    )
    if (
        relaciones_publicas & (catalogo["Especialidad"] != "Comunicación")
    ).any():
        problemas.append("relaciones públicas/protocolo no es Comunicación")
    if (
        relaciones_publicas
        & (catalogo["Fortaleza_clave"] == "fortaleza_lengua")
    ).any():
        problemas.append("relaciones públicas/protocolo recibe fortaleza_lengua")

    if problemas:
        return "FALLA: " + "; ".join(problemas)

    return "OK: fortalezas separadas y correcciones aplicadas en catálogo"


def main():
    filas_ofertas = []
    filas_areas = []
    lineas = [
        "RESULTADOS DE LOS CASOS DE PRUEBA DEL RECOMENDADOR",
        "Puntaje por carrera = 60% interés + 40% fortaleza ajustada.",
        "Fortaleza ajustada = 50 + (fortaleza original - 50) * peso; sin fortaleza se usa neutro 50.",
        "El orden de áreas usa max(afinidad general del área, puntaje de la mejor carrera).",
        "Las ofertas se deduplican por Grupo_oferta antes de limitar por área.",
        "Los pesos son criterios de diseño, no relaciones científicamente validadas.",
        "Las especialidades se verifican completas sobre el top global de ofertas.",
        "",
    ]

    estado_global = verificar_fortalezas_y_correcciones()
    lineas.extend([estado_global, ""])
    print(estado_global)

    for caso in CASOS:
        resultado = recomendar_perfil(
            caso["perfil"],
            cantidad_areas=3,
            ofertas_por_area=10,
        )

        areas = resultado["areas"].copy()
        areas.insert(0, "caso", caso["id"])
        filas_areas.append(areas)

        ofertas = resultado["ofertas"][COLUMNAS_OFERTAS].copy()
        ofertas.insert(0, "caso", caso["id"])
        filas_ofertas.append(ofertas)

        top = ofertas.sort_values(
            "puntaje_carrera",
            ascending=False
        ).head(caso.get("top_n", 5))

        estado = verificar(caso, top)

        lineas.extend([
            "=" * 70,
            f"{caso['id']}: {caso['nombre']}",
            estado,
            "Áreas seleccionadas:",
            areas[[
                "codigo_area",
                "area",
                "afinidad_total",
                "puntaje_mejor_carrera",
                "puntaje_orden_area",
            ]].to_string(index=False),
            f"Top {len(top)} de ofertas:",
            top[[
                "Carrera",
                "Especialidad",
                "puntaje_interes",
                "puntaje_fortaleza",
                "puntaje_carrera",
                "regla_puntaje",
            ]].to_string(index=False),
            "",
        ])

        print(f"{caso['id']}: {estado}")
        print(top[[
            "Carrera",
            "Especialidad",
            "puntaje_carrera",
        ]].to_string(index=False))
        print()

    pd.concat(filas_ofertas, ignore_index=True).to_csv(
        RUTA_RESULTADOS / "casos_prueba_ofertas.csv",
        index=False,
        encoding="utf-8-sig",
    )

    pd.concat(filas_areas, ignore_index=True).to_csv(
        RUTA_RESULTADOS / "casos_prueba_areas.csv",
        index=False,
        encoding="utf-8-sig",
    )

    (RUTA_RESULTADOS / "casos_prueba_recomendador.txt").write_text(
        "\n".join(lineas),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
