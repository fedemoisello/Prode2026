import pytest
from lib.scoring import puntos_partido_grupos, puntos_partido_eliminatoria
from lib.constants import (
    PUNTOS_TENDENCIA, PUNTOS_GOL_EQUIPO, PUNTOS_RESULTADO_BONUS,
    PUNTOS_GANADOR,
)


def test_resultado_exacto():
    pts = puntos_partido_grupos(2, 1, 2, 1)
    assert pts == PUNTOS_TENDENCIA + PUNTOS_GOL_EQUIPO * 2 + PUNTOS_RESULTADO_BONUS


def test_tendencia_correcta_sin_goles():
    pts = puntos_partido_grupos(2, 0, 3, 1)
    assert pts == PUNTOS_TENDENCIA


def test_tendencia_correcta_un_gol():
    pts = puntos_partido_grupos(2, 1, 2, 0)
    assert pts == PUNTOS_TENDENCIA + PUNTOS_GOL_EQUIPO


def test_tendencia_incorrecta_gol_local_ok():
    # Predije 2-1 (L gana), fue 2-2 (empate)
    pts = puntos_partido_grupos(2, 1, 2, 2)
    assert pts == PUNTOS_GOL_EQUIPO  # solo el gol local


def test_empate_exacto():
    pts = puntos_partido_grupos(1, 1, 1, 1)
    assert pts == PUNTOS_TENDENCIA + PUNTOS_GOL_EQUIPO * 2 + PUNTOS_RESULTADO_BONUS


def test_todo_mal():
    pts = puntos_partido_grupos(0, 0, 3, 2)
    assert pts == 0


def test_eliminatoria_ganador_correcto():
    pts = puntos_partido_eliminatoria("ARG", None, None, "ARG", 1, 0, "cuartos")
    assert pts == PUNTOS_GANADOR["cuartos"]


def test_eliminatoria_ganador_y_resultado():
    pts = puntos_partido_eliminatoria("ARG", 1, 0, "ARG", 1, 0, "semi")
    expected = PUNTOS_GANADOR["semi"] + PUNTOS_GOL_EQUIPO * 2 + PUNTOS_RESULTADO_BONUS
    assert pts == expected


def test_eliminatoria_ganador_incorrecto():
    pts = puntos_partido_eliminatoria("BRA", 1, 0, "ARG", 1, 0, "final")
    # Ganador mal (0 pts), pero gol local correcto (1pt) y gol visitante correcto (1pt), no bonus sin ganador
    assert pts == PUNTOS_GOL_EQUIPO * 2


def test_eliminatoria_sin_picks_goles():
    pts = puntos_partido_eliminatoria("ARG", None, None, "ARG", 2, 1, "16vos")
    assert pts == PUNTOS_GANADOR["16vos"]
