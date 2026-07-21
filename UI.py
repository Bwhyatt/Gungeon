import pygame

class Button:
    def __init__(self, rect, text, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 40)

    def draw(self, screen):
        pygame.draw.rect(screen, (20,20,20), self.rect)
        pygame.draw.rect(screen, (200,200,200), self.rect, 2)

        text = self.font.render(self.text, True, "white")
        screen.blit(
            text,
            (
                self.rect.centerx - text.get_width()/2,
                self.rect.centery - text.get_height()/2
            )
        )

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()


class GameUI:
    def __init__(self):
        self.font = pygame.font.Font(None, 35)

    def draw_game_ui(self, screen, player):
        # black UI background
        pygame.draw.rect(
            screen,
            (10,10,10),
            (0,0,280,130)
        )

        health = self.font.render(
            f"Health: {player.health}/{player.Maxhealth}",
            True,
            "white"
        )

        ammo = self.font.render(
            f"Ammo: {player.gun.ammo}/{player.gun.capacity}",
            True,
            "white"
        )

        screen.blit(health,(20,20))
        screen.blit(ammo,(20,60))


    def draw_weapon(self, screen, player):
        x = 1050
        y = 570

        pygame.draw.rect(
            screen,
            (10,10,10),
            (x,y,200,140)
        )

        if player.weapon_mode == "gun":
            name = player.GivenGun
            image = player.gun.image
        else:
            name = player.GivenSword
            image = player.Sword.OriginalImage


        image = pygame.transform.scale(
            image,
            (80,80)
        )

        screen.blit(image,(x+60,y+10))

        text = self.font.render(
            name,
            True,
            "white"
        )

        screen.blit(
            text,
            (x+20,y+100)
        )