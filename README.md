# Proyecto Final Integrador — Recomendador vocacional

Proyecto de ciencia de datos y programación que integra limpieza y modelado de datos educativos de Jujuy con una aplicación web para orientación vocacional. Incluye los datasets, los notebooks de análisis, los scripts de procesamiento y la aplicación Streamlit.

## Objetivo de la aplicación

La aplicación vocacional toma los intereses y fortalezas declaradas por un estudiante y sugiere áreas de conocimiento y carreras concretas del catálogo integrado, mostrando además el motivo de cada recomendación. No promete resultados definitivos: ofrece alternativas orientativas a partir de reglas transparentes.

## Tecnologías utilizadas

- Python 3.13
- Streamlit (interfaz web)
- pandas y NumPy (procesamiento de datos)
- Altair, Matplotlib y Seaborn (visualizaciones)
- scikit-learn y joblib (análisis exploratorio y serialización)
- openpyxl (lectura de archivos Excel de los padrones)
- Jupyter / ipykernel (ejecución de notebooks)

## Organización de carpetas

```text
Repositorio_GitHub/
├── Datos/
│   ├── Raw/                 datasets originales (CSV y XLSX)
│   ├── Procesados/          catálogo integrado, mapeo, particiones y escalador
│   └── Sinteticos/          perfiles sintéticos y su documentación
├── Notebook/                ocho notebooks definitivos (01 a 08)
├── Scripts/                 aplicación, recomendador y scripts de procesamiento
├── Resultados/              informes, tablas de pruebas y figuras
├── .streamlit/              configuración de tema y servidor (sin secretos)
├── requirements.txt         dependencias con versiones exactas
├── .gitignore
└── README.md
```

## Instalación y ejecución

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
streamlit run Scripts/app.py
```

Para trabajar con los notebooks:

```bash
cd Notebook
jupyter notebook
```

Para ejecutar las pruebas del recomendador:

```bash
python Scripts/casos_prueba_recomendador.py
```

Los scripts `corregir_mapeo.py` e `integracion_datos.py` permiten regenerar el mapeo corregido y el catálogo integrado usando los datasets incluidos.

## Sistema de afinidad 60/40

El motor combina dos dimensiones con pesos fijos:

- Afinidad por área: **60 % intereses + 40 % fortalezas** declaradas, convertidas a escala 0-100.
- Puntaje por carrera: **60 % del interés clave** de la oferta y **40 % de la fortaleza clave**. Cuando la fortaleza tiene un peso menor que 1, se atenúa la desviación respecto del neutro 50; si no hay fortaleza específica, se usa 50 explícitamente.
- Las áreas se ordenan por el mayor valor entre su afinidad general y el mejor puntaje de carrera, de modo que especialidades concretas puedan aparecer por encima de áreas con afinidad general alta.

Estos puntajes son criterios de diseño del prototipo, no probabilidades ni medidas validadas estadísticamente.

## K-Means

Los notebooks 07 y 08 emplean K-Means para explorar agrupamientos de los perfiles sintéticos y evaluar su separación. **K-Means no es el motor de recomendaciones**: la aplicación usa la matriz de afinidad y las reglas de especialidad implementadas en `Scripts/recomendador.py`.

## Streamlit Cloud

Archivo de entrada: `Scripts/app.py`.

## Autor

Soriano Josue Lautaro
