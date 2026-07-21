import glob
import os
from pathlib import Path
import pytmx

def _door_direction(door_obj, room_w, room_h):
    center_x = room_w / 2
    center_y = room_h / 2
    dx = door_obj.x - center_x
    dy = door_obj.y - center_y

    if abs(dx) > abs(dy):
        return 2 if dx > 0 else 4
    else:
        return 3 if dy > 0 else 1

def discover_rooms(folder="TileRooms"):
    paths = []
    RoomList = []

    files = glob.glob(os.path.join(folder, "*.tmx"))

    print("Found room files:")
    for f in files:
        print(" ", Path(f).name)

    try:
        files.sort(key=lambda x: int(Path(x).stem))
    except ValueError:
        print("One or more room filenames are not numbers.")
        raise

    for path in files:
        tmx_data = pytmx.load_pygame(path)

        room_w = tmx_data.width * tmx_data.tilewidth
        room_h = tmx_data.height * tmx_data.tileheight

        exits = []

        for obj in tmx_data.objects:
            if getattr(obj, "Tag", "") == "Door":
                direction = _door_direction(obj, room_w, room_h)
                if direction not in exits:
                    exits.append(direction)

        if exits:
            paths.append(path)
            RoomList.append([(d, False) for d in sorted(exits)])

    print("\nLoaded rooms:")
    for path, exits in zip(paths, RoomList):
        print(Path(path).name, exits)

    return paths, RoomList