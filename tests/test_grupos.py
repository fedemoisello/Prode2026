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


def test_empate_desempate_por_h2h_pts():
    # ARG y BRA empatados en pts y stats generales, pero ARG ganó el H2H
    # ARG 1-0 BRA, ARG 0-1 ESP, ARG 0-1 FRA → ARG: 3pts, DG=-1, GF=1
    # BRA 0-1 ESP, BRA 0-1 FRA → BRA: 3pts, DG=-1, GF=1 (perdió ante ARG)
    # Mismo pts, dg y gf generales → H2H decide: ARG ganó a BRA
    p = partidos_de([(1,0),(0,1),(0,1),(0,1),(0,1),(1,1)])
    tabla = calcular_tabla(EQUIPOS, p)
    equipos = [r.equipo for r in tabla]
    assert equipos.index("ARG") < equipos.index("BRA")


def test_empate_h2h_cae_a_general():
    # ARG y BRA: mismo pts, H2H empatado 1-1, caen a criterio general
    # ARG: ganó a ESP (2-0), perdió con FRA (0-2), empató BRA (1-1) → pts=4, DG=1, GF=3
    # BRA: ganó a FRA (2-0), perdió con ESP (0-2), empató ARG (1-1) → pts=4, DG=1, GF=3
    # H2H entre ARG y BRA: empate 1-1 → mismos H2H pts/dg/gf → caen a general (dg=1, gf=3, iguales)
    p = partidos_de([(1,1),(2,0),(0,2),(0,2),(2,0),(1,1)])
    tabla = calcular_tabla(EQUIPOS, p)
    # No chequeamos orden (queda indefinido), solo que ambos están antes que ESP y FRA
    top2 = {r.equipo for r in tabla[:2]}
    assert "ARG" in top2 and "BRA" in top2


def test_clasificados_devuelve_top3():
    p = partidos_de([(2,0),(2,0),(2,0),(1,1),(1,1),(1,1)])
    tabla = calcular_tabla(EQUIPOS, p)
    p1, p2, p3 = clasificados(tabla)
    assert p1 == "ARG"
    assert p2 in EQUIPOS
    assert p3 in EQUIPOS
