from constants import TILE_SIZE

class RaceCoordinator:

    """Classe qui coordonne la progression des voitures sur le circuit.
    Attributes:
        circuit (Circuit): Le circuit sur lequel la course se déroule.
        progression (dict): Dictionnaire qui stocke le dernier checkpoint atteint par chaque voiture.
        depart (dict): Dictionnaire qui stocke les positions de départ par chaque voiture.
    """

    def __init__(self, circuit):

        """Initialise le coordinateur de course avec un circuit donné.
        Args:
            circuit (Circuit): Le circuit sur lequel la course se déroule.
        """
        
        self.circuit = circuit
        self.progression = {}
        self.depart = {}  # Dictionnaire pour stocker les positions de départ des voitures

    def ajouter_voiture(self,voiture, col, row)-> None:

        """Ajoute une voiture au départ de la course.
        Args:
            voiture (Car): La voiture à ajouter.
            col (int): La colonne de la position de départ.
            row (int): La ligne de la position de départ.
        """

        self.progression[voiture] = -1  # -1 signifie que la voiture n'a pas encore franchi de checkpoint
        self.depart[voiture] = (col, row)

    def verifier_checkpoint(self, voiture,col, row)-> None:

        """Vérifie si la voiture a franchi un checkpoint et met à jour sa progression.
        Args:
            voiture (Car): La voiture à vérifier.
            col (int): La colonne de la case à vérifier.
            row (int): La ligne de la case à vérifier.
        """

        prochain = self.progression[voiture] + 1

        if prochain < len(self.circuit.checkpoints):
            checkpoint = self.circuit.checkpoints[prochain]

            if (col, row) in checkpoint["cases"]:
                self.progression[voiture] = prochain
                print(f"Voiture {voiture} a franchi le checkpoint {prochain}.")


    def faire_reapparaitre(self, voiture)-> None:

        """Fait réapparaître la voiture au dernier checkpoint atteint. Si la voiture n'a pas encore franchi de checkpoint, 
        elle réapparaît au départ.
        Args:
            voiture (Car): La voiture à faire réapparaître.
        """

        dernier_checkpoint = self.progression[voiture]

        if dernier_checkpoint == -1:
            # La voiture n'a pas encore franchi de checkpoint, réapparition au départ
            col, row = self.depart[voiture]
            print("Aucun checkpoint validé : retour au départ")
        else:
            # La voiture a franchi un checkpoint, réapparition au dernier checkpoint atteint
            col, row = self.circuit.checkpoints[dernier_checkpoint]["reapparition"]
            print(f"Dernier checkpoint validé : {dernier_checkpoint + 1}")

        voiture.x = col * TILE_SIZE + TILE_SIZE // 2
        voiture.y = row * TILE_SIZE + TILE_SIZE // 2
        voiture.speed = 0.0
        voiture.vx = 0.0
        voiture.vy = 0.0

        print(f"Réapparition sur la case : ({col}, {row})")
        print(f"Position en pixels : ({voiture.x}, {voiture.y})")