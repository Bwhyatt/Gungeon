import pygame
import Gun
import Sword
import math
import Wall
class BaseEnemy:#Use generalisation to make a bunch of different enemies that are the same but with a different gun
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        #with the which gun do the same as what happened in player class
        self.health = health
        self.speed = speed
        self.pos = pygame.Vector2(position)
        self.size = pygame.Vector2(size)
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        self.stunned = False
        self.stunTime = 0
        self.bulletList = []
        self.UsesGun = True if WhichGun != "None" else False
        self.UsesSword = True if WhichSword != "None" else False
        if(self.UsesGun):
            ChosenGun = Gun.WhichGun[WhichGun]
            self.gun = ChosenGun((50, 20), WhichGun, pygame.mouse.get_pos(), self.pos, True)
        if(self.UsesSword):
            ChosenSword = Sword.WhichSword[WhichSword]
            self.Sword = ChosenSword((100, 100), WhichSword, pygame.mouse.get_pos(), self.pos, True)
        self.CanMove = True
        self.AttackCoolDown = 5
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 2
        self.ParryRect = None
        self.tag = "Enemy"
        self.Parryable = False
        self.dir = pygame.Vector2(0, 0)
        self.BannedDirections = []
        self.KnockedBack = False
        self.KnockbackTimer = 0
        self.KnockbackDuration = 0
        self.KnockbackDirection = pygame.Vector2(0, 0)
        self.KnockbackSpeed = 0
        self.damage = 20
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
    def Knockback(self, HitterPos, speed, duration, stunTime=0):
        direction = self.pos - pygame.Vector2(HitterPos)

        self.KnockedBack = True
        self.KnockbackDirection = direction
        self.KnockbackSpeed = speed
        self.KnockbackDuration = duration
        self.KnockbackTimer = duration

        self.SelfStun(stunTime)
    def Die(self):
        pass
    def CanAttacK(self, player_pos):
        pass #This will check if there is nothin obstructing the enemy like a wall, if it is out of range or if the attack is on cooldown for melee attacks
    def draw(self, screen, camera):
        pygame.draw.rect(screen,"red",camera.apply(self.Rect))
    def DetermineAction(self, dt, player_pos, ):
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
            
    def update(self, dt, player_pos, playerbulletlist, screen):
        

        self.AttackDuration -= dt
        self.AttackCoolDownTimer -= dt
        for i in range(len(playerbulletlist)):
            if(self.Collision(playerbulletlist[i])):
                self.ResolveCollision(playerbulletlist[i])
         #make sure this happens after all the bullets update   
        if self.health <= 0:
            self.Die()
        if(self.stunned):
            self.stunTime -= dt
            if(self.stunTime <= 0):
                self.stunned = False
        if self.KnockedBack:
            self.pos += self.KnockbackDirection * self.KnockbackSpeed * dt
            self.KnockbackTimer -= dt
            if self.KnockbackTimer <= 0:
                self.KnockedBack = False    
        if(not self.stunned and not self.KnockedBack):
            self.DetermineAction(dt, player_pos)
        #run other functions
        if(self.UsesGun):
            self.bulletList = [bullet for bullet in self.gun.bulletList]
        self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
        
        

class Bowler(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        super().__init__(health,speed, position, size, WhichGun, WhichSword)
        self.pos = position
        self.AttackDuration = 2
        self.IsAttacking = False
        self.LaunchSpeed = 600
        self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        self.launchTarget = (0,0)
        self.Parryable = True
    def determinedir(self, Targetpos):
        angle = math.atan2(Targetpos.y - self.pos.y, Targetpos.x - self.pos.x)
        return angle
        #self.pos += pygame.Vector2(math.cos(angle) * LaunchSpeed * dt, math.sin(angle)* dt * LaunchSpeed)
    def Attack(self, player_pos):
        print("attacking")
        self.IsAttacking = True
        self.CanMove = False
        self.AttackDuration = 2
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.angle = self.determinedir(player_pos)
        self.angleTargetPos = pygame.Vector2(player_pos)
        self.launchTarget = pygame.Vector2(player_pos)
    def HasOverShot(self):
        if self.launchTarget == (0, 0):#(0,0) is a magic number and is just a placeholder position
            return False
        direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))
        ToTarget = self.launchTarget - self.pos
        return ToTarget.dot(direction) < 0 # dot product will be negative if 
    def ResolveCollision(self, obj2):
        if(obj2.tag != "Wall" and obj2.tag != "Door"):
            obj2.TakeDamage(self.damage)
            self.destroy()
        if(obj2.tag == "Door"):
            self.destroy()
        if(obj2.tag == "Wall"):
            obj2.WallCollision(self)
            if( 1 in self.BannedDirections or  3 in self.BannedDirections):
                self.angle *= -1
            if(2 in self.BannedDirections  or 4 in self.BannedDirections ):
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown
    def DetermineAction(self, dt, player_pos):
        self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        if(not self.stunned):
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
            if(self.CanMove and not self.IsAttacking and self.AttackDuration <= 0 and self.AttackCoolDownTimer <= 0):
                self.angle = self.determinedir(player_pos)
                self.angleTargetPos = pygame.Vector2(player_pos)
                self.Attack(player_pos)
            elif(not self.CanMove and self.IsAttacking):#NEED SOMETHING TO END ATTACK
                self.pos += pygame.Vector2(math.cos(self.angle) * self.LaunchSpeed * dt, math.sin(self.angle)* dt * self.LaunchSpeed)
                if self.HasOverShot() or self.AttackDuration <= 0:
                    self.IsAttacking = False
                    self.CanMove = True
                    self.AttackCoolDownTimer = self.AttackCoolDown
class Sheller(Bowler):
    def __init__(self, health,speed, position, size, WhichGun, WhichSword):
        super().__init__(health,speed, position, size, WhichGun, WhichSword)
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
        if(self.IsAttacking):
            self.Parryable = True
            self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        else:
            self.Parryable = False
            self.ParryRect = None
        if(not self.stunned):
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
            if(self.CanMove and not self.IsAttacking and self.AttackDuration <= 0 and self.AttackCoolDownTimer <= 0):
                self.Attack(player_pos)
            elif(not self.CanMove and self.IsAttacking):
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
class PinBaller(Bowler):
    def __init__(self, health,speed, position, size, WhichGun, WhichSword):
        super().__init__(health,speed, position, size, WhichGun, WhichSword)
        self.OverShootLimit = 2
        self.OverShootCount = 0
        self.pos = position
        self.AttackDuration = 4
        self.IsAttacking = False
        self.LaunchSpeed = 200
        self.ParryRect = None
        self.launchTarget = (0,0)
        self.BufferTimeLen = 0.5
        self.BufferTime = self.BufferTimeLen
        self.enablebuffertime = False
    def ResolveCollision(self, obj2):
        if(obj2.tag != "Wall" and obj2.tag != "Door"):
            obj2.TakeDamage(self.damage)
            self.destroy()
        if(obj2.tag == "Door"):
            self.destroy()
        if(obj2.tag == "Wall"):
            obj2.WallCollision(self)
            if(self.IsAttacking):
                if( 1 in self.BannedDirections or  3 in self.BannedDirections):
                    self.angle *= -1
                if(2 in self.BannedDirections  or 4 in self.BannedDirections ):
                    self.angle += math.pi
                    self.angle *= -1
    def DetermineAction(self, dt, player_pos):
        self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        if(not self.stunned):
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
            if(self.CanMove and not self.IsAttacking and self.AttackDuration <= 0 and self.AttackCoolDownTimer <= 0):
                self.angle = self.determinedir(player_pos)
                self.angleTargetPos = pygame.Vector2(player_pos)
                self.Attack(player_pos)
            elif(not self.CanMove and self.IsAttacking):#NEED SOMETHING TO END ATTACK
                self.pos += pygame.Vector2(math.cos(self.angle) * self.LaunchSpeed * dt, math.sin(self.angle)* dt * self.LaunchSpeed)
                if self.AttackDuration <= 0:
                    self.IsAttacking = False
                    self.CanMove = True
                    self.AttackCoolDownTimer = self.AttackCoolDown
class Shielder(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        super().__init__(health, speed, position, size, WhichGun, WhichSword)
        #shield stuff
        self.ShieldDirection = pygame.Vector2(0,0)
        self.ShieldActive = True
        self.ShieldBroken = False
        #sword stuff
        #attack stuff
        self.AttackCoolDown = 3
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 1
        self.IsAttacking = False
        self.damage = 40
        self.Parryable = True

    def FacePlayer(self, player_pos):
        self.ShieldDirection = pygame.Vector2(player_pos) - self.pos
        if(self.ShieldDirection.length() > 0):
            self.ShieldDirection = self.ShieldDirection.normalize()

    def TakeDirectionalDamage(self, damage, hitPosition):
        if(self.ShieldActive and not self.ShieldBroken):
            HitDirection = pygame.Vector2(hitPosition) - self.pos
            if(HitDirection.length() > 0):
                HitDirection = HitDirection.normalize()
            if(HitDirection.dot(self.ShieldDirection) > 0.5):
                print("Blocked by shield")
                return
        self.health -= damage

    def SelfStun(self, time):
        super().SelfStun(time)
        self.ShieldBroken = True

    def Attack(self, player_pos):
        self.IsAttacking = True
        self.CanMove = False
        self.AttackDuration = 1
        if(self.Sword != None):
            self.Sword.Swing(self.pos)

    def DetermineAction(self, dt, player_pos):
        self.FacePlayer(player_pos)
        if(self.CanMove):
            self.Move(dt, player_pos, self.speed)
        if(self.CanMove and not self.IsAttacking and self.AttackDuration <= 0 and self.AttackCoolDownTimer <= 0):
            self.Attack(player_pos)
        elif(not self.CanMove and self.IsAttacking):
            if(self.Sword != None):
                pass
            if(self.AttackDuration <= 0):
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown

    def update(self, dt, player_pos, playerbulletlist, screen):
        super().update(dt, player_pos, playerbulletlist, screen)
        
        if(self.Sword != None):
            self.Sword.update(dt, screen, None, self.pos, player_pos)
        if(not self.stunned):
            self.ShieldBroken = False
class Slime(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        super().__init__(health, speed, position, size, WhichGun, WhichSword)
        self.damage = 20
        self.AttackCoolDown = 1
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 0
        self.tag = "Enemy"

    def DetermineAction(self, dt, player_pos):
        if(not self.stunned):
            self.Move(dt, player_pos, self.speed)

    def ResolveCollision(self, obj2):
        if(obj2.tag == "Bullet"):
            self.TakeDamage(obj2.damage)

    def Die(self):
        print("Slime died")