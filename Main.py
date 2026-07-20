import pygame
import Player
import Bullet
import Wall
import Enemy
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
Enemies = []
EnemyBullets = []
myEnemy = Enemy.BaseEnemy(100, 300, (500, 500), (30, 30), "Pistol")
Enemy2 = Enemy.PinBaller(100, 50, (200, 500), (30, 30), "None")
Enemies.append(myEnemy)
Enemies.append(Enemy2)
SingleWall = Wall.TheWall((300, 300), (100, 100), 1)
#this will eventually be dependent on the room and it will just give us the list of enemies so it's fine to just hard code them for now
Theplayer = Player.Realplayer(300, (32, 32), (100,100), 100,"Shotgun", "RegularSword")
while running:
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
    SingleWall.WallCollision(Theplayer)
    Theplayer.draw(screen)
    Theplayer.gun.update(dt, screen, pygame.key.get_pressed(), Theplayer.pos, pygame.mouse.get_pos()) 
    Theplayer.Sword.update(dt, screen, pygame.key.get_pressed(), Theplayer.pos, pygame.mouse.get_pos())
    SingleWall.WallCollision(Theplayer)
    for i in range(len(Enemies)):
        Enemies[i].update(dt, Theplayer.pos, Theplayer.gun.bulletList, screen)
        SingleWall.WallCollision(Enemies[i])
        Enemies[i].draw(screen)
        if Enemies[i].gun != None:
             Enemies[i].gun.update(dt, screen, pygame.key.get_pressed(), myEnemy.pos, Theplayer.pos)
        if(Theplayer.Sword.Swinging):
             if(Theplayer.Sword.Collision(Enemies[i])):
                  Theplayer.Sword.ResolveCollision(Enemies[i], Theplayer.Sword.damage)
        if(Enemies[i].Parryable and Theplayer.Sword.Parrying):
             if(Theplayer.Sword.ParryCollision(Enemies[i])):
                  Theplayer.Sword.ResolveParryCollision(Enemies[i])
                  if(Theplayer.Sword == "Vampire"):
                       Theplayer.health += Theplayer.sword.RegenAmount if Theplayer.health + Theplayer.sword.RegenAmount < Theplayer.MaxHealth else Theplayer.MaxHealth
    SingleWall.draw(screen)
                  

    #player bullet list and enemy bullet list
    for bullet in Theplayer.gun.bulletList:
        bullet.update(dt, screen)
    for bullet in EnemyBullets:
         bullet.update(dt, screen)
    Theplayer.draw(screen)

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()