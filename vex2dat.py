# Python version 3 (and 2)
# Contents: vexファイルをdat(pointing含む)に変換するスクリプト
# Since   : Nov, 2019
#           Yuki Hamae
# Update  : Oct, 2020
#           Beta版リリース

from decimal import Decimal, ROUND_HALF_UP
import os
import math

import util as ut



class Vex2Dat():
    def __init__(self):
        self.datout = [None, None, None, None] * 17
        self.IFREQ = [6] * 16
        self.dat_filename = ''
        self.dat_file_flag = True
        self.rx_range_list = {}
        self.first_LO = {}
        self.debag = False
        self.yes =True
        self.center_freq_at_sam45 = 3
        self.second_LO_max = 11000
        self.change_name_prm = {'H22R':'H20ch1', 'H22L':'H20ch2'}

        tmp_rx = {'H22':['L', 'R'], 'H40':'', 'Z45':['V', 'H'], 'TZ2':['V', 'H']}
        tmp_rx_range_list = {'H22': [5,7], 'H40': [5,7], 'Z45':[4,8], 'TZ2':[4,8]}
        tmp_first_LO = {'H22': 0, 'H40': 0, 'Z45':0, 'TZ2':0}

        for key in tmp_rx.keys():
            for val in tmp_rx[key]:
                self.rx_range_list[key + val] = tmp_rx_range_list[key]
                self.first_LO[key + val] = tmp_first_LO[key]
            if len(tmp_rx[key]) == 0:
                self.rx_range_list[key] = tmp_rx_range_list[key]
                self.first_LO[key] = tmp_first_LO[key]


        self.datout = ['VLBI']
        for i in range(0, 16):
            self.datout.append(str(i + 1).zfill(2) + ',#     ,,')
        # self.datout[1] = str(i + 1).zfill(2) + ',' +  str(’H20ch1).ljust(max_leng) + ',' +  lists[6][1] + ',' +  str(Decimal(str(secont_lo_freq)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))


    def cal_2nd_LO_freq(self, obs_center, rx_freq, side_band2, pflag = False):
      # USBの場合LOの周波数増やすとピークは周波数低い方向にシフト
        if not pflag:
            sign = 1
        else:
            sign = 0
        if side_band2 == 'USB':
            second_LO = 6000 + 3000 + sign * 8 + obs_center - rx_freq
            if pflag:
                print('    2ndLO = 6000 + 3000 + ' + str(obs_center) + ' - ' + str(rx_freq) + ' = ' + str(Decimal(str(second_LO)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)) + 'MHz')
            else:
                print('    2ndLO = 6000 + 3000 + ' + '8 + ' + str(obs_center) + ' - ' + str(rx_freq) + ' = ' + str(Decimal(str(second_LO)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)) + 'MHz')


        if side_band2 == 'LSB':
            second_LO = 6000 + 3000 + sign * 8 - obs_center + rx_freq
            if pflag:
                print('    2ndLO = 6000 + 3000 + ' - str(obs_center) + ' + ' + str(rx_freq) + ' = ' + str(Decimal(str(second_LO)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)) + 'MHz')
            else:
                print('    2ndLO = 6000 + 3000 + ' + '8 - ' + str(obs_center) + ' + ' + str(rx_freq) + ' = ' + str(Decimal(str(second_LO)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)) + 'MHz')


        return second_LO


    def convert_vex_to_dat(self):
        print(ut.pycolor.UNDERLINE + 'VLBI Dat file' + ut.pycolor.END)

        # self.datout[0] = 'VLBI'
        # print(len(self.datout))
        max_leng = max([len(str(self.array_list[i][0])) for i in range(0, len(self.array_list))])
        if max_leng < 6:
            max_leng = 6

        for i, lists in enumerate(self.array_list):
            # if i == 0:
            #     continue
            if lists[4] != -1:
                # print(self.rx_range_list[lists[0]])
                f = lists[3] + lists[7] / 2



                # if 'TZ2V' == lists[0] or 'TZ2H' == lists[0]:
                #     sideband = 'LSB'
                # else:
                #     sideband = 'USB'
                # print(lists[2])
                first_lo = self.rxlist[lists[4]][2]
                # if self.debag:
                    # ut.UtilFunc.chkprint(first_lo)
                    # ut.UtilFunc.chkprint(f)
                    # ut.UtilFunc.chkprintstr('f = ' + str(lists[3]) + " + "  + str(lists[7]) + ' / 2')
                    # print()
                if i + 1 in self.pointing_array_num.values() or i + 1 == 1 or i + 1 == 2:
                    print('A' + str(i + 1).zfill(2) + ' ' + lists[0] + ', ' + lists[6][1] + ', POINTING')
                else:
                    print('A' + str(i + 1).zfill(2) + ' ' + lists[0] + ', ' + lists[6][1])

                # secont_lo_freq = str(Vex2Dat.cal_2nd_LO_freq(self, f, first_lo * 1000, sideband1, sideband2))
                secont_lo_freq = str(Vex2Dat.cal_2nd_LO_freq(self, f, first_lo * 1000, lists[6][1], pflag = (i + 1 in self.pointing_array_num.values() or i + 1 == 1 or i + 1 == 2)))

                if lists[0] in self.change_name_prm.keys():
                    rx_name = self.change_name_prm[lists[0]]
                else:
                    rx_name = lists[0]
                # self.datout[i + 1] = str(i + 1).zfill(2) + , +  str(rx_name).ljust(max_leng) + , +  str(lists[6][1]) + , +  str(Decimal(str(secont_lo_freq)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))
                self.datout[i + 1] = str(i + 1).zfill(2) + ',' +  str(rx_name).ljust(max_leng) + ',' +  lists[6][1] + ',' +  str(Decimal(str(secont_lo_freq)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))

                # if float(secont_lo_freq) > self.second_LO_max:
                #     ut.UtilFunc.print_err_msg(False, '', "2nd L.O.の周波数が11GHｚを超えました", "2nd L.O.の周波数が11GHz以下になるように設定を変更してください")
            else:
                print('A' + str(i + 1).zfill(2) + ' N/A, N/A')
                print('    2ndLO = N/A')
            # else:
            #     self.datout[i + 1] = [str(i + 1).zfill(2), '#'.ljust(max_leng),'', '']
        write_line = self.datout
        # print(write_line)
        # for lists in self.datout[1:]:
        #     write_line.append(,.join(map(str, lists)))
        # print(write_line)
        # print("-" * 20)
        # print('\n'.join(write_line))
        # print("-" * 20)


        ut.UtilFunc.ask_and_write(self.dat_filename, write_line, self.dat_file_flag, self.yes)
        return True










