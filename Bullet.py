import pygame
import math
class bullet:
    def __init(self, size, shape, speed, mousepos, position):
        self.size = size
        self.shape = shape
        self.speed = pygame.Vector2(speed)
        self.pos = pygame.Vector2(position)
        self.mousepos = mousepos
        self.upY = 1 if mousepos[1] > self.pos[1] else -1
        self.upX = 1 if mousepos[0] > self.pos[0] else -1
        self.dircounter = 0
    def determinedir(self, mousepos):
        acute_rad = math.atan((mousepos[1] - self.pos[1]), (mousepos[0] - self.pos[0]))
        return acute_rad
    def move(self, speed, dt):
        self.pos[0] += math.cos(self.acute_rad) * self.upX * speed * dt
        self.pos[1] += math.sin(self.acute_rad) * self.upY * dt * speed
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.pos, self.size)
    def update(self, dt, screen):
        if self.dircounter == 0:
            self.acute_rad = self.determinedir(self.mousepos)
            self.dircounter += 1
        self.move(self.speed, dt)
        self.draw(screen)
#so basically we get cosx component to move on X axis and sinx component to move on y axis
#base class
#child class circle
#child class square