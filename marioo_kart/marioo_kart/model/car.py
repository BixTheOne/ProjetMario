import pygame
import math
from constants import (
    CAR_ACCELERATION, CAR_WIDTH, CAR_HEIGHT, TILE_SIZE
)
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class CarStats:
    name: str
    color: tuple[int, int, int]
    acceleration: float
    max_speed: float
    brake_power: float
    turn_speed: float

    

class Car:
    

    def __init__(self, stats: CarStats, start_col: int, start_row: int):

        self.stats = stats

        #données de position et de mouvement qui évolue
        self.speed = 0.0
        self.angle = 0.0
        #les trois vecteurs sur la voiture comme sur le schéma
        self.heading: float = 0.0   # orientation de la caisse (rad)
        self.steering: float = 0.0  # angle des roues avant / caisse (rad)
        self.vx: float = 0.0        # vitesse réelle, vecteur en fonction de la vitesse et de l'angle (px/s)
        self.vy: float = 0.0
        self.x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = start_row * TILE_SIZE + TILE_SIZE // 2
        
        self.sprite = self.build_sprite()

    def accelerate(self) -> None:
        self.speed = min(self.speed + self.stats.acceleration, self.stats.max_speed)

    def brake(self) -> None:
        self.speed = max(self.speed - self.stats.brake_power, -self.stats.max_speed / 4)

    def turn_left(self) -> None:
        self.angle -= self.stats.turn_speed

    def turn_right(self) -> None:
        self.angle += self.stats.turn_speed

    def update_position(self) -> None:
        """
        Mets a jour la position de la voiture en fonction de sa vitesse et de son angle.
        """
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))

    def build_sprite(self) -> pygame.Surface:
        surf = pygame.Surface((CAR_HEIGHT, CAR_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 0), (0, 0, CAR_HEIGHT,
                         CAR_WIDTH), border_radius=5)
        return surf

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        rotated = pygame.transform.rotate(self.sprite, -self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        return rotated, rect




#exemples de voitures avec leurs stats
SPORTS = CarStats("Sports", (220, 30, 30), acceleration=0.3, max_speed=12.0, brake_power=0.5, turn_speed=4.0)
TRUCK  = CarStats("Truck",  (40, 90, 200), acceleration=0.1, max_speed=6.0,  brake_power=0.3, turn_speed=2.0)
SPORTS_BLUE = CarStats("Sports Blue", (30, 30, 220), acceleration=0.3, max_speed=12.0, brake_power=0.5, turn_speed=4.0)