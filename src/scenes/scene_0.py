from pygame import Surface


class Scene0(object):
    """ Scene n°0
            Qu'es-ce qu'il se passe ?
                1. Debut = Fade in sur "intro-bg.png" pendant 1.5s
                2. Reste static pendant Stage1Msc
                3. Fade out sur "intro-bg.png" pendant 1.5s
                4. Fin = Passe à la Scene n°1
    """

    def __init__(self, res):
        self.step = [True, False]
        self.finish = False
        self.background = res["annexe"]["introBG"]
        self.alpha = 0
        self.t = 0

    def getFinish(self) -> bool:
        return self.finish

    def start(self, surface: Surface, dt: float) -> None:
        """ Demarre l'animation.
            (Fade in par default)
                :param dt: DeltaTime """
        surface.fill((0, 0, 0))

        # Timer
        if int(self.t) == 100:
            # Disable fade in and enable fade out
            self.step = [False, True]
        elif int(self.t) == 200:
            # Pass to scene n°1
            self.finish = True

        self.background.set_alpha(self.alpha)
        self.alpha += (5 * dt) if self.step[0] else 0
        self.alpha -= (5 * dt) if self.step[1] else 0
        surface.blit(self.background, (0, 0))
        self.t += (1*dt)
