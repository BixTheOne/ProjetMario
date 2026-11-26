import pygame
from constants import TILE_SIZE
from model.terrain import Road


class RoadTile:
    """Classe représentant une case du cricuit associée à un type de terrain.
    Attributes:
        col (int): Indice de la colonne de la case
        row (int): Indice de la ligne de la case
        terrain (Terrain): Type de terrain associé à la case
        sprite (pygame.Surface | None): Représentation graphique de la case        
        """
    def __init__(self, col: int, row: int, terrain = None):
        """Initialise une case de circuit.
       Args:
            col (int): Indice de la colonne de la case
            row (int): Indice de la ligne de la case
            terrain (Terrain): Type de terrain de la case

        Par défaut la case est de type Road
        """
        self.col = col
        self.row = row 
        if terrain is None:
            self.terrain = Road()
        else:
            self.terrain = terrain
        self.sprite: pygame.Surface | None = None

    def get_sprite(self, tile_size: int = TILE_SIZE) -> pygame.Surface:
        """Crée ou récupère la représentation graphique de la case.        
        La couleur de la case dépend du type de terrain associé.
        Le sprite existant est réutilisé si taille adaptée.
        
        Args:
            tile_size (int): Taille de la case en pixels
            
        Returns:
            pygame.Surface: Surface graphique représentant la case
        """
        if self.sprite and self.sprite.get_width() == tile_size:
            return self.sprite
        surface = pygame.Surface((tile_size, tile_size))
        surface.fill(self.terrain.color)
        pygame.draw.rect(surface, (60, 60, 70), surface.get_rect(), 2)

        self.sprite = surface
        return self.sprite
