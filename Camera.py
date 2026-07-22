import pygame


class Camera:

    def __init__(self, width, height):

        # Stores how far the camera has moved away from the world origin.
        # This offset is applied to every object when drawing.
        self.offset = pygame.Vector2(0, 0)

        # Stores the size of the game window.
        # Used to keep the player centred on screen.
        self.width = width
        self.height = height

    def update(self, player):

        # Moves the camera so that the player's centre
        # stays in the middle of the screen.
        self.offset.x = player.Rect.centerx - self.width // 2
        self.offset.y = player.Rect.centery - self.height // 2

    def apply(self, target):

        # Converts world coordinates into screen coordinates.
        # This is used when drawing objects because the camera
        # only displays a section of the larger game world.

        # If the object is a rectangle, move the rectangle
        # by the camera offset.
        if isinstance(target, pygame.Rect):

            return target.move(
                -self.offset.x,
                -self.offset.y
            )

        # If the object is a Vector2 position,
        # subtract the camera offset instead.
        return target - self.offset
    
    def reverse(self, pos):

        # Converts screen coordinates back into world coordinates.
        # Used for things like mouse aiming because the mouse
        # position is relative to the screen, not the game world.
        return pygame.Vector2(pos) + self.offset