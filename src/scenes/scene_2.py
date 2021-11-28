from math import cos, sin

from window import Window


class Scene2(object):

    def __init__(self, res):
        self.window = Window(300, 200, 0, 0,
                             res=res["entities"], who="Mario")
        self.player_sheet = res["entities"]["player"]
        self.stars_sheet = res["tiles"]["starsSheet"]

        self.stars_position = [0, 0]
        self.multiplication = 1
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
            case 18: self.step = [False, False, True, False]
            case 33: self.step = [False, False, False, True]
        self.t += (.1 * dt)

        # TODO Ajuster le timing des etoiles.
        match int(self.t_cos):
            case 0: self.switch_multiplication = [True, False]
            case 7: self.switch_multiplication = [False, True]

        if self.finish != 1:
            if self.step[0]:
                # TODO Faire disposition d'affichage correct
                # TODO Arranger les positions des textes
                # TODO Verifier les getter et setter
                self.window.title = f"WORLD_{more_info[1]}"
                self.window.cases = ["MARIO", str(more_info[0])]

                # TODO Réparer l'animation de la fenêtre
                self.window.updates(dt)
                self.window.draw(surface)
            elif self.step[2]:
                # TODO Ajuster la vitesse pour qu'il soit plus rapide
                if self.switch_multiplication[0]:
                    self.multiplication += (1.5 * dt)
                    self.target += (0.05 * dt)
                elif self.switch_multiplication[1]:
                    self.multiplication -= (1.2 * dt)
                    self.target -= (0.05 * dt)
                    if int(self.target) == -1:
                        self.target = 0
                        self.switch_multiplication[1] = False

                # TODO Remettre a la fin les étoiles et augmenter leurs vitesse
                """
                # Stars
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 5) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 5) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 10) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 10) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 15) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 15) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 20) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 20) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 13) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 13) * self.multiplication) + item_frame.left / 1.5)) if self.t_cos > 5 else 0
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 23) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 23) * self.multiplication) + item_frame.left / 1.5)) if self.t_cos > 5 else 0
                """

                # Stars animation
                self.t_cos += (.1 * dt)
                self.t_sin += (.1 * dt)
                self.stars_position[0] += (.85 * dt)

            self.finish = True if self.step[3] else False
