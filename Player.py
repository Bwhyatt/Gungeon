
import pygame
class player:
    def __init__(self, speed, size, pos):
       self.speed = speed
       self.size = pygame.Vector2(size)
       self.pos = pygame.Vector2(pos)
       self.rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
    def update(self, screen, keys, dt, mousepos):
        self.move(keys, dt)
        self.shoot(mousepos)#for now keys will be passed in
        self.draw(screen)
        self.rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
    def draw(self, screen):
        pygame.draw.rect(screen, "green", self.rect)
    def move(self, keys, dt):
        if keys[pygame.K_w]:
            self.pos.y -= 300 * dt
        if keys[pygame.K_s]:
            self.pos.y += 300 * dt
        if keys[pygame.K_a]:
            self.pos.x -= 300 * dt
        if keys[pygame.K_d]:
            self.pos.x += 300 * dt
    def shoot(self, mousepos):
        pass