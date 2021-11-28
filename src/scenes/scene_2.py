from math import cos, sin

from window import Window


class Scene2(object):

    def __init__(self, res):
        self.window = Window(200, 95, 132, 40,
                             res=res["entities"], who="Mario")
        self.window.title = "WORLD_1"
        self.window.cases = ["MARIO", "5"]
        self.player_sheet = res["entities"]["player"]
        self.stars_sheet = res["tiles"]["starsSheet"]

        self.stars_position = [0, 0]
        self.multi = 1
        self.target = 0
        self.t_cos = 0
        self.t_sin = 0
        self.t = 0

        self.switch_multiplication = [False, False]
        self.step = [False, False, False, False]
        self.finish = False

    def start(self,surface,dt,more_info,sfx):
        match int(self.t):
            case 0: self.step[0] = True
            case 15: self.step[1] = True
            case 21: self.step = [False, False, True, False]
            case 28: self.step = [False, False, False, True]
        self.t += (.05 * dt)

        # TODO Ajuster le timing des etoiles.
        match int(self.t_cos):
            case 0: self.switch_multiplication = [True, False]
            case 13: self.switch_multiplication = [False, True]

        if self.finish != 1:
            if self.step[0]:
                self.window.updates(dt)
                self.window.draw(surface)
            if self.step[1]:
                self.window.animation()
                if self.window.get_width() <= 0:
                    self.t = 21
            elif self.step[2]:
                # TODO Ajuster la vitesse pour qu'il soit plus rapide
                if self.switch_multiplication[0]:
                    self.multi += (1.5 * dt)
                    self.target += (0.05 * dt)
                elif self.switch_multiplication[1]:
                    self.multi -= (1.2 * dt)
                    self.target -= (0.05 * dt)
                    if int(self.target) == -1:
                        self.target = 0
                        self.switch_multiplication[1] = False

                # Stars
                left = self.window.get_BarWindow()[0]; left_ = left / 1.5
                starsSheetPosition = (11 * int(self.target),0),(11,11)
                surface.blit(self.stars_sheet.subsurface(starsSheetPosition),(((cos(self.t_cos) * self.multi)+left) - self.stars_position[0], (sin(self.t_sin) * self.multi) + left_))
                surface.blit(self.stars_sheet.subsurface(starsSheetPosition),(((cos(self.t_cos - 5) * self.multi)+left) - self.stars_position[0], (sin(self.t_sin - 5) * self.multi) + left_))
                surface.blit(self.stars_sheet.subsurface(starsSheetPosition),(((cos(self.t_cos - 10) * self.multi)+left) - self.stars_position[0], (sin(self.t_sin - 10) * self.multi) + left_))
                surface.blit(self.stars_sheet.subsurface(starsSheetPosition),(((cos(self.t_cos - 15) * self.multi)+left) - self.stars_position[0], (sin(self.t_sin - 15) * self.multi) + left_))
                surface.blit(self.stars_sheet.subsurface(starsSheetPosition),(((cos(self.t_cos - 20) * self.multi)+left) - self.stars_position[0], (sin(self.t_sin - 20) * self.multi) + left_))
                surface.blit(self.stars_sheet.subsurface(starsSheetPosition),(((cos(self.t_cos - 13) * self.multi)+left) - self.stars_position[0], (sin(self.t_sin - 13) * self.multi) + left_)) if self.t_cos > 5 else 0
                surface.blit(self.stars_sheet.subsurface(starsSheetPosition),(((cos(self.t_cos - 23) * self.multi)+left) - self.stars_position[0], (sin(self.t_sin - 23) * self.multi) + left_)) if self.t_cos > 5 else 0

                # Stars animation
                self.t_cos += (.2 * dt)
                self.t_sin += (.2 * dt)
                self.stars_position[0] += (.85 * dt)

            self.finish = True if self.step[3] else False
