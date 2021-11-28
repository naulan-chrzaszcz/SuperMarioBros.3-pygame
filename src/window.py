from pygame import Surface, Rect, draw

from font import Font


class Window(object):
    itemFrame: Rect
    msgFrame: Rect

    __dt: float = .0
    __who: str
    __entitiesRes: dict

    _cases: list = []
    _title: str = ""

    def __init__(self, width: int, height: int,
                       x: float, y: float, **kwargs):
        self.__font = Font()

        self.__entitiesRes = kwargs["res"]
        self.__who = kwargs["who"]
        self.__playerImg = self.__entitiesRes[self.__who.lower()]

        self.__width = width
        self.__height = height
        self.__x = x
        self.__y = y

    def checkGoodChar(self, text: str):
        n = 1
        for char in text.upper():
            if char not in ['_',' ','.']:
                if char not in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9']:
                    return n
                n += 1
        return n

    @property
    def cases(self):
        """ It allow to specific what text for place in the window which has will display """
        return self._cases

    @property
    def title(self):
        """ It allow to specific a title for the window which has will display """
        return self._title
        
    @title.setter
    def title(self, title: str):
        n = self.checkGoodChar(title)
        self._title = "ERROR_BAD_CHARACTERS" if n != len(title)-1 else title.upper()

    @cases.setter
    def cases(self, l: list):
        s = 1
        for element in l:
            n = self.checkGoodChar(element)
            if n != len(element)-1:
                break
            s += 1

        self._cases = ["ERROR_BAD_CHARACTERS", "ERROR_BAD_CHARACTERS"] if s != len(l)-1 else l

    @title.getter
    def title(self) -> str:
        return self._title

    @cases.getter
    def cases(self) -> list:
        return self._cases

    def get_width(self) -> int:
        return self.__width

    def set_width(self, width: int):
        """ set_width()
                Attribute new width size to the window """
        self.__width = width

    def get_height(self) -> int:
        return self.__height

    def set_height(self, height: int):
        """ set_height()
                Attribute new height size to the window """
        self.__height = height

    def get_size(self) -> tuple:
        """ get_size() -> tuple
                Get the size of the windows in a tuple. """
        return (self.__width, self.__height)

    def get_position(self) -> tuple:
        """ get_position() -> tuple
                Get the position of the windows on the screen."""
        return (self.__x, self.__y)

    def animation(self, surface: Surface, msgFrame: Rect, dt: float):
        # TODO Réparer les animations de la fenêtre
        screen_w = surface.get_width()
        screen_h = surface.get_height()
        itemFrame_w = screen_w/6
        msgFrame_w = itemFrame_w/1.1
        white = (255, 255, 255)

        if int(itemFrame_w) >= 0:
            itemFrame_w -= (5*dt)
            msgFrame_w -= (5*dt)

        # Outline window
        if int(itemFrame_w) > 0:
            draw.line(surface, white, (msgFrame.topleft[0]-2, msgFrame.topleft[1]-1), (msgFrame.bottomleft[0]-2, msgFrame.bottomleft[1]), 2)
            draw.line(surface, white, (msgFrame.topleft[0] - 1, msgFrame.topleft[1] - 2), (msgFrame.topright[0], msgFrame.topright[1] - 2), 2)
            draw.line(surface, white, (msgFrame.bottomleft[0] - 1, msgFrame.bottomleft[1]), (msgFrame.bottomright[0], msgFrame.bottomright[1]), 2)
            draw.line(surface, white, (msgFrame.topright[0], msgFrame.topright[1] - 1), (msgFrame.bottomright[0], msgFrame.bottomright[1]), 2)

    def draw(self, surface: Surface):
        screen_w = surface.get_width()
        screen_h = surface.get_height()
        itemFrame_w = screen_w/3
        msgFrame_w = itemFrame_w/1.1
        self.itemFrame = Rect((screen_w/3, screen_h/4), (itemFrame_w, 80))
        self.msgFrame = Rect((screen_w/2.86, screen_h/3.52), (msgFrame_w, self.itemFrame.height/1.25))
        draw.rect(surface, (0, 0, 0), self.itemFrame)
        draw.rect(surface, (175, 232, 226), self.msgFrame)

        halfFrame_w = self.msgFrame.w/2
        halfFrame_h = self.msgFrame.h/2
        # TODO Arranger la position de l'image du joueur
        surface.blit(self.__playerImg.subsurface(32,16,16,16), ((screen_w+halfFrame_w)/2.18, (screen_h+halfFrame_h)/2.8))

        # TODO Arranger les position des textes afficher dans la fenêtre
        self.__font.draw_msg(surface, [((screen_w+halfFrame_w)/2.01), ((screen_h+halfFrame_h)/2.6)], self.cases[0])
        self.__font.draw_msg(surface, [((screen_w+halfFrame_w)/2.18), ((screen_h+halfFrame_h)/3.8)], self.title)
        self.__font.draw_msg(surface, [((screen_w+halfFrame_w)/2.48), ((screen_h+halfFrame_h)/2.6)], self.cases[1])
        self.animation(surface, self.msgFrame, self.__dt)

    def updates(self, dt: float):
        self.__dt = dt
