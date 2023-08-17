#!/usr/bin/env python3
import os
import sys

sys.path.append(os.getcwd() + "/../../src/")
import macropy
from pycram.bullet_world import BulletWorld, Object
from pycram import bullet_world_reasoning as btr
import tf
from pycram.designators.motion_designator import MotionDesignatorDescription, MoveArmJointsMotion
from pycram.process_module import simulated_robot, with_simulated_robot
from pycram.language import macros, par
from pycram.designators.location_designator import *
from pycram.designators.action_designator import *
from pycram.enums import Arms


class PouringPlan(object):
    """
        Low-level interface to KnowRob, which enables the easy access of NEEM data in Python.
        """

    def __init__(self):
        # pouring plan begins
        self.world = BulletWorld()

        # spawn apartment
        self.apartment = Object("apartment", "environment", "apartment.urdf")
        self.apartment_desig = ObjectDesignatorDescription(names=['apartment']).resolve()

        # spawn pr2
        self.pr2 = Object("pr2", "robot", "pr2.urdf", Pose([1, 2.5, 0]))
        self.robot_desig = ObjectDesignatorDescription(names=["pr2"]).resolve()
        # spawn Milkbox
        self.milk = Object("milk", "milk", "milk.stl", Pose([2.5, 2.5, 1]))
        self.milk_desig = ObjectDesignatorDescription(names=["milk"])
        #print("milk", self.milk.original_pose[0])

        # spawn bowl
        self.bowl = Object("bowl", "bowl", "bowl.stl", Pose([2.5, 2.8, 0.98]))
        self.bowl_desig = ObjectDesignatorDescription(names=["bowl"])

        # spawn SM_CokeBottle
        self.SM_CokeBottle = Object("SM_CokeBottle", "SM_CokeBottle", "SM_CokeBottle.stl", Pose([2.5, 3, 0.95]))
        self.SM_CokeBottle_desig = ObjectDesignatorDescription(names=["SM_CokeBottle"])

    def do_pouring(self):
        self.pouring_plan(self.milk, self.milk_desig, self.bowl, self.bowl_desig, 90)

    def pouring_plan(self, source_obj, source_obj_desig, destination_obj, destination_obj_desig, pouring_angle):
        with simulated_robot:
            ParkArmsAction([Arms.BOTH]).resolve().perform()

            MoveTorsoAction([0.3]).resolve().perform()

            pickup_pose = CostmapLocation(target=source_obj_desig.resolve(), reachable_for=self.robot_desig).resolve()
            pickup_arm = pickup_pose.reachable_arms[0]
            print('pickup_arm', pickup_arm)

            NavigateAction(target_locations=[pickup_pose.pose]).resolve().perform()

            ParkArmsAction([Arms.BOTH]).resolve().perform()
            PickUpAction(object_designator_description=source_obj_desig, arms=[pickup_arm],
                         grasps=["front"]).resolve().perform()

            ParkArmsAction([Arms.BOTH]).resolve().perform()

            # do pouring by tilting, and accept time interval and speed as well
            quaternion = tf.transformations.quaternion_from_euler(pouring_angle, 0, 0, axes="sxyz")
            print('quaternion', quaternion)

            # tilting_pose = SemanticCostmapLocation.Location(pose=[[2.52, 2.86, 1.1], quaternion])
            # revert_tilting_pose = SemanticCostmapLocation.Location(pose=[[2.52, 2.86, 1.1], [0.0, 0, 0, 1]])
            tilting_pose = SemanticCostmapLocation.Location(Pose([destination_obj.original_pose[0], quaternion]))
            revert_tilting_pose = SemanticCostmapLocation.Location(Pose([destination_obj.original_pose[0], [0.0, 0, 0, 1]]))

            PourAction(source_obj_desig, pouring_location=[tilting_pose.pose],
                       revert_location=[revert_tilting_pose.pose],
                       arms=[pickup_arm], wait_duration=5).resolve().perform()

            ParkArmsAction([Arms.BOTH]).resolve().perform()

            place_pose = SemanticCostmapLocation.Location(pose=[source_obj.original_pose[0], [0.0, 0, 0, 1.0]])

            PlaceAction(source_obj_desig, target_locations=[place_pose.pose], arms=[pickup_arm]).resolve().perform()

            ParkArmsAction([Arms.BOTH]).resolve().perform()

            end_pose = SemanticCostmapLocation.Location(pose=[[1, 2.5, 0], [0.0, 0, 0, 1.0]])
            # end_pose = CostmapLocation(target=robot_desig.resolve(), reachable_for=robot_desig).resolve()
            NavigateAction(target_locations=[end_pose.pose]).resolve().perform()


PouringPlan().do_pouring()