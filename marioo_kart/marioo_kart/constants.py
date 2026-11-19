WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

TILE_SIZE = 64
GRID_COLS = 16
GRID_ROWS = 12

CAR_ACCELERATION = 0.05
CAR_WIDTH = 30
CAR_HEIGHT = 50

# --- Hitboxes ---
COLLISION_REBOND = 0.5          # 0 = choc mou, 1 = rebond total
ASPIRATION_LONGUEUR = 60        # longueur de la zone derrière la voiture (px)
ASPIRATION_LARGEUR = CAR_WIDTH  # même largeur que la voiture
DEBUG_HITBOXES = True           # affiche les zones d'aspiration


class GameState:
    MENU = "menu"
    RACING = "racing"
    CAR_SELECT = "car_selection"
    TRACK_SELECT = "track_selection"


# --- Couleurs UI ---
COLOR_BG = (15, 15, 25)
COLOR_TEXT = (240, 240, 240)
COLOR_ACCENT = (255, 200, 0)
COLOR_PANEL = (30, 30, 50)
COLOR_PANEL_BORDER = (60, 60, 100)
