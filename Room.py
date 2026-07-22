import pygame
import pytmx
import Wall
import door
import EnemyStats
from pathlib import Path
import EnemyStats

class TheRoom:
    # Represents a single dungeon room.
    # Loads the room layout from a Tiled (.tmx) file and manages
    # the walls, doors, enemies and room transitions.
    def __init__(self, RoomFile, ClassMap, coord=None, door_directions=None, RoomRegistry=None):
        # RoomFile: location of the Tiled map file
        # ClassMap: dictionary converting enemy names into Python classes
        # RoomRegistry: shared dictionary containing all generated rooms
        self.RoomFile = RoomFile
        self.ClassMap = ClassMap
        self.EnemyList = []
        self.WallList = []
        self.DoorList = []# Stores all interactive objects belonging to this room.
        self.Cleared = False
        self.coord = coord
        self.door_directions = door_directions or {}   # {direction: neighbor_coord}
        self.RoomRegistry = RoomRegistry or {}          # shared {coord: TheRoom} for the whole dungeon

        stem = Path(self.RoomFile).stem
        self.RoomNum = int(stem) if stem.isdigit() else stem
        # Extracts the room identifier from the filename.
        # Used to identify the room when creating walls and debugging.
        self.LoadRoom()

    def LoadRoom(self):
        # Reads the Tiled map and converts placed objects into game objects.
        # Objects are identified using their Tiled tags.
        print("This number  is " + str(self.RoomNum))
        self.tmx_data = pytmx.load_pygame(self.RoomFile)
        room_w = self.tmx_data.width * self.tmx_data.tilewidth
        room_h = self.tmx_data.height * self.tmx_data.tileheight
        # Every object placed in Tiled is converted into the corresponding game object
        for obj in self.tmx_data.objects:
            if obj.Tag.upper() == "Wall".upper():
                self.WallList.append(Wall.TheWall((obj.x, obj.y), (obj.width, obj.height), self.RoomNum))

            elif obj.Tag.upper() == "Door".upper():
                center_x, center_y = room_w / 2, room_h / 2
                dx, dy = obj.x - center_x, obj.y - center_y
                # Determines the door direction by comparing its position
                # relative to the room centre
                direction = (2 if dx > 0 else 4) if abs(dx) > abs(dy) else (3 if dy > 0 else 1)
                self.DoorList.append(door.door((obj.x, obj.y), (obj.width, obj.height), direction))

            elif obj.Tag == "Enemy":
                EnemyName = obj.properties["Enemy"]

                stats = EnemyStats.EnemyStats[EnemyName]
                # Gets the predefined stats for this enemy type.
                NewEnemy = self.ClassMap[EnemyName](
                    stats["health"],
                    stats["speed"],
                    (obj.x, obj.y),
                    stats["size"],
                    stats["gun"],
                    stats["sword"]
                )
                # Dynamically creates the correct enemy class using the name from Tiled.
                # This allows new enemies to be added without modifying room loading.
                self.EnemyList.append(NewEnemy)

    def LinkDoors(self): # Connects each door to the room it leads to after the dungeon has been generated.
        for d in self.DoorList:
            neighbor_coord = self.door_directions.get(d.direction)
            if (neighbor_coord is not None):
                d.leadsto = self.RoomRegistry.get(neighbor_coord)
            if (d.leadsto is None):
                print("BROKEN DOOR",self.RoomNum,"direction",d.direction)
                #if there is no room the door is linked to then it gets turned into a wall
                self.WallList.append(Wall.TheWall(d.pos, d.size, self.RoomNum))
            print("Door direction:", d.direction, "leads to:", d.leadsto)
    def draw(self, screen, camera):#draws the tile map onto the room
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, surf in layer.tiles():
                    world_pos = pygame.Vector2(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                    screen.blit(surf, camera.apply(world_pos))

        for wall in self.WallList:
            wall.draw(screen, camera)

        for d in self.DoorList:
            pass
            #d.draw(screen, camera)

        for enemy in self.EnemyList:

            if not enemy.dead:
                enemy.draw(screen, camera)
    def UpdateClear(self):
        self.Cleared = all(e.dead for e in self.EnemyList)
    def CheckChange(self, dt, player):
        self.Cleared = all(getattr(e, "dead", False) for e in self.EnemyList)
        if not self.Cleared:
            return None
        for d in self.DoorList:
            if d.leadsto is not None and d.Collision(player):
                new_room = d.determineRoom()
                if new_room is None:
                    continue
                for new_door in new_room.DoorList:
                    if new_door.leadsto is not None and new_door.direction == door.OppositeDirection[d.direction]:
                        if new_door.leadsto is not None and new_door.direction == door.OppositeDirection[d.direction]:
                            print("BEFORE TELEPORT:", player.pos)

                            new_pos = new_door.GetExitPosition(player.size)

                            print("TELEPORTING TO:", new_pos)

                            player.pos = new_pos
                            player.Rect.topleft = new_pos

                            print("AFTER TELEPORT:", player.pos)
                            break
                return new_room
        return None
