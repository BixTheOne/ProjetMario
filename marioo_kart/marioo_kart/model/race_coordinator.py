from constants import TILE_SIZE

class RaceCoordinator:

    """Classe qui coordonne la progression des voitures sur le circuit.
    Attributes:
        circuit (Circuit): Le circuit sur lequel la course se déroule.
        progression (dict): Dictionnaire qui stocke le dernier checkpoint atteint par chaque voiture.
        depart (dict): Dictionnaire qui stocke les positions de départ par chaque voiture.
        tours (dict): Dictionnaire qui stocke le nombre de tours complétés par chaque voiture.
        nb_tours (int): Le nombre de tours requis pour terminer la course.
        vainqueur (Car | None): La voiture qui a terminé la course en premier.
    """

    def __init__(self, circuit):

        """Initialise le coordinateur de course avec un circuit donné.
        Args:
            circuit (Circuit): Le circuit sur lequel la course se déroule.
        """
        
        self.circuit = circuit
        self.progression = {}
        self.depart = {}  
        self.tours={}
        self.nb_tours=3
        self.vainqueur=None


    def ajouter_voiture(self,voiture, col, row)-> None:

        """Ajoute une voiture au départ de la course.
        Args:
            voiture (Car): La voiture à ajouter.
            col (int): La colonne de la position de départ.
            row (int): La ligne de la position de départ.
        """

        self.progression[voiture] = -1  # -1 => voiture n'a pas encore franchi de checkpoint
        self.depart[voiture] = (col, row)
        self.tours[voiture]=0

    def verifier_checkpoint(self, voiture,col, row)-> bool:

        """Vérifie si la voiture a franchi un checkpoint et met à jour sa progression.
        Args:
            voiture (Car): La voiture à vérifier.
            col (int): La colonne de la case à vérifier.
            row (int): La ligne de la case à vérifier.
        Returns:
            bool: True si la voiture a franchi un checkpoint, False sinon.
        """

        prochain = self.progression[voiture] + 1

        if prochain < len(self.circuit.checkpoints):
            checkpoint = self.circuit.checkpoints[prochain]

            if (col, row) in checkpoint["cases"]:
                self.progression[voiture] = prochain
                print(f"Voiture {voiture} a franchi le checkpoint {prochain}.")
                return True
        return False


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
        voiture.accelerated = 0.0
        voiture.steering = 0.0
        voiture.drifting = False

        print(f"Réapparition sur la case : ({col}, {row})")
        print(f"Position en pixels : ({voiture.x}, {voiture.y})")


    def verifier_arrivee(self,voiture,col,row)-> bool:

        """Vérifie si une voiture a terminé un tour.
        Un tour est validé si la voiture a franchi la ligne d'arrivée après avoir franchi tous les checkpoints dans l'ordre.
        Args:
            voiture (Car): La voiture à vérifier.
            col (int): La colonne de la case à vérifier.
            row (int): La ligne de la case à vérifier.
        Returns:
            bool: True si un tour est validé, False sinon.
        """

        if self.tours[voiture] >= self.nb_tours:
            return False #  # La voiture a déjà terminé la course

        if(col,row) not in self.circuit.arrivee:
            return False  #voiture n'est pas sur la ligne d'arrivée

        dernier = len(self.circuit.checkpoints) - 1

        if self.progression[voiture] != dernier:
            return False  #voiture n'a pas franchi tous les checkpoints

        #alors validation tour

        self.tours[voiture]+=1
        self.progression[voiture]=-1 #réinitialisation progression pour prochain tour

        print(f"Tour validé pour la voiture {voiture}. Tours complétés : {self.tours[voiture]}")

        #vérfication victoire 
        if self.tours[voiture]>=self.nb_tours:
            if self.vainqueur is None:
                self.vainqueur=voiture
                print(f"La voiture {voiture} a gagné la course !")
            else:
                print(f"La voiture {voiture} a terminé ses 3 tours !")

        return True


        