import pygame
import math
class bullet:
    def __init__(self, size, shape, speed, mousepos, position):
        self.size = size
        self.shape = shape
        self.speed = speed
        self.pos = pygame.Vector2(position)
        self.mousepos = mousepos
        self.upY = -1 if mousepos[1] > self.pos[1] else 1
        self.upX = 1 if mousepos[0] > self.pos[0] else -1
        self.dircounter = 0
    def determinedir(self, mousepos):
       #since the up is reversed and down for me on the screen is up which is the opposite on num plane so needs to be self 1 for rise
        print("mousepos is " + str(mousepos))
        print("self pos is " + str(self.pos))
        acute_rad = math.atan2((mousepos[1] - self.pos[1]), (mousepos[0] - self.pos[0]))
        print("acutesef sjdfjse " + str(acute_rad))
        return acute_rad
    def move(self, speed, dt, angle):
        #remember plus both will go bottom right
        self.pos += pygame.Vector2(math.cos(angle) * speed * dt, math.sin(angle)* dt * speed)
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.pos, self.size)
    def update(self, dt, screen):
        if self.dircounter == 0:
            self.acute_rad = self.determinedir(self.mousepos)
            self.dircounter += 1
        self.move(self.speed, dt, self.acute_rad)
        self.draw(screen)
#so basically we get cosx component to move on X axis and sinx component to move on y axis
#base class
#child class circle
#child class square