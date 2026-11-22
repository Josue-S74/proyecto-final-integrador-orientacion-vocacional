import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_MAPEO = BASE_DIR / "Datos" / "Procesados" / "mapeo_carreras_areas.csv"
RUTA_LIMPIO = BASE_DIR / "Datos" / "Procesados" / "catalogo_carreras_jujuy_limpio.csv"
RUTA_INTEGRADO = BASE_DIR / "Datos" / "Procesados" / "catalogo_carreras_integrado.csv"
RUTA_RESULTADOS = BASE_DIR / "Resultados"

ESPECIALIDADES = {
    "Matemática": ("AC01", "Ciencias Exactas y Naturales", "fortaleza_matematica", "interes_tecnologia", 1.0),
    "Física": ("AC01", "Ciencias Exactas y Naturales", "fortaleza_fisica", "interes_tecnologia", 1.0),
    "Química": ("AC01", "Ciencias Exactas y Naturales", "", "interes_tecnologia", 0.0),
    "Biología": ("AC01", "Ciencias Exactas y Naturales", "fortaleza_biologia", "interes_salud", 1.0),
    "Informática": ("AC03", "Tecnologia e Informatica", "fortaleza_tecnologia", "interes_tecnologia", 1.0),
    "Tecnología Industrial": ("AC03", "Tecnologia e Informatica", "", "interes_tecnologia", 0.0),
    "Salud": ("AC02", "Salud y Ciencias de la Vida", "fortaleza_biologia", "interes_salud", 0.8),
    "Psicología": ("AC02", "Salud y Ciencias de la Vida", "", "interes_salud", 0.0),
    "Historia": ("AC04", "Ciencias Sociales y Humanas", "fortaleza_historia", "interes_social", 0.8),
    "Geografía": ("AC04", "Ciencias Sociales y Humanas", "fortaleza_historia", "interes_social", 0.8),
    "Ciencia Política": ("AC04", "Ciencias Sociales y Humanas", "", "interes_social", 0.0),
    "Sociología": ("AC04", "Ciencias Sociales y Humanas", "", "interes_social", 0.0),
    "Filosofía": ("AC04", "Ciencias Sociales y Humanas", "", "interes_social", 0.0),
    "Derecho": ("AC04", "Ciencias Sociales y Humanas", "", "interes_social", 0.0),
    "Economía y Administración": ("AC06", "Economia, Administracion y Negocios", "fortaleza_matematica", "interes_social", 0.6),
    "Lengua y Literatura": ("AC04", "Ciencias Sociales y Humanas", "fortaleza_lengua", "interes_social", 1.0),
    "Comunicación": ("AC04", "Ciencias Sociales y Humanas", "", "interes_social", 0.0),
    "Idiomas": ("AC05", "Educacion y Formacion Docente", "fortaleza_lengua", "interes_educacion", 1.0),
    "Artes": ("AC07", "Arte, Diseño y Comunicacion", "", "interes_arte", 0.0),
    "Deportes": ("AC02", "Salud y Ciencias de la Vida", "", "interes_salud", 0.0),
    "Ambiente y Producción": ("AC08", "Ambiente, Produccion y Ciencias Agropecuarias", "fortaleza_biologia", "interes_ambiente", 0.8),
    "Educación Física": ("AC05", "Educacion y Formacion Docente", "", "interes_educacion", 0.0),
    "Educación Especial": ("AC05", "Educacion y Formacion Docente", "", "interes_educacion", 0.0),
    "Educación Primaria": ("AC05", "Educacion y Formacion Docente", "", "interes_educacion", 0.0),
    "Educación Inicial": ("AC05", "Educacion y Formacion Docente", "", "interes_educacion", 0.0),
    "Educación Tecnológica": ("AC05", "Educacion y Formacion Docente", "", "interes_educacion", 0.0),
    "Educación": ("AC05", "Educacion y Formacion Docente", "", "interes_educacion", 0.0),
}

REGLAS = [
    (r"educacion\s+fisica|educ\.\s*fisica|educ\.\s*fis", "Educación Física"),
    (r"educacion\s+especial|educ(?:acion)?\.?\s+esp", "Educación Especial"),
    (r"primaria", "Educación Primaria"),
    (r"inicial", "Educación Inicial"),
    (r"educacion\s+tecnologica|educ\.?\s*tecnol", "Educación Tecnológica"),
    (r"deport|recreacion|entrenamiento|preparacion fisica", "Deportes"),
    (r"quimic", "Química"),
    (r"matematic|estadistic", "Matemática"),
    (r"biolog|bioimagenes", "Biología"),
    (r"higiene.*seguridad", "Salud"),
    (r"ambient|sustentab|agropecuari|rural|forestal|energias renovables|geocienci|miner|alimentos|agroindustrial", "Ambiente y Producción"),
    (r"mantenimiento industrial|mecanica automotriz|mecatronic|robot|automatizacion|sistemas electricos|electromecan", "Tecnología Industrial"),
    (r"informatic|software|ciencia de datos|inteligencia artificial|\bsistemas\b|tecnologias de informacion|tecnologia de la informacion|infraestructura de tecnologia|\btic\b|videojuegos", "Informática"),
    (r"danza|musica|teatro|arte|diseno|\bmoda\b|indumentaria|ceramica|escultura|fotografia|grabado|pintura|animacion", "Artes"),
    (r"psicolog", "Psicología"),
    (r"enfermer|medicin|farmacia|hemoterapia|podolog|salud|terapeut|psicomotric|protesis|esterilizacion|laboratorio|instrumentacion|mecanica dental|acompannamiento", "Salud"),
    (r"historia", "Historia"),
    (r"geografia", "Geografía"),
    (r"ciencia politica|ciencias politicas|relaciones internacionales", "Ciencia Política"),
    (r"sociolog", "Sociología"),
    (r"filosof", "Filosofía"),
    (r"abogac|derecho|criminal|juridic|procurador|martillero|criminolog|escena del crimen", "Derecho"),
    (r"administraci|econom|finanz|comercializ|comercio|logistic|marketing|recursos humanos|turismo|hoteler|gastronom|contable|impositiv|emprendedurismo", "Economía y Administración"),
    (r"relaciones publicas|protocolo", "Comunicación"),
    (r"lengua|literatura|traduccion|comunicacion social|periodismo|publicidad", "Lengua y Literatura"),
    (r"ingles|frances|portugues|idiomas", "Idiomas"),
    (r"\bfisica\b", "Física"),
    (r"educacion|profesor|docen", "Educación"),
]

AJUSTES_MANUALES = {
    "abogacia - modalidad online": (
        "Derecho", None, None,
        "Revisión manual: 'Modalidad Online' indica formato, no especialidad; Abogacía → Derecho",
    ),
    "martillero y corredor publico e inmobiliario - modalidad online": (
        "Derecho", None, None,
        "Revisión manual: 'Modalidad Online' indica formato, no especialidad; Martillero → Derecho",
    ),
    "licenciatura en comunicacion social - modalidad online": (
        "Lengua y Literatura", None, None,
        "Revisión manual: 'Modalidad Online' no es Artes; Comunicación Social → Lengua y Literatura",
    ),
    "licenciatura en publicidad y narrativas digitales - modalidad online": (
        "Lengua y Literatura", None, None,
        "Revisión manual: 'Modalidad Online' no es Artes; Publicidad → Lengua y Literatura",
    ),
    "licenciatura en gestion de la comunicacion estrategica - modalidad online": (
        "Lengua y Literatura", None, None,
        "Revisión manual: 'Modalidad Online' no es Artes; Comunicación Estratégica → Lengua y Literatura",
    ),
    "tecnicatura superior en estadisticas de salud": (
        "Salud", "fortaleza_matematica", 0.6,
        "Revisión manual: estadística aplicada a la salud; se conserva fortaleza matemática con peso 0.6",
    ),
    "tecnicatura superior en preparacion fisica": (
        "Deportes", None, None,
        "Revisión manual: preparación física → Deportes, sin fortaleza física",
    ),
}

POR_AREA = {
    "AC01": "Matemática",
    "AC02": "Salud",
    "AC03": "Informática",
    "AC04": "Historia",
    "AC05": "Educación",
    "AC06": "Economía y Administración",
    "AC07": "Artes",
    "AC08": "Ambiente y Producción",
}

GENERALES_DOCENTES = {
    "Educación Física",
    "Educación Especial",
    "Educación Primaria",
    "Educación Inicial",
    "Educación Tecnológica",
    "Educación",
}


def sin_acentos(valor):
    texto = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode("ascii")
    return texto.lower()


def detectar_profesorado(carrera):
    texto = sin_acentos(carrera)
    return bool(re.search(r"\bprof\.|\bprof\b|profesor|profesorado", texto))


def detectar_especialidad(carrera, codigo_area):
    texto = sin_acentos(carrera)
    for patron, especialidad in REGLAS:
        if re.search(patron, texto):
            return especialidad
    return POR_AREA.get(codigo_area, "Educación")


def clasificar(carrera, codigo_area, area_principal):
    profesorado = detectar_profesorado(carrera)
    ajuste = AJUSTES_MANUALES.get(sin_acentos(carrera))

    if ajuste:
        especialidad, fortaleza_manual, peso_manual, texto_ajuste = ajuste
    else:
        especialidad = detectar_especialidad(carrera, codigo_area)

    codigo, area, fortaleza, interes, peso = ESPECIALIDADES[especialidad]

    if profesorado:
        interes = "interes_educacion"
        if especialidad == "Deportes":
            especialidad = "Educación Física"
            codigo, area, fortaleza, _, peso = ESPECIALIDADES[especialidad]
        if especialidad in GENERALES_DOCENTES:
            fortaleza = ""
            peso = 0.0
        criterio = f"Profesorado: especialidad '{especialidad}' con interes_educacion"
        if fortaleza:
            criterio += f" y fortaleza {fortaleza} (peso {peso:.1f})"
    else:
        if especialidad == "Idiomas":
            codigo, area, fortaleza, interes, peso = "AC04", ESPECIALIDADES["Lengua y Literatura"][1], "fortaleza_lengua", "interes_social", 1.0
        if re.search(r"preparacion fisica", sin_acentos(carrera)):
            especialidad = "Deportes"
            codigo, area, fortaleza, interes, peso = ESPECIALIDADES["Deportes"]
        if peso:
            criterio = f"Especialidad '{especialidad}' por nombre de la oferta (peso {peso:.1f})"
        else:
            criterio = f"Especialidad '{especialidad}' por nombre de la oferta, sin fortaleza"

    if ajuste:
        if fortaleza_manual is not None:
            fortaleza = fortaleza_manual
        if peso_manual is not None:
            peso = peso_manual
        criterio = texto_ajuste

    return {
        "Es_profesorado": "Sí" if profesorado else "No",
        "Especialidad": especialidad,
        "Codigo_area_especialidad": codigo,
        "Area_especialidad": area,
        "Fortaleza_clave": fortaleza,
        "Peso_fortaleza": peso,
        "Interes_clave": interes,
        "Criterio_especialidad": criterio,
        "Codigo_area": codigo,
        "Area_principal": area,
    }


def main():
    mapeo = pd.read_csv(RUTA_MAPEO, encoding="utf-8-sig")
    columnas_originales = [
        "Carrera",
        "Categoria",
        "Subarea",
        "Criterio_asignacion",
        "Codigo_area_original",
        "Area_principal_original",
    ]
    faltantes = [columna for columna in columnas_originales if columna not in mapeo.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas originales en el mapeo: {faltantes}")
    mapeo = mapeo[columnas_originales].copy()

    clasificaciones = pd.DataFrame([
        clasificar(fila["Carrera"], fila["Codigo_area_original"], fila["Area_principal_original"])
        for _, fila in mapeo.iterrows()
    ])
    mapeo = pd.concat([mapeo, clasificaciones], axis=1)
    mapeo.to_csv(RUTA_MAPEO, index=False, encoding="utf-8-sig")

    reclasificados = mapeo.loc[
        mapeo["Codigo_area"] != mapeo["Codigo_area_original"],
        ["Carrera", "Categoria", "Codigo_area_original", "Area_principal_original",
         "Codigo_area", "Area_principal", "Especialidad", "Criterio_especialidad"],
    ].copy()
    reclasificados.to_csv(RUTA_RESULTADOS / "reclasificaciones.csv", index=False, encoding="utf-8-sig")

    columnas = [
        "Carrera", "Categoria", "Codigo_area", "Area_principal", "Subarea",
        "Criterio_asignacion", "Codigo_area_original", "Area_principal_original",
        "Es_profesorado", "Especialidad", "Codigo_area_especialidad",
        "Area_especialidad", "Fortaleza_clave", "Peso_fortaleza", "Interes_clave", "Criterio_especialidad",
    ]
    limpio = pd.read_csv(RUTA_LIMPIO, encoding="utf-8-sig")
    integrado = limpio.merge(
        mapeo[columnas],
        on=["Carrera", "Categoria"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    if (integrado["_merge"] != "both").any():
        raise ValueError("Hay ofertas del catálogo sin correspondencia en el mapeo corregido")
    integrado = integrado.drop(columns="_merge")

    clave = ["Carrera", "Institucion_normalizada", "Localidad_normalizada"]
    grupos = integrado.groupby(clave, dropna=False)
    integrado["Grupo_oferta"] = grupos.ngroup() + 1
    integrado["Duplicado_probable"] = integrado.duplicated(clave, keep=False)
    integrado["Fuentes_relacionadas"] = grupos["Archivo_origen"].transform(
        lambda values: " | ".join(sorted(set(values.dropna())))
    )
    integrado["Categorias_relacionadas"] = grupos["Categoria"].transform(
        lambda values: " | ".join(sorted(set(values.dropna())))
    )
    integrado.to_csv(RUTA_INTEGRADO, index=False, encoding="utf-8-sig")

    duplicados = integrado.loc[
        integrado["Duplicado_probable"],
         ["Grupo_oferta", "Carrera", "Categoria", "Institucion", "Institucion_normalizada",
          "Localidad_normalizada", "Archivo_origen", "Fuentes_relacionadas",
          "Categorias_relacionadas", "Codigo_area", "Especialidad"],
    ].sort_values(["Grupo_oferta", "Carrera"])
    duplicados.to_csv(RUTA_RESULTADOS / "duplicados_probables.csv", index=False, encoding="utf-8-sig")

    print("MAPEO CORREGIDO")
    print("Filas de mapeo:", len(mapeo))
    print("Reclasificaciones de area:", len(reclasificados))
    print("Ofertas integradas:", len(integrado))
    print("Grupos de oferta:", integrado["Grupo_oferta"].nunique())
    print("Filas en duplicados probables:", len(duplicados))
    print("Profesorados detectados:", (integrado["Es_profesorado"] == "Sí").sum())
    print("\nRECLASIFICACIONES POR ESPECIALIDAD")
    print(reclasificados.groupby(["Especialidad", "Codigo_area"]).size().to_string())
    print("\nDISTRIBUCION FINAL POR AREA")
    print(integrado.groupby(["Codigo_area", "Area_principal"]).size().to_string())


if __name__ == "__main__":
    main()
