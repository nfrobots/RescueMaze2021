from RMMLIB4 import Mapping, Logger, Constants
from RMMLIB4.Constants import Direction, RelDirection

Logger.PATH = './Pi/out/log.txt'
Logger.clear()

#import Pi.Interpreter
import tools.Simulation

Interpreter = tools.Simulation
Mover = tools.Simulation

map = Mapping.Map(logging=True)
just_started = True

while True:
    # if map.robotIsAtStart() and not just_started: ##### FIX!!! ROOBT MIGHT GO TO START, BUT IS NOT FINISHED
    #     break
    if just_started:
        just_started = False

    current_tile = Interpreter.get_data()
    map.setAtRobot(current_tile)

    for relDirection in (RelDirection.LEFT, RelDirection.FORWARD, RelDirection.RIGHT, RelDirection.BACKWARD):
        if map.getAtRobot()[map.relDirectionToDirection(relDirection)]: #wall
            continue
        destination = map.get(map.robot.x + map.relDirectionToOffset(relDirection)[0],
                              map.robot.y + map.relDirectionToOffset(relDirection)[1])
        if destination != None and destination[Constants.BLACK]:
            continue
        drive_succes = Mover.driveRobot(relDirection)
        if drive_succes == True:
            map.driveRobot(relDirection)
            break
        if drive_succes == Constants.BLACK: # no succes due to black tile
            map.setAttributeAtRobotOffset(relDirection, Constants.BLACK, True)
