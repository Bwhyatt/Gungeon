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
        self.timer = 0 # timer to basically act as firerate checker
        self.reloadpressed = False
        self.bulletList = []
    
    def determinedir(self, mousepos):
        acute_rad = math.atan2((mousepos.y - self.pos.y), (mousepos.x - self.pos.x))
        return acute_rad
    def CanShoot(self):
        if self.ammo > 0 and self.timer <= 0:
            return True
        else:
            return False
    def reload(self):
        if self.ammo < self.capacity:
            self.ammo = self.capacity
        self.reloadpressed = False
    def shoot(self, mousepos):
        if self.CanShoot():
            print("shooting")
            self.ammo -= 1
            self.timer = self.fireRate
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
        self.timer -= dt
        if keys[pygame.K_r]:
            self.reloadpressed = True
        if(self.reloadpressed):
            self.reloadtime -= dt
            if self.reloadtime <= 0:
                self.reload()
        
        if(pygame.mouse.get_pressed()[0]):
            self.shoot(mousepos)

        self.pos = pygame.Vector2(position)
        #make position player position
        #self.draw(screen)
    