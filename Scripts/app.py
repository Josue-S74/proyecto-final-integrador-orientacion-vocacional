import html
import re
import unicodedata

import altair as alt
import pandas as pd
import streamlit as st

from recomendador import calcular_todas_las_areas, recomendar_perfil

VARIABLES_INTERESES = [
    "interes_salud",
    "interes_tecnologia",
    "interes_educacion",
    "interes_arte",
    "interes_social",
    "interes_ambiente",
]

VARIABLES_FORTALEZAS = [
    "fortaleza_matematica",
    "fortaleza_lengua",
    "fortaleza_biologia",
    "fortaleza_historia",
    "fortaleza_fisica",
    "fortaleza_tecnologia",
]

VARIABLES_MODELO = VARIABLES_INTERESES + VARIABLES_FORTALEZAS

ETIQUETAS_INTERESES = {
    "interes_salud": "Salud",
    "interes_tecnologia": "Tecnología",
    "interes_educacion": "Educación",
    "interes_arte": "Arte",
    "interes_social": "Ciencias sociales",
    "interes_ambiente": "Ambiente",
}

ETIQUETAS_FORTALEZAS = {
    "fortaleza_matematica": "Matemática",
    "fortaleza_lengua": "Lengua",
    "fortaleza_biologia": "Biología",
    "fortaleza_historia": "Historia",
    "fortaleza_fisica": "Física",
    "fortaleza_tecnologia": "Tecnología",
}

VALORES_INICIALES = {
    **{variable: 3 for variable in VARIABLES_INTERESES},
    **{variable: 5 for variable in VARIABLES_FORTALEZAS},
}

AZUL_PROFUNDO = "#142D4E"
AZUL_PRINCIPAL = "#245B85"
AZUL_SECUNDARIO = "#3988B9"
DORADO = "#D6A84F"

st.set_page_config(
    page_title="Sistema de Orientación Vocacional",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --azul-profundo: #142D4E;
        --azul-principal: #245B85;
        --azul-secundario: #3988B9;
        --turquesa: #65B6B1;
        --dorado: #D6A84F;
        --fondo: #F4F6F8;
        --texto: #202B38;
        --secundario: #64748B;
        --borde: #DCE3EA;
    }
    .stApp {
        background-color: var(--fondo);
        color: var(--texto);
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stSidebar"] { display: none; }
    h1, h2, h3, h4 { color: var(--azul-profundo); }
    .encabezado {
        border-top: 4px solid var(--azul-principal);
        border-bottom: 1px solid var(--borde);
        padding: 1.1rem 0 1rem;
        margin-bottom: 1.4rem;
    }
    .linea-institucional {
        color: var(--azul-principal);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.14em;
    }
    .encabezado h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.35rem 0 0.25rem;
    }
    .encabezado p {
        color: var(--secundario);
        margin: 0;
        max-width: 78ch;
        line-height: 1.5;
    }
    .encabezado p.bajada {
        font-size: 0.82rem;
        font-weight: 400;
    }
    .titulo-seccion {
        margin: 1.6rem 0 0.8rem;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid var(--borde);
        color: var(--azul-profundo);
        font-size: 1.2rem;
        font-weight: 700;
    }
    .nota {
        color: var(--secundario);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .nota-final {
        border-top: 1px solid var(--borde);
        padding-top: 0.9rem;
        color: var(--secundario);
        font-size: 0.9rem;
        line-height: 1.6;
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: var(--azul-principal);
        color: #FFFFFF;
        border: 1px solid var(--azul-principal);
        border-radius: 5px;
        font-weight: 600;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: var(--azul-profundo);
        color: #FFFFFF;
        border-color: var(--azul-profundo);
    }
    .tabla-datos {
        width: 100%;
        overflow-x: auto;
    }
    .tabla-datos table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        background-color: #FFFFFF;
        border: 1px solid var(--borde);
        border-top: 3px solid var(--turquesa);
    }
    .tabla-datos th, .tabla-datos td {
        padding: 8px 10px;
        border-bottom: 1px solid var(--borde);
        font-size: 0.84rem;
        line-height: 1.35;
        vertical-align: top;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: break-word;
    }
    .tabla-datos th {
        color: var(--azul-profundo);
        background-color: var(--fondo);
        text-align: left;
        font-weight: 700;
    }
    .tabla-datos tbody tr:last-child td { border-bottom: none; }
    .tabla-principal td:nth-child(1) { width: 34%; }
    .tabla-principal td:nth-child(2) { width: 24%; }
    .tabla-principal td:nth-child(3) { width: 12%; }
    .tabla-principal td:nth-child(4) { width: 12%; }
    .tabla-principal td:nth-child(5) { width: 10%; }
    .tabla-principal td:nth-child(6) { width: 8%; text-align: right; }
    .tabla-detalle td:nth-child(1) { width: 30%; }
    .tabla-detalle td:nth-child(2) { width: 22%; }
    .tabla-detalle td:nth-child(3) { width: 38%; }
    .tabla-detalle td:nth-child(4) { width: 10%; }
    .tabla-detalle.sin-denominaciones td:nth-child(1) { width: 34%; }
    .tabla-detalle.sin-denominaciones td:nth-child(2) { width: 26%; }
    .tabla-detalle.sin-denominaciones td:nth-child(3) { width: 40%; }
    .tabla-datos .valor { display: inline; }
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 0 !important;
        }
        .tabla-datos { overflow-x: visible; }
        .tabla-datos table {
            display: block;
            table-layout: auto;
            min-width: 0;
        }
        .tabla-datos thead { display: none; }
        .tabla-datos tbody, .tabla-datos tr, .tabla-datos td {
            display: block;
            width: 100% !important;
        }
        .tabla-datos tbody tr {
            margin-bottom: 14px;
            padding: 4px 0;
            border: 1px solid var(--borde);
            border-left: 3px solid var(--turquesa);
            border-radius: 5px;
            background-color: #FFFFFF;
        }
        .tabla-datos tbody tr:last-child { margin-bottom: 0; }
        .tabla-datos td {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 8px 10px;
            border-bottom: 1px solid var(--borde);
        }
        .tabla-datos td:last-child { border-bottom: none; }
        .tabla-datos td::before {
            content: attr(data-label);
            flex: 0 1 auto;
            min-width: 35%;
            max-width: 55%;
            color: var(--azul-profundo);
            font-weight: 700;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        .tabla-datos td .valor {
            display: block;
            flex: 1 1 auto;
            min-width: 0;
            white-space: normal;
            overflow-wrap: anywhere;
            word-break: break-word;
        }
        .tabla-principal td:nth-child(6) .valor {
            text-align: right;
            font-variant-numeric: tabular-nums;
            font-weight: 700;
            color: var(--azul-profundo);
        }
    }
    hr { border-color: var(--borde); }
    </style>
    """,
    unsafe_allow_html=True,
)


def titulo_seccion(texto):
    st.markdown(
        f'<div class="titulo-seccion">{texto}</div>',
        unsafe_allow_html=True,
    )


def texto_seguro(valor, predeterminado=""):
    if pd.isna(valor):
        return predeterminado
    texto = str(valor).strip()
    return texto if texto else predeterminado


def normalizar_texto(valor):
    texto = texto_seguro(valor).lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    reemplazos = [
        (r"\bi\.e\.s\.?\b", "instituto de educacion superior"),
        (r"\bies\.?\b", "instituto de educacion superior"),
        (r"\bprof\.?\b", "profesorado"),
        (r"\beduc\.?\b", "educacion"),
        (r"\bsec\.?\b", "secundaria"),
        (r"\btec\.?\b", "tecnicatura"),
    ]
    for patron, reemplazo in reemplazos:
        texto = re.sub(patron, reemplazo, texto)
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def clave_presentacion(fila):
    partes = [
        normalizar_texto(fila.get("Carrera")),
        normalizar_texto(fila.get("Especialidad")),
        normalizar_texto(fila.get("Institucion")),
        normalizar_texto(fila.get("Localidad")),
    ]
    return "|".join(partes)


def unir_con_y(elementos):
    if len(elementos) == 1:
        return elementos[0]
    return ", ".join(elementos[:-1]) + " y " + elementos[-1]


def resumir_criterio(valor):
    texto = texto_seguro(valor)
    if not texto:
        return ""
    texto = re.sub(r"\s*\(peso [^)]*\)", "", texto)
    for codigo, etiqueta in ETIQUETAS_FORTALEZAS.items():
        texto = texto.replace(f"fortaleza {codigo}", f"fortaleza en {etiqueta.lower()}")
    for codigo, etiqueta in ETIQUETAS_FORTALEZAS.items():
        texto = texto.replace(codigo, f"fortaleza en {etiqueta.lower()}")
    for codigo, etiqueta in ETIQUETAS_INTERESES.items():
        texto = texto.replace(codigo, f"interés en {etiqueta.lower()}")
    texto = texto.replace("interes ", "interés ")
    texto = texto.replace("especialidad '", "especialidad ").replace("' por", " por")
    texto = texto.replace("' con", " con").replace("'", "")
    texto = texto.replace("Profesorado:", "Para profesorados:")
    return texto[0].upper() + texto[1:]


def preparar_ofertas(ofertas):
    ofertas = ofertas.copy()
    if "puntaje_carrera" in ofertas.columns:
        ofertas = ofertas.sort_values(
            "puntaje_carrera",
            ascending=False,
            kind="mergesort",
        )
    if "Grupo_oferta" in ofertas.columns:
        ofertas = ofertas.drop_duplicates(subset="Grupo_oferta", keep="first")

    ofertas = ofertas.copy()
    ofertas["_clave_presentacion"] = ofertas.apply(clave_presentacion, axis=1)
    variantes = ofertas.groupby("_clave_presentacion")["Carrera"].apply(
        lambda valores: list(dict.fromkeys(valores.dropna().astype(str).str.strip()))
    )
    ofertas = ofertas.drop_duplicates(subset="_clave_presentacion", keep="first")
    ofertas["Otras denominaciones"] = ofertas.apply(
        lambda fila: " | ".join(
            variante
            for variante in variantes.get(fila["_clave_presentacion"], [])
            if variante != fila["Carrera"]
        ),
        axis=1,
    )
    return ofertas.reset_index(drop=True)


def etiqueta_variable(valor, etiquetas):
    texto = texto_seguro(valor)
    if not texto:
        return None
    return etiquetas.get(texto, texto)


def explicar_oferta(fila):
    elementos = []

    interes = etiqueta_variable(fila.get("Interes_clave"), ETIQUETAS_INTERESES)
    if interes:
        detalle = f"tu interés en {interes.lower()}"
        puntaje = fila.get("puntaje_interes")
        if pd.notna(puntaje):
            detalle += f" ({float(puntaje):.0f}/100)"
        elementos.append(detalle)
    else:
        elementos.append("el área recomendada")

    fortaleza = etiqueta_variable(fila.get("Fortaleza_clave"), ETIQUETAS_FORTALEZAS)
    if fortaleza:
        detalle = f"tu fortaleza en {fortaleza.lower()}"
        puntaje = fila.get("puntaje_fortaleza")
        if pd.notna(puntaje):
            detalle += f" ({float(puntaje):.0f}/100)"
        elementos.append(detalle)
    else:
        elementos.append("la ausencia de una fortaleza asignada en el mapeo")

    frase = f"Aparece por {unir_con_y(elementos)}."
    criterio = resumir_criterio(fila.get("Criterio_especialidad"))
    if criterio:
        frase += f" {criterio}."
    return frase


def preparar_tabla(ofertas, areas):
    area_por_codigo = dict(zip(areas["codigo_area"], areas["area"]))
    filas = []

    for _, oferta in ofertas.iterrows():
        codigo = texto_seguro(oferta.get("codigo_area_recomendacion"))
        area = area_por_codigo.get(
            codigo,
            texto_seguro(oferta.get("Area_principal"), "Área no disponible"),
        )
        puntaje = oferta.get("puntaje_carrera")

        filas.append(
            {
                "Carrera": texto_seguro(oferta.get("Carrera"), "Sin dato"),
                "Institución": texto_seguro(oferta.get("Institucion"), "Sin dato"),
                "Localidad": texto_seguro(oferta.get("Localidad"), "Sin dato"),
                "Área": texto_seguro(area, "Área no disponible"),
                "Especialidad": texto_seguro(
                    oferta.get("Especialidad"), "No especificada"
                ),
                "Puntaje de afinidad": (
                    round(float(puntaje), 1) if pd.notna(puntaje) else ""
                ),
                "Explicación": explicar_oferta(oferta),
                "Otras denominaciones": texto_seguro(oferta.get("Otras denominaciones")),
            }
        )

    return pd.DataFrame(filas)


def celda_html(columna, valor):
    texto = "" if pd.isna(valor) else html.escape(str(valor))
    return (
        f'<td data-label="{html.escape(str(columna))}">'
        f'<span class="valor">{texto}</span>'
        "</td>"
    )


def mostrar_tabla(dataframe, clase):
    cabecera = "".join(
        f"<th>{html.escape(str(columna))}</th>" for columna in dataframe.columns
    )
    filas = []
    for fila in dataframe.itertuples(index=False, name=None):
        celdas = "".join(
            celda_html(columna, valor)
            for columna, valor in zip(dataframe.columns, fila)
        )
        filas.append(f"<tr>{celdas}</tr>")

    st.markdown(
        f'<div class="tabla-datos {clase}"><table><thead><tr>{cabecera}</tr></thead>'
        f'<tbody>{"".join(filas)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def graficar_categorias(datos, color, altura, maximo):
    origen = datos.reset_index().rename(
        columns={"index": "Categoria", datos.columns[0]: "Nivel"}
    )
    grafico = (
        alt.Chart(origen)
        .mark_bar(color=color, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                "Categoria:N",
                title=None,
                sort=list(datos.index),
                axis=alt.Axis(
                    labelAngle=-50,
                    labelPadding=6,
                    labelLimit=180,
                    labelFontSize=10,
                    labelOverlap=False,
                ),
            ),
            y=alt.Y(
                "Nivel:Q",
                title=datos.columns[0],
                scale=alt.Scale(domain=[0, maximo]),
            ),
            tooltip=[
                alt.Tooltip("Categoria:N", title="Categoría"),
                alt.Tooltip("Nivel:Q", title=datos.columns[0]),
            ],
        )
        .properties(height=altura)
        .configure_axis(
            labelColor="#64748B",
            titleColor="#202B38",
            gridColor="#DCE3EA",
            domainColor="#DCE3EA",
            tickColor="#DCE3EA",
        )
        .configure_view(stroke=None)
    )
    st.altair_chart(grafico, width="stretch")


st.markdown(
    """
    <div class="encabezado">
        <div class="linea-institucional">PROYECTO INTEGRADOR · JUJUY</div>
        <h1>Sistema de Orientación Vocacional</h1>
        <p class="bajada">Esta herramienta ofrece recomendaciones orientativas basadas en tus intereses, fortalezas académicas y las ofertas educativas disponibles. Los resultados no representan probabilidades de éxito ni determinan tu futuro profesional</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "mostrar_resultados" not in st.session_state:
    st.session_state["mostrar_resultados"] = False

if "mostrar_todas_ofertas" not in st.session_state:
    st.session_state["mostrar_todas_ofertas"] = False

titulo_seccion("Intereses personales")
st.markdown(
    '<div class="nota">Indicá el nivel de interés para cada área. '
    "Escala: 1 = muy bajo, 5 = muy alto.</div>",
    unsafe_allow_html=True,
)

titulo_seccion("Fortalezas académicas")
st.markdown(
    '<div class="nota">Indicá tu desempeño estimado en cada materia. '
    "Escala: 1 = bajo, 10 = alto.</div>",
    unsafe_allow_html=True,
)

with st.form("formulario_perfil"):
    st.markdown("#### Áreas de interés")
    columnas_intereses = st.columns(2)
    for indice, variable in enumerate(VARIABLES_INTERESES):
        with columnas_intereses[indice % 2]:
            st.slider(
                ETIQUETAS_INTERESES[variable],
                min_value=1,
                max_value=5,
                value=VALORES_INICIALES[variable],
                key=variable,
            )

    st.markdown("#### Fortalezas por materia")
    columnas_fortalezas = st.columns(2)
    for indice, variable in enumerate(VARIABLES_FORTALEZAS):
        with columnas_fortalezas[indice % 2]:
            st.slider(
                ETIQUETAS_FORTALEZAS[variable],
                min_value=1,
                max_value=10,
                value=VALORES_INICIALES[variable],
                key=variable,
            )

    enviar = st.form_submit_button(
        "Mostrar análisis y recomendaciones",
        type="primary",
        width="stretch",
    )

if enviar:
    perfil = {variable: st.session_state[variable] for variable in VARIABLES_MODELO}
    try:
        st.session_state["resultado_vocacional"] = recomendar_perfil(
            perfil,
            cantidad_areas=3,
            ofertas_por_area=10,
        )
        st.session_state["perfil_actual"] = perfil
        st.session_state["afinidades_todas"] = calcular_todas_las_areas(pd.Series(perfil))
        st.session_state["mostrar_resultados"] = True
        st.session_state["mostrar_todas_ofertas"] = False
        st.rerun()
    except (ValueError, KeyError, FileNotFoundError) as error:
        st.session_state["mostrar_resultados"] = False
        st.error(f"No se pudieron calcular las recomendaciones: {error}")

resultado = st.session_state.get("resultado_vocacional")

if st.session_state["mostrar_resultados"] and resultado is not None:
    perfil_actual = st.session_state["perfil_actual"]
    afinidades_todas = st.session_state["afinidades_todas"]

    titulo_seccion("Análisis gráfico del perfil")
    col_intereses, col_fortalezas = st.columns(2)

    with col_intereses:
        st.markdown("##### Intereses declarados")
        st.caption("Escala de 1 a 5")
        datos_intereses = pd.DataFrame(
            {"Nivel (1-5)": [perfil_actual[v] for v in VARIABLES_INTERESES]},
            index=[ETIQUETAS_INTERESES[v] for v in VARIABLES_INTERESES],
        )
        graficar_categorias(datos_intereses, AZUL_SECUNDARIO, 240, 5)

    with col_fortalezas:
        st.markdown("##### Fortalezas académicas")
        st.caption("Escala de 1 a 10")
        datos_fortalezas = pd.DataFrame(
            {"Nivel (1-10)": [perfil_actual[v] for v in VARIABLES_FORTALEZAS]},
            index=[ETIQUETAS_FORTALEZAS[v] for v in VARIABLES_FORTALEZAS],
        )
        graficar_categorias(datos_fortalezas, DORADO, 240, 10)

    st.markdown("##### Afinidad con áreas de conocimiento")
    grafico_areas = (
        afinidades_todas.sort_values("afinidad_total", ascending=True)
        .set_index("area")[["afinidad_total"]]
        .rename(columns={"afinidad_total": "Afinidad directa"})
    )
    st.bar_chart(grafico_areas, horizontal=True, color=AZUL_PRINCIPAL, height=320)
    st.markdown(
        '<div class="nota">El gráfico muestra la afinidad calculada directamente para cada área. '
        "El orden de las áreas recomendadas también considera la mejor oferta disponible, "
        "un indicador distinto. Los valores no son probabilidades de éxito.</div>",
        unsafe_allow_html=True,
    )

    titulo_seccion("Carreras e instituciones recomendadas")
    areas = resultado["areas"]
    ofertas = preparar_ofertas(resultado["ofertas"])
    nombres_areas = ", ".join(areas["area"].tolist())

    st.markdown(f"**Áreas consideradas:** {nombres_areas}")

    st.checkbox("Mostrar más alternativas", key="mostrar_todas_ofertas")
    cantidad_visibles = None if st.session_state["mostrar_todas_ofertas"] else 5
    ofertas_visibles = (
        ofertas if cantidad_visibles is None else ofertas.head(cantidad_visibles)
    )

    if ofertas_visibles.empty:
        st.markdown(
            '<div class="nota">No hay ofertas disponibles para este perfil.</div>',
            unsafe_allow_html=True,
        )
    else:
        tabla_completa = preparar_tabla(ofertas_visibles, areas)
        tabla = tabla_completa.drop(columns=["Explicación", "Otras denominaciones"])
        st.caption(f"Se muestran {len(tabla)} de {len(ofertas)} alternativas disponibles.")
        mostrar_tabla(tabla, "tabla-principal")

        with st.expander("Ver por qué aparecen estas ofertas"):
            columna_otras = "Otras denominaciones del catálogo"
            detalle = tabla_completa[
                ["Carrera", "Institución", "Explicación", "Otras denominaciones"]
            ].rename(
                columns={
                    "Explicación": "Por qué aparece",
                    "Otras denominaciones": columna_otras,
                }
            )
            sin_otras = (
                detalle[columna_otras].fillna("").astype(str).str.strip().eq("").all()
            )
            if sin_otras:
                detalle = detalle.drop(columns=[columna_otras])
            mostrar_tabla(
                detalle,
                "tabla-detalle sin-denominaciones" if sin_otras else "tabla-detalle",
            )

else:
    st.markdown(
        '<div class="nota">Completá el cuestionario y seleccioná '
        "“Mostrar análisis y recomendaciones” para ver el perfil gráfico, "
        "las áreas sugeridas y las ofertas educativas.</div>",
        unsafe_allow_html=True,
    )

st.divider()
st.markdown(
    '<div class="nota-final">App Vocacional - Alumno: Soriano Josue Lautaro</div>',
    unsafe_allow_html=True,
)
