import pygame
from UI import Button
class TitleScreen:
    def __init__(self, screen, change_state):
        self.screen = screen
        self.change_state = change_state
        self.font = pygame.font.Font(None,80)
        self.buttons = [
            Button(
                (500,300,280,70),
                "Start",
                lambda:self.change_state("weapon_select")
            ),

            Button(
                (500,400,280,70),
                "How To Play",
                lambda:self.change_state("how_to_play")
            ),

            Button(
                (500,500,280,70),
                "Quit",
                pygame.quit
            )
        ]


    def update(self,event):
        for button in self.buttons:
            button.update(event)


    def draw(self):

        self.screen.fill((30,30,30))

        title = self.font.render(
            "7 Rooms",
            True,
            "white"
        )

        self.screen.blit(
            title,
            (
                640-title.get_width()/2,
                120
            )
        )


        for button in self.buttons:
            button.draw(self.screen)