#!/usr/bin/env python
from __future__ import print_function, division

import os
import sys
import errno
import logging

try:
    SUMO_HOME = os.environ.get('SUMO_HOME')
    sys.path.append(os.path.join(SUMO_HOME, 'tools'))
    sys.path.append(os.path.join(SUMO_HOME, 'tools', 'xml'))
    import traci
    import randomTrips
    import xml2csv
    from sumolib import checkBinary
except ImportError:
    sys.exit('please declare environment variable \'SUMO_HOME\' as the root '
             'directory of your sumo installation (it should contain folders '
             '\'bin\', \'tools\' and \'docs\')')


def main(args=None):
    if args.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # Create directories for generated files if they do not exist
    for path in ('routes', args.rundir):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    for seed in range(1, 4):
        print('Generating trips for simulation {}'.format(seed))
        routefile = 'routes/route-{}.rou.xml'.format(seed)
        netstate = os.path.join(args.rundir, 'netstate-{}.xml'.format(seed))
        tripinfo = os.path.join(args.rundir, 'tripinfo-{}.xml'.format(seed))
        randomTrips.main(randomTrips.get_options([
            '--net-file', 'grid.net.xml',
            '--route-file', routefile,
            '--seed', str(seed),
            '--prefix', 'vehicle',
            # prevent trips that start and end on the same edge
            '--min-distance', '1',
            '-b', '0',
            '-e', '3600',
            '-p', str(3600 / args.n)
        ]))

        print('Starting simulation {}'.format(seed))
        # this is the normal way of using traci. sumo is started as a
        # subprocess and then the python script connects and runs
        traci.start([sumoBinary,
                     '--seed', str(seed),
                     '-n', 'grid.net.xml',
                     '-r', routefile,
                     '--netstate-dump', netstate,
                     '--tripinfo-output', tripinfo])
        run(args.with_trader)

        # Convert xml files to csv for analysis with Pandas
        print('Converting tripinfo for simulation {} to csv'.format(seed))
        output = os.path.splitext(tripinfo)[0] + '.csv'
        xml2csv.main(xml2csv.get_options([
            tripinfo,
            '--separator', ',',
            '-o', output,
        ]))


if __name__ == "__main__":
    sys.path.append('..')
    from core import parse_args, run
    args = parse_args()

    logging.basicConfig(
        filename='sim.log',
        level=logging.DEBUG,
        format='%(asctime)s %(message)s',
    )
    main(args)
