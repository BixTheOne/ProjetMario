class CollisionManager:
    """Gère les collisions entre voitures et la détection d'aspiration.

    Version basique : hitboxes rectangulaires orientées, séparation des voitures
    et rebond simple sur la vitesse.

    Attributes:
        rebond (float): Coefficient de rebond (0 = mou, 1 = élastique).
    """

    def __init__(self, rebond: float):
        """Initialise le gestionnaire de collisions.

        Args:
            rebond (float): Coefficient de rebond entre 0 et 1.
        """
        self.rebond = rebond

    def gerer_collisions(self, voitures: list) -> None:
        """Teste chaque paire de voitures et résout les chevauchements.

        Args:
            voitures (list[Car]): Les voitures en course.
        """
        for i in range(len(voitures)):
            for j in range(i + 1, len(voitures)):
                self._resoudre(voitures[i], voitures[j])

    def _resoudre(self, a, b) -> None:
        """Sépare deux voitures qui se chevauchent et amortit leur vitesse.

        Args:
            a (Car): Première voiture.
            b (Car): Deuxième voiture.
        """
        contact = a.hitbox.penetration(a, b.hitbox, b)
        if contact is None:
            return
        profondeur, nx, ny = contact   # (nx, ny) : normale du choc, de a vers b

        # 1. Séparer : chacune recule de la moitié du chevauchement
        recul = profondeur / 2
        a.x -= nx * recul
        a.y -= ny * recul
        b.x += nx * recul
        b.y += ny * recul

        # 2. Vitesse : on retire la part qui rapproche les voitures
        v_rel = (b.vx - a.vx) * nx + (b.vy - a.vy) * ny
        if v_rel < 0:                  # elles se rapprochent
            impulsion = -(1 + self.rebond) * v_rel / 2
            a.vx -= impulsion * nx
            a.vy -= impulsion * ny
            b.vx += impulsion * nx
            b.vy += impulsion * ny

    def detecter_aspiration(self, voitures: list) -> None:
        """Met à jour `en_aspiration` pour chaque voiture.

        Une voiture est en aspiration si sa hitbox est dans la zone
        d'aspiration d'une autre voiture. Aucun effet physique pour l'instant.

        Args:
            voitures (list[Car]): Les voitures en course.
        """
        for suiveuse in voitures:
            suiveuse.en_aspiration = any(
                meneuse.zone_aspiration.touche(meneuse, suiveuse.hitbox, suiveuse)
                for meneuse in voitures if meneuse is not suiveuse
            )
