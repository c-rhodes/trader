#!/usr/bin/env python
from __future__ import division, print_function

import os
import sys
import math
import logging
import argparse

logger = logging.getLogger(__name__)

try:
    SUMO_HOME = os.environ.get('SUMO_HOME')
    sys.path.append(os.path.join(SUMO_HOME, 'tools'))
    import traci
except ImportError:
    sys.exit('please declare environment variable \'SUMO_HOME\' as the root '
             'directory of your sumo installation (it should contain folders '
             '\'bin\', \'tools\' and \'docs\')')

from traci.constants import (
    VAR_SPEED,
    VAR_NEXT_TLS,
    VAR_ALLOWED_SPEED,
    VAR_ACCEL,
    TL_NEXT_SWITCH
)


vehicle_constants = [
    VAR_SPEED,
    VAR_NEXT_TLS,
    VAR_ALLOWED_SPEED,
    VAR_ACCEL,
]

tls_constants = [
    TL_NEXT_SWITCH
]


def run(enabled):
    """TraCI Control Loop"""
    for tls_id in traci.trafficlights.getIDList():
        traci.trafficlights.subscribe(tls_id, tls_constants)

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if not enabled:
            continue

        for vehicle_id in traci.simulation.getDepartedIDList():
            traci.vehicle.subscribe(vehicle_id, vehicle_constants)

        tls_data = traci.trafficlights.getSubscriptionResults()
        vehicle_data = traci.vehicle.getSubscriptionResults()

        current_time = traci.simulation.getCurrentTime()
        for vehicle_id in traci.vehicle.getIDList():
            vehicle = vehicle_data[vehicle_id]
            current_speed = vehicle[VAR_SPEED]
            if current_speed <= 0:
                continue

            # [(tlsID, tlsIndex, distance, state), ...]
            try:
                tls_id, _, distance, state = vehicle[VAR_NEXT_TLS][0]
                if state == 'G':
                    next_switch = tls_data[tls_id][TL_NEXT_SWITCH]
                    allowed_speed = vehicle[VAR_ALLOWED_SPEED]
                    accel = vehicle[VAR_ACCEL]
                    process_vehicle(vehicle_id, tls_id, distance,
                                    current_time, current_speed,
                                    next_switch, allowed_speed,
                                    accel)
            except IndexError:
                pass
    traci.close()


def process_vehicle(vehicle_id, tls_id, distance, current_time, current_speed,
                    next_switch, allowed_speed, accel):

    t = (distance / current_speed) * 1000
    if (current_time + t) < next_switch:
        logging.debug('{} will transit'.format(vehicle_id))
        if current_speed < allowed_speed:
            traci.vehicle.setSpeed(vehicle_id, allowed_speed)
    else:
        logging.debug('{} will not transit at current speed'.format(vehicle_id))
        t, v = travel_time(distance, current_speed, accel)
        if (current_time + t) < next_switch:
            logging.debug('{} final velocity {}'.format(vehicle_id, v))
            if v < allowed_speed:
                assert current_speed < v, 'Final speed is less than current'
                logging.debug('{} increasing speed from {} to {}'.format(
                    vehicle_id, current_speed, allowed_speed))
                traci.vehicle.setSpeed(vehicle_id, allowed_speed)


def travel_time(distance, speed, accel):
    """Travel time for distance given initial speed and constant acceleration.

    Solve using SUVAT equation assuming constant acceleration:

        s = distance
        u = current speed
        A = acceleration
        s = ut + 1/2 * A * t^2
        s / (1/2) = ut + A * t^2
        0 = A * t^2 + ut - (s / 1/2)
        solve with quadratic equation
        ax^2 + bx + c = 0
        x = (-b +- sqrt(b^2 - 4ac)) / 2a

    Return tuple of (time (ms), final velocity).
    """
    s = distance
    u = speed
    A = accel
    c = -(s / 0.5)
    discriminant = u ** 2 - 4 * A * c
    if discriminant <= 0:
        # No solution, will not pass junction
        return
    x1 = (-u + math.sqrt(u**2 - 4 * A * c)) / (2 * A)
    x2 = (-u - math.sqrt(u**2 - 4 * A * c)) / (2 * A)
    t = max((x1, x2))
    v = u + A * t
    return (t * 1000, v)


def parse_args():
    """define options for this script and interpret the command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-trader', action='store_true', default=False,
                        help='Enable trader algorithm')
    parser.add_argument('--nogui', action='store_true', default=False,
                        help='run the commandline version of sumo')
    parser.add_argument('--rundir', metavar='DIR',
                        help='dir to store simulation output')
    parser.add_argument('-n', type=int,
                        help='number of vehicles in simulation')
    args = parser.parse_args()
    return args
