
import pygame
from Bullet import bullet
class Realplayer:
    def __init__(self, speed, size, pos):
       self.speed = speed
       self.size = pygame.Vector2(size)
       self.pos = pygame.Vector2(pos)
       self.bulletList = []
       self.rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
       self.alive = True
    def update(self, screen, keys, dt, mousepos):
        self.move(keys, dt, self.speed)
        if pygame.mouse.get_pressed()[0]:
        
            self.shoot(mousepos)#for now keys will be passed in
        self.draw(screen)
        self.rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
    def draw(self, screen):
        pygame.draw.rect(screen, "green", self.rect)
    def move(self, keys, dt, speed):
        if keys[pygame.K_w]:
            self.pos.y -= speed * dt
        if keys[pygame.K_s]:
            self.pos.y += speed * dt
        if keys[pygame.K_a]:
            self.pos.x -= speed * dt
        if keys[pygame.K_d]:
            self.pos.x += speed * dt
    def shoot(self, mousepos):
        bullet1 = bullet(20, "circle", 500, mousepos, self.pos)
        self.bulletList.append(bullet1)
        #size, shape, speed, mousepos, position
        #bullet angle is tan (y component on x component)
        #x position of bullet is incremented speed multiplied by cos component
        pass