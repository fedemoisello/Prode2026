import pytest
from lib.terceros import mejores_terceros, asignar_terceros
from lib.constants import TERCEROS_VALIDOS


def make_terceros(grupos_con_pts):
    return {
        g: {"grupo": g, "equipo": f"EQ{g}", "pts": pts, "dg": 0, "gf": pts}
        for g, pts in grupos_con_pts.items()
    }


def test_mejores_terceros_toma_top8():
    tpg = make_terceros({g: 10 - i for i, g in enumerate("ABCDEFGHIJKL")})
    mejores = mejores_terceros(tpg)
    assert len(mejores) == 8
    grupos_mejores = {t["grupo"] for t in mejores}
    assert "A" in grupos_mejores  # el mejor
    assert "L" not in grupos_mejores  # el peor


def test_mejores_terceros_ordena_por_pts():
    tpg = make_terceros({"A": 3, "B": 7, "C": 5})
    for g in "DEFGHIJKL":
        tpg[g] = {"grupo": g, "equipo": f"EQ{g}", "pts": 1, "dg": 0, "gf": 1}
    mejores = mejores_terceros(tpg)
    assert mejores[0]["grupo"] == "B"
    assert mejores[1]["grupo"] == "C"
    assert mejores[2]["grupo"] == "A"


def test_asignar_terceros_respeta_restricciones():
    # Usar grupos que tengan al menos un slot válido cada uno
    tpg = make_terceros({"A": 9, "C": 8, "E": 7, "F": 6, "G": 5, "H": 4, "I": 3, "J": 2})
    mejores = mejores_terceros(tpg)
    asignacion = asignar_terceros(mejores)

    assert len(asignacion) == 8
    for slot, equipo in asignacion.items():
        grupo_asignado = equipo[2]  # "EQA" → "A"
        assert grupo_asignado in TERCEROS_VALIDOS[slot], \
            f"Grupo {grupo_asignado} no válido para slot {slot}"


def test_asignar_terceros_sin_repeticion():
    tpg = make_terceros({"A": 9, "C": 8, "E": 7, "F": 6, "G": 5, "H": 4, "I": 3, "J": 2})
    mejores = mejores_terceros(tpg)
    asignacion = asignar_terceros(mejores)
    equipos = list(asignacion.values())
    assert len(set(equipos)) == len(equipos), "No debe haber equipos repetidos"
