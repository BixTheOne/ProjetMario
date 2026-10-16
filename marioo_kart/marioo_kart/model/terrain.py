class Terrain:
    def __init__(self, name: str, traction: float, grip : float,  friction: float, color : tuple[int, int, int]):
        self.name = name
        self.traction = traction
        self.grip = grip
        self.friction = friction
        self.color = color

class Road(Terrain):
    """Revêtement de type route, avec une traction et un grip élevés."""
    def __init__(self):
        super().__init__("Road", traction=0.9, grip=0.8, friction=0.7, color=(80, 80, 90))

class Herbe(Terrain):
    """Revêtement de type herbe, avec une traction et un grip plus faible que la route."""
    def __init__(self):
        super().__init__("Grass", traction=0.6, grip=0.4, friction=0.5, color=(50, 160, 50))

class Terre(Terrain):
    """Revêtement de type terre, avec une traction et un grip plus faible que l'herbe."""
    def __init__(self):
        super().__init__("Terre", traction=0.5, grip=0.25, friction=0.3, color=(150, 100, 50))

class Glace(Terrain):
    """Revêtement de type glace, avec une traction et un grip très faible."""
    def __init__(self):
        super().__init__("Glace", traction=0.2, grip=0.05, friction=0.02, color=(150, 220, 255))

class Vide(Terrain):
    """Revêtement de type vide, avec une traction et un grip nuls."""
    def __init__(self):
        super().__init__("Vide", traction=0.0, grip=0.0, friction=0.0, color=(15,15, 25))

if __name__ == "__main__":
    road = Road()
    print(f"Terrain: {road.name}, Traction: {road.traction}, Grip: {road.grip}, Friction: {road.friction}, Color: {road.color}")
    herbe = Herbe()
    print(f"Terrain: {herbe.name}, Traction: {herbe.traction}, Grip: {herbe.grip}, Friction: {herbe.friction}, Color: {herbe.color}")
    terre = Terre()
    print(f"Terrain: {terre.name}, Traction: {terre.traction}, Grip: {terre.grip}, Friction: {terre.friction}, Color: {terre.color}")
    glace = Glace()
    print(f"Terrain: {glace.name}, Traction: {glace.traction}, Grip: {glace.grip}, Friction: {glace.friction}, Color: {glace.color}")
    vide = Vide()
    print(f"Terrain: {vide.name}, Traction: {vide.traction}, Grip: {vide.grip}, Friction: {vide.friction}, Color: {vide.color}")