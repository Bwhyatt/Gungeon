import pygame
import math
class bullet:
    def __init__(self, size, shape, speed, targetpos, position, damage):
        self.size = size
        self.shape = shape
        self.speed = speed
        self.pos = pygame.Vector2(position)
        self.targetpos = targetpos
        self.damage = damage
        self.dircounter = 0
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.tag = "Bullet"
        self.lifetime = 0
        self.BannedDirections = []
    def determinedir(self, targetpos):
       #since the up is reversed and down for me on the screen is up which is the opposite on num plane so needs to be self 1 for rise
        
        #print("targetpos is " + str(targetpos))
        #print("self pos is " + str(self.pos))

        acute_rad = math.atan2((targetpos[1] - self.pos[1]), (targetpos[0] - self.pos[0]))

        #print("acutesef sjdfjse " + str(acute_rad))
        return acute_rad
    def move(self, speed, dt, angle):
        #remember plus both will go bottom right
        self.pos += pygame.Vector2(math.cos(angle) * speed * dt, math.sin(angle)* dt * speed)
    def draw(self, screen, camera):
        screen_pos = camera.apply(self.pos)
        pygame.draw.circle(screen, "white", screen_pos, self.size)
    def destroy(self):
        pass
    def update(self, dt, screen):
        self.BannedDirections = []
        if(self.lifetime > 7):
            self.destroy()
        if self.dircounter == 0:
            self.acute_rad = self.determinedir(self.targetpos)
            self.dircounter += 1
        self.move(self.speed, dt, self.acute_rad)        
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
    def Collision(self, obj2):
        if(self.Rect.colliderect(obj2.Rect)):
            return True
        return False
    def ResolveCollision(self, obj2):
        if(obj2.tag != "Wall" and obj2.tag != "Door"):
            obj2.TakeDamage(self.damage)
        self.destroy()

class Bouncy(bullet):
    def __init__(self, size, shape, speed, targetpos, position, damage):
        super().__init__(size, shape, speed, targetpos, position, damage)
    def ResolveCollision(self, obj2):
        if(obj2.tag != "Wall" and obj2.tag != "Door"):
            obj2.TakeDamage(self.damage)
            self.destroy()
        if(obj2.tag == "Door"):
            self.destroy()
        if(obj2.tag == "Wall"):
            obj2.WallCollision(self)
            if( 1 in self.BannedDirections or  3 in self.BannedDirections):
                self.acute_rad *= -1
            if(2 in self.BannedDirections  or 4 in self.BannedDirections ):
                self.acute_rad += math.pi
                self.acute_rad *= -1
class Dynamite(bullet):
    def __init__(self, size, shape, speed, targetpos, position, damage):
        super().__init__(size, shape, speed, targetpos, position, damage)   
        self.ExplosionTimer = 1
        self.launchTarget = targetpos
        self.TimerStarted = False
    def HasOverShot(self):
        if self.launchTarget == (0, 0):#(0,0) is a magic number and is just a placeholder position
            return False
        direction = pygame.Vector2(math.cos(self.acute_rad), math.sin(self.acute_rad))
        ToTarget = self.launchTarget - self.pos
        return ToTarget.dot(direction)
    def update(self, dt, screen):
        self.BannedDirections = []
        if(self.lifetime > 7):
            self.destroy()
        if self.dircounter == 0:
            self.acute_rad = self.determinedir(self.targetpos)
            self.dircounter += 1
        if  self.HasOverShot() > 0:
            self.move(self.speed, dt, self.acute_rad)
        else:
            self.TimerStarted = True
        if(self.TimerStarted):
            self.ExplosionTimer -= dt
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
    def Collision(self, obj2):
        if self.ExplosionTimer <= 0:
            self.ResolveCollision( obj2)
            return super().Collision(obj2)
class Rail(bullet):
    def __init__(self, size, shape, speed, targetpos, position, damage):
        super().__init__(size, shape, speed, targetpos, position, damage)
        

WhichBullet = {cls.__name__: cls for cls in bullet.__subclasses__()}
WhichBullet["bullet"] = bullet
#so basically we get cosx component to move on X axis and sinx component to move on y axis
#base class
#child class circle
#child class square