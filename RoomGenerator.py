import random
import math
#    1
# 4 Room 2
#    3
def generate_Dungeon(RoomList, TheGivenStart=0, NeededRooms=None):
    if NeededRooms is None:
        NeededRooms = len(RoomList)

    connections = []
    used_rooms = {TheGivenStart}

    Available = [list(room) for room in RoomList]

    def opposite(direction):
        return {1: 3, 3: 1, 2: 4, 4: 2}[direction]

    def search():
        if len(used_rooms) == NeededRooms:
            return True

        possible = []

        for room_a in list(used_rooms):
            for exit_index, exit_data in enumerate(Available[room_a]):
                direction = exit_data[0]

                if exit_data[1]:
                    continue

                for room_b in range(len(RoomList)):
                    if room_b in used_rooms:
                        continue

                    for exit_b_index, exit_b in enumerate(Available[room_b]):
                        if exit_b[1]:
                            continue

                        if exit_b[0] == opposite(direction):
                            possible.append(
                                (room_a, exit_index, direction, room_b, exit_b_index)
                            )

        random.shuffle(possible)

        for room_a, exit_a, direction, room_b, exit_b in possible:
            old_a = Available[room_a][exit_a]
            old_b = Available[room_b][exit_b]

            Available[room_a][exit_a] = (old_a[0], True)
            Available[room_b][exit_b] = (old_b[0], True)

            connections.append(f"{room_a:02d}{direction}{room_b:02d}")
            used_rooms.add(room_b)

            if search():
                return connections


            return []
            used_rooms.remove(room_b)
            connections.pop()

            Available[room_a][exit_a] = old_a
            Available[room_b][exit_b] = old_b

        return False

    if search():
        return connections

    return []


def MakeDungeonGrid(TheGrid, RoomList, coords, ThecurrentNum):
    start_room = f"{ThecurrentNum:02d}"

    # Place room 0 in the middle
    x, y = coords
    TheGrid[y][x] = start_room

    placed = {start_room: (x, y)}
    remaining = RoomList.copy()

    while remaining:
        progress = False

        for connection in remaining[:]:
            parent = connection[:2]
            direction = int(connection[2])
            child = connection[3:5]

            # Parent hasn't been placed yet
            if parent not in placed:
                continue

            px, py = placed[parent]

            if direction == 1:
                nx, ny = px, py - 1
            elif direction == 2:
                nx, ny = px + 1, py
            elif direction == 3:
                nx, ny = px, py + 1
            else:  # direction == 4
                nx, ny = px - 1, py

            # Already placed elsewhere
            if child in placed:
                remaining.remove(connection)
                progress = True
                continue

            # Cell occupied by another room
            if TheGrid[ny][nx] != '':
                continue

            TheGrid[ny][nx] = child
            placed[child] = (nx, ny)

            remaining.remove(connection)
            progress = True

        if not progress:
            return None
    return TheGrid


def ValidateGrid(ConnectionNum, GivenRoomLen):
    return ConnectionNum == GivenRoomLen - 1


def CheckConnections(GivenGrid, GivenNum, GivenRoomLen, NumberBeenChecked, Visited=None):
    if Visited is None:
        Visited = set()

    j = GivenNum[0]
    i = GivenNum[1]
    if (i, j) in Visited:
        return 0
    Visited.add((i, j))

    ConnectionNum = 0
    NumberChecked = NumberBeenChecked
    ValidateList = []

    if i - 1 >= 0 and GivenGrid[i-1][j] != '' and (i-1, j) not in Visited:
        ConnectionNum += 1
        NumberChecked += 1
        ValidateList.append((j, i-1))
    if i + 1 < len(GivenGrid) and GivenGrid[i+1][j] != '' and (i+1, j) not in Visited:
        ConnectionNum += 1
        NumberChecked += 1
        ValidateList.append((j, i+1))
    if j - 1 >= 0 and GivenGrid[i][j-1] != '' and (i, j-1) not in Visited:
        ConnectionNum += 1
        NumberChecked += 1
        ValidateList.append((j-1, i))
    if j + 1 < len(GivenGrid[0]) and GivenGrid[i][j+1] != '' and (i, j+1) not in Visited:
        ConnectionNum += 1
        NumberChecked += 1
        ValidateList.append((j+1, i))

    if NumberBeenChecked < GivenRoomLen:
        for coord in ValidateList:
            ConnectionNum += CheckConnections(GivenGrid, coord, GivenRoomLen, NumberChecked, Visited)

    return ConnectionNum