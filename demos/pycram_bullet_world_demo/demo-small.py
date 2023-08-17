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



world = BulletWorld()
world.set_gravity([0, 0, -9.8])
plane = Object("floor", "environment", "plane.urdf", world=world)
robot = Object("pr2", "robot", "../../resources/" + robot_description.name + ".urdf")
robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
spawning_poses = {
    'milk': Pose([1.3, 1, 0.93]),
    'spoon': Pose([1.35, 0.9, 0.78]),
    'cereal': Pose([1.3, 0.6, 0.94]),
    'bowl': Pose([1.3, 0.8, 0.94])
}

kitchen = Object("kitchen", "environment", "kitchen.urdf")

milk = Object("milk", "milk", "milk.stl", spawning_poses["milk"])
spoon = Object("spoon", "spoon", "spoon.stl", spawning_poses["spoon"])
kitchen.attach(spoon, link="sink_area_left_upper_drawer_main")
cereal = Object("cereal", "cereal", "breakfast_cereal.stl", spawning_poses["cereal"])
bowl = Object("bowl", "bowl", "bowl.stl", spawning_poses["bowl"])

robot.set_joint_state(robot_description.torso_joint, 0.24)

milk_desig = ObjectDesignatorDescription(names=["milk"])
spoon_desig = ObjectDesignatorDescription(names=["spoon"])
cereal_desig = ObjectDesignatorDescription(names=["cereal"])
bowl_desig = ObjectDesignatorDescription(names=["bowl"])
kitchen_desig = ObjectDesignatorDescription(names=["kitchen"])

kitchen.set_color([0.2, 0, 0.4, 0.6])

# Pick and Place
with simulated_robot:
    ParkArmsAction([Arms.BOTH]).resolve().perform()

    NavigateAction([Pose([0, 1, 0], [0, 0, 0, 1])]).resolve().perform()

    LookAtAction(targets=[milk_desig.resolve().pose]).resolve().perform()

    obj_desig = DetectAction(milk_desig).resolve().perform()

    print(obj_desig)

    obj_desig.

    # #Detect object
    # #try to detect object via camera, if it fails..
    #
    # det_obj = DetectAction(object_designator_description=milk_desig).resolve().perform()
    # block_new = None
    # if det_obj is None:
    #     block = btr.blocking(det_obj, BulletWorld.robot, BulletWorld.objects)
    #     block_new = list(filter(lambda obj: milk_desig != "environment", block))
    # else:
    #     det_obj = WorldStateDetectingMotion(object_designator_description=milk_desig).resolve().perform()
    # If something is in the way, move it first and then move back to the sink.
    # if block_new:
    #     move_object(block_new[0].type, targets[block_new[0].type][0], arm, robot_name)
    #     move_robot(robot_name, 'sink', object_type)
    #
    # if det_obj.type == "spoon":
    #     kitchen.detach(det_obj)

    # PickUpAction(object_designator_description=milk_desig, arms=[pickup_arm], grasps=["front"]).resolve().perform()
    #
    # ParkArmsAction([Arms.BOTH]).resolve().perform()
    #
    # # think about where to place the milk karton
    # place_island = SemanticCostmapLocation("kitchen_island_surface", kitchen_desig.resolve(),
    #                                        milk_desig.resolve()).resolve()
    #
    # place_stand = CostmapLocation(place_island.pose, reachable_for=robot_desig, reachable_arm=pickup_arm).resolve()
    #
    # NavigateAction(target_locations=[place_stand.pose]).resolve().perform()
    #
    # PlaceAction(milk_desig, target_locations=[place_island.pose], arms=[pickup_arm]).resolve().perform()
    #
    # ParkArmsAction([Arms.BOTH]).resolve().perform()
