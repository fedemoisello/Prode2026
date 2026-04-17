GRUPOS = list("ABCDEFGHIJKL")

# Equipos por grupo
EQUIPOS_POR_GRUPO = {
    "A": ["MEX", "RSA", "KOR", "CZE"],
    "B": ["CAN", "BIH", "QAT", "SUI"],
    "C": ["BRA", "MAR", "HAI", "SCO"],
    "D": ["USA", "PAR", "AUS", "TUR"],
    "E": ["GER", "CUW", "CIV", "ECU"],
    "F": ["NED", "JPN", "SWE", "TUN"],
    "G": ["BEL", "EGY", "IRN", "NZL"],
    "H": ["ESP", "CPV", "KSA", "URU"],
    "I": ["FRA", "SEN", "IRQ", "NOR"],
    "J": ["ARG", "ALG", "AUT", "JOR"],
    "K": ["POR", "COD", "UZB", "COL"],
    "L": ["ENG", "CRO", "GHA", "PAN"],
}

# Partidos de fase de grupos por grupo (IDs 1-72)
PARTIDOS_POR_GRUPO = {
    "A": [1, 2, 3, 4, 5, 6],
    "B": [7, 8, 9, 10, 11, 12],
    "C": [13, 14, 15, 16, 17, 18],
    "D": [19, 20, 21, 22, 23, 24],
    "E": [25, 26, 27, 28, 29, 30],
    "F": [31, 32, 33, 34, 35, 36],
    "G": [37, 38, 39, 40, 41, 42],
    "H": [43, 44, 45, 46, 47, 48],
    "I": [49, 50, 51, 52, 53, 54],
    "J": [55, 56, 57, 58, 59, 60],
    "K": [61, 62, 63, 64, 65, 66],
    "L": [67, 68, 69, 70, 71, 72],
}

# Bracket de 16vos: grupos de terceros válidos por partido
# Clave: partido_id, Valor: set de grupos de los que puede venir el 3ro
TERCEROS_VALIDOS = {
    74: set("ABCDF"),
    77: set("CDFGH"),
    79: set("CEFHI"),
    80: set("EHIJK"),
    81: set("BEFIJ"),
    82: set("AEHIJ"),
    85: set("EFGIJ"),
    87: set("DEIJL"),
}

# Bracket de 16vos: qué partidos se conectan en 8vos (W = winner)
BRACKET_8VOS = {
    89: (74, 77),
    90: (73, 75),
    91: (76, 78),
    92: (79, 80),
    93: (83, 84),
    94: (81, 82),
    95: (86, 88),
    96: (85, 87),
}

BRACKET_CUARTOS = {
    97: (89, 90),
    98: (93, 94),
    99: (91, 92),
    100: (95, 96),
}

BRACKET_SEMIS = {
    101: (97, 98),
    102: (99, 100),
}

BRACKET_FINAL = {104: (101, 102)}
BRACKET_TERCER = {103: (101, 102)}  # losers

# Puntos por fase para ganador de cruce
PUNTOS_GANADOR = {
    "16vos":         5,
    "8vos":         10,
    "cuartos":      20,
    "semi":         40,
    "tercer_puesto": 20,
    "final":        80,  # campeón
}

# Scoring grupos y eliminatorias
PUNTOS_TENDENCIA = 2       # W/D/L correcto
PUNTOS_GOL_EQUIPO = 1      # goles de un equipo exactos
PUNTOS_RESULTADO_BONUS = 2 # bonus cuando tendencia + ambos goles correctos
PUNTOS_CLASIFICADO_12 = 3  # acertar 1ro o 2do de grupo
PUNTOS_MEJOR_TERCERO = 5   # acertar que el 3ro de un grupo clasificó
PUNTOS_SUBCAMPEON = 40
PUNTOS_TERCER_PUESTO = 20
