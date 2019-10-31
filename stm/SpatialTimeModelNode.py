from datetime import time

import Utils
from stm.TransitionMatrixEntry import TransitionMatrixEntry


class SpatialTimeModelNode(object):
    def __init__(self, parent: 'SpatialTimeModelNode',
                 id_sp_origin: int,
                 id_sp_destination: int,
                 consolidated_tod_arrival_origin: time,
                 consolidated_tod_departure_origin: time,
                 consolidated_tod_arrival_dest: time,
                 consolidated_tod_departure_dest: time):

        self.parent = parent
        self.id_sp_origin = id_sp_origin
        self.id_sp_destination = id_sp_destination

        self.consolidated_t_in_origin = consolidated_tod_arrival_origin
        self.tods_in_origin = [consolidated_tod_arrival_origin]

        self.consolidated_t_out_origin = consolidated_tod_departure_origin
        self.tods_out_origin = [consolidated_tod_departure_origin]

        self.consolidated_t_in_dest = consolidated_tod_arrival_dest
        self.tods_in_dest = [consolidated_tod_arrival_dest]

        self.consolidated_t_out_dest = consolidated_tod_departure_dest
        self.tods_out_dest = [consolidated_tod_departure_dest]

        self.children = []
        self.use_counter = 0
        self.increment_use_counter()

    def fuse_with_node(self, node: 'SpatialTimeModelNode', t_fusion_mode: int):
        self.tods_in_origin.extend(node.tods_in_origin)
        self.tods_out_origin.extend(node.tods_out_origin)
        self.tods_in_dest.extend(node.tods_in_dest)
        self.tods_in_origin.extend(node.tods_out_dest)
        self.use_counter += node.use_counter

        self.consolidated_t_in_origin = Utils.get_representative_t(self.tods_in_origin, t_fusion_mode)
        self.consolidated_t_out_origin = Utils.get_representative_t(self.tods_out_origin, t_fusion_mode)
        self.consolidated_t_in_dest = Utils.get_representative_t(self.tods_in_dest, t_fusion_mode)
        self.consolidated_t_out_dest = Utils.get_representative_t(self.tods_out_dest, t_fusion_mode)

    @staticmethod
    def build_from_transition_entry(parent: 'SpatialTimeModelNode',
                                    transition_entry: TransitionMatrixEntry) -> 'SpatialTimeModelNode':
        node = SpatialTimeModelNode(parent, transition_entry.id_sp_origin, transition_entry.id_sp_destination,
                                    Utils.build_time_from_datetime(transition_entry.arrival_time_sp_origin),
                                    Utils.build_time_from_datetime(transition_entry.departure_time_sp_origin),
                                    Utils.build_time_from_datetime(transition_entry.arrival_time_sp_dest),
                                    Utils.build_time_from_datetime(transition_entry.departure_time_sp_dest)
                                    )
        return node

    def is_equivalent_to(self, node: 'SpatialTimeModelNode', delta_time_minutes: int) -> bool:
        if self.id_sp_origin == node.id_sp_origin and self.id_sp_destination == node.id_sp_destination:
            if Utils.within_time(self.consolidated_t_out_origin, node.consolidated_t_out_origin, delta_time_minutes):
                return True

        return False

    def increment_use_counter(self):
        self.use_counter = self.use_counter + 1

    def add_child(self, child: 'SpatialTimeModelNode'):
        self.children.append(child)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def __str__(self):
        return '{} [{}-{}] -> {} [{}-{}], {} children, {} use'.format(self.id_sp_origin,
                                                                      self.consolidated_t_in_origin,
                                                                      self.consolidated_t_out_origin,
                                                                      self.id_sp_destination,
                                                                      self.consolidated_t_in_dest,
                                                                      self.consolidated_t_out_dest,
                                                                      len(self.children), self.use_counter)
