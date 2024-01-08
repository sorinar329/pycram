import dataclasses
from ...designators.action_designator import (MixingWhirlstormAction)

from ...designators.motion_designator import *

from owlready2 import *

from ontology.task import *
from ontology.container import *
from ontology.ingredient import *
from ontology.motion import *
from ontology.rules import onto

SOMA = get_ontology("http://www.ease-crc.org/ont/SOMA.owl")
MIXING = onto


class MixingActionSWRL(MixingWhirlstormAction):

    def __init__(self, object_designator_description: ObjectDesignatorDescription,
                 object_tool_designator_description: ObjectDesignatorDescription,
                 ingredients: List[str], task: str, arms: List[str], grasps: List[str]):
        super().__init__(object_designator_description, object_tool_designator_description, arms, grasps)
        # self.knowledge_graph = get_ontology("/home/mkuempel/workspace/cram/src/PouringLiquids/src/mixing").load()
        self.ingredients = ingredients
        self.task = task
        self.knowledge_graph = MIXING
        self.motion = ""
        self.motion_parameters = {}

    def name2owl(self):
        container_instance, tool_instance = self.create_container_tool_instances()
        ingredient_instances = self.create_ingredient_instances()
        task_instance = self.create_task_instance()
        motion = MIXING.Motion("motion")
        union = set()

        for ingredient_instance in ingredient_instances:
            ing_ancestors = set(ingredient_instance.is_a[0].ancestors())
            union = union.union(ing_ancestors)
        intersection1 = set(MIXING.Ingredient.subclasses()).intersection(union)
        rules = set()
        for r in MIXING.rules():
            body_classes = {pred.class_predicate for pred in r.body}

            if len(body_classes.intersection(intersection1)) == len(intersection1)\
                    and task_instance.is_a[0] in body_classes:
                rules.add(r)

        other_rules = set(MIXING.rules()).difference(rules)
        for r in other_rules:
            destroy_entity(r)

        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        motion_cls = motion.is_a[0]
        self.motion = motion_cls.label[0].split('motion')[0].strip()

        if MIXING.angle_shift1 in motion.get_properties():
            self.motion_parameters.update({'angle_shift1': motion.angle_shift1[0]})
        if MIXING.angle_shift2 in motion.get_properties():
            self.motion_parameters.update({'angle_shift2': motion.angle_shift2[0]})
        if MIXING.height_increment in motion.get_properties():
            self.motion_parameters.update({'height_increment': motion.height_increment[0]})
        if MIXING.radius_upper_bound in motion.get_properties() and MIXING.radius_lower_bound in motion.get_properties():
            self.motion_parameters.update(
                {'radius_bounds': [motion.radius_upper_bound[0], motion.radius_lower_bound[0]]})
        if MIXING.vertical_increment in motion.get_properties():
            self.motion_parameters.update({'vertical_increment': motion.vertical_increment[0]})

        with MIXING:
            for r in other_rules:
                other_rule = Imp()
                other_rule.set_as_rule(str(r), namespaces=[MIXING, SOMA])

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

    def parameters_from_owl(self):
        self.name2owl()
        # "Supported motions are: circular, folding, whirlstorm and vertical circular"
        # self.motion = "vertical circular"
        # self.motion_parameters = {"radius_bounds": [0.7, 0.0], "angle_shift1": 22.5, "angle_shift2": 90}
        return self.Action(self.object_designator_description.ground(),
                           self.object_tool_designator_description.ground(),
                           self.arms[0], self.grasps[0], self.motion, self.motion_parameters)
