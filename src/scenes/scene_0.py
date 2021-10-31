class Scene0(object):
    """ Scene n°0:
            - Manage intro screen. """
    def __init__(self, res, event):
        self.step = [True, False]
        self.finish = False

        self.event = event
        self.background = res["annexe"]["introBG"]

        self.title_y = 0
        self.alpha = 0
        self.t = 0

    def start(self, surface, dt):
        surface.fill((0, 0, 0))

        # Timer
        if int(self.t) == 100:
            # Disable fadein
            self.step[0] = False
            # Enable fadeout
            self.step[1] = True
        elif int(self.t) == 200:
            self.finish = True

        self.background.set_alpha(self.alpha)
        surface.blit(self.background, (0, 0))

        self.alpha += (5*dt) if self.step[0] else 0
        self.alpha -= (5*dt) if self.step[1] else 0
        self.t += (1*dt)
