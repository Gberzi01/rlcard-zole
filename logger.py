import os
import csv


class Logger(object):
    """ Logger saves the running results and helps make plots from the results
    """

    def __init__(self, log_dir: str):
        """ Initialize the labels, legend and paths of the plot and log file.

        Args:
            log_dir (str): The path the log files
        """
        self.log_dir = log_dir

    def __enter__(self):
        self.csv_path = os.path.join(self.log_dir, 'performance.csv')

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.csv_file = open(self.csv_path, 'w')
        fieldnames = [
            'large_win_0',
            'large_win_1',
            'large_win_2',
            'small_win_0',
            'small_win_1',
            'small_win_2',
            'as_large_0',
            'as_large_1',
            'as_large_2',
            'score_0',
            'score_1',
            'score_2',
        ]
        self.writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.writer.writeheader()

        return self

    def log_performance(self, large_win: list[str], small_win: list[str], as_large: list[str], score: list[float]):
        """ Log a point in the curve
        """
        self.writer.writerow({
            'large_win_0': float(large_win[0]),
            'large_win_1': float(large_win[1]),
            'large_win_2': float(large_win[2]),
            'small_win_0': float(small_win[0]),
            'small_win_1': float(small_win[1]),
            'small_win_2': float(small_win[2]),
            'as_large_0': float(as_large[0]),
            'as_large_1': float(as_large[1]),
            'as_large_2': float(as_large[2]),
            'score_0': float(score[0]),
            'score_1': float(score[1]),
            'score_2': float(score[2]),
        })

    def __exit__(self, type, value, traceback):
        if self.csv_path is not None:
            self.csv_file.close()
        print('\nLogs saved in', self.log_dir)
