from RMMLIB4 import Mapping, Logger, Constants
from RMMLIB4.Constants import Direction, RelDirection

from time import sleep

Logger.I_PATH = './Pi/out/log.txt'
Logger.clear()

from InterpreterCI import Interpreter
import Mover
Interpreter = Interpreter()
from ReceiverCI import Receiver

# import tools.Simulation

# Interpreter = tools.Simulation
# Mover = tools.Simulation
# Receiver = tools.Simulation

UNKNOWN_FILTER = Mapping.create_any_tile()
UNKNOWN_FILTER[Constants.KNOWN] = False


def perform_turn(map):
    sensor_data = Receiver().get_data_s()
    current_tile = Interpreter.get_tile(robot=map.robot, arduino_data=sensor_data)
    map.setAtRobot(current_tile)
    
    if current_tile[Constants.VICTIM]:
        print("KITTT")
        
        victim_is_right = sensor_data.temp_left > sensor_data.temp_right

        if victim_is_right:
            Mover.rotateRobot(RelDirection.RIGHT)
        else:
            Mover.rotateRobot(RelDirection.LEFT)

        Mover.deploy_rescue_kit()
        sleep(1)

        if victim_is_right:
            Mover.rotateRobot(RelDirection.LEFT)
        else:
            Mover.rotateRobot(RelDirection.RIGHT)

    res = map.search(Mapping.Position(map.robot.x, map.robot.y), UNKNOWN_FILTER)
    print(res[1], res[2], map.robot.x, map.robot.y)
    if res == (None, None, None):
        print("DONE")
        # exit()
    path = map.findPath(map.robot.x, map.robot.y, res[1], res[2])
    directions = map.pathToDirections(path)

    for direction in directions:
        driveDirection = map.directionToRelDirection(direction)

        if not Receiver().get_data_s().main_switch:
            return False

        if map.getAtRobot()[direction]:
            break

        destination = map.get(map.robot.x + map.directionToOffset(direction)[0],
                            map.robot.y + map.directionToOffset(direction)[1])

        if destination != None and destination[Constants.BLACK]:
            break

        current_tile = Interpreter.get_tile(map.robot)
        if current_tile[direction]:
            break

        drive_succes = Mover.driveRobot(driveDirection)
        Mover.allign()
        if drive_succes == True:
            map.driveRobot(driveDirection)
        if drive_succes == Constants.BLACK: # no succes due to black tile
            map.setAttributeAtRobotRelDirection(driveDirection, Constants.BLACK, True)
            map.setAttributeAtRobotRelDirection(driveDirection, Constants.KNOWN, True)
            break

    return True


if __name__ == "__main__":
    while True:
        try:
            while not Receiver().get_data_s().main_switch:
                sleep(1)
            map = Mapping.Map(logging=True, path_pre_expand=True, neighbours=True)
            while True:
                if not Receiver().get_data_s().main_switch:
                    break
                perform_turn(map)
        except Exception as e:
            if e == KeyboardInterrupt:
                exit()
            print(e) 
            pass