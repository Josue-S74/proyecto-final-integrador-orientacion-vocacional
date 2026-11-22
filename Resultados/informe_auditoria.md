# Informe de auditoría y corrección del recomendador vocacional

Fecha: 2026-11-22

## 1. Respaldo y alcance

Antes de modificar archivos se creó `Respaldo_Auditoria_20261122/` con copias de:

- `Datos/Procesados/mapeo_carreras_areas.csv`
- `Datos/Procesados/catalogo_carreras_integrado.csv`
- `Scripts/recomendador.py`

No se modificaron `app.py`, notebooks ni estilos visuales. La carpeta `Respaldo_Auditoria_20261122/` se conservó sin cambios y fue la fuente obligatoria para recuperar la clasificación original durante la segunda corrección.

## 2. Normalización institucional

La normalización ya estaba realizada y no se repitió:

- `Localidad` / `Localidad_normalizada`: 24 filas con variantes de escritura ya corregidas; 0 nulos.
- `Institucion` / `Institucion_normalizada`: 221 filas con variantes ya corregidas; 0 nulos.
- Se conservaron las columnas originales (`Institucion`, `Localidad`) y las normalizadas.

`app.py` no se tocó, pero `recomendar_perfil()` ahora devuelve en `Institucion` y `Localidad` los valores normalizados (visible en Streamlit), conservando los originales en `Institucion_original` y `Localidad_original`.

## 3. Auditoría del mapeo

Se revisaron 312 filas del mapeo y 463 ofertas del catálogo.

Hallazgos principales:

- Una misma oferta aparece en distintas categorías/fuentes (por ejemplo, profesorados también listados en Ciencias Sociales, Derecho, Deportes, Idiomas, Arte y Diseño o Salud y Psicología).
- Varios profesorados estaban asignados solo por la categoría de la Expo y no por su especialidad real.
- `Profesorado de Educación Física` estaba mal ubicado en Ciencias Exactas en un registro; se separó explícitamente de `Profesorado de Educación Secundaria en Física`.

Corrección aplicada:

- 45 registros de mapeo reclasificados de área (`reclasificaciones.csv`).
- Se agregaron `Especialidad`, `Codigo_area_especialidad`, `Area_especialidad`, `Fortaleza_clave`, `Peso_fortaleza`, `Interes_clave`, `Criterio_especialidad`, `Es_profesorado`, `Codigo_area_original` y `Area_principal_original`.
- No se eliminó ninguna fila: las 463 ofertas siguen presentes.
- Segunda corrección: se aplicaron siete ajustes manuales justificados para evitar falsos positivos de `moda`/`modalidad`, confirmar `preparación física → Deportes` y reclasificar `estadísticas de salud → Salud` conservando `fortaleza_matematica` con peso 0.6.

Distribución final por área:

| Área | Ofertas |
|---|---:|
| AC01 Ciencias Exactas y Naturales | 33 |
| AC02 Salud y Ciencias de la Vida | 97 |
| AC03 Tecnologia e Informatica | 53 |
| AC04 Ciencias Sociales y Humanas | 78 |
| AC05 Educacion y Formacion Docente | 60 |
| AC06 Economia, Administracion y Negocios | 77 |
| AC07 Arte, Diseño y Comunicacion | 30 |
| AC08 Ambiente, Produccion y Ciencias Agropecuarias | 35 |

Criterios destacados:

- Matemática → AC01, `fortaleza_matematica`, peso 1.0.
- Física y Química → AC01, `fortaleza_fisica`, peso 1.0 (no se usa `fortaleza_fisica` para Educación Física).
- Biología → AC01, `fortaleza_biologia`, peso 1.0.
- Informática/TIC → AC03, `fortaleza_tecnologia`, peso 1.0.
- Educación Física, Especial, Primaria e Inicial → AC05, sin fortaleza disciplinar propia y con `interes_educacion`.
- Artes → AC07, sin fortaleza disciplinar disponible en el modelo.
- Economía/Administración → AC06 con `fortaleza_matematica` peso 0.6; Psicología → AC02 con `fortaleza_biologia` peso 0.6; historia/geografía/ciencia política/sociología/filosofía/derecho → AC04 con `fortaleza_historia` peso 0.8. El peso expresa que la fortaleza es relacionada, no idéntica a la especialidad.
- `corregir_mapeo.py` usa `\bmoda\b`, ejecuta la regla de Deportes antes que Física y aplica ajustes manuales con `Criterio_especialidad` explícito.
- El script vuelve a leer siempre `Respaldo_Auditoria_20261122/mapeo_carreras_areas.csv`: dos ejecuciones consecutivas producen hash idéntico, por lo que es idempotente y no reescribe `Codigo_area_original`.

## 4. Duplicados probables

Se detectaron 56 grupos que abarcan 113 filas, usando como clave `Carrera` + `Institucion_normalizada` + `Localidad_normalizada`.

Criterio: mismo nombre de carrera, misma institución normalizada y misma localidad normalizada, aunque difieran `Categoria` o `Archivo_origen`.

No se eliminaron registros. Se agregaron al catálogo:

- `Grupo_oferta`: identificador del grupo.
- `Duplicado_probable`: marca booleana.
- `Fuentes_relacionadas`: archivos de origen del mismo grupo.
- `Categorias_relacionadas`: categorías del mismo grupo, conservadas como trazabilidad.

El recomendador conserva las 463 filas del catálogo, pero descarta repeticiones de un mismo `Grupo_oferta` antes de limitar las ofertas por área; en la comprobación final no quedaron grupos repetidos en los resultados.

Detalle completo en `duplicados_probables.csv`.

## 5. Recomendador actualizado

`Scripts/recomendador.py` ya no usa `.head()` sobre el orden del CSV:

- Puntaje por carrera: `0.60 * interés + 0.40 * fortaleza ajustada`.
- Fortaleza ajustada: `50 + (fortaleza original - 50) * Peso_fortaleza`. Así un peso 1.0 no altera el valor y un peso menor solo atenúa la desviación respecto de 50.
- Para carreras sin fortaleza específica se usa explícitamente el neutro 50; la regla aplicada queda en `regla_puntaje`.
- Se mantienen tres conceptos separados: `afinidad_total` (afinidad general del área), `puntaje_mejor_carrera` y `puntaje_orden_area` (`max` de ambos) para ordenar áreas. El puntaje de una carrera nunca se presenta como porcentaje de afinidad general del área.
- Las áreas se ordenan por `puntaje_orden_area`, para que aparezcan profesorados específicos cuando corresponda.
- Columnas nuevas en las ofertas devueltas: `puntaje_interes`, `puntaje_fortaleza`, `puntaje_carrera`, `regla_puntaje`, `Grupo_oferta`, `Fuentes_relacionadas` y `Categorias_relacionadas`.

No se incorporaron variables nuevas. Los pesos son criterios de diseño de este prototipo, no relaciones científicamente validadas.

## 6. Casos de prueba

Resultados en `casos_prueba_recomendador.txt`, `casos_prueba_ofertas.csv` y `casos_prueba_areas.csv`.

| Caso | Verificación | Resultado |
|---|---|---|
| 1 | Educación alta + matemática alta → profesorados de Matemática | OK |
| 2 | Educación alta + física/química alta → profesorados de Física/Química | OK |
| 3 | Educación alta + biología alta → profesorados de Biología | OK |
| 4 | Educación alta sin fortalezas destacadas → puntajes homogéneos y ofertas generales presentes | OK |
| 5 | Tecnología alta + matemática alta → carreras de Informática, sin profesorados | OK |
| 6 | Educación 5, matemática 8 y física/química 9 → Física y Química | OK |

Las seis pruebas exigen que todas las especialidades esperadas aparezcan, verifican que el orden sea descendente por `puntaje_carrera` y comprueban que no se repita `Grupo_oferta`. Resultado final: 6/6 OK.

## 7. Entregables

- `Datos/Procesados/mapeo_carreras_areas.csv` corregido.
- `Datos/Procesados/catalogo_carreras_integrado.csv` actualizado con trazabilidad.
- `Scripts/corregir_mapeo.py`, `Scripts/integracion_datos.py`, `Scripts/recomendador.py` y `Scripts/casos_prueba_recomendador.py`.
- `Resultados/reclasificaciones.csv`, `Resultados/duplicados_probables.csv`.
- `Resultados/casos_prueba_*.csv`, `Resultados/casos_prueba_recomendador.txt`.
- Este informe.

`integracion_datos.py` usa `Path(__file__).resolve().parent.parent` y reproduce exactamente el catálogo integrado actual incluso al ejecutarse desde otro directorio (hash SHA256 verificado).

Segunda corrección: se modificaron únicamente los archivos existentes `Scripts/corregir_mapeo.py`, `Scripts/integracion_datos.py`, `Scripts/recomendador.py`, `Scripts/casos_prueba_recomendador.py`, los CSV/TXT de resultados ya existentes y este informe. No se crearon scripts, notebooks, datasets, configuraciones ni informes adicionales; `Respaldo_Auditoria_20261122/` permanece intacto.
