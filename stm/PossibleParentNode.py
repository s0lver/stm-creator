from stm.SpatialTimeModelNode import SpatialTimeModelNode


class PossibleParentNode(object):
    def __init__(self, absolute_time_difference: float, node: SpatialTimeModelNode):
        self.absolute_time_difference = absolute_time_difference
        self.spatial_time_model_node = node
