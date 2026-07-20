import pygame
import math

import Bullet
class GunParent:
    def __init__(self, size, gunName, Targetpos, position, Enemy):
        self.size = pygame.Vector2(size)
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
        #note to self: self spread will be self.acute_rad in radians that will determine the self.acute_rad of the sector
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
            bullet1 = Bullet.bullet(20, "circle", 500, Targetpos, position, damage)
            self.bulletList.append(bullet1)
        else:
            #print("cant shoot")
            pass
    def draw(self, screen, camera, size, position):
        #pygame.draw.rect(screen, "red", (position[0],position[1], size[0], size[1]))
        self.acute_rad_deg = math.degrees(self.acute_rad)

        # Build the original, unrotated rectself.acute_rad once and cache it
        if not hasattr(self, "original_image"):
            self.original_image = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, "red", (0, 0, size[0], size[1]))

        rotated_image = pygame.transform.rotate(self.original_image, self.acute_rad_deg)
        screen_pos = camera.apply(pygame.Vector2(position))
        rect = rotated_image.get_rect(center=screen_pos)
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
        #self.draw(screen, self.size, (self.pos.x, self.pos.y), self.Targetpos)

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
            self.acute_rad = self.determinedir(self.Targetpos)
            for i in range(self.bulletsPershot):
                bullet1 = Bullet.bullet(20, "circsle", 500, Targetpos, position, damage)
                t = i /(self.bulletsPershot - 1) if self.bulletsPershot > 1 else 0.5
                self.acute_rad_offset = -(self.spread/2) + t * self.spread
                self.acute_rad = self.acute_rad + self.acute_rad_offset
                ThisTarget = pygame.Vector2(position[0] + math.cos(self.acute_rad) * 500, position[1] - math.sin(self.acute_rad) * 500)
                bullet1 = Bullet.bullet(20, "circle", 500, ThisTarget, position, damage)
                self.bulletList.append(bullet1)
                #print("Shot one")
        #def __init__(self, size, shape, speed, targetpos, position, damage):
class BallGun(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.ammo = 10
        self.capacity = 10
        self.fireRate = 0.5
        self.bulletsPershot = 1
        self.spread = math.radians(32)
        self.BulletType = "Bouncy"
    def shoot(self, position, Targetpos, damage):
        ChosenBullet = Bullet.WhichBullet[self.BulletType]
        if self.CanShoot(self.ammo, self.fireratetimer):
            bullet1 = ChosenBullet(8, "bouncy", 500, Targetpos, position, damage)
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            self.bulletList.append(bullet1)
class Dynamite(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.ammo = 3
        self.capacity = 3
        self.fireRate = 1
        self.bulletsPershot = 1
        self.BulletType = "Dynamite"
    def shoot(self, position, Targetpos, damage):
        ChosenBullet = Bullet.WhichBullet[self.BulletType]
        if self.CanShoot(self.ammo, self.fireratetimer):
            bullet1 = ChosenBullet(10, "bouncy", 500, Targetpos, position, damage)
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            self.bulletList.append(bullet1)
class Sniper(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.ammo = 1
        self.capacity = 1
        self.fireRate = 1
        self.bulletsPershot = 1
        self.BulletType = "Ray"
        self.Charging = False
        self.TheChargeRay = None
        self.ChargeDuration = 0
        self.MaxChargeTime = 3
    def CanShoot(self, ammo, Charging):
        if not self.Charging and self.ammo > 0 and not self.reloadpressed:
            return True
        return False
    def shoot(self, position, Targetpos, damage):
        if(self.ammo > 0):
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            ChargePercent = self.ChargeDuration / self.MaxChargeTime
            damage = 20 + (80 * ChargePercent)
            bullet1 = Bullet.bullet(20, "Rail", 2000, Targetpos, position, damage)
            self.bulletList.append(bullet1)
    def MakeChargeRay(self, WallList, screen):
        self.acute_rad_deg = math.degrees(self.acute_rad)
        dx = math.cos(self.acute_rad)
        dy = -math.sin(self.acute_rad)
        cur_x, cur_y = float(self.pos[0]), float(self.pos[1])
        while True:
            cur_x += dx * 2
            cur_y += dy * 2
            if cur_x < 0 or cur_x > screen.get_width() or cur_y < 0 or cur_y > screen.get_height():
                return (int(cur_x), int(cur_y))
            for wall in WallList:
                if wall.Rect.collidepoint(cur_x, cur_y):
                    return (int(cur_x), int(cur_y))
    def draw(self, screen, camera, size, position):
        self.acute_rad_deg = math.degrees(self.acute_rad)

        # Build the original, unrotated rectself.acute_rad once and cache it
        if not hasattr(self, "original_image"):
            self.original_image = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, "purple", (0, 0, size[0], size[1]))
        if(self.Charging and self.TheChargeRay != None):
                length = int(math.hypot(self.TheChargeRay[0] - self.pos[0], self.TheChargeRay[1] - self.pos[1]))
                ray_thickness = 4
                if length > 0:
                    ray_surface = pygame.Surface((length, ray_thickness), pygame.SRCALPHA)
                    pygame.draw.rect(ray_surface, "red", (0, 0, length, ray_thickness))

                    # pivot = the LEFT-MIDDLE edge of the ray surface — i.e. where the
                    # beam starts — not the surface's center
                    pivot_on_sprite = pygame.Vector2(0, ray_thickness / 2)
                    rotated_ray, ray_rect = rotate_around_pivot(
                        ray_surface, self.acute_rad_deg, pivot_on_sprite, self.pos
                    )
                    screen.blit(rotated_ray, ray_rect)       
        rotated_image = pygame.transform.rotate(self.original_image, self.acute_rad_deg)
        screen_pos = camera.apply(pygame.Vector2(position))
        rect = rotated_image.get_rect(center=screen_pos)
        screen.blit(rotated_image, rect)
        
    def update(self, dt, screen, keys, position, Targetpos):
        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)
        self.acute_rad = self.determinedir(self.Targetpos)
        self.fireratetimer -= dt
        if keys[pygame.K_r]:
            self.reloadpressed = True   
        # reload
        if(self.reloadpressed or self.ammo <= 0):
            self.reloadtimer -= dt
            if self.reloadtimer <= 0:
                self.ammo = self.reload(self.ammo, self.capacity)
        # start charging
        if(pygame.mouse.get_pressed()[0] and not self.EnemyOwner and self.CanShoot(self.ammo, self.Charging)):
            self.Charging = True
        # charging
        if(self.Charging):
            self.ChargeDuration += dt
            if(self.ChargeDuration >= self.MaxChargeTime):
                self.ChargeDuration = self.MaxChargeTime
        # release shot
        if(self.Charging and not pygame.mouse.get_pressed()[0]):
            damage = 20 + (40 * (self.ChargeDuration / self.MaxChargeTime))
            self.shoot(
                self.pos,
                self.Targetpos,
                damage
            )
            self.Charging = False
            self.ChargeDuration = 0

        # enemy behaviour stays the same
        if(self.EnemyOwner):
            if(self.CanShoot(self.ammo, self.fireratetimer)):
                self.shoot(self.pos, self.Targetpos, 20)

        #self.draw(screen, self.size, self.pos)
def rotate_around_pivot(image, angle_deg, pivot_on_sprite, pivot_on_screen):
        w, h = image.get_size()
        center = pygame.Vector2(w / 2, h / 2)
        offset = pivot_on_sprite - center
        rotated_offset = offset.rotate(-angle_deg)
        rotated_image = pygame.transform.rotate(image, angle_deg)
        new_center = pivot_on_screen - rotated_offset
        rect = rotated_image.get_rect(center=new_center)
        return rotated_image, rect
    
WhichGun = {cls.__name__: cls for cls in GunParent.__subclasses__()}
WhichGun["GunParent"] = GunParent
class ChargeGun(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.ChargeDuration = 0
        self.MaxChargeTime = 4
        self.Stage1Threshold = 1
        self.Stage3Threshold = 3
        self.Stage2Threshold = 2
        self.Stage4Threshold = 4
        self.Charging = False

    def StartCharge(self):
        self.ChargeDuration = 0
        self.Charging = True
    def shoot(self, position, Targetpos, damage):
        if(self.CanShoot(self.ammo, self.fireratetimer)):
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            bullet1 = Bullet.bullet(20, "circle", 500, Targetpos, position, damage)
            self.bulletList.append(bullet1)

    def draw(self, screen, camera, size, position):
        self.acute_rad_deg = math.degrees(self.acute_rad)

        if not hasattr(self, "original_image"):
            self.original_image = pygame.Surface(size, pygame.SRCALPHA)

        self.original_image.fill((0,0,0,0))

        if(self.Charging):
            if(self.ChargeDuration >= self.Stage4Threshold):
                colour = "purple" #replace this with different sprites when we charge it up soon
            elif(self.ChargeDuration >= self.Stage3Threshold):
                colour = "red"
            elif(self.ChargeDuration >= self.Stage2Threshold):
                colour = "orange"
            elif(self.ChargeDuration >= self.Stage1Threshold):
                colour = "yellow"
            else:
                colour = "grey"
        else:
            colour = "red"

        pygame.draw.rect(self.original_image, colour, (0,0,size[0],size[1]))

        rotated_image = pygame.transform.rotate(self.original_image, self.acute_rad_deg)
        screen_pos = camera.apply(pygame.Vector2(position))
        rect = rotated_image.get_rect(center=screen_pos)
        screen.blit(rotated_image, rect)

    def update(self, dt, screen, keys, position, Targetpos):
        self.Targetpos = pygame.Vector2(Targetpos)
        self.acute_rad = self.determinedir(self.Targetpos)
        self.fireratetimer -= dt
        if keys[pygame.K_r]:
            self.reloadpressed = True
        if(self.reloadpressed or self.ammo <= 0):
            self.reloadtimer -= dt
            if self.reloadtimer <= 0:
                self.ammo = self.reload(self.ammo, self.capacity)

        self.pos = pygame.Vector2(position)

        if(self.EnemyOwner):
            if(self.CanShoot(self.ammo, self.fireratetimer)):
                self.shoot(self.pos, self.Targetpos, 20)

        if(self.CanShoot(self.ammo, self.fireratetimer) and not self.EnemyOwner and pygame.mouse.get_pressed()[0] and not self.Charging):
            self.StartCharge()

        if(self.Charging):
            self.ChargeDuration += dt

            if(self.ChargeDuration > self.MaxChargeTime):
                self.ChargeDuration = self.MaxChargeTime

        if(self.Charging and not pygame.mouse.get_pressed()[0]):
            if(self.ChargeDuration >= self.Stage4Threshold):
                damage = 60
            elif(self.ChargeDuration >= self.Stage3Threshold):
                damage = 40
            elif(self.ChargeDuration >= self.Stage2Threshold):
                damage = 30
            elif(self.ChargeDuration >= self.Stage1Threshold):
                damage = 20
            else:
                damage = 10

            self.shoot(self.pos, self.Targetpos, damage)
            self.Charging = False
            self.ChargeDuration = 0

        #self.draw(screen, self.size, self.pos, self.Targetpos)