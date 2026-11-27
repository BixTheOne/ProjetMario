import pygame
import sys
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    GameState
)
from model.game_model import GameModel
from view.game_view import GameView
from controller.input_handler import InputHandler
from model.bloc_special import Banane,Bombe,Etoile,CarapaceBleue


class GameController:

    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.model = GameModel()
        self.view = GameView(self.screen)
        self.input_handler = InputHandler()
        self.running = True

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

    def handle_keydown(self, key: int) -> None:

        state = self.model.state

        if state == GameState.MENU:
            self.handle_menu_key(key)
        elif state == GameState.CAR_SELECT:
            self.handle_car_select_key(key)
        elif state == GameState.TRACK_SELECT:
            self.handle_track_select_key(key)
        elif state == GameState.RULES:
            if key == pygame.K_ESCAPE:
                self.model.state = GameState.MENU
        elif state == GameState.RACING:
            if key == pygame.K_RETURN:
                voiture = self.model.car
            elif key == pygame.K_SPACE:
                voiture = self.model.car2
            else:
                return

            objet = self.model.objets_voitures[voiture]

            if objet is not None:
                if isinstance(objet,(Banane,Bombe,Etoile,CarapaceBleue)):
                    objet.utiliser(voiture,self.model)
                else:
                    objet.utiliser(voiture)#cas cadeau Champignon

                print(f"Utilisation du cadeau : {objet.nom}")
                self.model.objets_voitures[voiture] = None
            else:
                print("Cette voiture ne possède pas de cadeau")

    def handle_menu_key(self, key: int) -> None:
        nb_options = len(self.model.menu_options)

        if key == pygame.K_UP:
            self.model.menu_selection = (self.model.menu_selection - 1) % nb_options
        elif key == pygame.K_DOWN:
            self.model.menu_selection = (self.model.menu_selection + 1) % nb_options
        elif key == pygame.K_RETURN:
            choix = self.model.menu_options[self.model.menu_selection]
            if choix == "JOUER":
                self.model.reset_selection()
                self.model.state = GameState.CAR_SELECT
            elif choix == "RÈGLES":
                self.model.state = GameState.RULES
            elif choix == "QUITTER":
                self.quit()
        elif key == pygame.K_ESCAPE:
            self.quit()

    def update(self) -> None:
        if self.model.state != GameState.RACING:
            return
        self.apply_input(self.model.car, self.input_handler.get_inputs(1))
        self.apply_input(self.model.car2, self.input_handler.get_inputs(2))
        self.model.update()

    def apply_input(self, car, player_input) -> None:
        if player_input['accelerate']:
            car.accelerate()
        if player_input['brake']:
            car.brake()
        if player_input['turn_left']:
            car.turn_left()
        if player_input['turn_right']:
            car.turn_right()

    def render(self) -> None:
        self.view.draw(self.model)

    def quit(self) -> None:
        self.running = False
        pygame.quit()
        sys.exit()

    def handle_car_select_key(self, key: int) -> None:
        m = self.model
        # Joueur 1 : flèches gauche/droite pour choisir, Entrée pour valider
        if key == pygame.K_LEFT:
            m.changer_voiture(1, -1)
        elif key == pygame.K_RIGHT:
            m.changer_voiture(1, 1)
        elif key == pygame.K_RETURN:
            m.valider_voiture(1)
        # Joueur 2 : Q/D pour choisir, Espace pour valider
        elif key == pygame.K_q:
            m.changer_voiture(2, -1)
        elif key == pygame.K_d:
            m.changer_voiture(2, 1)
        elif key == pygame.K_SPACE:
            m.valider_voiture(2)
        # Retour au menu
        elif key == pygame.K_ESCAPE:
            m.state = GameState.MENU
            return

        if m.tous_prets():
            m.state = GameState.TRACK_SELECT


    def handle_track_select_key(self, key: int) -> None:
        m = self.model
        if key in (pygame.K_LEFT, pygame.K_q):
            m.changer_circuit(-1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            m.changer_circuit(1)
        elif key == pygame.K_RETURN:
            m.load_circuit()
            m.state = GameState.RACING
        elif key == pygame.K_ESCAPE:
            m.reset_selection()
            m.state = GameState.CAR_SELECT