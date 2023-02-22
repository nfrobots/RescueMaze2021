from Pi.ReceiverCI import ArduinoData
from RMMLIB4 import Mapping, Constants, Logger
import Pi.Interpreter

enviroment = Mapping.Map.open('./Pi/out/map.json')

INTERPREDED_DATA_TEMPLATE = Pi.Interpreter.INTERPREDED_DATA_TEMPLATE

def interprete_data():
    return enviroment.getAtRobot()

def get_tile(robot: Mapping._Vctr) -> Mapping.MazeTile:
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

def allign():
    pass

def deploy_rescue_kit():
    pass

def get_data_s() -> ArduinoData:
    return ArduinoData(main_switch=True)