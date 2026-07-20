import pygame
import Gun
import math
import Wall
class BaseEnemy:#Use generalisation to make a bunch of different enemies that are the same but with a different gun
    def __init__(self, health, speed, position, size, WhichGun):
        #with the which gun do the same as what happened in player class
        self.health = health
        self.speed = speed
        self.pos = pygame.Vector2(position)
        self.size = pygame.Vector2(size)
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        self.stunned = False
        self.stunTime = 0
        self.bulletList = []
        self.gun = Gun.GunParent((50, 20), "None", pygame.mouse.get_pos(), self.pos, True)
        self.CanMove = True
        self.AttackCoolDown = 5
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 2
        self.ParryRect = None
        self.tag = "Enemy"
        self.Parryable = False
        self.dir = pygame.Vector2(0, 0)
        self.BannedDirections = []
    def Collision(self, obj2):#iterate through each of the player's bullets
        if(self.Rect.colliderect(obj2.Rect)):
            return True
        return False
    def ResolveCollision(self, obj2):
        #even though the only things to collide with are bullets and walls, 
        #this makes it modular and is better practice
        if(obj2.tag == "Bullet"):
            self.TakeDamage(obj2.damage)
    def SelfStun(self, time):
        print("Stunned")
        self.stunTime = time
        self.stunned = True
    def Attack(self, dt, player_pos, selfpos):
        
        pass
    def Move(self, dt, player_pos, speed):
        angle = math.atan2(player_pos[1] - self.pos[1],player_pos[0] - self.pos[0])
        Xamt = math.cos(angle) * speed * dt
        Yamt =  math.sin(angle)* dt * speed
        self.dir[0]  = 1 if math.cos(angle) >= 0 else -1
        self.dir[1] = 1 if math.sin(angle) >= 0 else -1
        if(self.dir[0] == 1 and 2 in self.BannedDirections) or (self.dir[0] == - 1 and 4 in self.BannedDirections):
            Xamt = 0
        if(self.dir[0] == 1 and 1 in self.BannedDirections) or (self.dir[1] == - 1 and 3 in self.BannedDirections):
            Yamt = 0
        self.pos += pygame.Vector2( Xamt, Yamt)
    def TakeDamage(self, damage):
        print("I took damage")
        self.health -= damage
    def Die(self):
        pass
    def CanAttacK(self, player_pos):
        pass #This will check if there is nothin obstructing the enemy like a wall, if it is out of range or if the attack is on cooldown for melee attacks
    def draw(self, screen):
        pygame.draw.rect(screen, "red", self.Rect)
        if self.ParryRect != None:
            pygame.draw.rect(screen, "blue", self.ParryRect)
    def DetermineAction(self, dt, player_pos, ):
        if(self.stunned):
            self.stunTime -= dt
            if(self.stunTime <= 0):
                self.stunned = False
        else:
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
            
    def update(self, dt, player_pos, playerbulletlist, screen):
        

        self.AttackDuration -= dt
        for i in range(len(playerbulletlist)):
            if(self.Collision(playerbulletlist[i])):
                self.ResolveCollision(playerbulletlist[i])
         #make sure this happens after all the bullets update   
        if self.health <= 0:
            self.Die()
        self.DetermineAction(dt, player_pos)
        #run other functions
        self.bulletList = [bullet for bullet in self.gun.bulletList]
        self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
        
        

class Bowler(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun):
        super().__init__(health,speed, position, size, WhichGun)
        self.pos = position
        self.AttackDuration = 2
        self.IsAttacking = False
        self.LaunchSpeed = 600
        self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        self.launchTarget = (0,0)
        self.Parryable = True
    def determinedir(self, Targetpos):
        acute_rad = math.atan2(Targetpos.y - self.pos.y, Targetpos.x - self.pos.x)
        return acute_rad
        #self.pos += pygame.Vector2(math.cos(angle) * LaunchSpeed * dt, math.sin(angle)* dt * LaunchSpeed)
    def Attack(self, player_pos):
        self.IsAttacking = True
        self.CanMove = False
        self.AttackDuration = 2
        self.angle = self.determinedir(player_pos)
        self.angleTargetPos = pygame.Vector2(player_pos)
        self.launchTarget = pygame.Vector2(self.angleTargetPos) if hasattr(self, "angleTargetPos") else None
    def HasOverShot(self):
        if self.launchTarget == (0, 0):#(0,0) is a magic number and is just a placeholder position
            return False
        direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))
        ToTarget = self.launchTarget - self.pos
        return ToTarget.dot(direction) < 0 # dot product will be negative if 
    def DetermineAction(self, dt, player_pos):
        self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        if(self.stunned):
            self.stunTime -= dt
            if(self.stunTime <= 0):
                self.stunned = False
        else:
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
            if(self.CanMove and not self.IsAttacking and self.AttackDuration <= 0):
                self.angle = self.determinedir(player_pos)
                self.angleTargetPos = pygame.Vector2(player_pos)
                self.Attack(player_pos)
            elif(not self.CanMove and self.IsAttacking):#NEED SOMETHING TO END ATTACK
                self.pos += pygame.Vector2(math.cos(self.angle) * self.LaunchSpeed * dt, math.sin(self.angle)* dt * self.LaunchSpeed)
                if self.HasOverShot() or self.AttackDuration <= 0:
                    self.IsAttacking = False
                    self.CanMove = True
                    self.AttackCoolDownTimer = self.AttackCoolDown
class PinBaller(Bowler):
    def __init__(self, health,speed, position, size, WhichGun):
        super().__init__(health,speed, position, size, WhichGun)
        self.OverShootLimit = 2
        self.OverShootCount = 0
        self.pos = position
        self.AttackDuration = 2
        self.IsAttacking = False
        self.LaunchSpeed = 300
        self.ParryRect = None
        self.launchTarget = (0,0)
        self.BufferTimeLen = 0.5
        self.BufferTime = self.BufferTimeLen
        self.enablebuffertime = False
    def DetermineAction(self, dt, player_pos):
        if(self.enablebuffertime):
            self.BufferTime -= dt #after it has overshot this delays it running again
        #print(self.AttackDuration)
        self.AttackCoolDownTimer -= dt
        if(self.IsAttacking):
            self.Parryable = True
            self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        else:
            self.Parryable = False
            self.ParryRect = None
        if(self.stunned):
            self.stunTime -= dt
            if(self.stunTime <= 0):
                self.stunned = False
        else:
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
            if(self.CanMove and not self.IsAttacking and self.AttackCoolDownTimer <= 0):
                self.Attack(player_pos)
            elif(not self.CanMove and self.IsAttacking):#NEED SOMETHING TO END ATTACK
                self.pos += pygame.Vector2(math.cos(self.angle) * self.LaunchSpeed * dt, math.sin(self.angle)* dt * self.LaunchSpeed)
                if self.HasOverShot() and self.AttackDuration > 0 and self.OverShootCount < self.OverShootLimit:
                    self.enablebuffertime = True
                    if(self.BufferTime <= 0):
                        self.Attack(player_pos)
                        self.OverShootCount +=1
                        self.AttackDuration += self.BufferTimeLen
                        self.BufferTime = self.BufferTimeLen
                if self.AttackDuration <= 0:#Or collides with wall
                    self.IsAttacking = False
                    self.CanMove = True
                    self.AttackCoolDownTimer = self.AttackCoolDown
                    self.OverShootCount = 0
                    self.BufferTime = self.BufferTimeLen
