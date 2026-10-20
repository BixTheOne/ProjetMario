import pygame


MAPPINGS = {
    1: {
        pygame.K_UP:    "accelerate",
        pygame.K_DOWN:  "brake",
        pygame.K_LEFT:  "turn_left",
        pygame.K_RIGHT: "turn_right",
    },
    2: {
        pygame.K_z: "accelerate",
        pygame.K_s: "brake",
        pygame.K_q: "turn_left",
        pygame.K_d: "turn_right",
    },
}


class InputHandler:

    def __init__(self):
        self.mappings = MAPPINGS

    def get_inputs(self, player_id: int) -> dict:
        keys = pygame.key.get_pressed()
        mapping = self.mappings[player_id]
        p = {action: False for action in mapping.values()}

        for key, action in mapping.items():
            if keys[key]:
                p[action] = True

        return p