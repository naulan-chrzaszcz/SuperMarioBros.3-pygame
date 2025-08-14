from pygame import Rect


class Camera(object):
    def __init__(self,size):
        # ### INT/FLOAT VARIABLES ###
        self.width = size[0]
        self.height = size[1]

        # ### RECT VARIABLES ###
        self.rect = Rect(0,0,size[0],size[1])

        # ### FUNCTION VARIABLES ###
        # apply() -> Set a new value for entity (or image) according to the position of the camera
        self.apply = lambda entity,add_x=0,add_y=0: entity.rect.move((self.rect.topleft[0] + add_x),(self.rect.topleft[1] + add_y))
        self.apply_rect = lambda rect: rect.move(self.rect.topleft)

    def update(self,target):
        x = -target.rect.x + 100
        y = -target.rect.y

        # limit scrolling to map size
        x = min(0,x)  # left
        y = min(0,y)  # top
        x = max(-self.width,x)  # right
        y = max(-(self.height - 237),y)  # bottom
        self.rect.update(x,y,self.width,self.height)
