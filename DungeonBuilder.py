import copy
import random
from pathlib import Path
from RoomGenerator import generate_Dungeon, MakeDungeonGrid, CheckConnections, ValidateGrid
from RoomLoader import discover_rooms
from Room import TheRoom

GRID_SIZE = 14
OPPOSITE_DIRECTION = {1: 3, 3: 1, 2: 4, 4: 2}


def _room_count(RoomConnections):
    used = set()
    for entry in RoomConnections:
        used.add(int(entry[:2]))
        used.add(int(entry[3:5]))
    return len(used)


def _room_connection_count(RoomConnections, room_index):
    count = 0

    for entry in RoomConnections:
        if int(entry[:2]) == room_index:
            count += 1

        if int(entry[3:5]) == room_index:
            count += 1

    return count


def build_dungeon(EnemyClassmap, folder="TileRooms", min_rooms=7, max_rooms=7, max_attempts=500, start_room_stem="0"):
    all_paths, all_room_list = discover_rooms(folder)

    if len(all_room_list) < 7:
        raise RuntimeError(f"Only found {len(all_room_list)} rooms with doors — need at least 7.")

    start_index = next((i for i, p in enumerate(all_paths) if Path(p).stem == start_room_stem), None)
    if start_index is None:
        raise RuntimeError(f"No room file named '{start_room_stem}.tmx' found in '{folder}'.")

    for attempt in range(max_attempts):
        pool_size = 7
        other_indices = random.sample(
            [i for i in range(len(all_room_list)) if i != start_index],
            pool_size - 1
        )
        indices = [start_index] + other_indices  # start room is always at position 0

        paths = [all_paths[i] for i in indices]
        RoomList = copy.deepcopy([all_room_list[i] for i in indices])

        RoomConnections = generate_Dungeon(RoomList, 0, pool_size)
        if not RoomConnections:
            continue
        if _room_count(RoomConnections) != pool_size:
            continue
        if _room_connection_count(RoomConnections,0) < 2:
            continue

        MyGrid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        start = (round(GRID_SIZE / 2), round(GRID_SIZE / 2))
        Grid = MakeDungeonGrid(MyGrid, RoomConnections, start, 0)
        if Grid is None:
            continue

        # ensure room 0 has neighbours
        x, y = start
        connected = False

        for dx, dy in [(0,-1),(1,0),(0,1),(-1,0)]:
            nx = x + dx
            ny = y + dy

            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if Grid[ny][nx] != '':
                    connected = True
                    break

        if not connected:
            continue
        visited = set()
        def count_rooms(grid, x, y):
            if (x,y) in visited:
                return 0

            if grid[y][x] == '':
                return 0

            visited.add((x,y))

            total = 1

            for dx,dy in [(0,-1),(1,0),(0,1),(-1,0)]:
                nx=x+dx
                ny=y+dy

                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    total += count_rooms(grid,nx,ny)

            return total


        if count_rooms(Grid,start[0],start[1]) != pool_size:
            continue

        return _instantiate(Grid, RoomConnections, paths, EnemyClassmap)

    raise RuntimeError(f"Couldn't build a dungeon in {max_attempts} attempts.")


def _instantiate(Grid, RoomConnections, paths, EnemyClassmap):
    coord_by_index = {}
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            cell = Grid[y][x]
            if cell != '':
                coord_by_index[int(cell)] = (x, y)

    door_directions_by_index = {i: {} for i in coord_by_index}
    for entry in RoomConnections:
        room_a = int(entry[:2])
        direction = int(entry[2])
        room_b = int(entry[3:5])
        door_directions_by_index[room_a][direction] = coord_by_index[room_b]
        door_directions_by_index[room_b][OPPOSITE_DIRECTION[direction]] = coord_by_index[room_a]

    RoomRegistry = {}
    for room_index, coord in coord_by_index.items():
        RoomRegistry[coord] = TheRoom(
            paths[room_index], EnemyClassmap,
            coord=coord, door_directions=door_directions_by_index[room_index], RoomRegistry=RoomRegistry,
        )

    for room in RoomRegistry.values():
        room.LinkDoors()

    start_coord = coord_by_index.get(0, next(iter(RoomRegistry)))
    start_room = RoomRegistry[start_coord]

    if len([d for d in start_room.DoorList if d.leadsto]) < 2:
        raise Exception("Room 0 spawned with less than 2 working exits")

    return RoomRegistry, RoomRegistry[start_coord]