import pygame
import math

from Bullet import bullet
class Gun:
    def __init__(self, size, gunName, mousepos, position):
        self.size = size
        #gunName will be used later when i design other guns
        self.pos = pygame.Vector2(position)
        self.mousepos = pygame.Vector2(mousepos)
        self.upY = 1 if self.mousepos.y > self.pos.y else -1
        self.upX = 1 if self.mousepos.x > self.pos.x else -1
        self.dircounter = 0
        self.ammo = 10
        self.capacity = 10
        self.reloadTime = 2
        self.fireRate = 0.5
        self.fireratetimer = 0 # timer to basically act as firerate checker
        self.reloadpressed = False
        self.bulletList = []

        self.bulletsPershot = 1
        self.spread = 0
        #note to self: self spread will be angle in radians that will determine the angle of the sector
    def determinedir(self, mousepos):
        acute_rad = math.atan2((mousepos.y - self.pos.y), (mousepos.x - self.pos.x))
        return acute_rad
    def CanShoot(self, ammo, timer):
        if ammo > 0 and timer <= 0:
            return True
        else:
            return False
    def reload(self, ammo, capacity):
        if ammo < capacity:
            ammo = capacity
            self.reloadpressed = False
        self.reloadtimerr = self.reloadTime
    def shoot(self, mousepos):
        if self.CanShoot(self.ammo, self.fireratetimer):
            print("shooting")
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            bullet1 = bullet(20, "circle", 500, mousepos, self.pos)
            self.bulletList.append(bullet1)
        else:
            print("cant shoot")
    def draw(self, screen):
        pygame.draw.rect(screen, "red", (self.pos.x, self.pos.y, self.size[0], self.size[1]))
    
    def update(self, dt, screen, keys, position, mousepos):
        self.mousepos = pygame.Vector2(mousepos)
        if self.dircounter == 0:
            self.acute_rad = self.determinedir(self.mousepos)
            self.dircounter += 1
        self.fireratetimer -= dt
        if keys[pygame.K_r]:
            self.reloadpressed = True
        #if they press it then the reload timer will be able to begin

        if(self.reloadpressed):
            self.reloadtimer -= dt
            if self.reloadtimer <= 0:
                self.reload(self.ammo, self.capacity)
        
        if(pygame.mouse.get_pressed()[0]):
            self.shoot(mousepos)

        self.pos = pygame.Vector2(position)
        #make position player position
        #self.draw(screen)
    