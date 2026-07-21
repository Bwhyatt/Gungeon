import pygame
class TheWall():
    def __init__(self, position, size, Room):
        self.pos = pygame.Vector2(position)
        self.size = pygame.Vector2(size)
        self.Rect = pygame.Rect(position, size)
        self.tag = "Wall"
    def WallCollision(self, obj2):
        obj2.BannedDirections = []
        if(self.Rect.colliderect(obj2.Rect)):
            self.ResolveWallCollision(obj2)
            
    def ResolveWallCollision(self, obj2):
        overlap_left   = obj2.Rect.right  - self.Rect.left
        overlap_right  = self.Rect.right  - obj2.Rect.left
        overlap_top    = obj2.Rect.bottom - self.Rect.top
        overlap_bottom = self.Rect.bottom - obj2.Rect.top
        Minoverlap = min(overlap_bottom, overlap_left, overlap_top, overlap_right)
        if(Minoverlap == overlap_left):
            obj2.BannedDirections.append(2)
            obj2.pos[0] -= overlap_left
        if(Minoverlap == overlap_right):
            obj2.BannedDirections.append(4)
            obj2.pos[0] += overlap_right
        if(Minoverlap == overlap_bottom):
            obj2.BannedDirections.append(3)
            obj2.pos[1] += overlap_bottom
        if(Minoverlap == overlap_top):
            obj2.BannedDirections.append(1)
            obj2.pos[1] -= overlap_top
        obj2.Rect.x = obj2.pos[0]
        obj2.Rect.y = obj2.pos[1]
    
    def draw(self, screen, camera):pass
