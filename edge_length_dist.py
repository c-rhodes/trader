import os
import sys

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from collections import defaultdict

try:
    SUMO_HOME = os.environ.get('SUMO_HOME')
    sys.path.append(os.path.join(SUMO_HOME, 'tools'))
    import sumolib
except ImportError:
    sys.exit('please declare environment variable \'SUMO_HOME\' as the root '
             'directory of your sumo installation (it should contain folders '
             '\'bin\', \'tools\' and \'docs\')')


def main():
    grid_net = sumolib.net.readNet('grid8/grid.net.xml')
    grid_edges = defaultdict(list)
    for edge in grid_net.getEdges():
        grid_edges['id'].append(edge.getID())
        grid_edges['length'].append(int(round(edge.getLength())))

    random_net = sumolib.net.readNet('abstract/random.net.xml')
    random_edges = defaultdict(list)
    for edge in random_net.getEdges():
        random_edges['id'].append(edge.getID())
        random_edges['length'].append(edge.getLength())

    df_grid = pd.DataFrame(grid_edges)
    df_random = pd.DataFrame(random_edges)

    xlabel = 'Edge length [m]'
    fig, axes = plt.subplots(nrows=1, ncols=2)
    df_grid.plot.hist(bins=2, ax=axes[0], title='8x8 Grid Network')
    axes[0].set_xlabel(xlabel)

    df_random.plot.hist(ax=axes[1], title='Abstract Network')
    axes[1].set_xlabel(xlabel)

    plt.suptitle('Edge Length Distribution')
    plt.show()


if __name__ == '__main__':
    main()
