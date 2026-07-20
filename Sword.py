import pygame
import math
class RegularSword():
    def __init__(self, size,Name, Targetpos, position, Enemy):
        
        #gunName will be used later when i design other guns
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

        self.damage = 20
        
        self.size = pygame.Vector2(size)
    def Swing(self, position, Targetpos=None):
        self.Swinging = True
        
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
            self.ParryRect = pygame.Rect(position[0], position [1], self.size[0] * 2, self.size[1] * 2)
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
    def draw(self, screen, size, position, Targetpos):
        #pygame.draw.rect(screen, "red", (position[0],position[1], size[0], size[1]))
        angle_deg = math.degrees(self.acute_rad)

        if not hasattr(self, "original_image"):
            self.original_image = pygame.Surface(size, pygame.SRCALPHA)
        self.original_image.fill((0,0,0,0))
        if(self.Swinging):
            pygame.draw.rect(self.original_image, "red", (0, 0, size[0], size[1]))
        if(self.Parrying):
            pygame.draw.rect(self.original_image, "blue", (0, 0, size[0], size[1]))
        rotated_image = pygame.transform.rotate(self.original_image, angle_deg)
        rect = rotated_image.get_rect(center=position)
        screen.blit(rotated_image, rect)
    def SwingStateChange(self, dt):
        if(self.Swinging):
            self.SwingDuration += dt
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
        if(self.Swinging or self.Parrying):
            self.draw(screen, self.size, self.pos, self.Targetpos) #self.ParryRect,
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
    def draw(self, screen, size, position):
        #pygame.draw.rect(screen, "red", (position[0],position[1], size[0], size[1]))
        angle_deg = math.degrees(self.acute_rad)

        if not hasattr(self, "original_image"):
            self.original_image = pygame.Surface(size, pygame.SRCALPHA)
        self.original_image.fill((0,0,0,0))
        if self.Charging:
                pygame.draw.rect(self.original_image, "orange", (0, 0, size[0], size[1]))

        elif self.Swinging:
            pygame.draw.rect(self.original_image, "red", (0, 0, size[0], size[1]))

        elif self.Parrying:
            pygame.draw.rect(self.original_image, "blue", (0, 0, size[0], size[1]))        
        rotated_image = pygame.transform.rotate(self.original_image, angle_deg)
        rect = rotated_image.get_rect(center=position)
        screen.blit(rotated_image, rect)
        
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
        self.draw(screen, self.size, self.pos)
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
        