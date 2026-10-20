from constants import GameState, GRID_ROWS, GRID_COLS
from model.car import Car, SPORTS, SPORTS_BLUE
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.terrain import Road, Herbe, Terre, Glace, Vide   

class GameModel:

    """Modèle du jeu pour gérer l'état et les interactions.
    Attributes:
        state (GameState): L'état actuel du jeu (MENU, RACING, etc.).
        circuit (Circuit | None): Le circuit actuel du jeu.
        car (Car | None): La voiture du joueur.
        terrain_precedent (str|None): Nom du dernier revêtement de la voiture.
        """

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.car: Car | None = None
        self.car2: Car | None = None
        self.terrain_precedent = None  

    def load_circuit(self) -> None:
        grid = []
        for row in range(GRID_ROWS):
            ligne = []
            for col in range(GRID_COLS):
                if row < 2:
                    terrain = Herbe()
                elif row < 4:
                    terrain = Terre()
                elif row < 7:
                    terrain = Glace()
                elif row < 10:
                    terrain = Vide()
                else:
                    terrain = Road()
                case = RoadTile(col, row, terrain)
                ligne.append(case)
            grid.append(ligne)

        self.circuit = Circuit(grid=grid)
        self.terrain_precedent = None
        self.spawn_car()

    def spawn_car(self) -> None:
        self.car = Car(SPORTS, 7, 3)
        self.car2 = Car(SPORTS_BLUE, 8, 3)

    def update(self) -> None:
        """Met à jour l'état du jeu, y compris la position de la voiture et les interactions avec le circuit.
            Les caractéristiques du terrain sont affichées si la voiture rentre sur un revêtement différent
            ou affiche un message si la voiture est en dehors du circuit.
            
            Returns: None"""
        if self.state != GameState.RACING or self.circuit is None:
            return
        #Mise à jour la position de la voiture en fonction de son état actuel et des entrées du joueur.
        self.car.update_position()
        self.car2.update_position()
        
        case = self.circuit.get_tile_at_pixel(self.car.x, self.car.y)
        if case is not None:
            terrain = case.terrain
            if terrain.name != self.terrain_precedent:
                print(f"Terrain: {terrain.name}, Traction: {terrain.traction}, Grip: {terrain.grip}, Friction: {terrain.friction}")
                self.terrain_precedent = terrain.name
        else:
            if self.terrain_precedent != "Vide":
                print("La voiture est en dehors du circuit.")                
                self.terrain_precedent = "Vide"