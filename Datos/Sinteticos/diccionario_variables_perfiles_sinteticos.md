# Diccionario de variables — Perfiles de estudiantes sintéticos

Sistema de Orientación Vocacional Inteligente · Provincia de Jujuy, Argentina
Documento de diseño previo a la generación. Versión del esquema: 1.0.0

> **ADVERTENCIA**: todos los registros serán completamente ficticios. No representan
> estudiantes reales ni permiten validar científicamente la orientación vocacional.
> Este dataset sirve para probar código, estructura, preprocesamiento, clustering,
> ranking de afinidad e interfaz. No es una fuente de verdad vocacional.

## Decisiones confirmadas por el usuario

| Decisión | Valor confirmado |
|---|---|
| Cantidad de registros | **1.000** perfiles |
| Áreas de interés | **6 áreas amplias**: salud, tecnología, educación, arte, ciencias sociales, ambiente |
| Fortalezas académicas | **Notas sintéticas en escala 1–10** (un decimal) |
| Preferencias | 4 variables (se incluyen las 2 adicionales propuestas) |
| Semilla por defecto | 42 (configurable por parámetro) |
| Departamento | Columna opcional `departamento_sintetico`, asignación ficticia independiente |

## Separación de grupos de variables

El esquema mantiene separados tres bloques con significado distinto: **fortalezas
académicas** (rendimiento/aptitud simulada por materia), **intereses** (preferencia
temática declarada) y **preferencias** (modalidad de aprendizaje/trabajo). No se
mezclan en una sola escala sin documentar su significado.

---

## A. Metadatos técnicos

| Variable | Definición | Tipo | Escala / Valores | Justificación |
|---|---|---|---|---|
| `perfil_id` | Identificador artificial secuencial, no identificable | string | `PERF-0001` … `PERF-1000` | Trazabilidad sin datos personales |
| `version_generador` | Versión del script generador | string | `1.0.0` | Reproducibilidad y trazabilidad |
| `seed` | Semilla aleatoria usada en la corrida | int | `42` (configurable) | Reproducibilidad estricta |
| `origen_dato` | Marca de origen del registro | constante | `"sintetico"` | Distinguir de datos reales |
| `fecha_generacion` | Fecha de generación del dataset | date | ISO `YYYY-MM-DD` | Trazabilidad |

---

## B. Fortalezas académicas — notas sintéticas 1–10

Escala continua simulada `1.0`–`10.0`, con un decimal. Representa una nota/rendimiento
**simulado** en la materia, NO un atributo real del estudiante.

| Variable | Definición | Tipo | Rango | Área principal vinculada |
|---|---|---|---|---|
| `fortaleza_matematica` | Rendimiento simulado en matemática | float | 1.0–10.0 | Tecnología, Ambiente |
| `fortaleza_lengua` | Rendimiento simulado en lengua y literatura | float | 1.0–10.0 | Educación, Ciencias sociales |
| `fortaleza_biologia` | Rendimiento simulado en biología / ciencias naturales | float | 1.0–10.0 | Salud, Ambiente |
| `fortaleza_historia` | Rendimiento simulado en historia / ciencias sociales | float | 1.0–10.0 | Ciencias sociales, Educación |
| `fortaleza_fisica` | Rendimiento simulado en física / química | float | 1.0–10.0 | Tecnología, Salud |
| `fortaleza_tecnologia` | Rendimiento simulado en informática / tecnología | float | 1.0–10.0 | Tecnología |

> Nota: la relación materia→área es orientativa y configurable en el recomendador.
> No se impone que un interés alto en un área implique una nota alta en la materia
> asociada (ver §8 del documento de especificación).

---

## C. Intereses — escala ordinal 1–5

Escala ordinal `1`–`5` (1 = interés muy bajo, 5 = interés muy alto). Un interés por
área es una preferencia declarada simulada.

| Variable | Definición | Tipo | Rango | Área |
|---|---|---|---|---|
| `interes_salud` | Interés declarado por el área de salud | int | 1–5 | Salud |
| `interes_tecnologia` | Interés declarado por tecnología | int | 1–5 | Tecnología |
| `interes_educacion` | Interés declarado por educación/docencia | int | 1–5 | Educación |
| `interes_arte` | Interés declarado por arte y expresión | int | 1–5 | Arte |
| `interes_social` | Interés declarado por ciencias sociales | int | 1–5 | Ciencias sociales |
| `interes_ambiente` | Interés declarado por ambiente y naturaleza | int | 1–5 | Ambiente |

---

## D. Preferencias de aprendizaje / trabajo — escala ordinal 1–5

Escala ordinal `1`–`5` con anclajes definidos explícitamente.

| Variable | Definición | Tipo | Anclaje 1 | Anclaje 5 |
|---|---|---|---|---|
| `preferencia_trabajo_equipo` | Gusto por trabajar en grupo | int | 1 = prefiere trabajar solo | 5 = prefiere siempre en equipo |
| `preferencia_trabajo_practico` | Preferencia por lo práctico vs. lo teórico | int | 1 = prefiere lo teórico | 5 = prefiere lo práctico |
| `preferencia_trabajo_autonomo` | Preferencia por autonomía vs. guía | int | 1 = prefiere trabajo guiado | 5 = prefiere trabajo autónomo |
| `preferencia_investigacion` | Interés por actividades de investigación | int | 1 = nada | 5 = mucho |

---

## E. Contexto (opcional, explícitamente ficticio)

| Variable | Definición | Tipo | Valores | Precaución |
|---|---|---|---|---|
| `contexto_curso` | Contexto mínimo del perfil | constante | `"ultimo_anio_secundario"` | Sin fecha de nacimiento ni datos personales |
| `departamento_sintetico` | Departamento asignado al azar para probar filtros territoriales | categórico | 16 departamentos de Jujuy | Asignación **independiente** de los indicadores agregados; NO usar tasas departamentales para inferir atributos individuales |

---

## F. Vínculo variable → área → carrera (uso en el recomendador)

1. **Perfil → vector de áreas**: agregar fortalezas e intereses por área mediante una
   tabla de pesos configurable y documentada. La afinidad es exploratoria, no una
   "verdad vocacional".
2. **Carrera → áreas**: construir una tabla nueva `mapeo_carrera_areas.csv` (revisable
   por el usuario) a partir del catálogo limpio. Una carrera puede pertenecer a varias
   áreas; no borrarla por aparecer en más de una categoría.
3. **Afinidad**: similitud coseno o regla ponderada entre el vector-perfil y el
   vector-carrera, mostrando qué dimensiones aportaron al puntaje y aclarando que el
   ranking depende de reglas y pesos definidos.
4. **Disponibilidad territorial ≠ afinidad**: que una carrera se ofrezca en una
   localidad no aumenta la afinidad del perfil por ella.

---

## G. Elementos excluidos por diseño

No se incluyen (ni se generarán): `carrera_ideal`, `exito_profesional`,
`prob_graduacion`, `prob_empleo`, nombres, DNI, domicilios, teléfonos, escuelas
específicas, ni ningún identificador o dato personal realista. No se usan
departamento, género o situación económica como atajos para asignar intereses o
fortalezas. No se generan correlaciones perfectas no justificadas ni etiquetas de
carrera como si fueran resultados reales.

## H. Límites y advertencias

- Los datos sintéticos no representan necesariamente a la población real de
  estudiantes de Jujuy.
- Las distribuciones se construyen para probar el prototipo y pueden introducir
  sesgos o simplificaciones.
- El dataset no permite concluir que el sistema recomiende correctamente carreras
  reales sin una evaluación independiente con participantes y procedimientos
  adecuados.

---

## Pendientes antes de generar el dataset

- Definir las distribuciones concretas y las dependencias/ruido por variable
  (documentar por qué se eligen; evitar uniformidad artificial).
- Crear la tabla de mapeo `carrera → áreas` a partir del catálogo limpio.
- Confirmar nombres exactos de columnas y orden final.
