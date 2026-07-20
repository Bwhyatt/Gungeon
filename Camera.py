import pygame

class Camera:
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height

    def update(self, player):
        self.offset.x = player.Rect.centerx - self.width // 2
        self.offset.y = player.Rect.centery - self.height // 2

    def apply(self, target):
        if isinstance(target, pygame.Rect):
            return target.move(-self.offset.x, -self.offset.y)

        return target - self.offset