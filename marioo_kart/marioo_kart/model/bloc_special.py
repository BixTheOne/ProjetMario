from abc import ABC, abstractmethod
import math
import time

class BlocSpecial(ABC):
    """Classe abstraite représentant un bloc spécial dans le circuit. (effectué avant l'information que les classes 
    abstraites/héréditaires ne sont plus évaluées). Cette classe est laissée mais n'est pas utilisée dans le jeu.
    Il a été décidé de seulement s'occuper des blocs cadeaux et de ne pas faire les blocs à effets spéciaux."""

    def __init__(self, col: int, row: int):
        """Initialise la position du bloc dans la grille.
        Args:
            col (int): La colonne du bloc dans la grille.
            row (int): La ligne du bloc dans la grille.
        """
        self.col = col
        self.row = row

    @abstractmethod
    def appliquer_effet(self, voiture):
        """Définie l'effet du bloc sur le véhicule."""
        pass


class BlocObjet(BlocSpecial):
    """Classe représentant un bloc permettant de récupérer un objet."""

    def __init__(self, col: int, row: int):
        """ Initialise la position du bloc dans la grille.
        Args:
            col (int): La colonne du bloc dans la grille.
            row (int): La ligne du bloc dans la grille.
        """
        super().__init__(col, row)

    def appliquer_effet(self, voiture):
        """Applique l'effet du bloc sur le véhicule.
        Args:
            voiture (Car): La voiture qui passe sur le bloc.
        """
        pass

class BlocEffet(BlocSpecial):
    """Classe représentant un bloc qui applique un effet sur le véhicule."""

    def __init__(self, col: int, row: int):
        """Initialise la position du bloc dans la grille.
        Args:
            col (int): La colonne du bloc dans la grille.
            row (int): La ligne du bloc dans la grille.
        """
        super().__init__(col, row)

    def appliquer_effet(self, voiture):
        """Applique l'effet du bloc sur le véhicule.
        Args:
            voiture (Car): La voiture qui passe sur le bloc.
        """
        pass



class Objet:
    """Classe mère représentant un objet utilisable par la voiture"""

    def __init__(self,nom: str):
        """initialise un objet

        Args : 
            nom (str): nom de l'objet.
            """

        self.nom = nom

    def utiliser(self, voiture):
        """Définit l'utilisation de l'objet par une voiture.
        
        Args :
            voiture(Car) : voiture qui utilise l'objet"""

        pass

class Champignon(Objet):
    """Classe représentant un champignon donnant un bonus de vitesse."""

    def __init__(self):
        super().__init__("Champignon")

    def utiliser(self, voiture):
        """Permettra d'augmenter temporairement la vitesse de la voiture.
        
        Args:
            voiture (Car): voiture qui utilise le champignon
        """
        voiture.speed = min(voiture.speed + 2,voiture.stats.max_speed)
        voiture.vx = voiture.speed * math.cos(voiture.heading)
        voiture.vy = voiture.speed * math.sin(voiture.heading)

class Banane(Objet):
    """Classe représentant une banane qui fait déraper une voiture."""

    def __init__(self):
        super().__init__("Banane")

    def utiliser(self, voiture,model):
        """Permettra de déposer une banane sur le circuit.
                
        Args:
            voiture (Car): voiture qui utilise la banane
            model (GameModel): Modèle du jeu contenant les bananes déposées
        """
        distance = 40
        x = voiture.x - distance*math.cos(voiture.heading)
        y = voiture.y - distance*math.sin(voiture.heading)

        model.bananes.append((x,y))
        print("Banane déposée :", x, y)
        

class Bombe(Objet):
    """Classe représentant une bombe qui explose sur le circuit."""

    def __init__(self):
        super().__init__("Bombe")

    def utiliser(self, voiture,model):
        """Permettra de déposer une bombe sur le circuit.
                        
        Args:
            voiture (Car): voiture qui utilise la bombe
            model (GameModel): Modèle du jeu contenant les bombes déposées
        """        
        distance = 40
        x = voiture.x - distance*math.cos(voiture.heading)
        y = voiture.y - distance*math.sin(voiture.heading)
        
        model.bombes.append((x,y))
        model.temps_bombes[(x,y)]=time.monotonic()
        print("Bombe déposée :", x, y)

class Etoile(Objet):
    """Classe représentant une étoile qui rend la voiture invincible."""

    def __init__(self):
        super().__init__("Etoile")

    def utiliser(self, voiture,model):
        """Permettra de rentre temporairement la voiture invincible.
        
        Args:
            voiture (Car): voiture qui utilise l'étoile.
            model (GameModel) : Modèle contenant les durées d'invincibilté
        """
        model.temps_etoiles[voiture]= time.monotonic() +10

        print("Etoile activée pendant 10 secondes")

class CarapaceBleue(Objet):
    """Classe représentant une carapace bleue qui dépose une bombe directement sur l'adversaire."""

    def __init__(self):
        super().__init__("Carapace Bleue")

    def utiliser(self, voiture,model):
        """Attaque directement la voiture adverse en tenant compte de son invincibilité
        
        Args:
            Voiture (Car): voiture qui utilise la carapace bleue.
            model (GameModel) : Modèle contenant les voitures et les étoiles actives
        """
        if voiture == model.car:
            adversaire = model.car2
        else:
            adversaire = model.car

        if adversaire in model.temps_etoiles:
            print(f"{adversaire.stats.name} est protégée par son étoile !")
        else:
            print(f"{adversaire.stats.name} est touchée par la carapace bleue !")