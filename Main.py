import pygame
import Player
import Bullet
import Wall
import Enemy
import Room
import Camera
pygame.init()
Width = 1280
Height = 720
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
EnemyClassmap = {cls.__name__: cls for cls in Enemy.BaseEnemy.__subclasses__()}
EnemyClassmap["BaseEnemy"] = Enemy.BaseEnemy
running = True
dt = 0
Enemies = []
EnemyBullets = []
myEnemy = Enemy.BaseEnemy(100, 50, (500, 500), (30, 30), "GunParent", "None")
Enemy2 = Enemy.Shielder(100, 50, (200, 500), (30, 30), "GunParent", "RegularSword")
Enemies.append(myEnemy)
Enemies.append(Enemy2)
WallList = []
#this will eventually be dependent on the room and it will just give us the list of enemies so it's fine to just hard code them for now
Theplayer = Player.Realplayer(300, (32, 32), (100,100), 100,"Sniper", "BaseballBat")
CurrentRoom = Room.TheRoom("TileRooms/1.tmx", EnemyClassmap)
camera = Camera.Camera(Width, Height)
while running:
    CurrentRoom.EnemyList = Enemies# TBD REPLACE LATER
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #enemy bullets = each bullet in the bullet list of each enemy in the enemy list
    
    EnemyBullets = []
    for i in range(len(Enemies)):
        for j in range(len(Enemies[i].bulletList)):
                EnemyBullets.append(Enemies[i].bulletList[j]) 
                
    screen.fill("purple")
    Theplayer.update(screen, pygame.key.get_pressed(), dt, pygame.mouse.get_pos())
    camera.update(Theplayer)
    
    
    Theplayer.gun.update(dt, screen, pygame.key.get_pressed(), Theplayer.pos, pygame.mouse.get_pos()) 
    if(Theplayer.GivenGun == "RailGun"):
         if(Theplayer.gun.Charging):
              Theplayer.gun.TheChargeRay = Theplayer.gun.MakeChargeRay(WallList, screen)
         else:
              Theplayer.gun.TheChargeRay = None
    Theplayer.Sword.update(dt, screen, pygame.key.get_pressed(), Theplayer.pos, pygame.mouse.get_pos())

    print(CurrentRoom.WallList)
    WallList = CurrentRoom.WallList


    for i in range(len(WallList)):
         WallList[i].WallCollision(Theplayer)

    for i in range(len(Enemies)):
        Enemies[i].update(dt, Theplayer.pos, Theplayer.gun.bulletList, screen)
        for j in range(len(WallList)):
            WallList[j].WallCollision(Enemies[i])
            if(Enemies[i].Collision(WallList[j])):
                Enemies[i].ResolveCollision(WallList[j])
        if Enemies[i].UsesGun:
             Enemies[i].gun.update(dt, screen, pygame.key.get_pressed(), Enemies[i].pos, Theplayer.pos)
        if(Enemies[i].UsesSword):
             Enemies[i].Sword.update(dt, screen, pygame.key.get_pressed(), myEnemy.pos, Theplayer.pos)
             if(Enemies[i].Sword.Collision(Theplayer)):
                 Enemies[i].Sword.ResolveCollision(Theplayer,Enemies[i].Sword.damage)
        if(Theplayer.Sword.Swinging):
             if(Theplayer.Sword.Collision(Enemies[i])):
                  Theplayer.Sword.ResolveCollision(Enemies[i], Theplayer.Sword.damage)
        if(Enemies[i].Parryable and Theplayer.Sword.Parrying):
             if(Theplayer.Sword.ParryCollision(Enemies[i])):
                  Theplayer.Sword.ResolveParryCollision(Enemies[i])
                  if(Theplayer.Sword == "Vampire"):
                       Theplayer.health += Theplayer.sword.RegenAmount if Theplayer.health + Theplayer.sword.RegenAmount < Theplayer.MaxHealth else Theplayer.MaxHealth
    
    
    #if(self.Swinging or self.Parrying):
    
    
    CurrentRoom.draw(screen, camera)
    #player bullet list and enemy bullet list
    for bullet in Theplayer.gun.bulletList:
        bullet.update(dt, screen)

        bullet.draw(screen, camera)

        for wall in WallList:
            if bullet.Collision(wall):
                bullet.ResolveCollision(wall)
    for bullet in EnemyBullets:
        bullet.update(dt, screen)
        bullet.draw(screen, camera)
        if bullet.Collision(Theplayer):
            bullet.ResolveCollision(Theplayer)
        for wall in WallList:
            if bullet.Collision(wall):
                bullet.ResolveCollision(wall)
            
    Theplayer.draw(screen, camera)
    Theplayer.gun.draw(screen,camera,Theplayer.gun.size,Theplayer.pos)
    Theplayer.Sword.draw(screen,camera,Theplayer.Sword.size,Theplayer.pos)
    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()