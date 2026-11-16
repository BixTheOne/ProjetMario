import math


class Hitbox:
    """Hitbox rectangulaire orientée, rattachée à une voiture.

    Le rectangle tourne avec la voiture. Son centre est décalé le long
    de l'axe avant/arrière : décalage positif = devant, négatif = derrière.

    Attributes:
        longueur (float): Taille le long de l'axe avant/arrière (px).
        largeur (float): Taille le long de l'axe gauche/droite (px).
        decalage (float): Décalage du centre par rapport au centre de la voiture (px).
    """

    def __init__(self, longueur: float, largeur: float, decalage: float = 0.0):
        """Initialise la hitbox.

        Args:
            longueur (float): Taille avant/arrière (px).
            largeur (float): Taille gauche/droite (px).
            decalage (float): Décalage avant (+) / arrière (-) du centre (px).
        """
        self.longueur = longueur
        self.largeur = largeur
        self.decalage = decalage

    def axes(self, voiture) -> tuple[tuple[float, float], tuple[float, float]]:
        """Renvoie les deux axes unitaires du rectangle (avant, côté).

        Args:
            voiture (Car): La voiture qui porte la hitbox.
        Returns:
            tuple: ((avant_x, avant_y), (cote_x, cote_y)).
        """
        ax, ay = math.cos(voiture.heading), math.sin(voiture.heading)
        return (ax, ay), (-ay, ax)

    def centre(self, voiture) -> tuple[float, float]:
        """Renvoie la position du centre de la hitbox dans le monde.

        Args:
            voiture (Car): La voiture qui porte la hitbox.
        Returns:
            tuple[float, float]: Coordonnées (x, y) du centre en pixels.
        """
        (ax, ay), _ = self.axes(voiture)
        return voiture.x + ax * self.decalage, voiture.y + ay * self.decalage

    def coins(self, voiture) -> list[tuple[float, float]]:
        """Renvoie les 4 coins du rectangle dans le monde.

        Args:
            voiture (Car): La voiture qui porte la hitbox.
        Returns:
            list[tuple[float, float]]: Les 4 coins, dans l'ordre du contour.
        """
        cx, cy = self.centre(voiture)
        (ax, ay), (sx, sy) = self.axes(voiture)
        hl, hw = self.longueur / 2, self.largeur / 2
        return [(cx + ax * l + sx * w, cy + ay * l + sy * w)
                for l, w in ((hl, hw), (hl, -hw), (-hl, -hw), (-hl, hw))]

    def penetration(self, voiture, autre: "Hitbox", autre_voiture):
        """Teste le chevauchement avec une autre hitbox (théorème des axes séparateurs).

        Args:
            voiture (Car): Voiture qui porte cette hitbox.
            autre (Hitbox): Hitbox à tester.
            autre_voiture (Car): Voiture qui porte l'autre hitbox.
        Returns:
            tuple[float, float, float] | None: (profondeur, nx, ny) avec (nx, ny)
            la direction pour pousser l'autre hors de celle-ci, ou None sans contact.
        """
        coins_a = self.coins(voiture)
        coins_b = autre.coins(autre_voiture)
        meilleur = None
        for nx, ny in self.axes(voiture) + autre.axes(autre_voiture):
            proj_a = [x * nx + y * ny for x, y in coins_a]
            proj_b = [x * nx + y * ny for x, y in coins_b]
            chevauchement = min(max(proj_a), max(proj_b)) - max(min(proj_a), min(proj_b))
            if chevauchement <= 0:
                return None          # axe séparateur trouvé : pas de contact
            if meilleur is None or chevauchement < meilleur[0]:
                meilleur = (chevauchement, nx, ny)

        # Orienter la normale de cette hitbox vers l'autre
        profondeur, nx, ny = meilleur
        (cax, cay), (cbx, cby) = self.centre(voiture), autre.centre(autre_voiture)
        if (cbx - cax) * nx + (cby - cay) * ny < 0:
            nx, ny = -nx, -ny
        return profondeur, nx, ny

    def touche(self, voiture, autre: "Hitbox", autre_voiture) -> bool:
        """Indique si cette hitbox chevauche une autre hitbox.

        Args:
            voiture (Car): Voiture qui porte cette hitbox.
            autre (Hitbox): Hitbox à tester.
            autre_voiture (Car): Voiture qui porte l'autre hitbox.
        Returns:
            bool: True si les deux rectangles se chevauchent.
        """
        return self.penetration(voiture, autre, autre_voiture) is not None
