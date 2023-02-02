from pygame import Surface


class Creator(object):
    __instance = None

    screen: Surface
    display: Surface

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Creator, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self, screen: Surface, display: Surface):
        self.screen = screen
        self.display = display

    @staticmethod
    def get_instance():
        if Creator.__instance is None:
            Creator.__instance = Creator(None, None)
        return Creator.__instance

    def run(self):
        while True:
            pass
