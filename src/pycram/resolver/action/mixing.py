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
                 object_tool_designator_description: ObjectDesignatorDescription, arms: List[str],
                 grasps: List[str]):
        super().__init__(object_designator_description, object_tool_designator_description, arms, grasps)
        # self.knowledge_graph = get_ontology("/home/mkuempel/workspace/cram/src/PouringLiquids/src/mixing").load()
        self.knowledge_graph = MIXING

    def name2owl(self):
        object_name = self.object_designator_description.names[0]
        tool_name = self.object_tool_designator_description.names[0]
        owl_object = SOMA.Bowl(object_name)
        owl_tool = MIXING.Whisk(tool_name)
        MIXING.Flour("flour")
        MIXING.Sugar("sugar")
        MIXING.Water("water")
        MIXING.StirringTask("task")
        motion = MIXING.Motion("motion")
        superclasses_water = MIXING.Water.ancestors()
        superclasses_flour = MIXING.Flour.ancestors()

        union = superclasses_flour.union(superclasses_water)
        intersection1 = set(MIXING.Ingredient.subclasses()).intersection(union)

        rules = set()
        for r in MIXING.rules():
            body_classes = {pred.class_predicate for pred in r.body}
            if len(body_classes.intersection(intersection1)) == len(intersection1):
                rules.add(r)

        other_rules = set(MIXING.rules()).difference(rules)
        for r in other_rules:
            destroy_entity(r)
        for r in MIXING.rules():
            print(r)

        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        print(motion.is_a)

    def parameters_from_owl(self):
        self.name2owl()
        radius_bounds = [0.7, 0]
        return self.Action(self.object_designator_description.ground(),
                           self.object_tool_designator_description.ground(),
                           self.arms[0], self.grasps[0], radius_bounds)
