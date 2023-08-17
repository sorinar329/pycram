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
plane.set_color([0, 0, 0, 1])
# Action designator example from notebook
# makin a simple pouring plan
from pycram.designators.object_designator import *

# spawn kitchen
kitchen = Object("kitchen", "environment", "kitchen.urdf")
kitchen.set_color([0.2, 0, 0.4, 0.6])
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

# pouring plan begins
with simulated_robot:
    ParkArmsAction([Arms.BOTH]).resolve().perform()

    MoveTorsoAction([0.3]).resolve().perform()

    pickup_pose = CostmapLocation(target=milk_desig.resolve(), reachable_for=robot_desig).resolve()
    pickup_arm = pickup_pose.reachable_arms[0]

    NavigateAction(target_locations=[pickup_pose.pose]).resolve().perform()

    PickUpAction(object_designator_description=milk_desig, arms=[pickup_arm], grasps=["front"]).resolve().perform()

    ParkArmsAction([Arms.BOTH]).resolve().perform()

    # do pouring by tilting, and accept time interval and speed as well
    quaternion = tf.transformations.quaternion_from_euler(90, 0, 0, axes="sxyz")

    print('quaternion', quaternion)
    tilting_pose = SemanticCostmapLocation.Location(Pose([1.6, 1.05, 1], [0.8509035, 0, 0, 0.525322]))

    revert_tilting_pose = SemanticCostmapLocation.Location(Pose([1.6, 1.05, 1], [0.0, 0, 0, 1]))
    PourAction(milk_desig, pouring_location=tilting_pose.pose, revert_location=revert_tilting_pose.pose,
               arms=[pickup_arm], wait_duration=5).resolve().perform()

    ParkArmsAction([Arms.BOTH]).resolve().perform()

    # think about where to place the milk karton
    place_island = SemanticCostmapLocation("kitchen_island_surface", kitchen_desig.resolve(),
                                           milk_desig.resolve()).resolve()

    place_stand = CostmapLocation(place_island.pose, reachable_for=robot_desig, reachable_arm=pickup_arm).resolve()

    NavigateAction(target_locations=[place_stand.pose]).resolve().perform()

    PlaceAction(milk_desig, target_locations=[place_island.pose], arms=[pickup_arm]).resolve().perform()

    ParkArmsAction([Arms.BOTH]).resolve().perform()
