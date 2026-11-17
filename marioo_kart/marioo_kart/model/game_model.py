from unittest import case

from constants import GameState, GRID_ROWS, GRID_COLS, COLLISION_REBOND
from model.collision import CollisionManager
from model.car import Car, SPORTS, SPORTS_BLUE, TRUCK
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.terrain import Road, Herbe, Terre, Glace, Vide   
from model.race_coordinator import RaceCoordinator

class GameModel:

    """Modèle du jeu pour gérer l'état et les interactions.
    Attributes:
        state (GameState): L'état actuel du jeu (MENU, RACING, etc.).
        circuit (Circuit | None): Le circuit actuel du jeu.
        car (Car | None): La voiture du joueur.
        car2 (Car | None): La deuxième voiture du joueur.
        terrain_precedent (str|None): Nom du dernier revêtement de la voiture.
        """

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.car: Car | None = None
        self.car2: Car | None = None
        self.coordinateur: RaceCoordinator | None = None
        self.terrain_precedent = None
        self.collisions = CollisionManager(COLLISION_REBOND)
        self.menu_options = ["JOUER", "QUITTER"]
        self.menu_selection = 0  # index du bouton sélectionné dans le menu

    def load_circuit(self) -> None:
        """Crée le circuit, les checkpoints et les deux voitures.

        Returns:
            None
        """

        # R = Route, H = Herbe, T = Terre, G = Glace, V = Vide
        
        plan = [
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
        "RRRRRRRRHHHHHHHH"
    ]
        terrains = {"R": Road,"H": Herbe,"T": Terre,"G": Glace,"V": Vide}

        grid = []

        for row in range(GRID_ROWS):
            ligne = []
            for col in range(GRID_COLS):
                lettre = plan[row][col]
                terrain = terrains[lettre]()
                case = RoadTile(col, row, terrain)
                ligne.append(case)
            grid.append(ligne)

        self.circuit = Circuit(grid=grid)

        #Création des checkpoints avec leurs cases et leurs positions de réapparition
        self.circuit.add_checkpoint(cases=[(col, 9) for col in range(13, 16)],reapparition=(14,9))
        self.circuit.add_checkpoint(cases=[(col, 1) for col in range(12, 16)],reapparition=(13, 1))
        self.circuit.add_checkpoint(cases=[(col, 3) for col in range(0, 12)],reapparition=(7, 3))

        #Placement des boosts
        self.circuit.add_boost(13, 1)
        self.circuit.add_boost(14, 1)
        self.circuit.add_boost(13, 2)
        self.circuit.add_boost(14, 2)

        #Placement de la ligne d'arrivée
        self.circuit.add_arrivee(8, 10)
        self.circuit.add_arrivee(8, 11)

        #Placement des positions de départ pour les deux joueurs
        self.circuit.add_depart(1,7, 10)
        self.circuit.add_depart(2,7, 11)

        self.terrain_precedent = None

        #création voiture
        self.spawn_car()

        #Création du coordinateur de course
        self.coordinateur = RaceCoordinator(self.circuit)

        #Enregistrement des 2 voitures 
        col1,row1 = self.circuit.departs[1]
        col2,row2 = self.circuit.departs[2]

        self.coordinateur.ajouter_voiture(self.car,col1,row1)
        self.coordinateur.ajouter_voiture(self.car2,col2,row2)

        #Mémorise si chaque voiture est déjà sur un boost
        self.sur_boost = {self.car: False,self.car2: False}

        print(self.coordinateur.progression)  # Affiche l'état initial de la progression des voitures

    def spawn_car(self) -> None:

        """Crée les deux voitures du jeu avec leurs caractéristiques respectives."""

        col1,row1 = self.circuit.departs[1]
        col2,row2 = self.circuit.departs[2]

        self.car = Car(SPORTS,col1,row1)
        self.car2 = Car(TRUCK,col2,row2)

    def update(self) -> None:
        """Met à jour l'état du jeu, y compris la position de la voiture et les interactions avec le circuit.
            Les caractéristiques du terrain sont affichées si la voiture rentre sur un revêtement différent
            ou affiche un message si la voiture est en dehors du circuit.
            
            Returns: None"""
        if self.state != GameState.RACING or self.circuit is None:
            return

        for voiture in [self.car, self.car2]:

            # Terrain avant déplacement : utilisé pour la physique
            case = self.circuit.get_tile_at_pixel(voiture.x, voiture.y)

            if case is None or isinstance(case.terrain, Vide):
                self.sur_boost[voiture] = False
                self.coordinateur.faire_reapparaitre(voiture)
                continue

            # Déplacement avec la physique développée par l'équipe
            derapait_avant = voiture.drifting
            voiture.update_position(case.terrain)

            if voiture.drifting != derapait_avant:
                etat = "DÉRAPE" if voiture.drifting else "adhère"
                print(f"{voiture.stats.name} {etat} sur {case.terrain.name}")

            # Nouvelle position après déplacement
            case = self.circuit.get_tile_at_pixel(voiture.x, voiture.y)

            if case is None or isinstance(case.terrain, Vide):
                self.sur_boost[voiture] = False
                self.coordinateur.faire_reapparaitre(voiture)
                continue

            # Checkpoints
            if self.coordinateur.verifier_checkpoint(voiture, case.col, case.row):
                indice = self.coordinateur.progression[voiture]
                print(f"Checkpoint {indice + 1} validé sur la case ({case.col}, {case.row})")

            # Ligne d'arrivée
            if self.coordinateur.verifier_arrivee(voiture, case.col, case.row):
                print(f"Tour terminé : {self.coordinateur.tours[voiture]}/3")

            # Boosts
            est_sur_boost = (case.col, case.row) in self.circuit.boosts

            if est_sur_boost and not self.sur_boost[voiture]:
                voiture.speed = min(voiture.speed + 3, voiture.stats.max_speed)
                print(f"Boost activé ! Vitesse : {voiture.speed}")

            self.sur_boost[voiture] = est_sur_boost

        # Collisions entre voitures et détection d'aspiration
        voitures = [self.car, self.car2]
        self.collisions.gerer_collisions(voitures)
        aspiration_avant = {v: v.en_aspiration for v in voitures}
        self.collisions.detecter_aspiration(voitures)
        for v in voitures:
            if v.en_aspiration != aspiration_avant[v]:
                etat = "entre en" if v.en_aspiration else "sort de"
                print(f"{v.stats.name} {etat} aspiration")

        # Affichage des changements de terrain du joueur 1
        case = self.circuit.get_tile_at_pixel(self.car.x, self.car.y)

        if case is not None:
            terrain = case.terrain

            if terrain.name != self.terrain_precedent:
                print(f"Terrain: {terrain.name}, Traction: {terrain.traction}, Grip: {terrain.grip}, Friction: {terrain.friction}")
                self.terrain_precedent = terrain.name

        

        