import pygame
OppositeDirection = {1: 3, 3: 1, 2: 4, 4: 2}
class door:
    def __init__(self, pos, size, direction ,leads_to=None):
        self.size = size
        self.pos = pos
        self.Rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.open = False
        self.tag = "Door"
        self.direction = direction
        self.leadsto = leads_to
    def Collision(self, obj2):
        if self.Rect.colliderect(obj2.Rect):
            return True
        return False
    def determineRoom(self):
        print("Putting in next  room")
        return self.leadsto
    def draw(self, screen, camera):
        pygame.draw.rect(screen, "white", camera.apply(self.Rect))
    def GetExitPosition(self, player_size, offset=50):
        #this will make it so that when the player goes into the 
        #door they will spawn offset from the respective door in the new room
        door_center = pygame.Vector2(self.Rect.center)

        if self.direction == 1:  # top enter spawn bottom of door
            return pygame.Vector2(
                door_center.x,
                self.Rect.bottom + offset
            )

        elif self.direction == 2:  
            return pygame.Vector2(
                self.Rect.left - player_size[0] - offset,
                door_center.y
            )

        elif self.direction == 3: 
            return pygame.Vector2(
                door_center.x,
                self.Rect.top - player_size[1] - offset
            )

        elif self.direction == 4: 
            return pygame.Vector2(
                self.Rect.right + offset,
                door_center.y
            )
    def update(self, screen, obj2):
        if(self.collide(obj2)):
            self.determineRoom(obj2)
        self.draw(screen)