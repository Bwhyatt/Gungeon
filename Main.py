import pygame
import Player
import Bullet
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
Theplayer = Player.Realplayer(300, (100, 100), (100,100))
while running:
    for event in pygame.event.get():
       
        if event.type == pygame.QUIT:
            running = False
    screen.fill("purple")
    Theplayer.gun.update(dt, screen, pygame.key.get_pressed(), Theplayer.pos, pygame.mouse.get_pos())   
    Theplayer.update(screen, pygame.key.get_pressed(), dt, pygame.mouse.get_pos())
    
    for bullet in Theplayer.gun.bulletList:
        bullet.update(dt, screen)
    Theplayer.draw(screen)
    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()