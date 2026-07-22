import pygame


# Stores the opposite direction for each door direction.
# Used when linking doors between rooms.
OppositeDirection = {1: 3, 3: 1, 2: 4, 4: 2}


class door:

    def __init__(self, pos, size, direction, leads_to=None):

        # Stores the size and position of the door.
        self.size = size
        self.pos = pos

        # Rectangle used for collision detection.
        self.Rect = pygame.Rect(
            self.pos[0],
            self.pos[1],
            self.size[0],
            self.size[1]
        )

        # Tracks whether the door is currently open.
        self.open = False

        # Tag allows other objects to identify this object as a door.
        self.tag = "Door"

        # Direction determines which side of the room the door is on.
        self.direction = direction

        # Stores the room that this door connects to.
        self.leadsto = leads_to


    def Collision(self, obj2):

        # Checks if another object's rectangle overlaps with the door.
        if self.Rect.colliderect(obj2.Rect):
            return True

        return False


    def determineRoom(self):

        # Returns the room connected to this door.
        print("Putting in next room")
        return self.leadsto


    def draw(self, screen, camera):

        # Draws the door using the camera position.
        pygame.draw.rect(
            screen,
            "white",
            camera.apply(self.Rect)
        )


    def GetExitPosition(self, player_size, offset=50):

        # Calculates where the player should appear after entering this door.
        # The player is placed slightly away from the matching door.

        door_center = pygame.Vector2(
            self.Rect.center
        )


        # Top door places player below the door.
        if self.direction == 1:

            return pygame.Vector2(
                door_center.x,
                self.Rect.bottom + offset
            )


        # Left door places player to the left of the door.
        elif self.direction == 2:

            return pygame.Vector2(
                self.Rect.left - player_size[0] - offset,
                door_center.y
            )


        # Bottom door places player above the door.
        elif self.direction == 3:

            return pygame.Vector2(
                door_center.x,
                self.Rect.top - player_size[1] - offset
            )


        # Right door places player to the right of the door.
        elif self.direction == 4:

            return pygame.Vector2(
                self.Rect.right + offset,
                door_center.y
            )


    def update(self, screen, obj2):

        # Checks whether an object has entered the door.
        if(self.collide(obj2)):

            self.determineRoom(obj2)

        # Draws the door every frame.
        self.draw(screen)