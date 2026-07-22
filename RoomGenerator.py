import random
import math

# Room connection directions:
#       1
#     4 Room 2
#       3
#
# 1 = Up, 2 = Right, 3 = Down, 4 = Left


def generate_Dungeon(RoomList, TheGivenStart=0, NeededRooms=None):

    # If no required room amount is given, use every available room.
    if NeededRooms is None:
        NeededRooms = len(RoomList)


    # Stores the connections created between rooms.
    connections = []


    # Stores rooms that have already been added to the dungeon.
    # The starting room is always added first.
    used_rooms = {TheGivenStart}


    # Creates a copy of the room data so the original list is not modified.
    Available = [list(room) for room in RoomList]


    def opposite(direction):

        # Returns the direction on the opposite side of a room.
        # This ensures connected doors line up correctly.
        return {
            1: 3,
            3: 1,
            2: 4,
            4: 2
        }[direction]



    def search():

        # Stops when the dungeon contains enough rooms.
        if len(used_rooms) == NeededRooms:
            return True


        # Stores every possible room connection that can currently be made.
        possible = []


        # Checks every room already placed in the dungeon.
        for room_a in list(used_rooms):

            # Checks every unused door in that room.
            for exit_index, exit_data in enumerate(Available[room_a]):

                direction = exit_data[0]


                # Skips doors that are already connected.
                if exit_data[1]:
                    continue


                # Searches for another room with the opposite door.
                for room_b in range(len(RoomList)):

                    # Prevents connecting a room to itself or a room already used.
                    if room_b in used_rooms:
                        continue


                    # Checks every door of the possible connecting room.
                    for exit_b_index, exit_b in enumerate(Available[room_b]):

                        # Skips already used doors.
                        if exit_b[1]:
                            continue


                        # If the doors are opposite directions,
                        # they can create a valid connection.
                        if exit_b[0] == opposite(direction):

                            possible.append(
                                (
                                    room_a,
                                    exit_index,
                                    direction,
                                    room_b,
                                    exit_b_index
                                )
                            )


        # Randomises the order so every dungeon layout can be different.
        random.shuffle(possible)


        # Attempts every possible connection until one works.
        for room_a, exit_a, direction, room_b, exit_b in possible:

            # Saves the previous door states in case this path fails.
            old_a = Available[room_a][exit_a]
            old_b = Available[room_b][exit_b]


            # Marks both doors as connected.
            Available[room_a][exit_a] = (old_a[0], True)
            Available[room_b][exit_b] = (old_b[0], True)


            # Stores the connection as:
            # Parent room + direction + child room.
            connections.append(
                f"{room_a:02d}{direction}{room_b:02d}"
            )


            # Adds the new room to the dungeon.
            used_rooms.add(room_b)


            # Recursively searches for the rest of the dungeon.
            if search():
                return connections


            # If the path failed, undo all changes.
            return []

            used_rooms.remove(room_b)
            connections.pop()

            Available[room_a][exit_a] = old_a
            Available[room_b][exit_b] = old_b


        # No valid connections were found.
        return False



    # Starts the dungeon generation process.
    if search():
        return connections


    # Returns an empty dungeon if generation failed.
    return []



def MakeDungeonGrid(TheGrid, RoomList, coords, ThecurrentNum):

    # Converts the starting room number into a two digit string.
    start_room = f"{ThecurrentNum:02d}"


    # Places the starting room in the given grid position.
    x, y = coords
    TheGrid[y][x] = start_room


    # Stores the location of every placed room.
    placed = {
        start_room: (x, y)
    }


    # Copies the connection list so the original is unchanged.
    remaining = RoomList.copy()


    # Continues placing rooms until every connection is processed.
    while remaining:

        progress = False


        # Checks each remaining connection.
        for connection in remaining[:]:

            # Extracts the parent room, direction and child room.
            parent = connection[:2]
            direction = int(connection[2])
            child = connection[3:5]


            # The parent room must exist before placing the child.
            if parent not in placed:
                continue


            # Gets the parent's current grid position.
            px, py = placed[parent]


            # Calculates where the child room should be placed.
            if direction == 1:
                nx, ny = px, py - 1

            elif direction == 2:
                nx, ny = px + 1, py

            elif direction == 3:
                nx, ny = px, py + 1

            else:
                nx, ny = px - 1, py



            # If the child already exists, it does not need placement.
            if child in placed:
                remaining.remove(connection)
                progress = True
                continue


            # Prevents two rooms occupying the same grid space.
            if TheGrid[ny][nx] != '':
                continue


            # Places the new room into the grid.
            TheGrid[ny][nx] = child
            placed[child] = (nx, ny)


            # Removes the completed connection.
            remaining.remove(connection)
            progress = True


        # Stops if no rooms could be placed.
        if not progress:
            return None


    return TheGrid



def ValidateGrid(ConnectionNum, GivenRoomLen):

    # A valid dungeon with N rooms should contain N-1 connections.
    return ConnectionNum == GivenRoomLen - 1



def CheckConnections(GivenGrid, GivenNum, GivenRoomLen, NumberBeenChecked, Visited=None):

    # Creates the visited set during the first recursive call.
    if Visited is None:
        Visited = set()


    # Gets the current grid coordinates.
    j = GivenNum[0]
    i = GivenNum[1]


    # Stops checking rooms that have already been visited.
    if (i, j) in Visited:
        return 0


    Visited.add((i, j))


    # Counts the number of valid connections found.
    ConnectionNum = 0


    # Stores how many rooms have been checked.
    NumberChecked = NumberBeenChecked


    # Stores neighbouring rooms to check recursively.
    ValidateList = []



    # Checks the room above.
    if i - 1 >= 0 and GivenGrid[i-1][j] != '' and (i-1, j) not in Visited:

        ConnectionNum += 1
        NumberChecked += 1
        ValidateList.append((j, i-1))


    # Checks the room below.
    if i + 1 < len(GivenGrid) and GivenGrid[i+1][j] != '' and (i+1, j) not in Visited:

        ConnectionNum += 1
        NumberChecked += 1
        ValidateList.append((j, i+1))


    # Checks the room to the left.
    if j - 1 >= 0 and GivenGrid[i][j-1] != '' and (i, j-1) not in Visited:

        ConnectionNum += 1
        NumberChecked += 1
        ValidateList.append((j-1, i))


    # Checks the room to the right.
    if j + 1 < len(GivenGrid[0]) and GivenGrid[i][j+1] != '' and (i, j+1) not in Visited:

        ConnectionNum += 1
        NumberChecked += 1
        ValidateList.append((j+1, i))



    # Recursively checks connected rooms until every room is visited.
    if NumberBeenChecked < GivenRoomLen:

        for coord in ValidateList:

            ConnectionNum += CheckConnections(
                GivenGrid,
                coord,
                GivenRoomLen,
                NumberChecked,
                Visited
            )


    # Returns the total number of connections found.
    return ConnectionNum