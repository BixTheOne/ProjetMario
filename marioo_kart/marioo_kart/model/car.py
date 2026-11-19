import pygame
import math
from constants import (
    CAR_ACCELERATION, CAR_WIDTH, CAR_HEIGHT, TILE_SIZE,
    ASPIRATION_LONGUEUR, ASPIRATION_LARGEUR
)
from model.hitbox import Hitbox
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class CarStats:
    name: str
    color: tuple[int, int, int]
    acceleration: float
    max_speed: float
    brake_power: float
    turn_speed: float

DRIFT_SEUIL_ENTREE = 1.0     # plus c'est haut, plus il est dur de déraper
DRIFT_SEUIL_SORTIE = 0.5     # doit rester plus petit que le seuil d'entrée
DRIFT_FACTEUR_GRIP = 0.2     # part du grip conservée pendant un dérapage
FROTTEMENT = 0.1             # intensité du ralentissement quand on n'accélère pas

class Car:
    

    def __init__(self, stats: CarStats, start_col: int, start_row: int):

        self.stats = stats

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
        v_long = max(-self.stats.max_speed / 4, min(v_long, self.stats.max_speed))

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
        longueur = CAR_HEIGHT   # axe avant/arrière (horizontal sur le sprite)
        largeur = CAR_WIDTH     # axe gauche/droite (vertical sur le sprite)
        surf = pygame.Surface((longueur, largeur), pygame.SRCALPHA)

        # Carrosserie
        pygame.draw.rect(surf, self.stats.color, (0, 0, longueur, largeur), border_radius=5)

        # Pare-brise sombre, placé vers l'avant de la voiture
        pare_brise = pygame.Rect(
            int(longueur * 0.55),   # un peu après le milieu
            int(largeur * 0.15),    # léger retrait par rapport au bord
            int(longueur * 0.15),   # épaisseur du pare-brise
            int(largeur * 0.7),     # largeur du pare-brise
        )
        pygame.draw.rect(surf, (30, 30, 40), pare_brise, border_radius=2)

        # Deux phares jaunes sur le bord avant 
        rayon = max(2, largeur // 7)
        x_phares = longueur - rayon - 1
        pygame.draw.circle(surf, (255, 230, 120), (x_phares, rayon + 2), rayon)             # phare gauche
        pygame.draw.circle(surf, (255, 230, 120), (x_phares, largeur - rayon - 2), rayon)   # phare droit
        return surf

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        #heading est en radian, pygame.transform.rotate prend un angle en degré donc conversion
        angle_degrees = math.degrees(self.heading)
        rotated = pygame.transform.rotate(self.sprite, -angle_degrees)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        return rotated, rect

    


#exemples de voitures avec leurs stats
SPORTS = CarStats("Sports", (220, 30, 30), acceleration=0.10, max_speed=5.0, brake_power=0.5, turn_speed=4.0)
TRUCK  = CarStats("Truck",  (40, 90, 200), acceleration=0.1, max_speed=3.0,  brake_power=0.3, turn_speed=2.0)
SPORTS_BLUE = CarStats("Sports Blue", (30, 30, 220), acceleration=0.3, max_speed=12.0, brake_power=0.5, turn_speed=4.0)
CARS = [SPORTS, TRUCK, SPORTS_BLUE]