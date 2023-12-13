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
        self.knowledge_graph = get_ontology("/home/mkuempel/workspace/cram/src/PouringLiquids/src/mixing").load()
        #self.knowledge_graph = MIXING

    def name2owl(self):
        object_name = self.object_designator_description.names[0]
        tool_name = self.object_tool_designator_description.names[0]
        owl_object = SOMA.Bowl(object_name)
        owl_tool = MIXING.Whisk(tool_name)
        MIXING.Flour("flour")
        MIXING.Sugar("sugar")
        MIXING.StirringTask("task")
        motion = MIXING.Motion("motion")
        print(list(MIXING.rules()))
        # sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        # print(motion.is_a)

    def parameters_from_owl(self):
        self.name2owl()
        radius_bounds = [0.7, 0]
        return self.Action(self.object_designator_description.ground(),
                           self.object_tool_designator_description.ground(),
                           self.arms[0], self.grasps[0], radius_bounds)
