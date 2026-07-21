import pygame
from UI import Button
class WeaponSelect:

    def __init__(self,screen,change_state,start_game):
        self.screen=screen
        self.change_state=change_state
        self.start_game=start_game

        self.selected_gun=None
        self.selected_sword=None

        self.font=pygame.font.Font(None,35)


        self.buttons=[]


    def setup(self):

        import Gun
        import Sword


        guns=list(Gun.WhichGun.keys())
        swords=list(Sword.WhichSword.keys())


        for i,g in enumerate(guns):

            self.buttons.append(
                Button(
                    (50+i*130,150,120,100),
                    g,
                    lambda g=g:self.select_gun(g)
                )
            )


        for i,s in enumerate(swords):

            self.buttons.append(
                Button(
                    (50+i*130,350,120,100),
                    s,
                    lambda s=s:self.select_sword(s)
                )
            )


        self.buttons.append(
            Button(
                (500,600,250,70),
                "Start Game",
                self.begin
            )
        )


    def select_gun(self,name):
        self.selected_gun=name


    def select_sword(self,name):
        self.selected_sword=name


    def begin(self):

        if self.selected_gun and self.selected_sword:
            self.start_game(
                self.selected_gun,
                self.selected_sword
            )


    def update(self,event):
        for b in self.buttons:
            b.update(event)


    def draw(self):

        self.screen.fill((30,30,30))

        title=self.font.render(
            "Choose Weapons",
            True,
            "white"
        )

        self.screen.blit(title,(450,50))


        for b in self.buttons:
            b.draw(self.screen)