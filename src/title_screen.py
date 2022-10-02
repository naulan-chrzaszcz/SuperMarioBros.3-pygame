from pygame import Surface
from pygame.locals import K_a
from src.scenes.scene_1 import Scene1


class TitleScreen(Scene1):
    sheet: Surface
    keys: dict = {}
    dt: float = .0

    def __init__(self, res):
        super().__init__()
        self.sheet = res["tiles"]["titleScreenSheet"]
        self.voice = res["sfx"]["voice_superMarioBros3"]
        self.titleScreenMusic = res["musics"]["TitleScreenMsc"]
        self.titleScreenMusic.set_volume(.5); self.voice.set_volume(.35)
        self.color = (0, 0, 0)
        
        self.pass_stage_menu = False
        self.is_title = True
        self.play_voice = False
        self.play_titleScreen = False

    def getIsTitle(self) -> bool:
        return self.is_title

    def getPassStageMenu(self) -> bool:
        return self.pass_stage_menu

    def draw(self, surface) -> None:
        surface.fill(self.getBackgroundColor())
        h = surface.get_height()

        self.start(surface, self.dt)
        if int(self.t) >= 20 and not self.play_titleScreen:
            self.titleScreenMusic.play(loops=-1)
            self.play_titleScreen = True
        if int(self.t) > 40 and not self.play_voice:
            self.voice.play()
            self.play_voice = True
        # Curtain
        surface.blit(self.sheet.subsurface((0, 0), (256, 35)),(0, -2 - self.curtain_y))
        surface.blit(self.sheet.subsurface((0, 0), (256, 35)),(256, -2 - self.curtain_y))
        surface.blit(self.sheet.subsurface((0, 0), (256, 187)),(0, (h-221) - self.curtain_y))
        surface.blit(self.sheet.subsurface((0, 0), (256, 187)),(256, (h-221) - self.curtain_y))
        # Floor
        surface.blit(self.sheet.subsurface((0,188),(256,37)),(0, h - 37))
        surface.blit(self.sheet.subsurface((0,188),(256,37)),(256, h - 37))

    def updates(self, dt, keys_pressed):
        self.keys = keys_pressed
        self.dt = dt

        if self.keys[f'{K_a}']:
            self.pass_stage_menu = True
            self.is_title = False
