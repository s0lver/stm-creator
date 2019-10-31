from datetime import timedelta, datetime

from entities.GpsFix import GpsFix
from pac.mobility_analyzer.Trajectory import Trajectory


class TrajectoryComparator(object):
    def __init__(self, ground_truth_trajectory: Trajectory, sub_sampled_trajectory: Trajectory):
        self._gt_trajectory = ground_truth_trajectory
        self._ss_trajectory = sub_sampled_trajectory

    def compare_synchronized(self):
        global_start_time = datetime.now()
        # internal_mapped_fixes = []
        distance_sum = 0
        total_mapped_fixes = 0
        sub_sampled_trj_size = self._ss_trajectory.get_size()
        index_equivalent_fix_left = 0
        index_equivalent_fix_right = 0
        start_timestamp = self._ss_trajectory.get_fix(0).timestamp
        end_timestamp = self._ss_trajectory.get_last().timestamp
        ss_time_length = (end_timestamp - start_timestamp).total_seconds()

        for i in range(0, sub_sampled_trj_size):
            # If we are @ last sampled fix, then everything is already done
            if (i + 1) == sub_sampled_trj_size:
                break

            # Get anchor points in sub-sampled trajectory
            left_fix = self._ss_trajectory.get_fix(i)
            right_fix = self._ss_trajectory.get_fix(i + 1)

            # Get sub-trajectory of ground truth enclosed by equivalent left and right fixes
            index_equivalent_fix_left = self._gt_trajectory.get_time_closest_fix_index(self._ss_trajectory.get_fix(i),
                                                                                       index_equivalent_fix_left)
            index_equivalent_fix_right = self._gt_trajectory.get_time_closest_fix_index(
                self._ss_trajectory.get_fix(i + 1), index_equivalent_fix_left)
            sub_trajectory = self._gt_trajectory.get_sub_trajectory(index_equivalent_fix_left,
                                                                    index_equivalent_fix_right)

            # 1. Get distance of initial fix in current sub trajectory
            distance_first_point = sub_trajectory.get_fix(0).distance_to(left_fix)
            distance_sum += distance_first_point

            # 2. Map all of he internal sub trajectory fixes
            # start_time = datetime.now()
            internal_mapped_fixes = self.project_fixes_synchronously(sub_trajectory, left_fix, right_fix)
            # 3. Get distance for all mapped internal fixes
            inner_distance = 0
            index_in_gt = 1

            for synthetic_fix in internal_mapped_fixes:
                current_gt_fix = sub_trajectory.get_fix(index_in_gt)
                inner_distance += synthetic_fix.distance_to(current_gt_fix)
                index_in_gt += 1
            distance_sum += inner_distance
            total_mapped_fixes += len(internal_mapped_fixes)
            # end_time = datetime.now()
            # print('Projecting and analyzing {} fixes took {} seconds'.format(len(internal_mapped_fixes),
            #                                                                  (end_time - start_time).total_seconds()))

        # 4. Get distance for the last fix that has not been processed
        index_equivalent_fix_right = self._gt_trajectory.get_time_closest_fix_index(self._ss_trajectory.get_last(),
                                                                                    index_equivalent_fix_right)
        last_fix = self._gt_trajectory.get_time_closest_fix(self._ss_trajectory.get_last(), index_equivalent_fix_right)
        distance_last_point = self._ss_trajectory.get_last().distance_to(last_fix)
        distance_sum += distance_last_point

        # I guess this is wrong if GT is not 1HZ --> projected_fixes = ss_time_length
        # global_end_time = datetime.now()
        # print('Trajectory comparison projected {} fixes and took {} seconds'.format(total_mapped_fixes, (
        #     global_end_time - global_start_time).total_seconds()))
        return distance_sum, total_mapped_fixes

    def project_fixes_synchronously(self, sub_trj: Trajectory, left_fix: GpsFix, right_fix: GpsFix):
        mapped_fixes = []
        size_ss = sub_trj.get_size()
        gt_internal_time = (sub_trj.get_last().timestamp - sub_trj.get_first().timestamp).total_seconds()

        for fix_i in range(1, size_ss - 1):
            current_fix_timestamp = sub_trj.get_fix(fix_i).timestamp
            elapsed_time_to_fix = (current_fix_timestamp - sub_trj.get_first().timestamp).total_seconds()
            k1 = elapsed_time_to_fix
            k2 = gt_internal_time - k1

            mapped_fix = self.build_synthetic_fix(current_fix_timestamp, left_fix, right_fix, k1, k2)
            mapped_fixes.append(mapped_fix)

        return mapped_fixes

    @staticmethod
    def build_synthetic_fix(timestamp_to_assign, start_segment_fix: GpsFix, end_segment_fix: GpsFix, k1, k2):
        """
        Builds a synthetic fix using a mathematical approach for splitting a line segment in the specified
        proportions k1 and k2. These proportion factors are scalars.
        :param timestamp_to_assign: The timestamp to assign to the produced fix
        :param start_segment_fix:  The fix that defines the start of the line segment.
        :param end_segment_fix:  The fix that defines the end of the line segment
        :param k1: The first proportion factor
        :param k2: The second proportion factor.
        :return: A GPS fixes situated in the line segment according to specified proportions and with the specified
        timestamp
        """
        if k1 == 0.0 and k2 == 0.0:
            mapped_latitude = end_segment_fix.latitude
            mapped_longitude = end_segment_fix.longitude
        else:
            mapped_latitude = ((k1 * end_segment_fix.latitude) + (k2 * start_segment_fix.latitude)) / (k1 + k2)
            mapped_longitude = ((k1 * end_segment_fix.longitude) + (k2 * start_segment_fix.longitude)) / (k1 + k2)

        return GpsFix(mapped_latitude, mapped_longitude, timestamp_to_assign, 0, 0, 0)

    def compare_synchronized_no_interpolation(self):
        distance_sum = 0
        sub_sampled_trj_size = self._ss_trajectory.get_size()
        index_equivalent_fix_left = 0
        index_equivalent_fix_right = 0
        projected_fixes = sub_sampled_trj_size
        for i in range(0, sub_sampled_trj_size):
            if (i + 1) == sub_sampled_trj_size:
                break

            # Get anchor points in sub-sampled trajectory
            ss_left_fix = self._ss_trajectory.get_fix(i)

            # Get sub-trajectory of ground truth enclosed by equivalent left and right fixes
            index_equivalent_fix_left = self._gt_trajectory.get_time_closest_fix_index(self._ss_trajectory.get_fix(i),
                                                                                       index_equivalent_fix_left)
            gt_left_fix = self._gt_trajectory.get_fix(index_equivalent_fix_left)
            distance = ss_left_fix.distance_to(gt_left_fix)
            if distance > 200:
                print('SS {} in GT is {}, distance is {}'.format(ss_left_fix, gt_left_fix, distance))
            distance_sum += distance

        index_equivalent_fix_right = self._gt_trajectory.get_time_closest_fix_index(self._ss_trajectory.get_last(),
                                                                                    index_equivalent_fix_right)
        print('Distance for {}'.format(self._ss_trajectory.get_last()))
        last_fix_in_gt = self._gt_trajectory.get_time_closest_fix(self._ss_trajectory.get_last(),
                                                                  index_equivalent_fix_right)
        distance_last_point = self._ss_trajectory.get_last().distance_to(last_fix_in_gt)
        distance_sum += distance_last_point

        return distance_sum, projected_fixes
