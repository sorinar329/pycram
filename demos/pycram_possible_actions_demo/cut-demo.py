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

world = BulletWorld()
world.set_gravity([0, 0, -9.8])
plane = Object("floor", "environment", "plane.urdf", world=world)
robot = Object("pr2", "robot", "../../resources/" + robot_description.name + ".urdf")
robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()


kitchen = Object("kitchen", "environment", "kitchen.urdf")



robot.set_joint_state(robot_description.torso_joint, 0.24)
kitchen_desig = ObjectDesignatorDescription(names=["kitchen"])

kitchen.set_color([0.2, 0, 0.4, 0.6])
spawning_poses = {
    'bigknife': Pose([-0.95, 1.2, 1.3], [1, -1, 1, -1]),
    'bread': Pose([-0.85, 0.9, 0.95],[0, 0, -1, 1])
}
bigknife = Object("bigknife", "bigkinfe", "big-knife.stl", spawning_poses["bigknife"])
bread = Object("bread", "bread", "bread.stl", spawning_poses["bread"])
bigknife_BO = BelieveObject(names=["bigknife"])
bread_BO = BelieveObject(names=["bread"])

with simulated_robot:
    ParkArmsAction([Arms.BOTH]).resolve().perform()

    MoveTorsoAction([0.33]).resolve().perform()

    pickup_pose_knife = CostmapLocation(target=bigknife_BO.resolve(), reachable_for=robot_desig).resolve()
    pickup_arm = pickup_pose_knife.reachable_arms[0]

    NavigateAction(target_locations=[pickup_pose_knife.pose]).resolve().perform()
    #PickUpAction(object_designator_description=bigknife_BO, arms=[left], grasps=["front"]).resolve().perform()
    PickUpAction(object_designator_description=bigknife_BO,
                     arms=["left"],
                     grasps=["top"]).resolve().perform()
    ParkArmsAction([Arms.BOTH]).resolve().perform()