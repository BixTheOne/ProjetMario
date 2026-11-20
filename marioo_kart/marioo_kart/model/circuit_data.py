"""
Données des circuits disponibles dans le jeu.

Chaque circuit est un dictionnaire contenant :
    nom (str): nom affiché à l'écran de sélection.
    plan (list[str]): une chaîne par ligne de la grille, une lettre par case.
        R = Route, H = Herbe, T = Terre, G = Glace, V = Vide
    checkpoints (list[dict]): dans l'ordre de passage, chacun avec ses cases
        et sa case de réapparition (col, row).
    boosts (list[tuple[int, int]]): cases de boost (col, row).
    arrivee (list[tuple[int, int]]): cases de la ligne d'arrivée (col, row).
    departs (dict[int, tuple[int, int]]): case de départ de chaque joueur (col, row).
"""

CIRCUITS = [
    {
        "nom": "Circuit 1",
        "plan": [
            "TTTTTTTTTTTTGGGG",
            "TTTTTTTTTTTTGGGG",
            "TTTTTTTTTTTTVGHH",
            "TTTTTTTTTTTTVGHH",
            "TTVVVVVTTTTTVVHH",
            "TTTTTTVTTTTTVVHH",
            "TTTTTTVTTTTTVVHH",
            "RTTTTTVTTTTTVVHH",
            "RRTTTTVVVVVVVVHH",
            "RRRTTTTTTTTTTHHH",
            "RRRRRRRRHHHHHHHH",
            "RRRRRRRRHHHHHHHH",
        ],
        "checkpoints": [
            {"cases": [(col, 9) for col in range(13, 16)], "reapparition": (14, 9)},
            {"cases": [(col, 1) for col in range(12, 16)], "reapparition": (13, 1)},
            {"cases": [(col, 3) for col in range(0, 12)],  "reapparition": (7, 3)},
        ],
        "boosts": [(7, 2), (8, 2), (9, 2), (10, 2)],
        "blocs_objets": [(5, 2), (6, 2)],
        "arrivee": [(8, 10), (8, 11)],
        "departs": {1: (7, 10), 2: (7, 11)},
    },
    {
        "nom": "Anneau",
        "plan": [
            "HHHHHHHHHHHHHHHH",
            "HRRRRRRRRRRRRRRH",
            "HRRRRRRRRRRRRRRH",
            "HRRHHHHHHHHHHRRH",
            "HRRHVVVVVVVVHRRH",
            "HRRHVVVVVVVVHRRH",
            "HRRHVVVVVVVVHRRH",
            "HRRHVVVVVVVVHRRH",
            "HRRHHHHHHHHHHRRH",
            "HRRRRRRRRRRRRRRH",
            "HRRRRRRRRRRRRRRH",
            "HHHHHHHHHHHHHHHH",
        ],
        "checkpoints": [
            {"cases": [(13, 5), (14, 5)], "reapparition": (13, 5)},
            {"cases": [(8, 1), (8, 2)],   "reapparition": (8, 1)},
            {"cases": [(1, 5), (2, 5)],   "reapparition": (1, 5)},
        ],
        "boosts": [(5, 1), (5, 2)],
        "blocs_objets": [(10, 1), (10, 2)],
        "arrivee": [(8, 9), (8, 10)],
        "departs": {1: (6, 9), 2: (6, 10)},
    },
]