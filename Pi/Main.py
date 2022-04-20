from RMMLIB4 import Mapping, Logger, Constants
from RMMLIB4.Constants import Direction, RelDirection

Logger.I_PATH = './Pi/out/log.txt'
Logger.clear()

# from ReceiverCI import Interpreter
# import Mover
# Interpreter = Interpreter()

import tools.Simulation

Interpreter = tools.Simulation
Mover = tools.Simulation

UNKNOWN_FILTER = Mapping.create_any_tile()
UNKNOWN_FILTER[Constants.KNOWN] = False

map = Mapping.Map(logging=True, path_pre_expand=True, neighbours=True)
just_started = True

while True:
    if just_started:
        just_started = False

    current_tile = Interpreter.get_tile(map.robot)
    map.setAtRobot(current_tile)
    
    res = map.search(Mapping.Position(map.robot.x, map.robot.y), UNKNOWN_FILTER)
    print(res[1], res[2], map.robot.x, map.robot.y)
    if res == (None, None, None):
        print("DONE")
        exit()
    path = map.findPath(map.robot.x, map.robot.y, res[1], res[2])
    directions = map.pathToDirections(path)

    for direction in directions:
        driveDirection = map.directionToRelDirection(direction)

        # if map.getAtRobot()[direction]:
        #     break

        destination = map.get(map.robot.x + map.directionToOffset(direction)[0],
                            map.robot.y + map.directionToOffset(direction)[1])

        if destination != None and destination[Constants.BLACK]:
            break

        drive_succes = Mover.driveRobot(driveDirection)
        if drive_succes == True:
            map.driveRobot(driveDirection)
        if drive_succes == Constants.BLACK: # no succes due to black tile
            map.setAttributeAtRobotRelDirection(driveDirection, Constants.BLACK, True)
            map.setAttributeAtRobotRelDirection(driveDirection, Constants.KNOWN, True)
            break