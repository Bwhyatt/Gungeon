import pygame
import math
class bullet:
    def __init__(self, size, shape, speed, targetpos, position, damage):
        self.size = size
        self.shape = shape
        self.speed = speed
        self.pos = pygame.Vector2(position)
        self.targetpos = targetpos
        self.damage = damage
        self.dircounter = 0
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.tag = "Bullet"
        self.lifetime = 0
    def determinedir(self, targetpos):
       #since the up is reversed and down for me on the screen is up which is the opposite on num plane so needs to be self 1 for rise
        
        #print("targetpos is " + str(targetpos))
        #print("self pos is " + str(self.pos))

        acute_rad = math.atan2((targetpos[1] - self.pos[1]), (targetpos[0] - self.pos[0]))

        #print("acutesef sjdfjse " + str(acute_rad))
        return acute_rad
    def move(self, speed, dt, angle):
        #remember plus both will go bottom right
        self.pos += pygame.Vector2(math.cos(angle) * speed * dt, math.sin(angle)* dt * speed)
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.pos, self.size)
    def destroy(self):
        pass
    def update(self, dt, screen):
        if(self.lifetime > 7):
            self.kill()
        if self.dircounter == 0:
            self.acute_rad = self.determinedir(self.targetpos)
            self.dircounter += 1
        self.move(self.speed, dt, self.acute_rad)
        self.draw(screen)
        
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
#so basically we get cosx component to move on X axis and sinx component to move on y axis
#base class
#child class circle
#child class square