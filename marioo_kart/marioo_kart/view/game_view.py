import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL, COLOR_PANEL_BORDER,
    GameState
)
from model.game_model import GameModel


class GameView:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, model: GameModel) -> None:
        self.screen.fill(COLOR_BG)
        if model.state == GameState.MENU:
            self._draw_menu(model)
        elif model.state == GameState.RACING:
            self._draw_racing(model)
        pygame.display.flip()

    def _draw_menu(self, model: GameModel) -> None:
        cx = WINDOW_WIDTH // 2

        title_surf = self.font.render(
            "Jeu de course 2D", True, COLOR_ACCENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(cx, 160)))

        for i, label in enumerate(model.menu_options):
            selectionne = (i == model.menu_selection)
            y = 320 + i * 80
            rect = pygame.Rect(cx - 140, y - 25, 280, 50)
            pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=8)
            pygame.draw.rect(self.screen,
                             COLOR_ACCENT if selectionne else COLOR_PANEL_BORDER,
                             rect, 2, border_radius=8)
            text_surf = self.font.render(
                label, True, COLOR_ACCENT if selectionne else COLOR_TEXT)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def _draw_racing(self, model: GameModel) -> None:

        """Affiche le circuit, les points de passage et les 2 voitures.
        Args:
            model (GameModel): Le modèle du jeu contenant l'état actuel.
        Returns:
            None
        """
        if model.circuit is None:
            return

        #Affichage des cases du circuit
        for row_idx, row in enumerate(model.circuit.grid):
            for col_idx, tile in enumerate(row):
                sprite = tile.get_sprite(TILE_SIZE)
                self.screen.blit(sprite, (col_idx * TILE_SIZE, row_idx * TILE_SIZE))


        #affichage des checkpoints

        texte_checkpoint = self.font.render("C",True,(255, 255, 255))

        for checkpoint in model.circuit.checkpoints:
            for col, row in checkpoint["cases"]:
                x = col * TILE_SIZE + TILE_SIZE // 2
                y = row * TILE_SIZE + TILE_SIZE // 2
                rect = texte_checkpoint.get_rect(center=(x, y))
                self.screen.blit(texte_checkpoint, rect)   

        #affichage des boosts

        texte_boost = self.font.render("B",True,(255, 255, 255))

        for col, row in model.circuit.boosts:
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2
            rect = texte_boost.get_rect(center=(x, y))
            self.screen.blit(texte_boost, rect)

        #affichage de la ligne d'arrivée

        texte_arrivee = self.font.render("F",True,(255, 255, 255))

        for col, row in model.circuit.arrivee:
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2
            rect = texte_arrivee.get_rect(center=(x, y))
            self.screen.blit(texte_arrivee, rect)

        #première voiture
        surf, rect = model.car.get_rotated_sprite()
        self.screen.blit(surf, rect)

        #deuxième voiture
        surf2, rect2 = model.car2.get_rotated_sprite()
        self.screen.blit(surf2, rect2)

        #affichage nb de tours

        tours_j1 = model.coordinateur.tours[model.car]
        tours_j2 = model.coordinateur.tours[model.car2]

        nb_tours= model.coordinateur.nb_tours

        texte_j1 = self.font.render(f"Joueur 1 : {tours_j1}/{nb_tours} tours", True, (255, 255, 255))
        texte_j2 = self.font.render(f"Joueur 2 : {tours_j2}/{nb_tours} tours", True, (255, 255, 255))

        self.screen.blit(texte_j1, (10, 10))
        self.screen.blit(texte_j2, (10, 40))

        #affichage du vainqueur

        vainqueur = model.coordinateur.vainqueur

        if vainqueur is not None:
            if vainqueur == model.car:
                texte_vainqueur = "Joueur 1 a gagné !"

            else:
                texte_vainqueur = "Joueur 2 a gagné !"

            message = self.font.render(texte_vainqueur, True, (255, 255, 255))

            #centrer le message sur la fenêtre
            x = (self.screen.get_width() - message.get_width()) // 2
            y = (self.screen.get_height() - message.get_height()) // 2            

            self.screen.blit(message,(x,y))
            