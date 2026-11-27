from unittest import case

from constants import GameState, GRID_ROWS, GRID_COLS, COLLISION_REBOND
from model.collision import CollisionManager
from model.car import Car, CARS
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.terrain import Road, Herbe, Terre, Glace, Vide   
from model.race_coordinator import RaceCoordinator
from model.circuit_data import CIRCUITS
from model.bloc_special import Champignon, Banane, CarapaceBleue, Bombe, Etoile
import random
import math
import time
from constants import COULEURS_JOUEURS


class GameModel:

    """Modèle du jeu pour gérer l'état et les interactions.
    Attributes:
        state (GameState): L'état actuel du jeu (MENU, RACING, etc.).
        circuit (Circuit | None): Le circuit actuel du jeu.
        car (Car | None): La voiture du joueur.
        car2 (Car | None): La deuxième voiture du joueur.
        terrain_precedent (str|None): Nom du dernier revêtement de la voiture.
        objets_voitures (dict): Associe chaque voiture à son cadeau.
                        None signifie qu'elle ne possède aucun cadeau.
        sur_cadeau (dict): Indique si chaque voiture se trouve sur un cadeau
        bananes (list): Liste des bananes déposées sur la piste
        bombes (list): Liste des bombes déposées sur la psite
        temps_bombes (dict): Associe à chaque bombe son instant de dépôt
        temps_etoile(dict): Associe chaque voiture à la fin de son invincibilité
        """

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.car: Car | None = None
        self.car2: Car | None = None
        self.coordinateur: RaceCoordinator | None = None
        self.terrain_precedent = None
        self.objets_voitures = {}
        self.sur_cadeau ={}
        self.bananes = []
        self.bombes = []
        self.temps_bombes={}
        self.temps_etoiles={}
        self.collisions = CollisionManager(COLLISION_REBOND)
        self.menu_options = ["JOUER", "RÈGLES", "QUITTER"]
        self.menu_selection = 0  # index du bouton sélectionné dans le menu

        #choix de la voiture et du circuit
        self.choix_voiture = {1: 0, 2: 1}         # indice dans CARS pour chaque joueur
        self.joueur_pret = {1: False, 2: False}   # True quand le joueur a validé
        self.choix_circuit = 0         
                    # indice dans CIRCUITS
    def load_circuit(self) -> None:
        """Crée le circuit choisi, ses checkpoints, boosts/blocs cadeaux, arrivée et départs,
        puis les deux voitures choisies.

        Returns:
            None
        """
        infos = CIRCUITS[self.choix_circuit]
        terrains = {"R": Road, "H": Herbe, "T": Terre, "G": Glace, "V": Vide}

        # Construction de la grille à partir du plan
        grid = []
        for row in range(GRID_ROWS):
            ligne = []
            for col in range(GRID_COLS):
                lettre = infos["plan"][row][col]
                terrain = terrains[lettre]()
                ligne.append(RoadTile(col, row, terrain))
            grid.append(ligne)

        self.circuit = Circuit(grid=grid)

        # Checkpoints, boosts,blocs cadeaux, arrivée et départs du circuit choisi
        for cp in infos["checkpoints"]:
            self.circuit.add_checkpoint(cases=cp["cases"], reapparition=cp["reapparition"])
        for col, row in infos["boosts"]:
            self.circuit.add_boost(col, row)
        for col, row in infos["blocs_objets"]:
            self.circuit.add_bloc_objet(col, row)
        for col, row in infos["arrivee"]:
            self.circuit.add_arrivee(col, row)
        for joueur, (col, row) in infos["departs"].items():
            self.circuit.add_depart(joueur, col, row)

        self.terrain_precedent = None

        # Création des voitures choisies
        self.spawn_car()

        # Création du coordinateur de course
        self.coordinateur = RaceCoordinator(self.circuit)
        col1, row1 = self.circuit.departs[1]
        col2, row2 = self.circuit.departs[2]
        self.coordinateur.ajouter_voiture(self.car, col1, row1)
        self.coordinateur.ajouter_voiture(self.car2, col2, row2)

        # Mémorise si chaque voiture est déjà sur un boost
        self.sur_boost = {self.car: False, self.car2: False}

    def spawn_car(self) -> None:

        """Crée les deux voitures du jeu avec leurs caractéristiques respectives sur leurs cases de départ"""

        col1, row1 = self.circuit.departs[1]
        col2, row2 = self.circuit.departs[2]

        self.car = Car(CARS[self.choix_voiture[1]], col1, row1, COULEURS_JOUEURS[1])
        self.car2 = Car(CARS[self.choix_voiture[2]], col2, row2, COULEURS_JOUEURS[2])

        #Objet possédé par voiture au départ => None

        self.objets_voitures = {self.car : None, self.car2 : None}
        self.sur_cadeau ={self.car : False, self.car2 : False}

    def update(self) -> None:
        """Met à jour l'état du jeu, y compris la position de la voiture et les interactions avec le circuit.
            Les caractéristiques du terrain sont affichées si la voiture rentre sur un revêtement différent
            ou affiche un message si la voiture est en dehors du circuit (uniquement pour le joueur 1) 
            Affichage de message pour les différents objets rencontrés (boosts/cadeaux) ainsi que leur activation 
            par un des joueurs.          
            Returns: 
                None
            """
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

            # Détection du passage sur un bloc cadeau
            est_sur_cadeau = False

            for bloc in self.circuit.blocs_objets:
                if case.col == bloc.col and case.row == bloc.row:
                    est_sur_cadeau = True

            #Affectation du type de bloc cadeau
            cadeaux = [Champignon,Banane,Bombe,Etoile,CarapaceBleue]

            if est_sur_cadeau and not self.sur_cadeau[voiture]:
                if self.objets_voitures[voiture] is None:

                    probabilites = [35,30,20,10,5]
                    cadeau = random.choices(cadeaux,weights=probabilites,k=1)[0]
                    self.objets_voitures[voiture] = cadeau()
                    print(f"Cadeau récupéré : {self.objets_voitures[voiture].nom} par {voiture.stats.name}")

            self.sur_cadeau[voiture]=est_sur_cadeau

        #Vérification coliisions avec objets déposés par un des joueurs

        self.verifier_collisions_bananes()
        self.verifier_collision_bombes()
        self.verifier_etoiles()

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
        

    # choix de la voiture et du circuit

    def reset_selection(self) -> None:
        """Remet les deux joueurs en mode 'pas encore prêt'."""
        self.joueur_pret = {1: False, 2: False}

    def changer_voiture(self, joueur: int, direction: int) -> None:
        """Passe à la voiture suivante (+1) ou précédente (-1), en boucle."""
        if self.joueur_pret[joueur]:
            return  # un joueur qui a validé ne peut plus changer
        self.choix_voiture[joueur] = (self.choix_voiture[joueur] + direction) % len(CARS)

    def valider_voiture(self, joueur: int) -> None:
        self.joueur_pret[joueur] = True

    def tous_prets(self) -> bool:
        return all(self.joueur_pret.values())

    def changer_circuit(self, direction: int) -> None:
        self.choix_circuit = (self.choix_circuit + direction) % len(CIRCUITS)

    #méthode vérification passage sur banane

    def verifier_collisions_bananes(self):
        """Détecte la collision entre une voiture et bananes déposées.
        Banane disparaît si la voiture passe suffisamment près."""

        for voiture in [self.car,self.car2]:
            for banane in self.bananes[:]:
                x,y = banane

                distance = math.sqrt((voiture.x-x)**2 + (voiture.y-y)**2)

                if distance < 20:
                    self.bananes.remove(banane)

                    if voiture in self.temps_etoiles:
                        print(f"{voiture.stats.name} a touché une banane avec invincibilité")
                    else:
                        print(f"{voiture.stats.name} a touché une banane sans invincibilité")

    #méthode vérification passage sur bombe

    def verifier_collision_bombes(self):
        """Détecte l'explosion d'une bombe.
        Une bombe explose après 3 secondes ou lorsque qu'une voiture passe à moins de 20 pixels.
        Toutes les voitures situées dans un rayon de 80 pixels seront touchées par l'explosion.
        """
        
        
        for bombe in self.bombes[:]:
            x,y = bombe

            temps_ecoule = time.monotonic() - self.temps_bombes[(x,y)]

            explosion = temps_ecoule >= 3

            for voiture in [self.car,self.car2]:

                distance = math.sqrt((voiture.x-x)**2 + (voiture.y-y)**2)
                
                if distance < 20:
                    explosion = True

            #Déclenchement explosion

            if explosion:
                print("Boum !")

                for voiture in [self.car,self.car2]:
                    distance = math.sqrt((voiture.x-x)**2 + (voiture.y-y)**2)

                    if distance < 120:
                        if voiture in self.temps_etoiles:
                            print(f"{voiture.stats.name} est protégée par son étoile !")
                        else:
                            print(f"{voiture.stats.name} est touchée par l'explosion !")

                self.bombes.remove((x,y))
                del self.temps_bombes[(x,y)]

    def verifier_etoiles(self):
        """Désactive l'invicibilité des voitures après 10 secondes."""

        for voiture in list(self.temps_etoiles):
            if time.monotonic() >= self.temps_etoiles[voiture]:
                del self.temps_etoiles[voiture]
                print("L'invincibilité de la voiture est terminée")
                 
