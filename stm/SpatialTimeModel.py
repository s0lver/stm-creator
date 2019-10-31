from typing import List

from stm.SpatialTimeModelNode import SpatialTimeModelNode


class SpatialTimeModel(object):
    def __init__(self, root_node: SpatialTimeModelNode):
        self.root_node = root_node
        self._traverse_result = []

    def bread_first_traversal_recursive(self):
        spatial_time_model_nodes = [self.root_node]
        self._traverse_result = []
        self._do_bfs_recursive(spatial_time_model_nodes)
        return self._traverse_result

    def _do_bfs_recursive(self, nodes: List[SpatialTimeModelNode]):
        if nodes is not None and len(nodes) > 0:
            children = []
            for node in nodes:
                self._traverse_result.append(node)
                children_current_node = node.children
                if children_current_node is not None and len(children_current_node) > 0:
                    children.extend(children_current_node)

            self._do_bfs_recursive(children)

    def __str__(self):
        self.bread_first_traversal_recursive()
        str_representation = ""
        for node in self._traverse_result:
            str_representation += str(node) + "\n"
        return str_representation
