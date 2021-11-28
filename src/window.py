from pygame import Surface, Rect, draw

from font import Font


def check_goodChar(text: str) -> bool:
    """ checkGoodChar() -> bool
            Check if all character insert into text variable is good or not. """
    for char in text.upper():
        if char not in ['_',' ','.','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9']:
            return False
    return True


class Window(object):
    """ Window()
            > It allow to display a window on the screen.


            self.cases must do 2 elements.
            self.cases[0] -> player name.
            self.cases[1] -> left texts.

            self.cases must not do 2 elements:
                * Print in the terminal a warning.
                * Replace everything in the list by "ERROR_BAD_LIST".

            if self.cases is not attribute after initialisation, the self.cases variable is going to set by empty list


            self.title must have good char like for self.cases[n]

            self.title must not have good char:
                * Print in the terminal a warning
                * Replace the title by "ERROR_BAD_CHARACTERS"

            if self.title is not attribute after initialisation, the self.title variable is going to set by "Unknown"


            def __init__(*arg):
                width or/and height:
                    if width is not attribute and height is attributed (Is same for height size):
                        * Print in the terminal a warning
                        * Width and height gonna be set with height default value is same for width
                **kwargs:
                    * "res" key is not optional ! The Window class at need that !
                    * Is same for "who" key ! The Window class at need that !


            The function for display the window is "draw()".
            You need to put on your code the "updates()" function. """
    __itemFrame: Rect
    __msgFrame: Rect
    __dt: float = .0
    __who: str
    __entitiesRes: dict

    _cases: list = []
    _title: str = "UNKNOWN"

    def __init__(self, width: int=None, height: int=None, x: float=.0, y: float=.0, **kwargs):
        """ :param width: Width of the Window (only int, default None)
            :param height: Height of the Window (only int, default None)
            :param x: Position on the abscissa (only float, default .0)
            :param y: Positon on the orderly (only float, default .0)
            :param kwargs: "res" needed, "who" needed """
        self.__font = Font()

        self.__entitiesRes = kwargs["res"]
        self.__who = kwargs["who"]
        self.__playerImg = self.__entitiesRes[self.__who.lower()]

        self.__width = width
        if self.__width is None:
            print("\033[93m Warn: 'width' argument is not attribute in Window class !\n",
                  "\033[93m Please attribute this argument if you want are window have the good size\033[0m")
        self.__height = height
        if self.__height is None:
            print("\033[93m Warn: 'height' argument is not attribute in Window class !\n",
                  "\033[93m Please attribute this argument if you want are window have the good size\033[0m")
        self.__x = x
        self.__y = y

        if self.__height is not None and self.__width is not None:
            self.__itemFrame = Rect((self.__x,self.__y),(self.__width + 10,self.__height + 10))
            self.__msgFrame = Rect((self.__x + 5,self.__y + 5),(self.__width,self.__height))
        else:
            self.__itemFrame = Rect((self.__x,self.__y),(0, 0))
            self.__msgFrame = Rect((self.__x + 5,self.__y + 5),(0, 0))

    @property
    def cases(self):
        """ It allow to specific what text for place in the window which has will display """
        return self._cases

    @property
    def title(self):
        """ It allow to specific a title for the window which has will display """
        return self._title

    def animation(self):
        self.__width -= (4*self.__dt) if self.__width >= 0 else 0

    def draw(self, surface: Surface):
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Size not custom by the user
        if self.__height is None or self.__width is None:
            self.__width = screen_w / 3
            msgFrame_w = self.__width / 1.1
            self.__itemFrame.width = self.__width
            self.__itemFrame.height = 80
            self.__msgFrame.width = msgFrame_w
            self.__msgFrame.height = self.__itemFrame.height / 1.25
        else:
            self.__itemFrame.width = self.__width+10
            self.__msgFrame.width = self.__width

        draw.rect(surface, (0, 0, 0), self.__itemFrame)
        draw.rect(surface, (175, 232, 226), self.__msgFrame)

        if self.__height is None or self.__width is None:
            halfHeight = screen_h / 2
            surface.blit(self.__playerImg.subsurface(32,16,16,16),(self.__x + (screen_w - 20),self.__y + halfHeight))

            halfWidth = screen_w / 2
            self.__font.draw_msg(surface,[self.__x + (screen_w - 35),self.__y + halfHeight],self.cases[0])
            self.__font.draw_msg(surface,[self.__x + (halfWidth + 15),self.__y + 10],self.title)
            self.__font.draw_msg(surface,[self.__x + (screen_w - 70),self.__y + halfHeight],self.cases[1])
        else:
            # TODO Améliorer l'affichage au cas où, si l'utilisateur utilise mal la classe Window
            halfHeight = self.__height/2
            surface.blit(self.__playerImg.subsurface(32,16,16,16), (self.__x+(self.__width-20), self.__y+halfHeight))

            halfWidth = self.__width/2
            self.__font.draw_msg(surface, [self.__x+(self.__width-35), self.__y+halfHeight], self.cases[0])
            self.__font.draw_msg(surface, [self.__x+(halfWidth+15), self.__y+10], self.title)
            self.__font.draw_msg(surface, [self.__x+(self.__width-70), self.__y+halfHeight], self.cases[1])

        white = (255, 255, 255)
        topLeft = self.get_cornerWindow()[0]; topRight = self.get_cornerWindow()[1]
        bottomLeft = self.get_cornerWindow()[2]; bottomRight = self.get_cornerWindow()[3]

        draw.line(surface, white, (topLeft[0]-2, topLeft[1]-1), (bottomLeft[0]-2, bottomLeft[1]), 2)
        draw.line(surface,white,(topLeft[0]-1, topLeft[1]-2), (topRight[0], topRight[1]-2), 2)
        draw.line(surface,white,(bottomLeft[0]-1, bottomLeft[1]), (bottomRight[0], bottomRight[1]), 2)
        draw.line(surface,white,(topRight[0], topRight[1]-1), (bottomRight[0], bottomRight[1]), 2)

    def updates(self, dt: float):
        self.__dt = dt

    @title.setter
    def title(self, title: str):
        """
            title = "My_Title"
                Attribute a new title in the window.
            :param title: On upper case, please use normal ASCII characters out special characters
        """
        if not check_goodChar(title):
            self._title = "ERROR_BAD_CHARACTERS"
            print(f"\033[93m Warn: The \033[96mtext\033[93m which as put in \33[95mself\033[0m.title\033[93m variable is not good, {title} is not good. \033[0m")
        else: self._title = title.upper()

    @cases.setter
    def cases(self, cases: list):
        """ cases = ["popoekdn", ...]
                Attribute the new text area to display in window.
            :param cases: Need 2 elements in the list. """
        if len(cases) < 2:
            self._cases = ["ERROR_BAD_LIST", "ERROR_BAD_LIST"]
            print(f"\033[93m Warn: The \033[96mlist\033[93m which as put in \33[95mself\033[0m.cases\033[93m variable is not good, list size ({len(cases)} element(s)) is not good. \033[0m")
        else:
            areGood = False
            for element in cases:
                areGood = check_goodChar(element)

            if not areGood:
                self._cases = ["ERROR_BAD_CHARACTERS", "ERROR_BAD_CHARACTERS"]
                print(f"\033[93m Warn: The \033[96mlist\033[93m which as put in \33[95mself\033[0m.cases\033[93m variable is not good, {element} is not good. \033[0m")
            else: self._cases = cases

    def set_width(self, width: int):
        """ set_width()
                Attribute new width size to the window
            :param width: New width for the window (only int). """
        self.__width = width

    def set_height(self, height: int):
        """ set_height()
                Attribute new height size to the window
            :param height: New height for the window (only int)."""
        self.__height = height

    @title.getter
    def title(self) -> str:
        return self._title

    @cases.getter
    def cases(self) -> list:
        return self._cases

    def get_width(self) -> int:
        """ get_width() -> int
                        Get the width of the window. """
        return self.__width

    def get_height(self) -> int:
        """ get_height() -> int
                Get the height of the window. """
        return self.__height

    def get_size(self) -> tuple:
        """ get_size() -> tuple
                Get the size of the windows in a tuple. """
        return (self.__width, self.__height)

    def get_position(self) -> tuple:
        """ get_position() -> tuple
                Get the position of the windows on the screen."""
        return (self.__x, self.__y)

    def get_cornerWindow(self) -> tuple:
        """ get_cornerWindow() -> tuple
                Get all corner of the Window.
             ↓________↓
             | Window |
             ↑‾‾‾‾‾‾‾‾↑ """
        return (self.__msgFrame.topleft, self.__msgFrame.topright, self.__msgFrame.bottomleft, self.__msgFrame.bottomright)

    def get_BarWindow(self) -> tuple:
        """ get_cornerWindow() -> tuple
                Get all corner of the Window.
              ____↓____
            →| Window  |←
              ‾‾‾‾↑‾‾‾‾ """
        return (self.__msgFrame.left, self.__msgFrame.top, self.__msgFrame.right, self.__msgFrame.bottom)

