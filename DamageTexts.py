import pygame

class FloatingText:
    def __init__(self, text, pos, duration=1):
        self.text = text
        self.pos = pygame.Vector2(pos)
        self.duration = duration
        self.timer = 0
        self.alive = True
        self.font = pygame.font.Font(None, 30)
    def update(self, dt):
        self.timer += dt
        # move upwards slowly
        self.pos.y -= 30 * dt

        if self.timer >= self.duration:
            self.alive = False

    def draw(self, screen, camera):
        if self.alive:
            image = self.font.render(self.text, True, (255, 255, 255))
            screen.blit(image, camera.apply(self.pos))