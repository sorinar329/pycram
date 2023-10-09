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
from pycram.designators.object_designator import *
from pycram.designators.object_designator import BelieveObject

# %%
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
from pycram.designators.object_designator import *
from pycram.designators.object_designator import BelieveObject
import pycram.helper as helper
from pycram.plan_failures import IKError
import math
import time
from datetime import timedelta



from pycram.resolver.action.cutting import CuttingActionSPARQL

world = BulletWorld()
world.set_gravity([0, 0, -9.8])
# plane = Object("floor", "environment", "plane.urdf", world=world)
robot = Object("pr2", "robot", "../../resources/" + robot_description.name + ".urdf")
robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()

kitchen = Object("kitchen", "environment", "kitchen.urdf")

robot.set_joint_state(robot_description.torso_joint, 0.24)
kitchen_desig = ObjectDesignatorDescription(names=["kitchen"])

#kitchen.set_color([0.2, 0, 0.4, 0.6])

# %%
spawning_poses = {
    # 'bigknife': Pose([-0.95, 1.2, 1.3], [1, -1, 1, -1]),
    'bigknife': Pose([0.9, 0.6, 0.8], [0, 0, 0, -1]),
    # 'bread': Pose([-0.85, 0.9, 0.90], [0, 0, -1, 1])
    'bread': Pose([-0.85, 0.9, 0.90], [0, 0, -1, -1]),
    'board': Pose([-0.85, 0.9, 0.85], [0, 0, -1, -1]),
    'cocumber': Pose([-0.85, 0.9, 0.87], [0, 0, -1, -1])
}
bigknife = Object("bigknife", "bigknife", "big-knife.stl", spawning_poses["bigknife"])
#bread = Object("bread", "bread", "bread.stl", spawning_poses["bread"])
cocumber = Object("cocumber", "cocumber", "cocumber.stl", spawning_poses["cocumber"])
board = Object("board", "board", "board.stl", spawning_poses["board"])

cocumber.set_color([0, 1, 0.04, 1])
board.set_color([0.4, 0.2, 0.06, 1])
bigknife_BO = BelieveObject(names=["bigknife"])
bread_BO = BelieveObject(names=["bread"])
cocumber_BO = BelieveObject(names=["cocumber"])
SPECIAL_KNOWLEDGE_CUTTING = {
    'bread' : "rectangleLength",
    'apple' : "circleRadius"
}




with simulated_robot:
    ParkArmsAction([Arms.BOTH]).resolve().perform()

    MoveTorsoAction([0.33]).resolve().perform()
    grasp = robot_description.grasps.get_orientation_for_grasp("top")
    arm = "left"
    #
    pickup_pose_knife = CostmapLocation(target=bigknife_BO.resolve(), reachable_for=robot_desig).resolve()
    pickup_arm = pickup_pose_knife.reachable_arms[0]

    NavigateAction(target_locations=[pickup_pose_knife.pose]).resolve().perform()

    PickUpAction(object_designator_description=bigknife_BO,
                 arms=["left"],
                 grasps=["top"]).resolve().perform()

    ParkArmsAction([Arms.BOTH]).resolve().perform()

    # # AB HIER BREAD----------------------------------------------------------------------
    original_quaternion = (0, 0, 0, 1)
    rotation_axis = (0, 0, 1)

    rotation_quaternion = helper.axis_angle_to_quaternion(rotation_axis, 180)
    resulting_quaternion = helper.multiply_quaternions(original_quaternion, rotation_quaternion)

    nav_pose = Pose([-0.3, 0.9, 0.0], resulting_quaternion)

    # NavigateAction(target_locations=[pickup_pose_knife.pose]).resolve().perform()
    NavigateAction(target_locations=[nav_pose]).resolve().perform()
    LookAtAction(targets=[cocumber_BO.resolve().pose]).resolve().perform()

    detected_bread_desig = DetectAction(cocumber_BO).resolve().perform()
    # CuttingActionSPARQL(object_designator_description=bread_BO,
    #              arms=["left"],
    #              grasps=["top"]).resolve().perform()

    CuttingAction(object_designator_description=cocumber_BO,
                        arms=["left"],
                        grasps=["top"],).resolve().perform()





