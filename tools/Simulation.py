from RMMLIB4 import Mapping, Constants, Logger
import Pi.Interpreter

enviroment = Mapping.Map.open('./Pi/out/testmap2.json')

INTERPREDED_DATA_TEMPLATE = Pi.Interpreter.INTERPREDED_DATA_TEMPLATE

def interprete_data():
    return enviroment.getAtRobot()

def get_data():
    tile = interprete_data()
    tile[Constants.KNOWN] = True
    return tile

def rotate(relDirection):
    enviroment.rotateRobot(relDirection)

def driveRobot(relDirection: Constants.RelDirection):
    if enviroment.getAtRobot()[enviroment.relDirectionToDirection(relDirection)]: #has wall
        return "wall"
    else:
        destination = enviroment.get(enviroment.robot.x + enviroment.relDirectionToOffset(relDirection)[0],
                                     enviroment.robot.y + enviroment.relDirectionToOffset(relDirection)[1])
        if destination != None and destination[Constants.BLACK]:
            return Constants.BLACK
        else:
            enviroment.driveRobot(relDirection)
            return True
        