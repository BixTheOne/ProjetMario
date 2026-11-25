import pygame
import math
from constants import (
    CAR_ACCELERATION, CAR_WIDTH, CAR_HEIGHT, TILE_SIZE,
    ASPIRATION_LONGUEUR, ASPIRATION_LARGEUR
)
from model.hitbox import Hitbox
from dataclasses import dataclass, replace
from constants import ASPIRATION_BONUS


@dataclass(frozen=True)
class CarStats:
    name: str
    color: tuple[int, int, int]
    acceleration: float
    max_speed: float
    brake_power: float
    turn_speed: float
    forme: str = "rectangle"  # forme de la voiture, par défaut rectangle

DRIFT_SEUIL_ENTREE = 1.0     # plus c'est haut, plus il est dur de déraper
DRIFT_SEUIL_SORTIE = 0.5     # doit rester plus petit que le seuil d'entrée
DRIFT_FACTEUR_GRIP = 0.2     # part du grip conservée pendant un dérapage
FROTTEMENT = 0.1             # intensité du ralentissement quand on n'accélère pas

class Car:
    

    def __init__(self, stats: CarStats, start_col: int, start_row: int, couleur: tuple[int, int, int] | None = None):

        self.stats = stats
        # Couleur du joueur si elle est fournie, sinon la couleur du véhicule
        self.couleur = couleur if couleur is not None else stats.color
        #données de position et de mouvement qui évolue
        self.speed = 0.0
        #les trois vecteurs sur la voiture comme sur le schéma
        self.accelerated = 0.0  # accélération de la voiture (px/s²)
        self.heading: float = 0.0   # orientation de la caisse (rad)
        self.drifting: bool = False  # indique si la voiture est en train de déraper
        self.steering: float = 0.0  # angle des roues avant / caisse (rad)
        self.vx: float = 0.0        # vitesse réelle, vecteur en fonction de la vitesse et de l'angle (px/s)
        self.vy: float = 0.0
        self.x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = start_row * TILE_SIZE + TILE_SIZE // 2

        # Hitboxes : collision entre voitures et zone d'aspiration derrière la voiture
        self.hitbox = Hitbox(CAR_HEIGHT, CAR_WIDTH)
        self.zone_aspiration = Hitbox(ASPIRATION_LONGUEUR, ASPIRATION_LARGEUR,
                                      decalage=-(CAR_HEIGHT + ASPIRATION_LONGUEUR) / 2)
        self.en_aspiration: bool = False   # True si la voiture suit une autre de près

        self.sprite = self.build_sprite()

    def accelerate(self) -> None:
        self.accelerated = 1

    def brake(self) -> None:
        self.accelerated = -1

    def turn_left(self) -> None:
        self.steering = -1

    def turn_right(self) -> None:
        self.steering = 1

    def update_position(self, terrain) -> None:
        """
        Mets a jour la position de la voiture en fonction du terrain et de ses actions.
        """
        # Mise à jour de la vitesse en fonction de l'accélération et du freinage
        ratio_vitesse = self.speed / self.stats.max_speed
        self.heading += self.steering * math.radians(self.stats.turn_speed) * ratio_vitesse
        #Les deux directions de la voiture
        avant_x = math.cos(self.heading)
        avant_y = math.sin(self.heading)
        cote_x = -avant_y
        cote_y = avant_x
         #Décomposer la vitesse réelle selon ces deux directions
        v_long = self.vx * avant_x + self.vy * avant_y
        v_lat = self.vx * cote_x + self.vy * cote_y
        if self.accelerated > 0:
            v_long += self.stats.acceleration * terrain.traction
        elif self.accelerated < 0:
            v_long -= self.stats.brake_power * terrain.traction
        else:
            ralentissement = FROTTEMENT * terrain.friction
            if v_long > 0:
                v_long = max(0, v_long - ralentissement)
            elif v_long < 0:
                v_long = min(0, v_long + ralentissement)
        vitesse_max = self.stats.max_speed
        if self.en_aspiration:
            vitesse_max = self.stats.max_speed * ASPIRATION_BONUS
        v_long = max(-self.stats.max_speed / 4, min(v_long, vitesse_max))

        # Gestion du dérapage
        demande = abs(v_lat)
        if not self.drifting and demande > terrain.grip * DRIFT_SEUIL_ENTREE:
            self.drifting = True
        elif self.drifting and demande < terrain.grip * DRIFT_SEUIL_SORTIE:
            self.drifting = False

        #Vitesse latérale : le grip "mange" le glissement
        if self.drifting:
            v_lat *= (1 - terrain.grip * DRIFT_FACTEUR_GRIP)
        else:
            v_lat *= (1 - terrain.grip)

        # Recombiner en vecteur vitesse
        self.vx = v_long * avant_x + v_lat * cote_x
        self.vy = v_long * avant_y + v_lat * cote_y
        self.speed = v_long

        # Déplacer la voiture
        self.x += self.vx
        self.y += self.vy

        # Remettre les intentions à zéro pour l'image suivante
        self.accelerated = 0.0  
        self.steering = 0.0

    def build_sprite(self) -> pygame.Surface:
        """Dessine la voiture vue de dessus, l'avant tourné vers la droite,
        avec un dessin différent selon la voiture que le joueur a choisi."""
        longueur = CAR_HEIGHT   # axe avant/arrière (horizontal sur le sprite)
        largeur = CAR_WIDTH     # axe gauche/droite (vertical sur le sprite)
        surf = pygame.Surface((longueur, largeur), pygame.SRCALPHA)

        match self.stats.forme:
            case "camion":
                self.dessiner_camion(surf, longueur, largeur)
            case "sport":
                self.dessiner_Sport(surf, longueur, largeur)
            case "bike":
                self.dessiner_moto(surf, longueur, largeur)
            case "formule1":
                self.dessiner_formule(surf, longueur, largeur)
            case "police":
                self.dessiner_police(surf, longueur, largeur)
        return surf

    def couleur_foncee(self, ecart: int = 70) -> tuple[int, int, int]:
        """Renvoie une version plus foncée de la couleur de la voiture."""
        r, g, b = self.couleur
        return (max(0, r - ecart), max(0, g - ecart), max(0, b - ecart))
    
    def dessin_phares(self, surf, longueur, largeur) -> None:    
        # Deux phares jaunes sur le bord avant 
        rayon = max(2, largeur // 7)
        x_phares = longueur - rayon - 1
        pygame.draw.circle(surf, (255, 230, 120), (x_phares, rayon + 2), rayon)             # phare gauche
        pygame.draw.circle(surf, (255, 230, 120), (x_phares, largeur - rayon - 2), rayon)   # phare droit

    def dessiner_Sport(self, surf, longueur, largeur) -> None:
        pygame.draw.rect(surf, self.couleur, (0, 0, longueur, largeur), border_radius=5)

        # Bande blanche au centre, sur toute la longueur
        epaisseur = max(1, largeur // 10)
        pygame.draw.rect(surf, (255, 255, 255),
                         (0, largeur // 2 - epaisseur, longueur, 2 * epaisseur))

        # Aileron à l'arrière (bord gauche du sprite)
        pygame.draw.rect(surf, self.couleur_foncee(),
                         (0, 0, max(2, int(longueur * 0.08)), largeur))

        # Pare-brise
        pygame.draw.rect(surf, (30, 30, 40),
                         (int(longueur * 0.55), int(largeur * 0.15),
                          int(longueur * 0.15), int(largeur * 0.7)),
                         border_radius=2)

        self.dessin_phares(surf, longueur, largeur)

    def dessiner_moto(self, surf, longueur, largeur) -> None:
        """Moto vue de dessus : deux roues, réservoir, selle, guidon et pilote casqué."""
        cy = largeur // 2                       # axe central de la moto
        epaisseur_roue = max(3, largeur // 4)
        longueur_roue = int(longueur * 0.22)
        noir = (20, 20, 20)
        gris = (150, 150, 150)

        # Roues arrière (bord gauche) et avant (bord droit)
        pygame.draw.rect(surf, noir, (0, cy - epaisseur_roue // 2,
                                      longueur_roue, epaisseur_roue), border_radius=3)
        pygame.draw.rect(surf, noir, (longueur - longueur_roue, cy - epaisseur_roue // 2,
                                      longueur_roue, epaisseur_roue), border_radius=3)

        # Corps de la moto (réservoir et carénage), à la couleur de la voiture
        epaisseur_corps = max(4, largeur // 3)
        pygame.draw.rect(surf, self.couleur,
                         (int(longueur * 0.18), cy - epaisseur_corps // 2,
                          int(longueur * 0.6), epaisseur_corps), border_radius=4)

        # Selle, à l'arrière du corps
        pygame.draw.rect(surf, (30, 30, 40),
                         (int(longueur * 0.22), cy - epaisseur_corps // 2 + 1,
                          int(longueur * 0.2), epaisseur_corps - 2), border_radius=3)

        # Bras du pilote, des épaules jusqu'aux poignées du guidon
        x_casque = int(longueur * 0.45)
        x_guidon = int(longueur * 0.72)
        rayon_casque = max(3, largeur // 4)
        epaisseur_bras = max(2, largeur // 10)
        couleur_bras = self.couleur_foncee()
        pygame.draw.line(surf, couleur_bras, (x_casque, cy - rayon_casque),
                         (x_guidon, int(largeur * 0.15)), epaisseur_bras)
        pygame.draw.line(surf, couleur_bras, (x_casque, cy + rayon_casque),
                         (x_guidon, int(largeur * 0.85)), epaisseur_bras)

        # Guidon, perpendiculaire à la moto
        pygame.draw.line(surf, gris, (x_guidon, int(largeur * 0.1)),
                         (x_guidon, int(largeur * 0.9)), max(2, largeur // 10))

        # Casque du pilote, avec une visière sombre tournée vers l'avant
        pygame.draw.circle(surf, (240, 240, 240), (x_casque, cy), rayon_casque)
        pygame.draw.circle(surf, (30, 30, 40),
                           (x_casque + rayon_casque // 2, cy), max(1, rayon_casque // 2))

        # Phare unique à l'avant
        pygame.draw.circle(surf, (255, 230, 120),
                           (longueur - longueur_roue - 2, cy), max(2, largeur // 8))

        self.dessin_phares(surf, longueur, largeur)

    def dessiner_camion(self, surf, longueur, largeur) -> None:
        # Dessin d'un camion vu de dessus, l'avant tourné vers la droite
        pygame.draw.rect(surf, self.couleur, (0, 0, longueur, largeur), border_radius=3)

        # Cabine du camion à l'avant
        cabine_longueur = int(longueur * 0.3)
        pygame.draw.rect(surf, (30, 30, 40), (longueur - cabine_longueur, 0, cabine_longueur, largeur),
                         border_radius=2)

        # Remorque du camion à l'arrière
        remorque_longueur = longueur - cabine_longueur
        pygame.draw.rect(surf, self.couleur, (0, 0, remorque_longueur, largeur),
                         border_radius=2)

        self.dessin_phares(surf, longueur, largeur)

    def dessiner_formule(self, surf, longueur, largeur) -> None:
        """Formule 1 vue de dessus"""
        cy = largeur // 2
        noir = (20, 20, 20)
        blanc = (240, 240, 240)
        fonce = self.couleur_foncee()
        epaisseur = max(4, largeur // 3)
        demi = epaisseur // 2

        # Ailerons arrière et avant, sur toute la largeur (dessinés en premier, sous le corps)
        largeur_aileron = max(2, int(longueur * 0.07))
        pygame.draw.rect(surf, fonce, (0, int(largeur * 0.05), largeur_aileron, int(largeur * 0.9)))
        pygame.draw.rect(surf, fonce, (int(longueur * 0.9), int(largeur * 0.05),
                                       largeur_aileron, int(largeur * 0.9)))

        # Quatre roues, aux coins
        longueur_roue = int(longueur * 0.16)
        epaisseur_roue = max(3, largeur // 4)
        for x in (int(longueur * 0.08), int(longueur * 0.68)):
            pygame.draw.rect(surf, noir, (x, 0, longueur_roue, epaisseur_roue), border_radius=2)
            pygame.draw.rect(surf, noir, (x, largeur - epaisseur_roue,
                                          longueur_roue, epaisseur_roue), border_radius=2)

        # Corps fin qui se termine en pointe à l'avant
        corps = [
            (int(longueur * 0.07), cy - demi),
            (int(longueur * 0.7), cy - demi),
            (longueur - 2, cy - 1),
            (longueur - 2, cy + 1),
            (int(longueur * 0.7), cy + demi),
            (int(longueur * 0.07), cy + demi),
        ]
        pygame.draw.polygon(surf, self.couleur, corps)

        # Pontons latéraux, plus larges, entre les roues
        pygame.draw.rect(surf, self.couleur,
                         (int(longueur * 0.3), cy - epaisseur, int(longueur * 0.3), 2 * epaisseur),
                         border_radius=3)

        # Cockpit et casque jaune du pilote
        pygame.draw.ellipse(surf, (30, 30, 40),
                            (int(longueur * 0.4), cy - demi + 1,
                             int(longueur * 0.16), max(2, epaisseur - 2)))
        pygame.draw.circle(surf, (250, 210, 0), (int(longueur * 0.46), cy), max(2, epaisseur // 3))

    
        
    def dessiner_police(self, surf, longueur, largeur, phase: int = 0) -> None:
        """Voiture de police : carrosserie, bandes bleues, vitres et gyrophare.
        phase 0 : rouge allumé, bleu éteint ; phase 1 : l'inverse."""
        cy = largeur // 2
        vitre = (30, 30, 40)
        bleu_bande = (20, 60, 200)

        # Carrosserie
        pygame.draw.rect(surf, (235, 235, 240), (0, 0, longueur, largeur), border_radius=5) # rectangle principal blanc puis bande de la couleur du joueur
        #bande en fonction de la couleur du joueur
        bande = max(1, largeur // 10)
        pygame.draw.rect(surf, self.couleur, (2, 1, longueur - 4, bande))
        pygame.draw.rect(surf, self.couleur, (2, largeur - 1 - bande, longueur - 4, bande))
        # Lunette arrière et pare-brise
        pygame.draw.rect(surf, vitre, (int(longueur * 0.18), int(largeur * 0.2),
                                       int(longueur * 0.1), int(largeur * 0.6)), border_radius=2)
        pygame.draw.rect(surf, vitre, (int(longueur * 0.55), int(largeur * 0.15),
                                       int(longueur * 0.15), int(largeur * 0.7)), border_radius=2)

        # Gyrophare sur le toit 
        x_gyro = int(longueur * 0.38)
        longueur_gyro = max(3, int(longueur * 0.1))
        haut = int(largeur * 0.15)
        bas = int(largeur * 0.85)
        if phase == 0:
            rouge, bleu = (255, 40, 40), (20, 30, 90)    # rouge allumé
        else:
            rouge, bleu = (90, 20, 20), (60, 120, 255)   # bleu allumé
        pygame.draw.rect(surf, rouge, (x_gyro, haut, longueur_gyro, cy - haut))
        pygame.draw.rect(surf, bleu, (x_gyro, cy, longueur_gyro, bas - cy))

        self.dessin_phares(surf, longueur, largeur)

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        #heading est en radian, pygame.transform.rotate prend un angle en degré donc conversion
        angle_degrees = math.degrees(self.heading)
        rotated = pygame.transform.rotate(self.sprite, -angle_degrees)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        return rotated, rect

    


#exemples de voitures avec leurs stats
SPORTS = CarStats("Sports", (220, 30, 30), acceleration=0.10, max_speed=5.0, brake_power=0.5, turn_speed=4.0, forme="sport")
CAMION  = CarStats("Camion",  (40, 90, 200), acceleration=0.1, max_speed=3.0,  brake_power=0.3, turn_speed=2.0, forme="camion")
BIKE = CarStats("Bike", (30, 220, 30), acceleration=0.2, max_speed=6.0, brake_power=0.4, turn_speed=5.0, forme="bike")
FORMULE1 = CarStats("Formule 1", (255, 255, 0), acceleration=0.15, max_speed=7.0, brake_power=0.6, turn_speed=6.0, forme="formule1")
POLICE = CarStats("Police", (0, 0, 0), acceleration=0.12, max_speed=5.5, brake_power=0.5, turn_speed=4.5, forme="police")
CARS = [SPORTS, CAMION, BIKE, FORMULE1, POLICE]