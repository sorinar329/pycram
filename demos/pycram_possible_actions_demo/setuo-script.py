import pycram
from pycram.bullet_world import BulletWorld, Object
import pycram.bullet_world_reasoning as btr
import tf
from pycram.designators.motion_designator import MotionDesignatorDescription, MoveArmJointsMotion
from pycram.process_module import simulated_robot, with_simulated_robot
from pycram.language import macros, par
from pycram.designators.location_designator import *
from pycram.designators.action_designator import *
from pycram.enums import Arms


world = BulletWorld()
world.set_gravity([0, 0, -9.8])
plane = Object("floor", "environment", "plane.urdf", world=world)

# Action designator example from notebook
# makin a simple pouring plan
from pycram.designators.object_designator import *

# spawn kitchen
kitchen = Object("kitchen", "environment", "kitchen.urdf")
kitchen_desig = ObjectDesignatorDescription(names=["kitchen"])
# spawn Milkbox
milk = Object("milk", "milk", "milk.stl", Pose([1.6, 1, 0.90]))
milk_desig = ObjectDesignatorDescription(names=["milk"])

# spawn bowl
bowl = Object("bowl", "bowl", "bowl.stl", Pose([1.6, 1, 0.90]))
bowl_desig = ObjectDesignatorDescription(names=["bowl"])

# spawn PR2
pr2 = Object("pr2", "robot", "pr2.urdf")
robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()