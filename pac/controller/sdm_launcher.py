from datetime import datetime, timedelta

from pac.controller.SamplingCurveGenerator import SamplingCurveGenerator
from pac.controller.SamplingDecisionMaker import SamplingDecisionMaker
from pac.controller.pool_policies import TYPE_LINEAR, TYPE_SIGMOID
from pac.mobility_analyzer.GeoFencingOutcome import GeoFencingOutcome


def generate_synthetic_arrivals_and_departures():
    tmp_ins = []
    tmp_outs = []
    tmp_ins.append(datetime.strptime('2017-04-03 09:30:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-03 18:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-03 19:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-04 09:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-04 09:30:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-04 18:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-04 19:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-05 09:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-05 09:30:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-05 18:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-05 19:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-06 09:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-06 09:30:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-06 18:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-06 19:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-07 09:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-07 09:30:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-07 18:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_ins.append(datetime.strptime('2017-04-07 19:00:00', '%Y-%m-%d %H:%M:%S'))
    tmp_outs.append(datetime.strptime('2017-04-08 09:00:00', '%Y-%m-%d %H:%M:%S'))

    return tmp_ins, tmp_outs


# sdm = SamplingDecisionMaker()
#
# arrivals, departures = generate_synthetic_arrivals_and_departures()
#
# print('Starting with stay point as in {} - {}'.format(arrivals[0], departures[0]))
#
# sdm.receive_notification(event_type=GeoFencingOutcome.TYPE_ARRIVING_STAY_POINT, prediction_start_time=arrivals[0],
#                          prediction_end_time=departures[0])
#
# while True:
#     action = sdm.generate_cognitive_action()
#     if action is None:
#         break
#     else:
#         print('Famous cognitive action is {}'.format(action))
#
# print('Ok, next, trajectory as {} - {}'.format(departures[0], arrivals[1]))
# sdm.receive_notification(event_type=GeoFencingOutcome.TYPE_LEAVING_STAY_POINT, prediction_start_time=departures[0],
#                          prediction_end_time=arrivals[1])
#
# while True:
#     action = sdm.generate_cognitive_action()
#     if action is None:
#         break
#     else:
#         print('Famous cognitive action is {}'.format(action))

# curve_generator = SamplingCurveGenerator(
#     prediction_start=datetime.strptime('2017-04-03 09:30:00', '%Y-%m-%d %H:%M:%S'),
#     prediction_end=datetime.strptime('2017-04-03 18:00:00', '%Y-%m-%d %H:%M:%S'),
#     total_schedules=10,
#     curve_type=TYPE_LINEAR)
#
# print('Sampling curve has been generated, sampling times are: ')
# for i in range(0, len(curve_generator.x)):
#     print(i, ' - ', curve_generator.y[i], 'with', curve_generator.mapped_y[i])
#
# # curve_generator.plot_real_world_values()


