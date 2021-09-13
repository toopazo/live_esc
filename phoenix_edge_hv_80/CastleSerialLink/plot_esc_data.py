
from read_esc_data import EscData
import matplotlib

import pandas as pd
import matplotlib.pyplot as plt


class PlotEscData:
    """
    Class to plot data from EscData
    """

    def __init__(self, escdata):
        assert isinstance(escdata, EscData)
        self.escdata = escdata

        # if type(rtuple) is not tuple:
        #     raise RuntimeError('{} is not tuple'.format(rtuple))
        self.escdata.data_dict['time'] = \
            pd.to_datetime(self.escdata.data_dict['time'])
        self.escdata.data_dict.pop('sample', None)

        matplotlib.use('Qt5Agg')

    def plot_using_pandas(self):
        df = pd.DataFrame(self.escdata.data_dict)
        df.set_index('time', inplace=True, verify_integrity=True)
        print(df)

        tfigsize = (12, 6)
        # fig, axs = plt.subplots(figsize=tfigsize)
        # df.plot()
        # df.plot.area(ax=axs, subplots=True)
        df.plot.area(figsize=tfigsize, subplots=True)

        # cmap = ListedColormap(['#0343df', '#e50000', '#ffff14', '#929591'])
        # ax = df.plot.bar(x='year', colormap=cmap)
        # ax.set_xlabel(None)
        # ax.set_ylabel('Seats')
        # ax.set_title('UK election results')

        # plt.show()
        plt.savefig("plot_using_pandas.png")


def main_read_data():
    filename = 'esc_data.pkl'
    escdata = EscData()
    escdata.load_from_file(filename)
    # print(escdata.data_dict)

    plotescdata = PlotEscData(escdata)
    plotescdata.plot_using_pandas()


if __name__ == "__main__":
    # main_collect_data()
    main_read_data()
