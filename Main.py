import pygame
import Player
import Bullet
import Enemy
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
Enemies = []
EnemyBullets = []
myEnemy = Enemy.BaseEnemy(100, 50, (500, 500), (30, 30))
Enemies.append(myEnemy)
#this will eventually be dependent on the room and it will just give us the list of enemies so it's fine to just hard code them for now
Theplayer = Player.Realplayer(300, (100, 100), (100,100))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #enemy bullets = each bullet in the bullet list of each enemy in the enemy list
    #for i in range(len(Enemies)):
     #   for j in range(Enemies[j].bulletList):
      #      if j not in EnemyBullets:
       #         EnemyBullets.append(j) 
    screen.fill("purple")
    Theplayer.gun.update(dt, screen, pygame.key.get_pressed(), Theplayer.pos, pygame.mouse.get_pos())   
    Theplayer.update(screen, pygame.key.get_pressed(), dt, pygame.mouse.get_pos())
    myEnemy.update(dt, Theplayer.pos, Theplayer.gun.bulletList, screen)
    #player bullet list and enemy bullet list
    for bullet in Theplayer.gun.bulletList:
        bullet.update(dt, screen)
    Theplayer.draw(screen)
    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()