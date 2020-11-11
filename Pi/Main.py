from RMMLIB4 import Mapping, Logger, Constants
from RMMLIB4.Constants import Direction, RelDirection

Logger.PATH = './Pi/out/log.txt'
Logger.ACTIVE = True
Logger.clear()

m = Mapping.Map()
m.setAttributeAtRobot(Direction.NORTH, True)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.RIGHT)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)
m.driveRobot(RelDirection.FORWARD)

m.save("./Pi/out/map.json")