from model.road_tile import RoadTile
from constants import TILE_SIZE
from model.terrain import Vide

class Circuit:

    """
    Classe représentant le circuit de course.
    Attributes:
        grid (list[list[RoadTile]]): Grille des cases du circuit.
        rows (int): Nombre de lignes dans la grille.
        cols (int): Nombre de colonnes dans la grille.
        checkpoints (list[dict]): Liste des points de passage, chaque point de passage est un dictionnaire contenant les cases et la position de réapparition.
        boosts (list[tuple[int, int]]): Liste des positions des boosts sur le circuit.
    """

    def __init__(self,  grid: list[list[RoadTile]]):
        """Initialise le circuit et points de passage.
        Args:
            grid (list[list[RoadTile]]): Grille des cases du circuit.
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        self.checkpoints = []
        self.boosts = []
        self.arrivee = []

    def get_tile(self, col: int, row: int) -> RoadTile | None:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def add_checkpoint(self, cases : list[tuple[int, int]], reapparition: tuple[int, int]) -> None:

        """Ajoute un point de passage à la liste des checkpoints.
        Args:
            cases (list[tuple[int, int]]): Liste des coordonnées des points de passage.
            reapparition (tuple[int, int]): Coordonnées de reapparition.
        Raises:
            ValueError: si la zone est vide ou si une case est hors du circuit ou de type Vide.
        """

        if not cases:
            raise ValueError("Un checkpoint doit contenir des cases.")

        for col, row in cases + [reapparition]:
            case = self.get_tile(col, row)
            if case is None or isinstance(case.terrain, Vide):
                raise ValueError(f"La case ({col}, {row}) n'est pas sur le circuit ou est de type Vide.")

        self.checkpoints.append({"cases": cases, "reapparition": reapparition})
       

    def get_tile_at_pixel(self, px: float, py: float) -> RoadTile | None:
        col = int(px // TILE_SIZE)
        row = int(py // TILE_SIZE)
        return self.get_tile(col, row)

    def pixel_width(self) -> int:
        return self.cols * TILE_SIZE

    def pixel_height(self) -> int:
        return self.rows * TILE_SIZE

    def add_boost(self, col: int, row: int) -> None:
        """Ajoute une case de boost au circuit.
        Args:
            col (int): Colonne de la case de boost.
            row (int): Ligne de la case de boost.
        Returns:
            None
        """
        self.boosts.append((col, row))

    def add_arrivee(self, col: int, row: int) -> None:
        """Ajoute une case d'arrivée au circuit.
        Args:
            col (int): Colonne de la case d'arrivée.
            row (int): Ligne de la case d'arrivée.
        Returns:
            None
        """
        self.arrivee.append((col, row))