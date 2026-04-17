import pytest
from lib.grupos import calcular_tabla, clasificados

EQUIPOS = ["ARG", "BRA", "ESP", "FRA"]

def partidos_de(resultados):
    pares = [
        ("ARG", "BRA"), ("ARG", "ESP"), ("ARG", "FRA"),
        ("BRA", "ESP"), ("BRA", "FRA"), ("ESP", "FRA"),
    ]
    return [
        {"local": l, "visitante": v, "goles_local": gl, "goles_visitante": gv}
        for (l, v), (gl, gv) in zip(pares, resultados)
    ]


def test_primero_claro():
    # ARG gana todos
    p = partidos_de([(2,0),(2,0),(2,0),(1,1),(1,1),(1,1)])
    tabla = calcular_tabla(EQUIPOS, p)
    assert tabla[0].equipo == "ARG"
    assert tabla[0].pts == 9


def test_empate_desempate_por_dg():
    # ARG y BRA con mismos puntos, ARG con mejor DG
    p = partidos_de([(3,0),(1,0),(1,0),(0,0),(0,0),(0,0)])
    tabla = calcular_tabla(EQUIPOS, p)
    assert tabla[0].equipo == "ARG"


def test_partidos_sin_resultado_ignorados():
    p = [
        {"local": "ARG", "visitante": "BRA", "goles_local": None, "goles_visitante": None},
        {"local": "ARG", "visitante": "ESP", "goles_local": 1, "goles_visitante": 0},
        {"local": "ARG", "visitante": "FRA", "goles_local": 1, "goles_visitante": 0},
        {"local": "BRA", "visitante": "ESP", "goles_local": 0, "goles_visitante": 0},
        {"local": "BRA", "visitante": "FRA", "goles_local": 0, "goles_visitante": 0},
        {"local": "ESP", "visitante": "FRA", "goles_local": 0, "goles_visitante": 0},
    ]
    tabla = calcular_tabla(EQUIPOS, p)
    arg = next(r for r in tabla if r.equipo == "ARG")
    assert arg.pj == 2


def test_todos_empatan():
    p = partidos_de([(1,1),(1,1),(1,1),(1,1),(1,1),(1,1)])
    tabla = calcular_tabla(EQUIPOS, p)
    for row in tabla:
        assert row.pts == 3
        assert row.dg == 0


def test_clasificados_devuelve_top3():
    p = partidos_de([(2,0),(2,0),(2,0),(1,1),(1,1),(1,1)])
    tabla = calcular_tabla(EQUIPOS, p)
    p1, p2, p3 = clasificados(tabla)
    assert p1 == "ARG"
    assert p2 in EQUIPOS
    assert p3 in EQUIPOS
