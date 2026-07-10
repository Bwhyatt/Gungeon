import pygame
class door:
    def __init__(self, size, pos, room1, room2):
        self.connectedrooms = (room1,room2)
        self.size = size
        self.pos = pos
        self.Rect = pygame.rect(pos.x, pos.y, size.x, size.y)
    def collide(self, obj2):
        if self.Rect.colliderect(obj2.Rect):
            return True
        return False
    def determineRoom(self, obj2):
        obj2.Room = self.connnectedrooms[1] if obj2.Room == self.connectedrooms[0] else self.connectedrooms[0]
    def draw(self, screen):
        pygame.draw.rect(screen, "white", self.Rect)
    def update(self, screen, obj2):
        if(self.collide(obj2)):
            self.determineRoom(obj2)
        self.draw(screen)