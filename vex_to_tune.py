# Python version 3 (and 2)
# Contents: vexファイルをtuneに変換するスクリプト
# Since   : Nov, 2019
#           Yuki Hamae


import util as ut






class VexToTune():
    def __init__(self):
        self.tune_file_name = ''
        self.tune_file = []
        self.tune_file_flag = True
        pass


    def convert_vex_to_tune(self):
        start_file = open(self.start_file_name, "r")
        start_lists = start_file.readlines()

        for line in start_lists:
            if 'OPEN VLBI' == line.split('\n')[0]:
                self.tune_file.append(line.split('\n')[0])
                break
            else:
                self.tune_file.append(line.split('\n')[0])
        self.tune_file.append('')
        self.tune_file.append('WAIT ANT')
        self.tune_file.append('WAIT MMC')
        self.tune_file.append('WAIT VLBI')
        self.tune_file.append('CLOSE ANT')
        self.tune_file.append('CLOSE MMC')
        self.tune_file.append('CLOSE VLBI')

        ut.UtilFunc.ask_and_write(self.tune_file_name, self.tune_file, self.tune_file_flag, self.yes)


        return True