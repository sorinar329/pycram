import owlready2.util
import rapidfuzz
from owlready2 import *

import pathlib

from ...designators.action_designator import (MixingWhirlstormAction)
from ...designators.motion_designator import *

SOMA = get_namespace("http://www.ease-crc.org/ont/SOMA.owl")
MIXING = get_namespace("http://www.ease-crc.org/ont/mixing#")
DUL = get_namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")


class MixingActionSWRL(MixingWhirlstormAction):

    def __init__(self, object_designator_description: ObjectDesignatorDescription,
                 object_tool_designator_description: ObjectDesignatorDescription,
                 ingredients: List[str], task: str, arms: List[str], grasps: List[str]):
        super().__init__(object_designator_description, object_tool_designator_description, arms, grasps)

        path_mixing_onto = str(pathlib.Path(__file__).parent.joinpath("ontologies", "mixing.owl"))

        self.knowledge_graph = get_ontology(path_mixing_onto).load()
        self.ingredients = ingredients
        self.task = task
        self.motion = ""
        self.motion_parameters = {}

    def create_ingredient_instances(self):
        ingredient_instances = []
        label_cls = {}

        for ing in self.knowledge_graph.Ingredient.descendants():
            labels = [lbl for lbl in ing.label if isinstance(lbl, owlready2.util.locstr) and lbl.lang == 'en']
            if len(labels) > 0:
                label_cls.update({labels[0]: ing})

        for ingredient_name in self.ingredients:
            matched_ing, _, _ = rapidfuzz.process.extractOne(query=ingredient_name, choices=label_cls.keys())
            ing_cls = label_cls.get(matched_ing)
            ingredient_instance = ing_cls(ingredient_name)
            ingredient_instances.append(ingredient_instance)
        return ingredient_instances

    def create_container_tool_instances(self):
        container_name = self.object_designator_description.names[0]
        tool_name = self.object_tool_designator_description.names[0]

        label_cls = {}
        for ing in SOMA.DesignedTool.descendants():
            labels = [lbl for lbl in ing.label if isinstance(lbl, owlready2.util.locstr) and lbl.lang == 'en']
            if len(labels) > 0:
                label_cls.update({labels[0]: ing})

        matched_container, _, _ = rapidfuzz.process.extractOne(query=container_name, choices=label_cls.keys())
        cls = label_cls.get(matched_container)
        container_instance = cls(container_name)

        matched_tool, _, _ = rapidfuzz.process.extractOne(query=tool_name, choices=label_cls.keys())
        cls = label_cls.get(matched_tool)
        tool_instance = cls(tool_name)

        return container_instance, tool_instance

    def create_task_instance(self):
        label_cls = {}
        for ing in DUL.Task.subclasses():
            labels = [lbl for lbl in ing.label if isinstance(lbl, owlready2.util.locstr) and lbl.lang == 'en']
            if len(labels) > 0:
                label_cls.update({labels[0]: ing})

        matched_task, _, _ = rapidfuzz.process.extractOne(query=self.task, choices=label_cls.keys())
        cls = label_cls.get(matched_task)
        task_instance = cls(self.task)
        return task_instance

    def assign_parameters(self, motion: owlready2.NamedIndividual):
        motion_cls = [cls for cls in motion.is_a if "Then" not in cls.name][0]
        self.motion = motion_cls.label[0].split('motion')[0].strip()
        """
        Get parameters from class restrictions
        """
        if len(motion_cls.folding_rotation_shift) > 0:
            self.motion_parameters.update({'folding_rotation_shift': motion_cls.folding_rotation_shift[0]})

        if len(motion_cls.repetitive_folding_rotation_shift) > 0:
            self.motion_parameters.update(
                {'repetitive_folding_rotation_shift': motion_cls.repetitive_folding_rotation_shift[0]})

        if len(motion_cls.height_increment) > 0:
            self.motion_parameters.update({'height_increment': motion_cls.height_increment[0]})

        if len(motion_cls.radius_upper_bound_relative) > 0 and len(motion_cls.radius_lower_bound_relative) > 0:
            self.motion_parameters.update(
                {'radius_bounds': [motion_cls.radius_upper_bound_relative[0],
                                   motion_cls.radius_lower_bound_relative[0]]}
            )

        if len(motion_cls.horizontal_increment) > 0:
            self.motion_parameters.update({'horizontal_increment': motion_cls.horizontal_increment[0]})

    def run_inference(self, motion):
        with self.knowledge_graph:
            self.create_container_tool_instances()
            ingredient_instances = self.create_ingredient_instances()
            task_instance = self.create_task_instance()
            task_instance.performMotion.append(motion)
            union = set()

            for ingredient_instance in ingredient_instances:
                task_instance.hasIngredient.append(ingredient_instance)
                ing_ancestors = set(ingredient_instance.is_a[0].ancestors())
                union = union.union(ing_ancestors)
            union.add(task_instance.is_a[0])
            matched_rule = -1
            rules = set()
            for r in self.knowledge_graph.rules():
                body_classes = {pred.class_predicate for pred in r.body}
                if matched_rule < len(union.intersection(body_classes)):
                    rules = set()
                    matched_rule = len(union.intersection(body_classes))
                    rules.add(r)

            other_rules = list(set(self.knowledge_graph.rules()).difference(rules))
            for i in range(len(other_rules)):
                name = other_rules[i].name
                rule_as_string = str(other_rules[i])
                destroy_entity(other_rules[i])
                other_rules[i] = (name, rule_as_string)
            sync_reasoner_pellet()

            for name, rule_as_string in other_rules:
                other_rule = Imp(name=name)
                other_rule.set_as_rule(rule_as_string)

    def parameters_from_owl(self):
        motion_instance = self.knowledge_graph.Motion("motion")

        self.run_inference(motion_instance)
        self.assign_parameters(motion_instance)

        print(self.motion)
        print(self.motion_parameters)
        # "Supported motions are: circular, folding, whirlstorm and horizontal elliptical"
        # self.motion = "horizontal elliptical"
        # self.motion_parameters = {"radius_bounds": [0.7, 0.0], "angle_shift1": 22.5, "angle_shift2": 90}
        return self.Action(self.object_designator_description.ground(),
                           self.object_tool_designator_description.ground(),
                           self.arms[0], self.grasps[0], self.motion, self.motion_parameters)
