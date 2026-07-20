import pygame
import math

from Bullet import bullet
class GunParent:
    def __init__(self, size, gunName, Targetpos, position, Enemy):
        self.size = size
        #gunName will be used later when i design other guns
        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)
        self.upY = 1 if self.Targetpos.y > self.pos.y else -1
        self.upX = 1 if self.Targetpos.x > self.pos.x else -1
        #counts up if direction has been determined every frame
        self.ammo = 10
        self.capacity = 10
        self.fireRate = 0.5
        self.fireratetimer = 0 # timer to basically act as firerate checker
        self.EnemyOwner = Enemy # checks if this is the player's gun or the enemy's
        #reload variables
        self.reloadTime = 2
        self.reloadpressed = False
        self.reloadtimer = self.reloadTime

        self.bulletList = []

        self.bulletsPershot = 1
        self.spread = 0
        #note to self: self spread will be angle in radians that will determine the angle of the sector
    def determinedir(self, Targetpos):
        acute_rad = math.atan2((self.pos.y - Targetpos.y ) , (Targetpos.x - self.pos.x))
        return acute_rad
    def CanShoot(self, ammo, timer):#checks if the firerate timer has gone off, not concerned with reload
        if ammo > 0 and timer <= 0:
            return True
        else:
            #print("timer is " + str(timer))
            #print("ammo is " + str(ammo))
            return False
    def reload(self, ammo, capacity):
        if ammo < capacity:
            ammo = capacity
            self.reloadpressed = False
            #print("reloaded")
        self.reloadtimer = self.reloadTime
        return ammo
    def shoot(self,position, Targetpos, damage):
        if self.CanShoot(self.ammo, self.fireratetimer):
            #print("shooting")
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            bullet1 = bullet(20, "circle", 500, Targetpos, position, damage)
            self.bulletList.append(bullet1)
        else:
            #print("cant shoot")
            pass
    def draw(self, screen, size, position, Targetpos):
        #pygame.draw.rect(screen, "red", (position[0],position[1], size[0], size[1]))
        angle_deg = math.degrees(self.acute_rad)

        # Build the original, unrotated rectangle once and cache it
        if not hasattr(self, "original_image"):
            self.original_image = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, "red", (0, 0, size[0], size[1]))

        rotated_image = pygame.transform.rotate(self.original_image, angle_deg)
        rect = rotated_image.get_rect(center=position)
        screen.blit(rotated_image, rect)
    
    def update(self, dt, screen, keys, position, Targetpos):
        self.Targetpos = pygame.Vector2(Targetpos)#Need to make this player pos
        self.acute_rad = self.determinedir(self.Targetpos)
        self.fireratetimer -= dt
        if keys[pygame.K_r]:
            self.reloadpressed = True
        #if they press it then the reload timer will be able to begin

        if(self.reloadpressed or self.ammo <= 0):
            self.reloadtimer -= dt
            if self.reloadtimer <= 0:
                self.ammo = self.reload(self.ammo, self.capacity)
        
        if(pygame.mouse.get_pressed()[0] and not self.EnemyOwner and self.CanShoot(self.ammo, self.fireratetimer)):
            self.shoot(self.pos, self.Targetpos, 20)# 20 is magic number rn TBD
        if(self.EnemyOwner):
            if(self.CanShoot(self.ammo, self.fireratetimer)):
                self.shoot(self.pos, self.Targetpos, 20)

        self.pos = pygame.Vector2(position)
        #make position player position
        self.draw(screen, self.size, (self.pos.x, self.pos.y), self.Targetpos)

class Shotgun(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.ammo = 6
        self.capacity = 6
        self.fireRate = 1.2
        self.bulletsPershot = 6
        self.spread = math.radians(32)
    def shoot(self, position, Targetpos, damage):
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            BaseAngle = self.determinedir(self.Targetpos)
            for i in range(self.bulletsPershot):
                bullet1 = bullet(20, "circle", 500, Targetpos, position, damage)
                t = i /(self.bulletsPershot - 1) if self.bulletsPershot > 1 else 0.5
                angle_offset = -(self.spread/2) + t * self.spread
                angle = BaseAngle + angle_offset
                ThisTarget = pygame.Vector2(position[0] + math.cos(angle) * 500, position[1] - math.sin(angle) * 500)
                bullet1 = bullet(20, "circle", 500, ThisTarget, position, damage)
                self.bulletList.append(bullet1)
                #print("Shot one")
        #def __init__(self, size, shape, speed, targetpos, position, damage):
WhichGun = {cls.__name__: cls for cls in GunParent.__subclasses__()}