import pygame
import Player
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
Theplayer = Player.player(100, (100, 100), (100,100))
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")
    Theplayer.move(dt)
    Theplayer.update()
    Theplayer.draw(screen)
    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()