from typing import List

import Utils
from stm.PossibleParentNode import PossibleParentNode
from stm.SpatialTimeModel import SpatialTimeModel
from stm.SpatialTimeModelNode import SpatialTimeModelNode
from stm.TransitionMatrix import TransitionMatrix
from stm.TransitionMatrixEntry import TransitionMatrixEntry


def build_flat_list_of_visits(transition_matrices: List[TransitionMatrix]) -> List[TransitionMatrixEntry]:
    flat_visits = []
    for tm in transition_matrices:
        flat_visits_of_matrix = tm.flat_visits()

        # sort the list of transition matrix entry here
        flat_visits_of_matrix.sort(key=lambda x: x.departure_time_sp_origin)

        flat_visits.extend(flat_visits_of_matrix)

    return flat_visits


class SpatialTimeModelBuilder(object):
    def __init__(self, transition_matrices: List[TransitionMatrix], delta_time_minutes, t_fusion_mode):
        """
        Basic constructor
        :param transition_matrices: The transition matrices representing all of the mobility data windows.
        :param delta_time_minutes: The time interval used for considering similarities of nodes during.
        :param t_fusion_mode: The time fusion mode to employ when consolidating different dates.
        """
        self._delta_t_minutes = delta_time_minutes
        self._t_fusion_mode = t_fusion_mode
        self._transition_matrices = transition_matrices
        self._all_transitions = build_flat_list_of_visits(transition_matrices)
        self._root_node = None

    def build_expanded_spatial_time_model(self) -> SpatialTimeModel:
        """
        Builds an expanded spatial time model from the transition matrices and deltaTimeMinutes specified in constructor call.
        :return: An expanded spatial time model object reference.
        """
        for transition in self._all_transitions:
            baby_node = SpatialTimeModelNode.build_from_transition_entry(self._root_node, transition)
            if self._root_node is None:
                self._root_node = baby_node
            else:
                self._allocate_node_in_tree(baby_node)
        return SpatialTimeModel(self._root_node)

    def _allocate_node_in_tree(self, new_node: SpatialTimeModelNode):
        """
        Tries to allocate the specified node into the mobility tree
        :param new_node: The node to add.
        :return:
        """
        target_node = self._search_target_node(new_node)  # type: SpatialTimeModelNode
        if target_node is None:
            possible_parents = self._find_possible_parents(new_node)
            parent = possible_parents[0] if len(possible_parents) > 0 else None  # type: SpatialTimeModelNode

            if parent is None:
                print('The new node might represent a new root!, not implemented yet! ' + str(new_node))
            else:
                new_node.parent = parent
                parent.add_child(new_node)
        else:
            target_node.fuse_with_node(new_node, self._t_fusion_mode)

    def _find_possible_parents(self, node: SpatialTimeModelNode) -> List[SpatialTimeModelNode]:
        """
        Finds a list of possible parent nodes for the specified node.
        Parents are ordered by increasing time difference.
        :param node: The node for which to find a parent is needed
        :return: The list of possible parent nodes for the specified node.
        """
        nodes_in_model = self._get_entries_in_tree()  # type: List[SpatialTimeModelNode]

        # Try to sort in order of time closeness to the argument node
        possible_parents = []  # type:  List[PossibleParentNode]

        for node_in_tree in nodes_in_model:
            if node_in_tree.id_sp_destination == node.id_sp_origin:
                abs_time_diff = Utils.minutes_difference(node_in_tree.consolidated_t_out_dest,
                                                         node.consolidated_t_out_origin)
                # This works as
                # abs_time_diff = node_in_tree.getConsolidatedDepartureFromDestinationToD().minutesDifferenceWith(node.getConsolidatedDepartureFromOriginToD());
                possible_parents.append(PossibleParentNode(abs_time_diff, node_in_tree))

        possible_parents.sort(key=lambda x: x.absolute_time_difference)
        ordered_parent_nodes = []  # type:  List[SpatialTimeModelNode]

        for parent in possible_parents:
            ordered_parent_nodes.append(parent.spatial_time_model_node)

        return ordered_parent_nodes

    def _search_target_node(self, node: SpatialTimeModelNode) -> SpatialTimeModelNode:
        """
        Tries to obtain an existing node in the tree, similar to the specified one.
        :param node: The node to whom a similar node will be obtained.
        :return: A similar node or null if none is found.
        """
        entries_in_tree = self._get_entries_in_tree()  # type: List[SpatialTimeModelNode]

        for currentNode in entries_in_tree:
            if node.is_equivalent_to(currentNode, self._delta_t_minutes):
                return currentNode

        return None

    def _get_entries_in_tree(self):
        """
        Gets the nodes inside the current tree
        :return: The list of nodes of the trees, in a BFS fashion
        """
        stm = SpatialTimeModel(self._root_node)
        nodes_in_model = stm.bread_first_traversal_recursive()
        return nodes_in_model
