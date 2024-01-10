import dataclasses

import owlready2
import regex
from ...designators.action_designator import (MixingWhirlstormAction)

from ...designators.motion_designator import *

from owlready2 import *

SOMA = get_ontology("http://www.ease-crc.org/ont/SOMA.owl")


class MixingActionSWRL(MixingWhirlstormAction):

    def __init__(self, object_container_designator_description: ObjectDesignatorDescription,
                 object_tool_designator_description: ObjectDesignatorDescription,
                 ingredients: List[str], task: str, arms: List[str], grasps: List[str]):
        super().__init__(object_container_designator_description, object_tool_designator_description, arms, grasps)

        self.knowledge_graph = get_ontology("/home/naser/workspace/cram/src/PouringLiquids/src/mixing.owl").load()
        self.ingredients = ingredients
        self.task = task
        self.motion = ""
        self.motion_parameters = {}

    def create_ingredient_instances(self):
        ingredient_instances = []
        ingredient_classes = list(self.knowledge_graph.Ingredient.descendants())
        for ingredient_name in self.ingredients:
            for ingredient in ingredient_classes:
                for lbl in ingredient.label:
                    if ingredient_name in lbl:
                        ingredient_instance = ingredient(ingredient_name)
                        ingredient_instances.append(ingredient_instance)
        return ingredient_instances

    def create_container_tool_instances(self):
        container_name = self.object_designator_description.names[0]
        tool_name = self.object_tool_designator_description.names[0]
        tools_classes = list(SOMA.DesignedTool.descendants())

        container_instance = None
        tool_instance = None

        for tool_class in tools_classes:
            if len(tool_class.label) > 0 and tool_class.label[0] in container_name:
                container_instance = tool_class(tool_name)
            if len(tool_class.label) > 0 and tool_name in tool_class.label[0]:
                tool_instance = tool_class(tool_name)
        return container_instance, tool_instance

    def create_task_instance(self):
        tasks = list(self.knowledge_graph.Task.subclasses())
        task_instance = None
        for task in tasks:
            if self.task in task.label[0]:
                task_instance = task(self.task)
        return task_instance

    def assign_parameters(self, motion: owlready2.NamedIndividual):
        motion_cls = motion.is_a[0]
        self.motion = motion_cls.label[0].split('motion')[0].strip()

        if self.knowledge_graph.angle_shift1 in motion.get_properties():
            self.motion_parameters.update({'angle_shift1': motion.angle_shift1[0]})

        if self.knowledge_graph.angle_shift2 in motion.get_properties():
            self.motion_parameters.update({'angle_shift2': motion.angle_shift2[0]})

        if self.knowledge_graph.height_increment in motion.get_properties():
            self.motion_parameters.update({'height_increment': motion.height_increment[0]})

        if self.knowledge_graph.radius_upper_bound_relative in motion.get_properties() and \
                self.knowledge_graph.radius_lower_bound_relative in motion.get_properties():
            self.motion_parameters.update(
                {'radius_bounds': [motion.radius_upper_bound_absolute, motion.radius_lower_bound_absolute]})

        if self.knowledge_graph.vertical_increment in motion.get_properties():
            self.motion_parameters.update({'vertical_increment': motion.vertical_increment[0]})

    def run_inference(self):
        self.create_container_tool_instances()
        ingredient_instances = self.create_ingredient_instances()
        task_instance = self.create_task_instance()
        union = set()

        for ingredient_instance in ingredient_instances:
            task_instance.ingredient.append(ingredient_instance)
            ing_ancestors = set(ingredient_instance.is_a[0].ancestors())
            union = union.union(ing_ancestors)
        intersection1 = set(self.knowledge_graph.Ingredient.subclasses()).intersection(union)
        rules = set()
        for r in self.knowledge_graph.rules():
            body_classes = {pred.class_predicate for pred in r.body}

            if len(body_classes.intersection(intersection1)) == len(intersection1) \
                    and task_instance.is_a[0] in body_classes:
                rules.add(r)

        other_rules = list(set(self.knowledge_graph.rules()).difference(rules))
        for i in range(len(other_rules)):
            name = other_rules[i].name
            rule_as_string = str(other_rules[i])
            destroy_entity(other_rules[i])
            other_rules[i] = (name, rule_as_string)

        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

        with self.knowledge_graph:
            for name, rule_as_string in other_rules:
                other_rule = Imp(name=name)
                other_rule.set_as_rule(rule_as_string)

    def parameters_from_owl(self):
        motion_instance = self.knowledge_graph.Motion("motion")
        self.run_inference()
        self.assign_parameters(motion_instance)
        # "Supported motions are: circular, folding, whirlstorm and vertical circular"
        # self.motion = "vertical circular"
        # self.motion_parameters = {"radius_bounds": [0.7, 0.0], "angle_shift1": 22.5, "angle_shift2": 90}
        return self.Action(self.object_designator_description.ground(),
                           self.object_tool_designator_description.ground(),
                           self.arms[0], self.grasps[0], self.motion, self.motion_parameters)
