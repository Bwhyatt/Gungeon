import pygame
import math
import os
def rotate_around_pivot(image, angle_deg, pivot_on_sprite, pivot_on_screen):
    w, h = image.get_size()
    center = pygame.Vector2(w / 2, h / 2)
    offset = pivot_on_sprite - center
    rotated_offset = offset.rotate(-angle_deg)
    rotated_image = pygame.transform.rotate(image, angle_deg)
    new_center = pivot_on_screen - rotated_offset
    rect = rotated_image.get_rect(center=new_center)
    return rotated_image, rect


class RegularSword():
    def __init__(self, size,Name, Targetpos, position, Enemy):
        #gunName will be used later when i design other guns
        self.size = pygame.Vector2(size)

        sprite_path = f"SpriteSheets/Swords/{Name}.png"
        if os.path.exists(sprite_path):
            self.OriginalImage = pygame.image.load(sprite_path).convert_alpha()
            self.OriginalImage = pygame.transform.scale(self.OriginalImage, self.size)
        else:
            self.OriginalImage = self._make_placeholder_sprite()  # fallback until the png exists

        self.PivotOnSprite = pygame.Vector2(self.size.x * 0.15, self.size.y / 2)
        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)
        self.upY = 1 if self.Targetpos.y > self.pos.y else -1
        self.upX = 1 if self.Targetpos.x > self.pos.x else -1
        #rotation stuff
        self.Mask = None
        self.Image = None
        self.ImageRect = None

        self.CoolDownDuration = 0.75
        self.CoolDownTimer = self.CoolDownDuration
        self.SwingDuration = 0 # will be dependent on animation
        self.SwingTimer = self.SwingDuration

        #Paryy stuff
        self.ParryDuration = 0
        self.ParryTimer = 2
        self.ParryCoolDownDuration = 0.75
        self.ParryCoolDownTimer = self.ParryCoolDownDuration
        self.ParryRect = None
        self.Parrying = False

        self.EnemyOwner = Enemy
        self.Rect = None
        self.Swinging = False

        self.damage = 50
        
        self.size = pygame.Vector2(size)
        
        self.PivotOnSprite = pygame.Vector2(self.size.x * 0.15, self.size.y / 2)  # hand grip, near left edge of the sprite

        self.SwingStartAngle = -70   # degrees, wound-up, relative to aim direction
        self.SwingEndAngle = 40      # degrees, follow-through
        self.ParryStartAngle = -25   # degrees, parry sweep start
        self.ParryEndAngle = 25      # degrees, parry sweep end
        self.CurrentAngleOffset = self.SwingStartAngle
        self.tag = "Sword"
        if self.SwingTimer <= 0:
            self.SwingTimer = 0.25
    def _make_placeholder_sprite(self):
        surf = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, "red", (0, 0, self.size.x, self.size.y))
        return surf
    def _draw_rotated(self, screen, camera, position, angle_offset):
        angle_deg = math.degrees(self.acute_rad) + angle_offset
        screen_pos = pygame.Vector2(camera.apply(pygame.Vector2(position)))
        rotated_image, rect = rotate_around_pivot(
            self.OriginalImage, angle_deg, self.PivotOnSprite, screen_pos
        )
        screen.blit(rotated_image, rect)
    def Swing(self, position, Targetpos=None):
        self.Swinging = True
        self.SwingDuration = 0
        self.CurrentAngleOffset = self.SwingStartAngle#reset the angle for rotation
        if(Targetpos != None):
            self.Targetpos = pygame.Vector2(Targetpos)
        self.pos = pygame.Vector2(position)
        self.Image = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(self.Image, "red", (0,0,self.size[0],self.size[1]))
        self.Image = pygame.transform.rotate(self.Image, math.degrees(self.acute_rad))
        self.ImageRect = self.Image.get_rect(center=self.pos)
        self.Mask = pygame.mask.from_surface(self.Image)
    def Parry(self, position, Targetpos):
            self.Parrying = True
            self.ParryDuration = 0
            self.CurrentAngleOffset = self.ParryStartAngle
            self.ParryRect = pygame.Rect(position[0], position[1], self.size[0] * 2, self.size[1] * 2)
    def determinedir(self, Targetpos):
        acute_rad = math.atan2((self.pos.y - Targetpos.y ) , (Targetpos.x - self.pos.x))
        return acute_rad
    def CanSwing(self, timer):#checks if the firerate timer has gone off, not concerned with reload
        if timer <= 0:
            return True
        else:
            return False
    def CanParry(self, timer):
        if timer <= 0:
            return True
        else:
            return False
    def ParryCollision(self, obj2):
        if(obj2.ParryRect != None):
            if(self.ParryRect.colliderect(obj2.ParryRect)):
                return True
        return False
    def ResolveParryCollision(self, obj2):
        if(obj2.tag == "Enemy"):
            obj2.SelfStun(4)
    def Collision(self, obj2):
        if(self.Mask != None):
            offset = (
                obj2.Rect.x - self.ImageRect.x,
                obj2.Rect.y - self.ImageRect.y
            )

            if(self.Mask.overlap(pygame.mask.Mask((obj2.Rect.width,obj2.Rect.height)), offset)):
                return True

        return False
    def ResolveCollision(self, obj2, damage):
        if(obj2.tag == "Enemy"):
            obj2.TakeDamage(damage)#Parse enemy object itself not just the position
    def draw(self, screen, camera, size, position):
        #pygame.draw.rect(screen, "red", (position[0],position[1], size[0], size[1]))
        if self.Swinging or self.Parrying:
            self._draw_rotated(screen, camera, position, self.CurrentAngleOffset)
    def SwingStateChange(self, dt):
        if(self.Swinging):
            self.SwingDuration += dt
            progress = min(self.SwingDuration / self.SwingTimer, 1) if self.SwingTimer > 0 else 1
            self.CurrentAngleOffset = self.SwingStartAngle + (self.SwingEndAngle - self.SwingStartAngle) * progress
            if(self.SwingDuration >= self.SwingTimer):
                self.SwingDuration = 0
                self.Swinging = False
                self.Rect = None
                self.CoolDownTimer = self.CoolDownDuration
        else:
            self.CoolDownTimer -= dt
        if(self.Parrying):
            self.ParryDuration += dt
            if(self.ParryDuration >= self.ParryTimer):
                self.ParryDuration = 0
                self.ParryCoolDownTimer = self.ParryCoolDownDuration
                self.Parrying = False
                self.ParryRect = None
        else:
            self.ParryCoolDownTimer -= dt
    def update(self, dt, screen, keys, position, Targetpos):
        self.SwingStateChange(dt)
        self.Targetpos = pygame.Vector2(Targetpos)#Need to make this player pos
        self.acute_rad = self.determinedir(self.Targetpos)
        #if they press it then the reload timer will be able to begin
        if(self.EnemyOwner):
            if(self.CanSwing(self.SwingTimer)):
                self.Swing(self.pos, self.Targetpos)

        self.pos = pygame.Vector2(position)
        #make position player position
        if(self.CanSwing(self.CoolDownTimer) and not self.EnemyOwner and pygame.mouse.get_pressed()[0] and not self.Swinging and not self.Parrying):
            self.Swing(self.pos, self.Targetpos)
        if(self.CanParry(self.ParryCoolDownTimer) and not self.EnemyOwner and pygame.mouse.get_pressed()[2] and not self.Swinging and not self.Parrying):
            #we will make it always show but only play animations later
            self.Parry(self.pos, Targetpos)
        #self.ParryRect,
class VampireSword(RegularSword):
    def __init__(self, size,Name, Targetpos, position, Enemy):
        super().__init__( size,Name, Targetpos, position, Enemy)
        self.RegenAmount = 10 #regen 10 health
    def ResolveParryCollision(self, obj2):
        return super().ResolveParryCollision(obj2)
class BaseballBat(RegularSword):
    def __init__(self, size,Name, Targetpos, position, Enemy):
        super().__init__( size,Name, Targetpos, position, Enemy)
        self.ChargeDuration = 0
        self.MaxChargeTime = 6
        self.Charging = False
        #self.KnockBack = False
    def StartCharge(self):
        self.ChargeDuration = 0
        self.Charging = True
    def draw(self, screen, camera, size, position):
        if self.Charging:
            self._draw_rotated(screen, camera, position, self.SwingStartAngle)
        elif self.Swinging or self.Parrying:
            self._draw_rotated(screen, camera, position, self.CurrentAngleOffset)
        
    def update(self, dt, screen, keys, position, Targetpos):
        self.SwingStateChange(dt)
        if self.Charging:
            self.ChargeDuration += dt
        self.Targetpos = pygame.Vector2(Targetpos)#Need to make this player pos
        self.acute_rad = self.determinedir(self.Targetpos)
        #if they press it then the reload timer will be able to begin
        if(self.EnemyOwner):
            if(self.CanSwing(self.CoolDownTimer)):
                self.Swing(self.pos, self.Targetpos)
    
        self.pos = pygame.Vector2(position)
        #make position player position
        if (self.CanSwing(self.CoolDownTimer) and not self.EnemyOwner and pygame.mouse.get_pressed()[0] and not self.Swinging and not self.Parrying and not self.Charging):
            self.StartCharge()
        if(self.Charging and self.CanSwing(self.CoolDownTimer) and not self.EnemyOwner and not pygame.mouse.get_pressed()[0] and not self.Swinging and not self.Parrying):
            
            self.damage = round(20 * self.ChargeDuration/3) if self.ChargeDuration < self.MaxChargeTime else 40
            self.Swing(self.pos, self.Targetpos)
            self.ChargeDuration = 0
            self.Charging = False
        if(self.CanParry(self.ParryCoolDownTimer) and not self.EnemyOwner and pygame.mouse.get_pressed()[2] and not self.Swinging and not self.Parrying):
            #we will make it always show but only play animations later
            self.Parry(self.pos, self.Targetpos)
        #self.draw(screen, self.size, self.pos)
    def ResolveCollision(self, obj2, damage):
        if(obj2.tag == "Enemy"):
            KnockBackstrength = min(self.ChargeDuration / self.MaxChargeTime, 1)

            obj2.Knockback(
                self.pos,
                speed=10 + 22 * KnockBackstrength,
                duration=0.2 + 0.2 * KnockBackstrength,
                stunTime=0.15 + 0.35 * KnockBackstrength
            )

class ReturnToSender(RegularSword):
    def __init__(self, size, Name, Targetpos, position, Enemy):
        super().__init__(size, Name, Targetpos, position, Enemy)
        self.damage = 20
    def ResolveParryCollision(self, obj2):
        if obj2.tag == "Enemy":
            obj2.TakeDamage(obj2.damage * 2)
            obj2.SelfStun(1)
class ShielderSword(RegularSword):
    def __init__(self, size, Name, Targetpos, position, Enemy):
        super().__init__(size, Name, Targetpos, position, Enemy)
        self.successful_parries = 0
        self.damage = 15
    def ResolveParryCollision(self, obj2):
        if obj2.tag == "Enemy":
            self.successful_parries += 1
            obj2.SelfStun(2)
            if self.successful_parries >= 3:
                self.GiveShield(obj2)
                self.successful_parries = 0

    def GiveShield(self, obj2):
        if hasattr(obj2, "shield"):
            obj2.shield += obj2.max_health * 0.2
class HeavyHitter(RegularSword):
    def __init__(self, size, Name, Targetpos, position, Enemy):
        super().__init__(size, Name, Targetpos, position, Enemy)
        self.damage = 50
        self.CoolDownDuration = 1.5
        self.CoolDownTimer = self.CoolDownDuration
WhichSword = {cls.__name__: cls for cls in RegularSword.__subclasses__()}
WhichSword["RegularSword"] = RegularSword
        