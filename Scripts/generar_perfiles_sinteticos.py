# -*- coding: utf-8 -*-
"""
Generador reproducible de perfiles de estudiantes sinteticos.

Sistema de Orientacion Vocacional Inteligente - Jujuy, Argentina.

ADVERTENCIA
-----------
Todos los registros generados son COMPLETAMENTE FICTICIOS. No representan
estudiantes reales ni permiten validar cientificamente la orientacion
vocacional. Sirven para probar codigo, estructura, preprocesamiento,
clustering, ranking de afinidad e interfaz.

Diseno
------
- Solo libreria estandar (random, csv, argparse, statistics): no incorpora
  dependencias nuevas y garantiza reproducibilidad en una notebook modesta.
- Semilla fija por defecto (42), configurable con --seed.
- Esquema definido en
  Datos/Procesados/diccionario_variables_perfiles_sinteticos.md
- NO se generan etiquetas de carrera ideal, exito, graduacion o empleo.
- Intereses y fortalezas se generan de forma INDEPENDIENTE: un interes alto
  en un area no implica una nota alta en la materia asociada.

Uso
---
    py Scripts/generar_perfiles_sinteticos.py
    py Scripts/generar_perfiles_sinteticos.py --n 1000 --seed 42
"""

import argparse
import csv
import datetime
import os
import random
import statistics

VERSION_GENERADOR = "1.0.0"

# ---------------------------------------------------------------------------
# Definiciones del esquema (deben coincidir con el diccionario de variables)
# ---------------------------------------------------------------------------

MATERIAS = [
    "matematica",
    "lengua",
    "biologia",
    "historia",
    "fisica",
    "tecnologia",
]

AREAS = [
    "salud",
    "tecnologia",
    "educacion",
    "arte",
    "social",
    "ambiente",
]

PREFERENCIAS = [
    "trabajo_equipo",
    "trabajo_practico",
    "trabajo_autonomo",
    "investigacion",
]

# 16 departamentos de la provincia de Jujuy (asignacion ficticia).
DEPARTAMENTOS = [
    "Cochinoca",
    "El Carmen",
    "Dr. Manuel Belgrano",
    "Humahuaca",
    "Ledesma",
    "Palpala",
    "Rinconada",
    "San Antonio",
    "San Pedro",
    "Santa Barbara",
    "Santa Catalina",
    "Susques",
    "Tilcara",
    "Tumbaya",
    "Valle Grande",
    "Yavi",
]

CONTEXTO_CURSO = "ultimo_anio_secundario"

# Arquetipos de intereses: generan diversidad (concentrados, mixtos,
# exploratorios y combinaciones menos frecuentes) sin correlacionarlos con
# las notas.
ARQUETIPOS = [
    ("concentrado", 0.28),
    ("mixto", 0.27),
    ("exploratorio", 0.20),
    ("bajo_general", 0.12),
    ("alto_general", 0.13),
]


def clip(valor, minimo, maximo):
    """Limita un valor al rango [minimo, maximo]."""
    return max(minimo, min(maximo, valor))


def elegir_arquetipo(rng):
    """Selecciona un arquetipo de intereses segun sus pesos."""
    r = rng.random()
    acumulado = 0.0
    for nombre, peso in ARQUETIPOS:
        acumulado += peso
        if r <= acumulado:
            return nombre
    return ARQUETIPOS[-1][0]


def generar_fortalezas(rng):
    """Genera 6 notas sinteticas (escala 1-10, un decimal).

    Un 'nivel academico general' por estudiante introduce una correlacion
    moderada entre materias (realista), mas un efecto y ruido por materia.
    Se evita que una sola variable domine todos los patrones.
    """
    nivel_general = rng.gauss(6.3, 1.15)
    fortalezas = {}
    for materia in MATERIAS:
        efecto_materia = rng.gauss(0.0, 0.9)
        ruido = rng.gauss(0.0, 0.7)
        nota = clip(nivel_general + efecto_materia + ruido, 1.0, 10.0)
        fortalezas["fortaleza_" + materia] = round(nota, 1)
    return fortalezas


def generar_intereses(rng):
    """Genera 6 intereses (ordinal 1-5) segun un arquetipo.

    Independientes de las fortalezas academicas (ver diseno).
    """
    arquetipo = elegir_arquetipo(rng)
    valores = {}
    if arquetipo == "concentrado":
        focales = rng.sample(AREAS, rng.choice([1, 2]))
        for area in AREAS:
            valores["interes_" + area] = rng.randint(4, 5) if area in focales else rng.randint(1, 2)
    elif arquetipo == "mixto":
        focales = rng.sample(AREAS, rng.choice([3, 4]))
        for area in AREAS:
            valores["interes_" + area] = rng.randint(3, 5) if area in focales else rng.randint(1, 3)
    elif arquetipo == "exploratorio":
        for area in AREAS:
            valores["interes_" + area] = rng.randint(2, 4)
    elif arquetipo == "bajo_general":
        for area in AREAS:
            valores["interes_" + area] = rng.randint(1, 2)
    else:  # alto_general
        for area in AREAS:
            valores["interes_" + area] = rng.randint(3, 5)
    return valores


def generar_preferencias(rng):
    """Genera 4 preferencias de aprendizaje/trabajo (ordinal 1-5)."""
    centros = {
        "trabajo_equipo": 3.6,
        "trabajo_practico": 3.8,
        "trabajo_autonomo": 3.4,
        "investigacion": 3.0,
    }
    valores = {}
    for pref in PREFERENCIAS:
        valor = clip(round(rng.gauss(centros[pref], 1.0)), 1, 5)
        valores["preferencia_" + pref] = int(valor)
    return valores


def generar_dataset(n, seed, fecha):
    """Genera la lista de registros sinteticos (una fila por perfil)."""
    rng = random.Random(seed)
    registros = []
    for i in range(1, n + 1):
        registro = {
            "perfil_id": "PERF-{:04d}".format(i),
            "version_generador": VERSION_GENERADOR,
            "seed": seed,
            "origen_dato": "sintetico",
            "fecha_generacion": fecha,
        }
        registro.update(generar_fortalezas(rng))
        registro.update(generar_intereses(rng))
        registro.update(generar_preferencias(rng))
        registro["contexto_curso"] = CONTEXTO_CURSO
        registro["departamento_sintetico"] = rng.choice(DEPARTAMENTOS)
        registros.append(registro)
    return registros


def columnas_orden():
    """Devuelve el orden de columnas del CSV."""
    cols = [
        "perfil_id",
        "version_generador",
        "seed",
        "origen_dato",
        "fecha_generacion",
    ]
    cols += ["fortaleza_" + m for m in MATERIAS]
    cols += ["interes_" + a for a in AREAS]
    cols += ["preferencia_" + p for p in PREFERENCIAS]
    cols += ["contexto_curso", "departamento_sintetico"]
    return cols


def escribir_csv(registros, ruta, columnas):
    """Escribe los registros a un CSV UTF-8."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        for registro in registros:
            writer.writerow(registro)


def validar(registros, n_esperado):
    """Ejecuta validaciones obligatorias y devuelve (ok, lineas_reporte)."""
    lineas = []
    ok = True
    columnas = columnas_orden()
    n = len(registros)

    lineas.append("INFORME DE VALIDACION - PERFILES SINTETICOS")
    lineas.append("=" * 55)
    lineas.append("")

    # Dimensiones
    lineas.append("[Dimensiones]")
    lineas.append("  Filas esperadas: {} | Filas generadas: {}".format(n_esperado, n))
    lineas.append("  Columnas: {}".format(len(columnas)))
    if n != n_esperado:
        ok = False
        lineas.append("  ERROR: cantidad de filas distinta de la esperada.")

    # Nulos
    lineas.append("")
    lineas.append("[Nulos]")
    nulos = 0
    for col in columnas:
        faltantes = sum(1 for r in registros if r.get(col) in (None, ""))
        nulos += faltantes
    lineas.append("  Total de celdas nulas: {}".format(nulos))
    if nulos > 0:
        ok = False
        lineas.append("  ERROR: se encontraron valores nulos.")

    # Rangos
    lineas.append("")
    lineas.append("[Rangos]")
    for m in MATERIAS:
        col = "fortaleza_" + m
        vals = [r[col] for r in registros]
        lineas.append("  {}: min={:.1f} max={:.1f} media={:.2f}".format(
            col, min(vals), max(vals), statistics.mean(vals)))
        if min(vals) < 1.0 or max(vals) > 10.0:
            ok = False
            lineas.append("    ERROR: fuera de rango 1-10.")
    for col in (["interes_" + a for a in AREAS] + ["preferencia_" + p for p in PREFERENCIAS]):
        vals = [r[col] for r in registros]
        lineas.append("  {}: min={} max={} media={:.2f}".format(
            col, min(vals), max(vals), statistics.mean(vals)))
        if min(vals) < 1 or max(vals) > 5:
            ok = False
            lineas.append("    ERROR: fuera de rango 1-5.")

    # Duplicados
    lineas.append("")
    lineas.append("[Duplicados]")
    ids = [r["perfil_id"] for r in registros]
    ids_unicos = len(set(ids))
    lineas.append("  perfil_id unicos: {} de {}".format(ids_unicos, n))
    if ids_unicos != n:
        ok = False
        lineas.append("  ERROR: perfil_id duplicados.")
    filas_tuplas = [tuple(r[c] for c in columnas) for r in registros]
    filas_unicas = len(set(filas_tuplas))
    lineas.append("  Filas identicas (duplicadas): {}".format(n - filas_unicas))
    if filas_unicas != n:
        lineas.append("  AVISO: hay filas completamente duplicadas.")

    # Distribuciones de intereses (que no todo se concentre en un valor)
    lineas.append("")
    lineas.append("[Distribucion de intereses (frecuencia por valor 1-5)]")
    for a in AREAS:
        col = "interes_" + a
        conteo = {v: sum(1 for r in registros if r[col] == v) for v in range(1, 6)}
        lineas.append("  {}: {}".format(col, conteo))
        valores_usados = sum(1 for v in conteo.values() if v > 0)
        if valores_usados < 3:
            lineas.append("    AVISO: poca variedad de valores.")

    # Distribucion de departamentos
    lineas.append("")
    lineas.append("[Distribucion de departamento_sintetico]")
    for d in DEPARTAMENTOS:
        c = sum(1 for r in registros if r["departamento_sintetico"] == d)
        lineas.append("  {}: {}".format(d, c))

    # Diversidad de combinaciones de intereses
    lineas.append("")
    lineas.append("[Diversidad]")
    combinaciones = set(
        tuple(r["interes_" + a] for a in AREAS) for r in registros
    )
    lineas.append("  Combinaciones distintas de intereses: {}".format(len(combinaciones)))
    if len(combinaciones) < n * 0.5:
        lineas.append("  AVISO: baja diversidad de combinaciones de intereses.")

    lineas.append("")
    lineas.append("RESULTADO: {}".format("OK" if ok else "CON ERRORES"))
    return ok, lineas


def main():
    parser = argparse.ArgumentParser(
        description="Genera perfiles de estudiantes sinteticos (datos ficticios).")
    parser.add_argument("--n", type=int, default=1000,
                        help="Cantidad de perfiles (default: 1000).")
    parser.add_argument("--seed", type=int, default=42,
                        help="Semilla aleatoria (default: 42).")
    parser.add_argument("--fecha", type=str, default=None,
                        help="Fecha de generacion ISO YYYY-MM-DD (default: hoy).")
    parser.add_argument("--out", type=str, default=None,
                        help="Ruta del CSV de salida.")
    parser.add_argument("--reporte", type=str, default=None,
                        help="Ruta del informe de validacion de texto.")
    args = parser.parse_args()

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_csv = args.out or os.path.join(
        base, "Datos", "Procesados", "perfiles_estudiantes_sinteticos.csv")
    ruta_reporte = args.reporte or os.path.join(
        base, "Datos", "Procesados", "informe_validacion_perfiles_sinteticos.txt")

    fecha = args.fecha or datetime.date.today().isoformat()

    registros = generar_dataset(args.n, args.seed, fecha)
    columnas = columnas_orden()
    escribir_csv(registros, ruta_csv, columnas)

    # Comprobacion de reproducibilidad: regenerar y comparar.
    registros_2 = generar_dataset(args.n, args.seed, fecha)
    reproducible = registros == registros_2

    ok, lineas = validar(registros, args.n)
    lineas.append("")
    lineas.append("[Reproducibilidad]")
    lineas.append("  Misma semilla produce el mismo dataset: {}".format(reproducible))
    if not reproducible:
        ok = False
        lineas.append("  ERROR: el dataset no es reproducible con la misma semilla.")
    lineas.append("")
    lineas.append("Semilla: {} | Registros: {} | Fecha: {}".format(args.seed, args.n, fecha))
    lineas.append("CSV: {}".format(ruta_csv))

    reporte = "\n".join(lineas)
    with open(ruta_reporte, "w", encoding="utf-8") as f:
        f.write(reporte + "\n")

    print(reporte)
    print("")
    print("Informe guardado en: {}".format(ruta_reporte))


if __name__ == "__main__":
    main()
