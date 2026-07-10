import pygame
import Bullet
import math

class BaseEnemy:
    def __init__(self, health, speed, position, size):
        self.health = health
        self.speed = speed
        self.pos = pygame.Vector2(position)
        self.size = pygame.Vector2(size)
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        self.stunned = False
        self.stunTime = 0
        self.bulletList = []
        
    def Collision(self, obj2):#iterate through each of the player's bullets
        if(self.Rect.colliderect(obj2.Rect)):
            print("YES COLLIDE")
            return True
        return False
    def ResolveCollision(self, obj2):
        #even though the only things to collide with are bullets and walls, 
        #this makes it modular and is better practice
        if(obj2.tag == "Bullet"):
            self.TakeDamage(obj2.damage)
    def SelfStun(self, dt, time):
        self.stunTime = time
        self.stunned = True
    def Attack(self, dt, player_pos, selfpos):
        Bullet1 = Bullet.bullet(20, "circle", 500, player_pos, selfpos,20)
        self.bulletList.append(Bullet1)
        #for now it will just shoot a bullet at the player before the abstraction happens
    def Move(self, dt, player_pos, speed):
        angle = math.atan2(player_pos[1] - self.pos[1],player_pos[0] - self.pos[0])
        self.pos += pygame.Vector2(math.cos(angle) * speed * dt, math.sin(angle)* dt * speed)

    def TakeDamage(self, damage):
        print("I took damage")
        self.health -= damage
    def Die(self):
        pass
    def WallCollision(self, wall):
        return False#is a bool
    #TBD
    def WallResolveCollision(self, wall):
        pass
    def draw(self, screen):
        pygame.draw.rect(screen, "red", self.Rect)
    def update(self, dt, player_pos, playerbulletlist, screen):
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
        else:
            self.Move(dt, player_pos, self.speed)
            self.Attack(dt, player_pos, self.pos)
            pass#run other functions
        self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
        self.draw(screen)
        pass

class Phonk(BaseEnemy):
    def __init__(self, health, speed, position, size):
        self.health = super().__init__(health)
        self.speed = super().__init__(speed)
        self.position = super().__init__(position)
        self.size = super().__init__(size)
