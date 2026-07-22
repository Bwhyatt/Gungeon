import pygame
import math
import os
import Bullet
import SpriteSheetLoader
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
        self.fireRate = 1.3
        self.fireratetimer = 0 # timer to basically act as firerate checker
        self.EnemyOwner = Enemy # checks if this is the player's gun or the enemy's
        #reload variables
        self.reloadTime = 2
        self.reloadpressed = False
        self.reloadtimer = self.reloadTime
        self.damage = 20
        self.bulletList = []

        self.bulletsPershot = 1
        self.spread = 0

        shoot_animation_path = f"SpriteSheets/Guns/{gunName}Shoot.png"
        if os.path.exists(shoot_animation_path):
            self.animations = {
                "shoot": SpriteSheetLoader.LoadSpriteSheet(
                    shoot_animation_path,
                    32,
                    32
                )
            }
        else:
            self.animations = {}     
        self.current_animation =  None
        self.frame_index = 0
        self.animation_timer = 0
        self.frame_duration = 0.1

        self.image = pygame.image.load(
            f"SpriteSheets/Guns/{gunName}.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            self.size
        )
        #note to self: self spread will be self.acute_rad in radians that will determine the self.acute_rad of the sector
    def determinedir(self, Targetpos):
        direction = pygame.Vector2(Targetpos) - pygame.Vector2(self.pos)
        return math.atan2(-direction.y, direction.x)
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
    def UpdateAnimation(self, dt):
        if self.current_animation is None:
            return

        self.animation_timer += dt

        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.frame_index += 1

            if self.frame_index >= len(self.animations[self.current_animation]):
                self.current_animation = None
                self.frame_index = 0
    def shoot(self,position, Targetpos, damage):
        if self.CanShoot(self.ammo, self.fireratetimer):
            self.StartShootAnimation()
            #print("shooting")
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            bullet1 = Bullet.bullet(7, "circle", 500, Targetpos, position, damage)
            self.bulletList.append(bullet1)
            self.current_animation = "shoot"
            self.frame_index = 0
            self.animation_timer = 0
        else:
            #print("cant shoot")
            pass
    def draw(self, screen, camera, size, position):
        if self.current_animation:
            frames = self.animations.get(self.current_animation, [])

            # prevent index error
            if self.frame_index >= len(frames):
                self.current_animation = None
                self.frame_index = 0
                image = self.image
            else:
                image = frames[self.frame_index]
        else:
            image = self.image

        rotated_image = pygame.transform.rotate(image, self.angle)
        rect = rotated_image.get_rect(
            center=camera.apply(self.pos)
        )

        screen.blit(rotated_image, rect)
    def StartShootAnimation(self):
        if "shoot" not in self.animations:
            self.current_animation = None
            return

        self.current_animation = "shoot"
        self.frame_index = 0
        self.animation_timer = 0
    def update(self, dt, screen, keys, position, Targetpos):
        
        self.UpdateAnimation(dt)
        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)#Need to make this player pos
        self.acute_rad = self.determinedir(self.Targetpos)
        self.angle = math.degrees(self.acute_rad)
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

        #make position player position
        #self.draw(screen, self.size, (self.pos.x, self.pos.y), self.Targetpos)

class Shotgun(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.damage = 12
        self.ammo = 6
        self.capacity = 6
        self.fireRate = 1.2
        self.bulletsPershot = 6
        self.damage = 10
        self.spread = math.radians(32)
    def shoot(self, position, Targetpos, damage):
        self.StartShootAnimation()

        self.ammo -= 1
        self.fireratetimer = self.fireRate

        # Get the direction you are aiming once
        base_angle = self.determinedir(self.Targetpos)

        for i in range(self.bulletsPershot):
            if self.bulletsPershot > 1:
                t = i / (self.bulletsPershot - 1)
            else:
                t = 0.5

            # Offset from left side of spread to right side
            angle_offset = -(self.spread / 2) + (t * self.spread)

            # Final angle of this pellet
            shot_angle = base_angle + angle_offset

            # Convert angle into a world-space target position
            pellet_target = pygame.Vector2(
                position[0] + math.cos(shot_angle) * 500,
                position[1] - math.sin(shot_angle) * 500
            )

            bullet = Bullet.bullet(7, "circle", 500, pellet_target, position, self.damage )

            self.bulletList.append(bullet)
                #print("Shot one")
        #def __init__(self, size, shape, speed, targetpos, position, damage):
class BallGun(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.ammo = 10
        self.capacity = 10
        self.fireRate = 0.5
        self.bulletsPershot = 1
        self.BulletType = "Bouncy"
    def shoot(self, position, Targetpos, damage):
        ChosenBullet = Bullet.WhichBullet[self.BulletType]
        if self.CanShoot(self.ammo, self.fireratetimer):
            #Essentially identical to the regular pistol since 
            #the bullets are what actually bounces
            self.StartShootAnimation()
            bullet1 = ChosenBullet(8, "bouncy", 500, Targetpos, position, 100)#TBD
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
            self.StartShootAnimation()
            bullet1 = ChosenBullet(10, "bouncy", 500, Targetpos, position, damage)
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            self.bulletList.append(bullet1)
class Sniper(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.damage = 150
        self.ammo = 1
        self.capacity = 1
        self.fireRate = 1
        self.bulletsPershot = 1
        self.BulletType = "Ray"
        self.Charging = False
        self.TheChargeRay = None
        self.ChargeDuration = 0
        self.MaxChargeTime = 3
        self.animations = {

    "shoot": SpriteSheetLoader.LoadSpriteSheet(
        "SpriteSheets/Guns/SniperShoot.png",
        32,
        32
    )
}
    def CanShoot(self, ammo, Charging):
        if not self.Charging and self.ammo > 0 and not self.reloadpressed:
            return True
        return False
    def shoot(self, position, Targetpos, damage):
        self.StartShootAnimation()
        if(self.ammo > 0):
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            ChargePercent = self.ChargeDuration / self.MaxChargeTime
            damage = self.damage + (80 * ChargePercent)
            bullet1 = Bullet.bullet(20, "Rail", 2000, Targetpos, position, damage)
            self.bulletList.append(bullet1)
    def MakeChargeRay(self, WallList, screen):
        self.angle = math.degrees(self.acute_rad)
        dx = math.cos(self.acute_rad)
        dy = -math.sin(self.acute_rad)
        cur_x, cur_y = float(self.pos[0]), float(self.pos[1])
        #get current x and y position
        while True:
            #iterating until the created point hits something
            cur_x += dx * 2
            cur_y += dy * 2
            if cur_x < 0 or cur_x > screen.get_width() or cur_y < 0 or cur_y > screen.get_height():
                return (int(cur_x), int(cur_y))
            for wall in WallList:
                if wall.Rect.collidepoint(cur_x, cur_y):
                    return (int(cur_x), int(cur_y))
        #The return value is a Vector 2 which will then act as the end of the ray
    def draw(self, screen, camera, size, position):
        self.angle = math.degrees(self.acute_rad)

        # Build the original, unrotated rectself.acute_rad once and cache it
        if not hasattr(self, "original_image"):
            self.original_image = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, "purple", (0, 0, size[0], size[1]))
        if(self.Charging and self.TheChargeRay != None):
                length = int(math.hypot(self.TheChargeRay[0] - self.pos[0], self.TheChargeRay[1] - self.pos[1]))
                #self.ChargeRay acts as the end of the ray
                ray_thickness = 4
                if length > 0:
                    ray_surface = pygame.Surface((length, ray_thickness), pygame.SRCALPHA)
                    pygame.draw.rect(ray_surface, "red", (0, 0, length, ray_thickness))

                    # pivot = the left middle edge of the ray surface i.e. where the
                    # beam starts, not the surface's center
                    pivot_on_sprite = pygame.Vector2(0, ray_thickness / 2)
                    screen_pos = camera.apply(self.pos)

                    rotated_ray, ray_rect = rotate_around_pivot(ray_surface, self.angle, pivot_on_sprite, screen_pos)

                    screen.blit(rotated_ray, ray_rect)
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        screen_pos = camera.apply(pygame.Vector2(position))
        rect = rotated_image.get_rect(center=screen_pos)
        screen.blit(rotated_image, rect)
        
    def update(self, dt, screen, keys, position, Targetpos):
        self.UpdateAnimation(dt)
        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)
        self.acute_rad = self.determinedir(self.Targetpos)
        self.angle = math.degrees(self.acute_rad)
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
    
class ChargeGun(GunParent):
    def __init__(self, size, GunName, Targetpos, position, Enemy):
        super().__init__(size, GunName, Targetpos, position, Enemy)
        self.ChargeDuration = 0
        self.MaxChargeTime = 4
        self.Stage1Threshold = 1
        self.Stage3Threshold = 3
        self.Stage2Threshold = 2
        self.Stage4Threshold = 4
        #After a certain amount of time charging the gun up,
        #  the duration will be long enough to reach the new thresholds
        self.Charging = False
        self.charge_images = SpriteSheetLoader.LoadSpriteSheet("SpriteSheets/Guns/ChargeGunCharge.png",16,16)

        print("CHARGE FRAMES:", len(self.charge_images))
        self.charge_frame = 0
        self.animations = {
        
        "shoot": SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/Guns/ChargeGunShoot.png",
            16,
            16
        )
    }
    def StartCharge(self):
        self.ChargeDuration = 0
        self.Charging = True
        self.charge_frame = 0
        self.frame_index = 0
    def shoot(self, position, Targetpos, damage):
        if self.CanShoot(self.ammo, self.fireratetimer):
            self.StartShootAnimation()
            self.ammo -= 1
            self.fireratetimer = self.fireRate
            bullet1 = Bullet.bullet(20, "circle", 500, Targetpos, position, damage)
            self.bulletList.append(bullet1)
            # start shoot animation
            self.current_animation = "shoot"
            self.frame_index = 0
            self.animation_timer = 0
    def draw(self, screen, camera, size, position):

            self.angle = math.degrees(self.acute_rad)

            if self.Charging:
                if self.charge_frame >= len(self.charge_images):
                    self.charge_frame = len(self.charge_images) - 1

                image = self.charge_images[self.charge_frame]

            elif self.current_animation:
                image = self.animations[self.current_animation][self.frame_index]

            else:
                return   # don't draw anything


            rotated_image = pygame.transform.rotate(
                image,
                self.angle
            )

            screen_pos = camera.apply(pygame.Vector2(position))

            rect = rotated_image.get_rect(
                center=screen_pos
            )

            screen.blit(rotated_image, rect)
    def update(self, dt, screen, keys, position, Targetpos):
        self.UpdateAnimation(dt)
        self.Targetpos = pygame.Vector2(Targetpos)
        self.acute_rad = self.determinedir(self.Targetpos)
        self.angle = math.degrees(self.acute_rad)
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
        if(self.Charging and pygame.mouse.get_pressed()[0]):
            if(self.ChargeDuration >= self.Stage4Threshold):
                self.charge_frame = 3
            elif(self.ChargeDuration >= self.Stage3Threshold):
                self.charge_frame = 2
            elif(self.ChargeDuration >= self.Stage2Threshold):
                self.charge_frame = 1
            else:
                self.charge_frame = 0
        if(self.Charging and not pygame.mouse.get_pressed()[0]):
            if(self.ChargeDuration >= self.Stage4Threshold):
                damage = 150
            elif(self.ChargeDuration >= self.Stage3Threshold):
                damage = 90
            elif(self.ChargeDuration >= self.Stage2Threshold):
                damage = 70
            elif(self.ChargeDuration >= self.Stage1Threshold):
                damage = 50
            else:
                damage = 10

            self.shoot(self.pos, self.Targetpos, damage)
            self.Charging = False
            self.ChargeDuration = 0

        #self.draw(screen, self.size, self.pos, self.Targetpos)

WhichGun = {cls.__name__: cls for cls in GunParent.__subclasses__()}
WhichGun["GunParent"] = GunParent
GunSizes = {
    "GunParent": (50, 20),
    "Shotgun": (50, 20),
    "BallGun": (16, 16),
    "Dynamite": (50, 20),
    "Sniper": (50, 20),
    "ChargeGun": (16, 16),
}