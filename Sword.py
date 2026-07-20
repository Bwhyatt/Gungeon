import pygame
import math
class RegularSword():
    def __init__(self, size,Name, Targetpos, position, Enemy):
        
        #gunName will be used later when i design other guns
        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)
        self.upY = 1 if self.Targetpos.y > self.pos.y else -1
        self.upX = 1 if self.Targetpos.x > self.pos.x else -1

        self.CoolDownDuration = 0.75
        self.CoolDownTimer = self.CoolDownDuration
        self.SwingDuration = 0.5 # will be dependent on animation
        self.SwingTimer = self.SwingDuration

        #Paryy stuff
        self.ParryDuration = 1
        self.ParryTimer = self.ParryDuration
        self.ParryCoolDownDuration = 0.75
        self.ParryCoolDownTimer = self.ParryCoolDownDuration
        self.ParryRect = None
        self.Parrying = False

        self.EnemyOwner = Enemy
        self.hitbox = None
        self.Swinging = False

        self.size = pygame.Vector2(size)
    def Swing(self,position, Targetpos, damage):
            self.Swinging = True
            self.hitbox = pygame.Rect(position[0], position [1], self.size[0], self.size[1])
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
        if(self.ParryRect.colliderect(obj2.Rect)):
            return True
        return False
    def ResolveParryCollision(self, obj2):
        if(obj2.tag == "Enemy"):
            obj2.SelfStun(4)
    def Collision(self, obj2):
        if(self.Rect.colliderect(obj2.Rect)):
            return True
        return False
    def ResolveCollision(self, obj2):
        if(obj2.tag == "Enemy"):
            obj2.TakeDamage(obj2.damage)#Parse enemy object itself not just the position
    def draw(self, screen, size, position, Targetpos):
        #pygame.draw.rect(screen, "red", (position[0],position[1], size[0], size[1]))
        angle_deg = math.degrees(self.acute_rad)

        # Build the original, unrotated rectangle once and cache it
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
    def update(self, dt, screen, keys, position, Targetpos):
        if(self.Swinging):
            self.SwingDuration += dt
            if(self.SwingDuration >= self.SwingTimer):
                self.SwingDuration = 0
                self.Swinging = False
                self.hitbox = None
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
        self.Targetpos = pygame.Vector2(Targetpos)#Need to make this player pos
        self.acute_rad = self.determinedir(self.Targetpos)
        #if they press it then the reload timer will be able to begin
        if(self.EnemyOwner):
            if(self.CanSwing(self.SwingTimer)):
                self.Swing(self.pos, self.Targetpos, 20)

        self.pos = pygame.Vector2(position)
        #make position player position
        if(self.CanSwing(self.CoolDownTimer) and not self.EnemyOwner and pygame.mouse.get_pressed()[0] and not self.Swinging and not self.Parrying):
            self.Swing(self.pos, Targetpos, 20)
        if(self.CanParry(self.ParryCoolDownTimer) and not self.EnemyOwner and pygame.mouse.get_pressed()[2] and not self.Swinging and not self.Parrying):
            #we will make it always show but only play animations later
            self.Parry(self.pos, Targetpos)
        if(self.Swinging or self.Parrying):
            self.draw(screen, self.size, self.pos, self.Targetpos) #self.ParryRect,