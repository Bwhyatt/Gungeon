
import pygame
import Gun
import Sword
class Realplayer:
    def __init__(self, speed, size, pos, health, GivenGun, GivenSword):
       self.GivenGun = GivenGun
       self.GivenSword = GivenSword
       ChosenSword = Sword.WhichSword[GivenSword]
       ChosenGun = Gun.WhichGun[GivenGun]
       self.speed = speed
       self.size = pygame.Vector2(size)
       self.pos = pygame.Vector2(pos)
       self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
       self.alive = True
       self.Maxhealth = health
       self.health = self.Maxhealth
       self.gun = ChosenGun((50, 20), GivenGun, pygame.mouse.get_pos(), self.pos, False)
       self.Sword = ChosenSword((100, 100), GivenSword, pygame.mouse.get_pos(), self.pos, False)
       self.inventory = []
       self.BannedDirections = []
       self.tag = "Player"
    def update(self, screen, keys, dt, mousepos):
        self.move(keys, dt, self.speed)
        #for now keys will be passed in
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
    def TakeDamage(self, damage):
        self.health -= damage
    def Regen(self, healing):
        self.health += healing
    #wall collision