class SpriteAnimation:

    class Undefined:
        def update(dt) -> None:
            pass
    
    def __init__(self, sprite, image, frames, speed, subsurface_direction="x"):
        self.sprite = sprite
        self.image = image
        self.frames = frames
        self.speed = speed
        self.subsurface_direction = subsurface_direction
        self.timer = 0

    def update(self, dt) -> None:
        self.timer += self.speed * dt
        self.timer %= self.frames

        frame = int(self.timer)
        if self.subsurface_direction == "x":
            self.sprite.image = self.image.subsurface(
                (frame * self.sprite.rect.width, 0),
                (self.sprite.rect.width, self.sprite.rect.height),
            )
        elif self.subsurface_direction == "y":
            self.sprite.image = self.image.subsurface(
                (0, frame * self.sprite.rect.height),
                (self.sprite.rect.width, self.sprite.rect.height),
            )
