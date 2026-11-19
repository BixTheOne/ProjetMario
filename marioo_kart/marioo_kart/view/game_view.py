import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL, COLOR_PANEL_BORDER,
    GameState, DEBUG_HITBOXES
)
from model.game_model import GameModel
from model.car import Car, CARS
from model.circuit_data import CIRCUITS
from model.terrain import Road, Herbe, Terre, Glace, Vide

class GameView:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_titre = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_petite = pygame.font.SysFont("Arial", 18)

        # Aperçu agrandi de chaque voiture, calculé une seule fois
        self.apercus = {}
        for stats in CARS:
            sprite = Car(stats, 0, 0).sprite
            taille = (sprite.get_width() * 3, sprite.get_height() * 3)
            self.apercus[stats.name] = pygame.transform.scale(sprite, taille)

        # Couleur de chaque lettre du plan, pour la mini-carte des circuits
        terrains = {"R": Road, "H": Herbe, "T": Terre, "G": Glace, "V": Vide}
        self.couleurs_plan = {lettre: classe().color for lettre, classe in terrains.items()}


    def draw(self, model: GameModel) -> None:
        self.screen.fill(COLOR_BG)
        if model.state == GameState.MENU:
            self._draw_menu(model)
        elif model.state == GameState.CAR_SELECT:
            self.draw_car_select(model)
        elif model.state == GameState.TRACK_SELECT:
            self.draw_track_select(model)
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

        texte_arrivee = self.font.render("L",True,(255, 255, 255))

        for col, row in model.circuit.arrivee:
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2
            rect = texte_arrivee.get_rect(center=(x, y))
            self.screen.blit(texte_arrivee, rect)

        #affichage des positions de départ

        for joueur, (col, row) in model.circuit.departs.items():
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2

            texte = self.font.render(str(joueur),True,(255, 255, 255))
            rect = texte.get_rect(center=(x, y))
            self.screen.blit(texte, rect)

        #première voiture
        surf, rect = model.car.get_rotated_sprite()
        self.screen.blit(surf, rect)

        #deuxième voiture
        surf2, rect2 = model.car2.get_rotated_sprite()
        self.screen.blit(surf2, rect2)

        #affichage debug des zones d'aspiration
        if DEBUG_HITBOXES:
            for voiture in [model.car, model.car2]:
                zone = voiture.zone_aspiration
                occupee = any(
                    autre is not voiture and zone.touche(voiture, autre.hitbox, autre)
                    for autre in [model.car, model.car2]
                )
                couleur = (0, 255, 0) if occupee else (0, 120, 255)
                pygame.draw.polygon(self.screen, couleur, zone.coins(voiture), 1)

        #affichage nb de tours

        tours_j1 = model.coordinateur.tours[model.car]
        tours_j2 = model.coordinateur.tours[model.car2]

        nb_tours= model.coordinateur.nb_tours

        texte_j1 = self.font.render(f"Joueur 1 : {tours_j1}/{nb_tours} tours", True, (255, 255, 255))
        texte_j2 = self.font.render(f"Joueur 2 : {tours_j2}/{nb_tours} tours", True, (255, 255, 255))

        self.screen.blit(texte_j1, (10, 10))
        self.screen.blit(texte_j2, (10, 40))

        #affichage sens circulation

        for row in [10,11]:
            texte_sens = self.font.render("->->->", True, (255, 255, 255))
            x = 6 * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2
            rect = texte_sens.get_rect(center=(x, y))
            self.screen.blit(texte_sens, rect)


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


    def _texte_centre(self, texte: str, police, couleur, x: int, y: int) -> None:
        """Affiche un texte centré sur la position (x, y)."""
        surface = police.render(texte, True, couleur)
        self.screen.blit(surface, surface.get_rect(center=(x, y)))

    def draw_car_select(self, model: GameModel) -> None:
        """Affiche l'écran de choix des voitures, une colonne par joueur."""
        cx = WINDOW_WIDTH // 2
        self._texte_centre("Choix des voitures", self.font_titre, COLOR_ACCENT, cx, 60)

        colonnes = {1: WINDOW_WIDTH // 4, 2: 3 * WINDOW_WIDTH // 4}
        touches = {1: "<- ->  puis Entrée", 2: "Q / D  puis Espace"}

        for joueur, x in colonnes.items():
            stats = CARS[model.choix_voiture[joueur]]
            pret = model.joueur_pret[joueur]

            # Panneau du joueur (bordure en couleur d'accent quand il est prêt)
            panneau = pygame.Rect(0, 0, 300, 360)
            panneau.center = (x, WINDOW_HEIGHT // 2 + 20)
            pygame.draw.rect(self.screen, COLOR_PANEL, panneau, border_radius=8)
            pygame.draw.rect(self.screen, COLOR_ACCENT if pret else COLOR_PANEL_BORDER,
                             panneau, 2, border_radius=8)

            y = panneau.top
            self._texte_centre(f"Joueur {joueur}", self.font, COLOR_TEXT, x, y + 30)

            # Aperçu de la voiture
            apercu = self.apercus[stats.name]
            self.screen.blit(apercu, apercu.get_rect(center=(x, y + 100)))

            # Nom et caractéristiques
            self._texte_centre(f"<  {stats.name}  >", self.font, COLOR_ACCENT, x, y + 170)
            self._texte_centre(f"Vitesse max : {stats.max_speed}", self.font_petite, COLOR_TEXT, x, y + 210)
            self._texte_centre(f"Accélération : {stats.acceleration}", self.font_petite, COLOR_TEXT, x, y + 238)
            self._texte_centre(f"Virage : {stats.turn_speed}", self.font_petite, COLOR_TEXT, x, y + 266)

            # Statut
            if pret:
                self._texte_centre("PRÊT !", self.font, (80, 220, 80), x, y + 320)
            else:
                self._texte_centre(touches[joueur], self.font_petite, COLOR_TEXT, x, y + 320)

        self._texte_centre("Échap : retour au menu", self.font_petite, COLOR_PANEL_BORDER,
                           cx, WINDOW_HEIGHT - 25)

    def draw_track_select(self, model: GameModel) -> None:
        """Affiche l'écran de choix du circuit avec une mini-carte du plan."""
        cx = WINDOW_WIDTH // 2
        infos = CIRCUITS[model.choix_circuit]
        self._texte_centre("Choix du circuit", self.font_titre, COLOR_ACCENT, cx, 60)

        # Mini-carte : une petite case colorée par lettre du plan
        taille = 16
        plan = infos["plan"]
        largeur = len(plan[0]) * taille
        hauteur = len(plan) * taille
        x0 = cx - largeur // 2
        y0 = 120

        for row, ligne in enumerate(plan):
            for col, lettre in enumerate(ligne):
                case = (x0 + col * taille, y0 + row * taille, taille, taille)
                pygame.draw.rect(self.screen, self.couleurs_plan[lettre], case)
        pygame.draw.rect(self.screen, COLOR_ACCENT, (x0 - 2, y0 - 2, largeur + 4, hauteur + 4), 2)

        # Nom et position dans la liste
        self._texte_centre(f"<  {infos['nom']}  >", self.font, COLOR_TEXT, cx, y0 + hauteur + 40)
        self._texte_centre(f"{model.choix_circuit + 1} / {len(CIRCUITS)}", self.font_petite,
                           COLOR_PANEL_BORDER, cx, y0 + hauteur + 72)

        self._texte_centre("<- ->  pour choisir,  Entrée pour lancer la course", self.font_petite,
                           COLOR_TEXT, cx, WINDOW_HEIGHT - 55)
        self._texte_centre("Échap : retour au choix des voitures", self.font_petite,
                           COLOR_PANEL_BORDER, cx, WINDOW_HEIGHT - 25)