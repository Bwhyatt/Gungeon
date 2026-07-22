import glob
import os
from pathlib import Path
import pytmx


def _door_direction(door_obj, room_w, room_h):
    # Finds the centre point of the room.
    # This is used to determine which side of the room the door is closest to.
    center_x = room_w / 2
    center_y = room_h / 2

    # Calculates the door's position relative to the centre of the room.
    dx = door_obj.x - center_x
    dy = door_obj.y - center_y

    # Determines whether the door is closer to a horizontal or vertical edge.
    # Returns a number representing the direction:
    # 1 = top, 2 = right, 3 = bottom, 4 = left.
    if abs(dx) > abs(dy):
        return 2 if dx > 0 else 4
    else:
        return 3 if dy > 0 else 1



def discover_rooms(folder="TileRooms"):
    # Stores the file paths of all valid rooms found.
    paths = []

    # Stores the exits contained in each room.
    # Each exit is stored as (direction, connected status).
    RoomList = []

    # Finds every Tiled map file inside the given folder.
    files = glob.glob(os.path.join(folder, "*.tmx"))


    # Prints all discovered room files for debugging.
    print("Found room files:")
    for f in files:
        print(" ", Path(f).name)


    # Sorts rooms numerically based on their filename.
    # This allows rooms named 1.tmx, 2.tmx, 3.tmx etc. to load in order.
    try:
        files.sort(key=lambda x: int(Path(x).stem))

    # Stops execution if a room filename is not a number.
    except ValueError:
        print("One or more room filenames are not numbers.")
        raise



    # Loads each room file and checks its objects.
    for path in files:

        # Loads the Tiled map data.
        tmx_data = pytmx.load_pygame(path)


        # Converts the tile dimensions into the actual pixel dimensions of the room.
        room_w = tmx_data.width * tmx_data.tilewidth
        room_h = tmx_data.height * tmx_data.tileheight


        # Stores all door directions found in this room.
        exits = []


        # Checks every object placed in Tiled.
        for obj in tmx_data.objects:

            # Finds objects marked with the custom property Tag = Door.
            if getattr(obj, "Tag", "") == "Door":

                # Converts the door's position into a direction number.
                direction = _door_direction(obj, room_w, room_h)


                # Prevents duplicate exits being stored.
                if direction not in exits:
                    exits.append(direction)



        # Only stores rooms that contain at least one door.
        if exits:

            # Saves the room file path.
            paths.append(path)

            # Creates the initial room connection data.
            # False means the door is not currently connected to another room.
            RoomList.append([(d, False) for d in sorted(exits)])



    # Prints the final list of loaded rooms and their exits.
    print("\nLoaded rooms:")
    for path, exits in zip(paths, RoomList):
        print(Path(path).name, exits)


    # Returns both the room locations and their available exits.
    return paths, RoomList