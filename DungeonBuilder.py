import copy
import random
from pathlib import Path
from RoomGenerator import generate_Dungeon, MakeDungeonGrid, CheckConnections, ValidateGrid
from RoomLoader import discover_rooms
from Room import TheRoom


# Size of the grid used to place generated rooms.
GRID_SIZE = 14

# Converts a door direction into the opposite direction.
# Used when linking two rooms together so both doors know about each other.
OPPOSITE_DIRECTION = {1: 3, 3: 1, 2: 4, 4: 2}


def _room_count(RoomConnections):

    # Stores every room index that appears in a connection.
    used = set()

    for entry in RoomConnections:
        used.add(int(entry[:2]))
        used.add(int(entry[3:5]))

    # Returns how many unique rooms are connected.
    return len(used)


def _room_connection_count(RoomConnections, room_index):

    # Counts how many connections a specific room has.
    count = 0

    for entry in RoomConnections:

        # Checks if the room is the first room in the connection.
        if int(entry[:2]) == room_index:
            count += 1

        # Checks if the room is the second room in the connection.
        if int(entry[3:5]) == room_index:
            count += 1

    return count


def build_dungeon(EnemyClassmap, folder="TileRooms", min_rooms=7, max_rooms=7, max_attempts=500, start_room_stem="0"):

    # Finds all available room files and their data.
    all_paths, all_room_list = discover_rooms(folder)

    # Makes sure there are enough rooms available to generate a dungeon.
    if len(all_room_list) < 7:
        raise RuntimeError(f"Only found {len(all_room_list)} rooms with doors — need at least 7.")


    # Finds the starting room file so it is always placed first.
    start_index = next(
        (i for i, p in enumerate(all_paths) if Path(p).stem == start_room_stem),
        None
    )

    if start_index is None:
        raise RuntimeError(f"No room file named '{start_room_stem}.tmx' found in '{folder}'.")


    # Attempts generation multiple times until a valid dungeon is created.
    for attempt in range(max_attempts):

        # Current dungeon size.
        pool_size = 7

        # Selects random rooms while keeping the starting room.
        other_indices = random.sample(
            [i for i in range(len(all_room_list)) if i != start_index],
            pool_size - 1
        )

        # Start room always stays at index 0.
        indices = [start_index] + other_indices

        paths = [all_paths[i] for i in indices]

        # Copies room data so generation does not modify the originals.
        RoomList = copy.deepcopy(
            [all_room_list[i] for i in indices]
        )


        # Generates connections between rooms.
        RoomConnections = generate_Dungeon(
            RoomList,
            0,
            pool_size
        )

        # Rejects invalid generated layouts.
        if not RoomConnections:
            continue

        if _room_count(RoomConnections) != pool_size:
            continue

        if _room_connection_count(RoomConnections,0) < 2:
            continue


        # Creates an empty grid for placing rooms.
        MyGrid = [
            ['' for _ in range(GRID_SIZE)]
            for _ in range(GRID_SIZE)
        ]

        # Places the first room in the middle.
        start = (
            round(GRID_SIZE / 2),
            round(GRID_SIZE / 2)
        )

        Grid = MakeDungeonGrid(
            MyGrid,
            RoomConnections,
            start,
            0
        )

        if Grid is None:
            continue


        # Checks that the starting room actually has a connected neighbour.
        x, y = start
        connected = False

        for dx, dy in [
            (0,-1),
            (1,0),
            (0,1),
            (-1,0)
        ]:

            nx = x + dx
            ny = y + dy

            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:

                if Grid[ny][nx] != '':
                    connected = True
                    break

        if not connected:
            continue


        # Recursively counts connected rooms from the starting room.
        visited = set()

        def count_rooms(grid, x, y):

            if (x,y) in visited:
                return 0

            if grid[y][x] == '':
                return 0

            visited.add((x,y))

            total = 1

            for dx,dy in [
                (0,-1),
                (1,0),
                (0,1),
                (-1,0)
            ]:

                nx = x + dx
                ny = y + dy

                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    total += count_rooms(grid,nx,ny)

            return total


        # Ensures every generated room is reachable.
        if count_rooms(Grid,start[0],start[1]) != pool_size:
            continue


        # Creates the actual room objects.
        return _instantiate(
            Grid,
            RoomConnections,
            paths,
            EnemyClassmap
        )


    raise RuntimeError(f"Couldn't build a dungeon in {max_attempts} attempts.")


def _instantiate(Grid, RoomConnections, paths, EnemyClassmap):

    # Stores the grid position of each room index.
    coord_by_index = {}

    for y in range(GRID_SIZE):

        for x in range(GRID_SIZE):

            cell = Grid[y][x]

            if cell != '':
                coord_by_index[int(cell)] = (x, y)


    # Stores which direction each room's doors connect to.
    door_directions_by_index = {
        i: {}
        for i in coord_by_index
    }


    # Creates two-way links between connected rooms.
    for entry in RoomConnections:

        room_a = int(entry[:2])
        direction = int(entry[2])
        room_b = int(entry[3:5])

        door_directions_by_index[room_a][direction] = coord_by_index[room_b]

        door_directions_by_index[room_b][OPPOSITE_DIRECTION[direction]] = coord_by_index[room_a]


    # Creates every room object and stores it by its grid position.
    RoomRegistry = {}

    for room_index, coord in coord_by_index.items():

        RoomRegistry[coord] = TheRoom(
            paths[room_index],
            EnemyClassmap,
            coord=coord,
            door_directions=door_directions_by_index[room_index],
            RoomRegistry=RoomRegistry
        )


    # Connects the doors after every room exists.
    for room in RoomRegistry.values():
        room.LinkDoors()


    # Finds the starting room.
    start_coord = coord_by_index.get(
        0,
        next(iter(RoomRegistry))
    )

    start_room = RoomRegistry[start_coord]


    # Makes sure the starting room generated correctly.
    if len([d for d in start_room.DoorList if d.leadsto]) < 2:
        raise Exception("Room 0 spawned with less than 2 working exits")


    return RoomRegistry, RoomRegistry[start_coord]