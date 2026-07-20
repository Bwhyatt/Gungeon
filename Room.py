import pygame
import Enemy
import pytmx
import Wall
import door#will iterate through
from pathlib import Path
class TheRoom:
    def __init__(self, RoomFile, ClassMap):
            self.RoomFile = RoomFile
            self.ClassMap = ClassMap
            self.EnemyList = []
            self.WallList = []
            self.DoorList = []
            self.Cleared = False
            self.exits = []
            
            self.RoomNum = int(Path(self.RoomFile).stem)
            self.LoadRoom()
    def LoadRoom(self):
        self.tmx_data = pytmx.load_pygame(self.RoomFile)

        for obj in self.tmx_data.objects:
            if obj.Tag == "Wall":
                NewWall = Wall.TheWall((obj.x,obj.y), (obj.width,obj.height),self.RoomNum)
                self.WallList.append(NewWall)
            elif obj.Tag == "Door":
                NewDoor = door.Door(
                    (obj.x,obj.y),
                    (obj.width,obj.height)
                )
                #if the door is below the center of the room and is facing front ways then you make (1, False)
                #tmx_data.width
                #tmx_data.height
                self.DoorList.append(NewDoor)
            elif obj.Tag == "Enemy":
                EnemyName = obj.properties["Enemy"]
                NewEnemy = self.ClassMap[EnemyName](
                    100,
                    200,
                    (obj.x,obj.y),
                    (50,50),
                    "None",
                    "None"
                )
                self.EnemyList.append(NewEnemy)
            #this allows us to load in all the enemies
           # self.EnemyList[i] = Enemy.
    def draw(self, screen, camera):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x,y,surf in layer.tiles():
                    
                    world_pos = pygame.Vector2(
                        x*self.tmx_data.tilewidth,
                        y*self.tmx_data.tileheight
                    )

                    screen.blit(
                        surf,
                        camera.apply(world_pos)
                    )

        for wall in self.WallList:
            wall.draw(screen, camera)

        for enemy in self.EnemyList:
            enemy.draw(screen, camera)
            if enemy.UsesGun:
                enemy.gun.draw(
                    screen,
                    camera,
                    enemy.gun.size,
                    enemy.pos
                )

            if enemy.UsesSword:
                enemy.Sword.draw(
                    screen,
                    camera,
                    enemy.Sword.size,
                    enemy.pos
                )
