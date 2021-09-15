from toopazo_tools.file_folder import FileFolderTools as FFTools
import datetime
import numpy as np
import os


class KDEcanLog:
    def __init__(self, folder):
        if FFTools.is_folder(folder):
            self.folder = folder
        else:
            arg = '{} is not a folder'.format(folder)
            raise RuntimeError(arg)

        self.file_fd = None
        self.file_name = None
        # log_141_2020-12-22-13-41-26.ulg
        self.file_separator = '_'
        self.file_logstr = 'log'
        self.file_extension = 'kdecan'
        self.logs_in_folder = []

        self.find_log_files()

    def find_log_files(self):
        file_lognum_arr = []
        lognum_arr = []
        logdate_arr = []
        logname_arr = []

        farr = FFTools.get_file_arr(self.folder, extension=self.file_extension)
        for file in farr:
            [head, tail] = FFTools.get_file_split(file)
            _ = head
            logname = tail
            res = self.parse_filename(logname)
            if res is not None:
                [logstr, lognum, logdate] = res
                _ = logstr
                file_lognum_arr.append(lognum)
                print('Detected log {} captured on {}, filename {}'.format(
                    lognum, logdate, logname))
                lognum_arr.append(lognum)
                logdate_arr.append(logdate)
                logname_arr.append(logname)

        # Convert to numpy arrays
        file_lognum_arr = np.array(file_lognum_arr)
        self.logs_in_folder = {'folder': self.folder, 'lognum': lognum_arr,
                               'logdate': logdate_arr, 'logname': logname_arr}
        # return [file_lognum_arr, ]

    def parse_filename(self, filename):
        if self.file_extension in filename:
            # log_141_2020-12-22-13-41-26.ulg
            tail = '.{}'.format(self.file_extension)
            filename = filename.replace(tail, '')
            farr = filename.split(self.file_separator)
            print(farr)
            logstr = farr[0] == self.file_logstr
            lognum = int(farr[1])
            logdate = datetime.datetime.strptime(farr[2], '%Y-%m-%d-%H-%M-%S')
            if len(farr) != 3:
                return None
            else:
                # print([logstr, lognum, logdate])
                return [logstr, lognum, logdate]
        else:
            return None

    def open_new_file(self):
        dtnow = datetime.datetime.now()
        logstr = self.file_logstr
        lognum = np.max(self.file_lognum_arr) + 1
        logdate = dtnow.strftime("%Y-%m-%d-%H-%M-%S")

        separator = self.file_separator
        extension = self.file_extension
        fnarr = [logstr, separator, str(lognum), separator, logdate, '.', extension]
        self.file_name = ''.join(fnarr)
        print(self.file_name)
        # log_141_2020-12-22-13-41-26.ulg
        # log_142_2021-09-14-17-25-22.kdecan
        self.file_fd = open(self.file_name, 'w')

    def write_current_file(self, data):
        self.file_fd.write(data)

    def close_current_file(self):
        self.file_fd.close()
