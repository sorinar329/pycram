import dataclasses

from ...designators.action_designator import (CuttingAction)
import os

from ...bullet_world import BulletWorld
from ...robot_descriptions import robot_description
from ...task import with_tree
from ... import helper
from ...designators.motion_designator import *

from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import OWL, RDF, RDFS


class CuttingActionSPARQL(CuttingAction):

    @dataclasses.dataclass
    class Action(CuttingAction.Action):

        def __post_init__(self):
            self.query_folder: str = os.path.join(os.path.expanduser("~", ), "pycram_ws", "src", "pycram", "demos",
                                                  "pycram_possible_actions_demo", "FoodCutting", "queries")
            task = "cut:Quartering"
            tobject = "obo:FOODON_03301710"

            self.knowledge_graph = Graph()

            # define prefixes to be used in the query
            SOMA = Namespace("http://www.ease-crc.org/ont/SOMA.owl#")
            CUT2 = Namespace("http://www.ease-crc.org/ont/situation_awareness#")
            CUT = Namespace("http://www.ease-crc.org/ont/food_cutting#")
            DUL = Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
            OBO = Namespace("http://purl.obolibrary.org/obo/")
            self.knowledge_graph.bind("owl", OWL)
            self.knowledge_graph.bind("rdfs", RDFS)
            self.knowledge_graph.bind("soma", SOMA)
            self.knowledge_graph.bind("cut2", CUT2)
            self.knowledge_graph.bind("cut", CUT)
            self.knowledge_graph.bind("dul", DUL)
            self.knowledge_graph.bind("obo", OBO)

        @property
        def repetitions(self):
            task = "cut:Quartering"
            tobject = "obo:FOODON_03301710"
            repetitionsquery = """  SELECT ?rep WHERE {
                  SERVICE <https://api.krr.triply.cc/datasets/mkumpel/FruitCuttingKG/services/FoodCuttingKG/sparql> {  
              {
                 OPTIONAL{ %s rdfs:subClassOf ?action}
                    ?action rdfs:subClassOf* ?rep_node.
                    ?rep_node owl:onProperty cut:repetitions.
                    FILTER EXISTS {
                        ?rep_node owl:hasValue ?val.}
                    BIND("1" AS ?rep)}
                UNION
                {
                   OPTIONAL{ %s rdfs:subClassOf ?action }
                    ?action rdfs:subClassOf* ?rep_node.
                    ?rep_node owl:onProperty cut:repetitions.
                    FILTER EXISTS {
                        ?rep_node owl:minQualifiedCardinality ?val.}
                    BIND("more than 1" AS ?rep)}} }""" % (task, task)
            for row in self.knowledge_graph.query(repetitionsquery):
                return row.rep
        @property
        def slice_first_pose(self):
            task = "cut:Quartering"
            tobject = "obo:FOODON_03301710"
            positionquery = """ SELECT ?pos WHERE {
            SERVICE <https://api.krr.triply.cc/datasets/mkumpel/FruitCuttingKG/services/FoodCuttingKG/sparql> {
            OPTIONAL { %s rdfs:subClassOf ?sub.}
            ?sub rdfs:subClassOf* ?node.
            ?node owl:onProperty cut:affordsPosition.
            ?node owl:someValuesFrom ?position.
            BIND(IF(?position = cut:halving_position, "halving", "slicing") AS ?pos)
            } }""" % (task)
            for row in self.knowledge_graph.query(positionquery):
                return row.pos

        @with_tree
        def perform(self) -> None:

            # Store the object's data copy at execution
            self.object_at_execution = self.object_designator.data_copy()

            robot = BulletWorld.robot
            # Retrieve object and robot from designators
            object = self.object_designator.bullet_world_object
            # Get grasp orientation and target pose
            grasp = robot_description.grasps.get_orientation_for_grasp(self.grasp)

            obj_dim = object.get_Object_Dimensions()

            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)

            # from bread_dim calculate def a calculation that gets me the highest number from the first 2 entries

            # Given slice thickness is 3 cm or 0.03 meters
            slice_thickness = 0.05
            # Calculate slices and transform them to the map frame with orientation
            obj_length = dim[0]
            obj_width = dim[1]
            obj_height = dim[2]

            '''            with open(os.path.join(self.query_folder, "get_repetitions.sparql"), "r") as f:
                repetitions = self.knowledge_graph.query(f.read())
                print(repetitions)
                for r in repetitions:
                    print("-"*80)
                    print(r)
                    print("+"*80)'''

            print("-" * 80)
            print(self.repetitions)
            print(self.slice_first_pose)
            print("+" * 80)


            if int(self.repetitions) > 1:
                num_slices = int(obj_length // slice_thickness)
            else:
                num_slices = int(self.repetitions)

            # Calculate the starting Y-coordinate offset if not halving
            if str(self.slice_first_pose) == "halving":
                start_offset = 0
                print("-" * 80)
            else:
                start_offset = -obj_length / 2 + slice_thickness / 2
                print("?" * 80)

            # Calculate slice coordinates
            slice_coordinates = [start_offset + i * slice_thickness for i in range(num_slices)]

            # Transform slice coordinates to map frame with orientation
            slice_poses = []
            for x in slice_coordinates:
                tmp_pose = object_pose.copy()
                tmp_pose.pose.position.y -= obj_width
                tmp_pose.pose.position.x = x
                sTm = object.local_transformer.transform_pose(tmp_pose, "map")
                slice_poses.append(sTm)

            for slice_pose in slice_poses:
                # rotate the slice_pose by grasp
                ori = helper.multiply_quaternions([slice_pose.orientation.x, slice_pose.orientation.y,
                                                   slice_pose.orientation.z, slice_pose.orientation.w],
                                                  grasp)

                oriR = helper.axis_angle_to_quaternion([0, 0, 1], 90)
                oriM = helper.multiply_quaternions([oriR[0], oriR[1], oriR[2], oriR[3]],
                                                   [ori[0], ori[1], ori[2], ori[3]])

                adjusted_slice_pose = slice_pose.copy()

                # Set the orientation of the object pose by grasp in MAP
                adjusted_slice_pose.orientation.x = oriM[0]
                adjusted_slice_pose.orientation.y = oriM[1]
                adjusted_slice_pose.orientation.z = oriM[2]
                adjusted_slice_pose.orientation.w = oriM[3]

                # Adjust the position of the object pose by grasp in MAP
                lift_pose = adjusted_slice_pose.copy()
                lift_pose.pose.position.z += obj_height
                # Perform the motion for lifting the tool
                BulletWorld.current_bullet_world.add_vis_axis(lift_pose)
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()
                # Perform the motion for cutting the object
                BulletWorld.current_bullet_world.add_vis_axis(adjusted_slice_pose)
                MoveTCPMotion(adjusted_slice_pose, self.arm).resolve().perform()
                # Perform the motion for lifting the tool
                BulletWorld.current_bullet_world.add_vis_axis(lift_pose)
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()

    def cutting_from_sparql(self) -> CuttingAction.Action:
        return self.Action(self.object_designator_description.ground(), self.arms[0], self.grasps[0])
