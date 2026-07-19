
import pygame
import Gun
class Realplayer:
    def __init__(self, speed, size, pos, GivenGun):
       ChosenGun = Gun.WhichGun[GivenGun]
       self.speed = speed
       self.size = pygame.Vector2(size)
       self.pos = pygame.Vector2(pos)
       self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
       self.alive = True
       self.gun = ChosenGun((50, 20), GivenGun, pygame.mouse.get_pos(), self.pos, False)
       self.inventory = []
    def update(self, screen, keys, dt, mousepos):
        self.move(keys, dt, self.speed)
        #for now keys will be passed in
        self.draw(screen)
        self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
    def draw(self, screen):
        pygame.draw.rect(screen, "green", self.Rect)
    def move(self, keys, dt, speed):
        if keys[pygame.K_w]:
            self.pos.y -= speed * dt
        if keys[pygame.K_s]:
            self.pos.y += speed * dt
        if keys[pygame.K_a]:
            self.pos.x -= speed * dt
        if keys[pygame.K_d]:
            self.pos.x += speed * dt
        #size, shape, speed, mousepos, position
        #bullet angle is tan (y component on x component)
        #x position of bullet is incremented speed multiplied by cos component