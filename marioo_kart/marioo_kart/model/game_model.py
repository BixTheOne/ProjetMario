from constants import GameState, GRID_ROWS, GRID_COLS
from model.car import Car
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.terrain import Road, Herbe, Terre, Glace, Vide   

class GameModel:

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.car: Car | None = None

    def load_circuit(self) -> None:
        grid = []
        for row in range(GRID_ROWS):
            ligne = []
            for col in range(GRID_COLS):
                if col < 4:
                    terrain = Herbe()
                elif col < 8:
                    terrain = Terre()
                elif col < 12:
                    terrain = Glace()
                else:
                    terrain = Road()
                case = RoadTile(col, row, terrain)
                ligne.append(case)
            grid.append(ligne)

        self.circuit = Circuit(grid=grid)
        self.spawn_car()

    def spawn_car(self) -> None:
        self.car = Car(7, 1)

    def update(self) -> None:
        if self.state != GameState.RACING or self.circuit is None:
            return
        self.car.update_position()
