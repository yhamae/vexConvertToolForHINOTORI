# Python version 3 (and 2)
# Contents: vexファイルをndevice(pointing含む)に変換するスクリプト
# Since   : Nov, 2019
#           Yuki Hamae
# Update  : Oct, 2020
#           Beta版リリース

import re
import math
import copy
from decimal import Decimal, ROUND_HALF_UP

import util as ut





class Vex2Ndevice:
    def __init__(self):
        self.device_fname = ""
        self.station_name = "Ny"
        self.DEV_NOTE ='Device for HINOTORI 22/40/86 GHz simultaneous VLBI observations'
        self.vexdata = {}
        self.result_status = {}
        self.yes =True
        self.device_file_flag = True
        self.debag = False
        self.out = []
        self.type_no = 0
        self.rx_range_list = {}
        self.nobs_version = '2.191021_vlbi'
        self.max_array_leng = 16
        self.pointing_flag = False
        self.array_list = [[None,None,None, None, -1, None, None, None, None]] * self.max_array_leng
        # [受信機名, SideBand, 静止周波数, vexファイルに記載された周波数, 受信機のindex, 受信機名（詳細）, L.O.の設定, 帯域幅(MHz)]
        # self.rx_inf = {"H22": 22.800, "H40": 43.2, "Z45": 43.2, "TZ2": 87.72}
        self.rx_inf = {"H22": 22.800, "H40": 43.2, "Z45": 43.2, "TZ2": 87.654}
        self.polarized_inf = {"H22R": ["H22Rcp"], 
                              "H22L": ["H22Lcp"], 
                              "H40": ["H40Lcp"], 
                              "Z45V": ["Z45Vlp", "Z45Vcp", "Z45Lcp"], 
                              "Z45H": ["Z45Hlp", "Z45Hcp", "Z45Rcp"], 
                              "TZ2V": ["TZ2Vlp", "TZ2Lcp", "TZ2Vcp"], 
                              "TZ2H": ["TZ2Hlp", "TZ2Rcp", "TZ2Hcp"]}
        self.rx_range = {"H22": 10, "H40": 10, "Z45": 10, "TZ2": 10}
        # self.rx_width = {"H22": 1024, "H40": 2048, "Z45": 1024, "TZ2": 2048}
        # self.rx_width = {"H22": 2048, "H40": 2048, "Z45": 2048, "TZ2": 2048}
        self.array_num = {"H22R": 3, 
                          "H22L": 5, 
                          "H40":    7, 
                          "TZ2H-1": 15, 
                          "TZ2V-1": 11, 
                          "TZ2H-2": 16, 
                          "TZ2V-2": 12, 
                          "Z45V-1": 16, 
                          "Z45H-1": 11, 
                          "Z45V-2": 10, 
                          "Z45H-2": 7}
        self.pfreq = {"H22R": 22.23508, 
                                   "H22L": 22.23508, 
                                   "H40":  42.820539}
        self.pointing_array_num = {"H22R": 4, 
                                   "H22L": 6, 
                                   "H40":  8}
        # self.pointing_array_num = {}
        
        self.att = [5] * self.max_array_leng
        self.IFFREQ = [6.0] * self.max_array_leng
        # self.res_freq = [22.8, 43.2, 87.714]
        # self.pointing_res_freq = [22.235080, 42.820539, 87.714]
        # self.static_freq = [22.8, 87.714, 43.2]
        self.static_freq = list(self.rx_inf.values())
        self.rx_comb_index = {"H22R": 1, "H22L": 2, "H40": 3, "TZ2V-1": 4, "TZ2H-1": 5, "TZ2V-2": 6, "TZ2H-2": 7, "Z45V-1": 8, "Z45H-1": 9, "Z45V-2": 10, "Z45H-2": 11}
        #              Type  1 2 3 4 5 6 7 8 9 0 1
        self.rx_comb = {1:  [1,1,0,0,0,0,0,0,0,0,0],
                        2:  [0,0,1,0,0,0,0,0,0,0,0],
                        3:  [0,0,0,0,0,0,0,1,1,0,0],
                        4:  [1,0,1,0,0,0,0,0,0,0,0],
                        5:  [0,0,0,1,1,0,0,0,0,0,0],
                        6:  [1,1,1,0,0,0,0,0,0,0,0],
                        7:  [1,0,1,1,0,0,0,0,0,0,0],
                        8:  [1,0,0,1,1,0,0,0,0,0,0],
                        9:  [0,0,1,1,1,0,0,0,0,0,0],
                        10: [1,1,0,1,1,0,0,0,0,0,0],
                        11: [1,0,1,1,1,0,0,0,0,0,0],
                        12: [0,0,0,1,1,1,1,0,0,0,0],
                        13: [0,0,0,0,0,0,0,1,1,1,1],
                        14: [1,1,1,1,1,0,0,0,0,0,0],
                        15: [1,1,0,1,1,1,1,0,0,0,0],
                        16: [1,1,0,0,0,0,0,1,1,0,0],
                        17: [0,0,0,1,1,0,0,0,0,0,0],
                        18: [1,1,1,1,1,1,1,0,0,0,0],
                        19: [1,1,1,0,0,0,0,1,1,1,1]}
        self.rxlist = []
        

    
    def __read_sched(self):
        '''
        $SHEDを読み、使われているMODEを取得
        '''
        SCHED_DATA = self.vexdata['SCHED']

        count = 0
        SCHED_bindex = []
        SCHED_eindex = []
        for data in SCHED_DATA:
            if "scan" == data.strip()[0:4]:
                SCHED_bindex.append(count)
            elif "endscan" == data.strip()[0:7]:
                SCHED_eindex.append(count)
            count += 1
        SCHED_bindex.sort()
        SCHED_eindex.sort()
        use_mode = []

        SCHED_LIST = []
        for i in range(len(SCHED_bindex)):
            SCHED_TEXT = ""
            tmpSCHED = SCHED_DATA[SCHED_bindex[i]:SCHED_eindex[i]]
            for data in tmpSCHED:
                if "*" != data[0]:
                    SCHED_TEXT = SCHED_TEXT + data
            tmpSCHED = SCHED_TEXT.split(';')
            

            for data in tmpSCHED:
                if "mode=" in ''.join(data.split()):
                    tmp_mode = ''.join(data.split())[5:]
                
                if str("station=" + self.station_name) == str(data.split(':')[0].strip()):
                    if self.debag:
                        ut.UtilFunc.chkprint(tmp_mode)
                    use_mode.append(tmp_mode)

        SCHED_mode_list = []
        for i in range(len(SCHED_LIST)):
            SCHED_mode_list.append(SCHED_LIST[i][1])
        if self.debag:
            ut.UtilFunc.chkprint(SCHED_mode_list, use_mode)
        return use_mode

    def __read_mode(self):
        '''
        $MODEを読み、指定された望遠鏡で使用するFREQ, IF, BBCのモードを取得
        '''

        MODE_DATA  = self.vexdata['MODE']
        
        FreqMode = {}
        IFMode = {}
        BBCMode = {}

        # count = 0
        mode_bindex = []
        mode_eindex = []
        for i in range(len(MODE_DATA)):
            data = MODE_DATA[i]
            if "def" == data.split("*")[0].strip()[0:3]:
                mode_bindex.append(i)
                ModeName = data.split()[1].strip(';')
                j = i + 1
                while True:
                    data = MODE_DATA[j].split('*')[0]

                    if "ref" == data.split("*")[0].strip()[0:3]:
                        if "$FREQ" == data.split("*")[0].split()[1] and self.station_name in data:
                            tmp = data.split(":")[0]

                            FreqMode[ModeName] = tmp.split("=")[1].strip()
                        if "$IF" == data.split("*")[0].split()[1] and self.station_name in data:
                            tmp = data.split(":")[0]
                            IFMode[ModeName] = tmp.split("=")[1].strip()
                        if "$BBC" == data.split("*")[0].split()[1] and self.station_name in data:
                            tmp = data.split(":")[0]
                            BBCMode[ModeName] = tmp.split("=")[1].strip()

                    if "enddef" == data.split("*")[0].strip()[0:6]:
                        mode_eindex.append(j)
                        
                        break
                    j += 1

            # elif "enddef" == data.strip()[0:6]:
            #     mode_eindex.append(count)
            # count += 1

        if self.debag:
            ut.UtilFunc.chkprint(FreqMode)
            ut.UtilFunc.chkprint(IFMode)
            ut.UtilFunc.chkprint(BBCMode)

        mode_bindex.sort()
        mode_eindex.sort()

        return mode_bindex, mode_eindex, FreqMode, IFMode, BBCMode

        
    def __check_sched_and_mode(self, mode_bindex, mode_eindex, use_mode, FreqMode, IFMode):
        '''
        ScheduleとModeを比較し、スケジュールで指定されているモードの中で野辺山45ｍの周波数設定がされていないものがないかを確認
        '''
        MODE_LIST = []
        MODE_DATA  = self.vexdata['MODE']

        for i in range(len(mode_bindex)):
            MODE_TEXT = ""
            tmpMODE = MODE_DATA[mode_bindex[i]:mode_eindex[i]]
            for data in tmpMODE:
                if "*" != data[0]:
                    MODE_TEXT = MODE_TEXT + data

            tmpMODE = MODE_TEXT.split(';')
            for data in tmpMODE:
                if "def" in ''.join(data.split()):
                    MODE_LIST.append([])
                    MODE_LIST[i].append(data.split()[1])
                if "PROCEDURES=" in ''.join(data.split()):
                    MODE_LIST[i].append(''.join(data.split()).replace('=', ':').split(':')[1])

        for tmp_mode in use_mode:
            if not tmp_mode in FreqMode.keys():
                self.result_status["MatchScheduleMode"] = False
            if not tmp_mode in IFMode.keys():
                self.result_status["MatchScheduleMode"] = False
        else: self.result_status["MatchScheduleMode"] = True

        return None

    def __read_freq(self, FreqMode):
        '''
        &FREQに書かれた情報を取得
        '''

        FREQ_DATA = self.vexdata['FREQ']
        freq_val = []
        freq_sb = []
        freq_pol = []
        freq_BBC = []
        freq_range = []
        # break_counter = 0
        for i in range(len(FREQ_DATA)):
            if "def" == FREQ_DATA[i].strip()[0:3] and FREQ_DATA[i].split()[1].split(';')[0] in FreqMode.values():
                j = i + 1
                while "enddef" != FREQ_DATA[j].strip()[0:6] and j < len(FREQ_DATA) - 1:
                    if "chan_def" == FREQ_DATA[j].split("*")[0].strip()[0:8]:
                        try:
                            freq_val.append(float(FREQ_DATA[j].split(':')[1].strip("MHz"" ")))
                            freq_BBC.append(FREQ_DATA[j].split(':')[5].strip('&'' '))
                            if self.debag: ut.UtilFunc.chkprint(FREQ_DATA[j].split(':')[1].strip("MHz"" "))
                            freq_sb.append(FREQ_DATA[j].split(':')[2].strip() + "SB")
                            freq_range.append(float(FREQ_DATA[j].split(':')[3].strip("MHz"" ")))
                        except IndexError as e:
                            ut.UtilFunc.print_err_msg(True, e, "周波数情報を正しく読み込めませんでした", "$FREQセクションを確認してください")
                        try:
                            # 偏波設定の読み込み
                            if self.debag:
                                # ut.UtilFunc.chkprint(FREQ_DATA[j].split("*")[0])
                                ut.UtilFunc.chkprint(re.split(";|:", FREQ_DATA[j].split("*")[0]))
                            tmp_rx = re.split(";|:", FREQ_DATA[j].split("*"" ")[0])[7].strip("\n"" ")
                            
                            if self.debag:
                                ut.UtilFunc.chkprint(tmp_rx)
                            # if tmp_rx in self.polarized_inf.values():
                            count = 0
                            break_flag = False
                            for keys in self.polarized_inf.keys():
                                for val2 in self.polarized_inf[keys]:
                                    # print(val2)
                                    if val2.endswith(tmp_rx) or self.polarized_inf[keys] == val2:
                                        tmp_pol = re.split(";|:", FREQ_DATA[j].split("*")[0])[7].strip("\n"" ")
                                        if tmp_pol == ' ':
                                            raise IndexError
                                        freq_pol.append(tmp_pol)
                                        count += 1
                                        break_flag = True
                                    if break_flag:
                                        break
                                if break_flag:
                                    break

                            # chan_defのところの順番が正しくない場合
                            # print(count)
                            if count != 1: raise IndexError


                        except IndexError:
                            count = 0
                            for tmp_data in re.split(";|:", FREQ_DATA[j]):
                                if 'cp' in tmp_data:
                                    tmp_rx = tmp_data.strip('*'' ''\n')
                                elif 'lp' in tmp_data:
                                    tmp_rx = tmp_data.strip('*'' ''\n')
                                else:
                                    tmp_rx = False
                                # tmp_rx = re.fullmatch('.cp|.lp', tmp_data.strip('*').strip())
                                if self.debag:
                                    ut.UtilFunc.chkprint(tmp_rx)
                                
                                if tmp_rx:
                                    # print(tmp_rx.group())
                                    freq_pol.append(tmp_rx)
                                    if self.debag:
                                        ut.UtilFunc.chkprint(tmp_rx)
                                    count = 1
                                    break
                                
                            if count == 0:
                                freq_pol.append("")
                            # self.result_status["GetFreqSettingError"] = False
                    j += 1
        

        # if self.debag:
        #     ut.UtilFunc.chkprint(break_counter, freq_pol)

        if self.debag:
            ut.UtilFunc.chkprint(freq_val)
            ut.UtilFunc.chkprint(freq_pol)
            ut.UtilFunc.chkprint(self.static_freq)

        # ut.UtilFunc.print_err_msg("", break_counter > 1, "周波数の設定が複数ありあります")
        ut.UtilFunc.print_err_msg("", len(freq_val) > self.max_array_leng, "周波数設定の数が多すぎます。")

        return freq_BBC, freq_val, freq_pol, freq_sb, freq_range

    def __read_bbc(self, BBCMode):
        '''
        $BBCを読む
        '''

        BBC_comb = {}

        for i, data in enumerate(self.vexdata['BBC']):
            if "def" == data.strip()[0:3] and data.split()[1].split(';')[0] in BBCMode.values():
                j = i + 1
                # print(len(self.vexdata['BBC']) - 1)
                while j < len(self.vexdata['BBC']) - 1 and "enddef" != self.vexdata['BBC'][j].strip()[0:6]:
                    data = self.vexdata['BBC'][j]
                    # print(j)
                    j += 1
                    # print(re.split('[=:]', data))
                    try:
                        if re.split('[=:]', data)[0].strip() == 'BBC_assign':
                            BBC_comb[re.split('[=:]', data)[1].strip('&'' ''\n')] = re.split('[=:]', data)[3].strip('&'' ''\n'';')
                    except IndexError as e:
                        ut.UtilFunc.print_err_msg(True, e, "BBCの情報を正しく読み込めませんでした。", "$BBCセクションを確認してください")



        if self.debag:
            ut.UtilFunc.chkprint(BBC_comb)

        return BBC_comb

    def __read_if(self, IFMode):
        '''
        $IFを読む
        '''

        IF_DATA = self.vexdata['IF']

        IF_val = []
        IF_sb = []
        IF_comb = {}
        for i in range(len(IF_DATA)):
            if "def" == IF_DATA[i].strip()[0:3] and IF_DATA[i].split()[1].split(';')[0] in IFMode.values():
                j = i + 1
                while j < len(IF_DATA) - 1 and "enddef" != IF_DATA[j].strip()[0:6]:
                    
                    if "if_def" == IF_DATA[j].split("*")[0].strip()[0:6]:
                        
                        try:
                            IF_val.append(float(IF_DATA[j].split(':')[3].strip("MHz"" ")))
                            if self.debag:
                                ut.UtilFunc.chkprint(IF_DATA[j].split(':')[3].strip("MHz"" "))
                                ut.UtilFunc.chkprint(re.split('[=:;]', IF_DATA[j]))
                            IF_sb.append(IF_DATA[j].split(':')[4].strip() + "SB")

                            IF_comb[re.split('[=:;]', IF_DATA[j])[1].strip(' ''&')] = [float(re.split('[=:;]', IF_DATA[j])[4].strip(' ''&''MHz')), re.split('[=:;]', IF_DATA[j])[5].strip(' ''&') + 'SB']
                        except IndexError as e:
                            ut.UtilFunc.print_err_msg(True, e, "L.O.の設定を正しく読み込めませんでした", "$IFセクションを確認してください")

                    j += 1
    

        if self.debag:
            ut.UtilFunc.chkprint(IF_val)
            ut.UtilFunc.chkprint(IF_comb)

        return IF_comb
    def __overwrite_bbc_with_if(self, BBC_comb, freq_BBC, IF_comb):
        '''
        BBCをIFの内容に書き換え
        '''
        for key in BBC_comb.keys():
            tmp = IF_comb[BBC_comb[key]]
            if not BBC_comb[key] in tmp:
                tmp.append(BBC_comb[key])
            BBC_comb[key] = tmp

        for i, val in enumerate(freq_BBC):
            freq_BBC[i] = BBC_comb[val]

        if self.debag:
            ut.UtilFunc.chkprint(BBC_comb)
            ut.UtilFunc.chkprint(freq_BBC)
        return freq_BBC

    def __dist_rx_and_pol(self, freq_val, freq_pol, freq_sb, freq_BBC, freq_range):
        '''
        受信機の判定と偏波の判定
        '''
        # Rx_Type_dec = {}
        tracking_freq = []
        rx_list = [0] * len(freq_val)
        row_rx_name = [0] * len(freq_val)
        rx_sb_name = []
        # row_rx_name = []
        comb_rx_freq = {}

        try:
            for i in range(len(freq_val)):  
                for tmp_key in self.rx_inf.keys():
                    count = 0
                    break_flag = False
                    # tmp_row_rx_name = ''
                    if self.debag:
                        ut.UtilFunc.chkprint(freq_val, freq_pol, tmp_key)
                    if math.fabs(float(freq_val[i]) - 1024 * float(self.rx_inf[tmp_key])) < float(
                            1024 * self.rx_range[tmp_key]):

                        tmp_pol = tmp_key + freq_pol[i]
                        tracking_freq.append(1024 * self.rx_inf[tmp_key])
                        # tmp_row_rx_name = tmp_key
                        if self.debag:
                            ut.UtilFunc.chkprint(tmp_pol)

                        
                        for tmp_key2 in self.polarized_inf.keys():
                            for val in self.polarized_inf[tmp_key2]:
                                # print(val)
                                if tmp_pol == val:
                                    comb_rx_freq[tmp_key2] = tmp_key
                                    rx_list[i] = tmp_key2
                                    row_rx_name[i] = tmp_key
                                    count += 1
                                    if self.debag:
                                        ut.UtilFunc.chkprint(val)
                                    break_flag = True

                                if break_flag:
                                    break
                            if break_flag:
                                break
                        # if break_flag: break
                        # if count == 0:
                        #     for tmp_key2 in self.other_polarized_inf.keys():
                        #         if tmp_pol == self.other_polarized_inf[tmp_key2]:
                        #             rx_list[i] = tmp_key2
                        #             count += 1

            if self.debag:
                ut.UtilFunc.chkprint(freq_val)

        except ValueError as e:
            ut.UtilFunc.print_err_msg(True, e, "周波数情報を正しく読み込めませんでした", "$FREQセクションを確認してください")

        if self.debag:
            ut.UtilFunc.chkprint(rx_list)

        try:
            for tmp_name1, tmp_name2, tmp_val, tmp_BBC , tmp_range, rx in zip(rx_list, freq_sb, freq_val, freq_BBC, freq_range, row_rx_name):
                rx_sb_name.append([tmp_name1, tmp_name2, float(tmp_val), tmp_BBC, tmp_range, rx])
        except TypeError as e:
            ut.UtilFunc.print_err_msg(True, e, "偏波の設定がされていないものがあります", "vexファイルの周波数設定の項目で偏波が設定されているか確認してください")


        if self.debag:
            ut.UtilFunc.chkprint(rx_sb_name)

        


        num_of_rx = {}
        for tmp in self.rx_comb_index.keys():
            if tmp.split('-')[0] in num_of_rx.keys():
                num_of_rx[tmp.split('-')[0]] += 1
            else:
                num_of_rx[tmp.split('-')[0]] =1
        if self.debag:
            ut.UtilFunc.chkprint(num_of_rx)
            ut.UtilFunc.chkprint(rx_sb_name)

        return comb_rx_freq, rx_sb_name, num_of_rx



    def __overwrite_sideband(self, rx_sb_name):
        '''
        SideBandをすべてLSBに書き換え
        '''
        tmp_rx_list = copy.copy(rx_sb_name)
        for i, lists in enumerate(rx_sb_name):
            if lists[0][0:2] == 'TZ':
                tmp_rx_list[i][1] = 'LSB'
                tmp_rx_list[i][3][1] = 'LSB'
            else:
                tmp_rx_list[i][1] = 'USB'
                tmp_rx_list[i][3][1] = 'USB'
            # tmp_rx_list[i][3][1] = 'USB'

        if self.debag:
            ut.UtilFunc.chkprint(tmp_rx_list)

        return tmp_rx_list

    def __set_freq(self, rx_sb_name):
        
        freq_dic = {}
        # ut.UtilFunc.chkprint(rx_sb_name)
        if self.debag:
            ut.UtilFunc.chkprint(rx_sb_name)
        try:
            for i, lists in enumerate(rx_sb_name):
                # print(lists[3][2] + lists[0])
                if not lists[3][2] + lists[0] in freq_dic.keys():
                    freq_dic[lists[3][2] + lists[0]] = lists
                    # ut.UtilFunc.chkprint(lists)
                else:
                    freq_dic[lists[3][2] + lists[0]][4] += lists[4]
        except TypeError as e:
            ut.UtilFunc.print_err_msg(True, e, "周波数情報を正しくないようです", "vexファイルの$FREQセクションの周波数が正しいか確認してください")
        # ut.UtilFunc.chkprint(freq_dic)
        if self.debag:
            ut.UtilFunc.chkprint(freq_dic)
        return list(freq_dic.values())

    def __set_h40(self, rx_sb_name):
        '''
        42GのところがすべてLcpか範囲が2048MHｚいないの場合、Z45をH40に書き換え
        '''
        count_h40 = 0
        for s in rx_sb_name:
            if s[0] == 'Z45V':
                count_h40 += 1
        if self.debag:
            ut.UtilFunc.chkprint(rx_sb_name)
        tmp_rx_list = copy.copy(rx_sb_name)
        for i, lst in enumerate(rx_sb_name):
            # print(lst)
            # print(lst[2][1] - lst[2][0] <= 2048)
            if lst[0] == 'Z45V' and lst[2][1] - lst[2][0] <= 2048 and count_h40 <= 1:
                # print(lst[0])
                tmp_rx_list[i][0] = 'H40'
                tmp_rx_list[i][5] = 'H40'
                # print(' ')
                # print(tmp_rx_list[i])
        if self.debag:
            ut.UtilFunc.chkprint(tmp_rx_list)
        return tmp_rx_list

            
    def __adjust_bandwidth(self, rx_sb_name):
        '''
        読み込んだ周波数を適切な帯域幅になるように調整
        '''

        # 隣接する周波数を結合
        freq_list = []
        freq_list_index = 0
        tmp_range = 0
        count = 0


        tmp_rx_sb_name = copy.copy(rx_sb_name)
        if self.debag:
            ut.UtilFunc.chkprint(tmp_rx_sb_name)
        for i, lists in enumerate(rx_sb_name):
            if lists[1] == 'USB':
                tmp_rx_sb_name[i][2] = [float(lists[2]), float(lists[2]) + float(lists[4])]
            elif lists[1] == 'LSB':
                tmp_rx_sb_name[i][2] = [float(lists[2]) - float(lists[4]), float(lists[2]),]

        

        freq_list.append(tmp_rx_sb_name[0])
        tmp_range = freq_list[freq_list_index][4]
        if self.debag:
            ut.UtilFunc.chkprint(freq_list)
        for i in range(1, len(tmp_rx_sb_name)):
            # 
            if self.debag:
                ut.UtilFunc.chkprint2('tmp_rx_sb_name[' + str(i) + ']', tmp_rx_sb_name[i])
            
            # if  1024 * self.rx_range[tmp_rx_sb_name[i][5]] >= math.fabs(tmp_rx_sb_name[i][2][0] - freq_list[freq_list_index][2][1]) and freq_list[freq_list_index][0:2] == tmp_rx_sb_name[i][0:2] and math.fabs(tmp_rx_sb_name[i][2][1] - freq_list[freq_list_index][2][0]) < 1024:
            
            # if  freq_list[freq_list_index][0:2] == tmp_rx_sb_name[i][0:2] and math.fabs(tmp_rx_sb_name[i][2][1] - freq_list[freq_list_index][2][0]) <= 1024:
            # if  freq_list[freq_list_index][0:2] == tmp_rx_sb_name[i][0:2] and math.fabs(tmp_rx_sb_name[i][2][1] - freq_list[freq_list_index][2][0]) <= 2048:
            if  freq_list[freq_list_index][0:2] == tmp_rx_sb_name[i][0:2]:
                if self.debag: 
                    ut.UtilFunc.chkprint2('tmp_rx_sb_name[' + str(i - 1) + '][2]', tmp_rx_sb_name[i - 1][2])
                    ut.UtilFunc.chkprint2('tmp_rx_sb_name[' + str(i) + '][2]', tmp_rx_sb_name[i][2])
                # tmp_rx_sb_name[i][2][1] = tmp_rx_sb_name[i][2][0]
                # freq_list[freq_list_index][2][0] = tmp_rx_sb_name[i - 1][2][0]
                freq_list[freq_list_index][2][1] = tmp_rx_sb_name[i][2][1]
                tmp_range += tmp_rx_sb_name[i][4]
                if self.debag: 
                    # ut.UtilFunc.chkprint2('tmp_rx_sb_name[' + str(i - 1) + '][3]', tmp_rx_sb_name[i - 1][3])
                    ut.UtilFunc.chkprint2('freq_list[' + str(freq_list_index) + ']', freq_list[freq_list_index])
                count += 1
            else:
                freq_list.append(tmp_rx_sb_name[i])
                if count != 0:
                    freq_list[freq_list_index][4] = tmp_range
                freq_list_index += 1
                tmp_range = freq_list[freq_list_index][4]
        # if len(freq_list) == 1:
        freq_list[freq_list_index][4] = tmp_range
        if self.debag:
            ut.UtilFunc.chklistprint('freq_list', freq_list)
            ut.UtilFunc.chkprint(self.rx_range_list)
        # tmp_rx_sb_name = 
        tmplst = []
        count = 0
        for i, lst in enumerate(copy.deepcopy(freq_list)):
            count += 1
            if lst[4] > 2048:
                a = int(lst[4] / 2048) + 1
                range_ini = lst[2][0]
                for j in range(0, a):
                    tmp_lst = copy.deepcopy(lst)
                    if self.debag: ut.UtilFunc.chkprint(tmp_lst)
                    tmp_width = lst[4] / a
                    tmp_lst[4] = tmp_width
                    tmp_lst[2] = [range_ini, range_ini + tmp_width]
                    tmplst.append(tmp_lst)
                    if self.debag: ut.UtilFunc.chkprint(j, a, tmp_width, range_ini, tmp_lst)
                    range_ini += tmp_width
                    
            else:
                tmplst.append(lst)
        freq_list = copy.deepcopy(tmplst)
        if self.debag:
            ut.UtilFunc.chklistprint('tmplst', tmplst)
            ut.UtilFunc.chklistprint('freq_list', freq_list)
            # ut.UtilFunc.chklprint(freq_list)

        # 周波数のチェックと分割
        
        # add_list = []
        new_freq_list = Vex2Ndevice.__set_h40(self, freq_list)
        pop_lis = []
        for j, lists in enumerate(freq_list):
            # print(self.rx_range_list)
            # print(self.rx_range_list)
            try:
                # print(lists)
                n = math.fabs(lists[2][1] - lists[2][0]) / 2048
                # print(self.rx_width[lists[5]])
            except KeyError as e:
                ut.UtilFunc.print_err_msg(True, e, "偏波の設定方法が間違っています", "vexファイルの周波数設定の項目で偏波が設定されているか確認してください")
            # print(n)
            if n > 1:
                pop_lis.append(j)
                # print(a)
                if self.debag: ut.UtilFunc.chkprint(n)
                for i in range(0, int(n)):
                    begin_val = float(lists[2][0] + (lists[2][1] - lists[2][0]) * i / int(n))
                    end_val = float(lists[2][0] + (lists[2][1] - lists[2][0]) * (i + 1) / int(n))
                    tmp_add = copy.copy(lists)
                    if self.debag:
                        ut.UtilFunc.chkprint(begin_val, end_val)
                    tmp_add[2] = [begin_val, end_val]
                    ut.UtilFunc.chkprint(tmp_add[4])
                    tmp_add[4] = tmp_add[4] / n
                    new_freq_list.append(tmp_add)
        freq_list = []
        # print(pop_lis)
        for i, lis in enumerate(new_freq_list):
            if not i in pop_lis:
                freq_list.append(copy.copy(lis))


        # freq_list = copy.copy(new_freq_list)

        if self.debag:
            ut.UtilFunc.chkprint(freq_list)
            ut.UtilFunc.chkprint(new_freq_list)

        for i, lists in enumerate(freq_list):
            freq_list[i][2] = freq_list[i][2][0]
            continue


            if lists[1] == 'USB':
                freq_list[i][2] = lists[2][0] + 0.5 * math.fabs(self.rx_range_list[lists[0]][1] - self.rx_range_list[lists[0]][0]) * 1024
            if lists[1] == 'LSB':
                freq_list[i][2] = lists[2][1] - 0.5 * math.fabs(self.rx_range_list[lists[0]][1] - self.rx_range_list[lists[0]][0]) * 1024
                



        if self.debag:
            ut.UtilFunc.chkprint(freq_list)
            # print(self.rx_range_list)
        return freq_list




    def __adjust_lo_freq(self, freq_list):
        '''
        LOの周波数の値を野辺山で使えるように調整
        '''
        
        tmp_list = copy.copy(freq_list)
        if self.debag:
            # print('\n'.join(map(str, freq_list)))
            ut.UtilFunc.chklistprint('freq_list', freq_list)
        for i, lists in enumerate(freq_list):
            # tmp_list[i][3][0] = lists[3][0] + 0.5 * math.fabs(self.rx_range_list[lists[0]][1] - self.rx_range_list[lists[0]][0]) * 1024
            tmp_list[i][3][0] = lists[3][0] + 0.5 * math.fabs(lists[4])

        return tmp_list

    def __change_sb_name(self, freq_list):
        '''
        それぞれのSideBand(USB or LSB)のLowなのかHighなのか調べる
        '''
        # 1st L.O.を入れた後の周波数で判別する
        if self.debag:
            ut.UtilFunc.chkprint(freq_list)
        tmp_list = copy.copy(freq_list)
        for i, lists in enumerate(freq_list):
            if math.fabs(self.rx_range_list[lists[0]][1] - self.rx_range_list[lists[0]][0]) * 1024 == 1024:
                tmp_list[i][1] = tmp_list[i][1] + '-L'
                # tmp_list[i][3][1] = tmp_list[i][3][1] + '-L'
            elif math.fabs(self.rx_range_list[lists[0]][1] - self.rx_range_list[lists[0]][0]) * 1024 == 2048:
                if lists[2] - lists[3][0] <= 1024 + self.rx_range_list[lists[0]][0]:
                    tmp_list[i][1] = tmp_list[i][1] + '-L'
                    # tmp_list[i][3][1] = tmp_list[i][3][1] + '-L'
                else:
                    tmp_list[i][1] = tmp_list[i][1] + '-H'
                    # tmp_list[i][3][1] = tmp_list[i][3][1] + '-H'


        return freq_list


    def __check_type(self, num_of_rx, freq_list):
        '''
        使用するTypeの判定
        '''
        # ut.UtilFunc.chkprint(freq_list)
        # ut.UtilFunc.chkprint(num_of_rx)
        tmp_type = [0] * len(self.rx_comb_index.keys())

        tmp_rx3 = dict.fromkeys(num_of_rx)
        for tmp_val in tmp_rx3:
            tmp_rx3[tmp_val] = []

        for tmp_val in freq_list:
            tmp_rx3[tmp_val[0]].append(tmp_val[1:])
        # ut.UtilFunc.chkprint(tmp_rx3)

        tmp_rx_comb = dict.fromkeys(num_of_rx)
        for tmp_key in num_of_rx:
            tmp_rx_comb[tmp_key] = len(tmp_rx3[tmp_key])

        use_polarized_comb = {}
        # ut.UtilFunc.chkprint(tmp_rx3)
        for key in tmp_rx3:
            if len(tmp_rx3[key]) == 1 and num_of_rx[key] == 1:
                use_polarized_comb[key] = tmp_rx3[key][0]
                tmp_type[self.rx_comb_index[key] - 1] = 1
            else:
                tmp_list = sorted(tmp_rx3[key])
                # ut.UtilFunc.chkprint(tmp_list)
                for i in range(0, len(tmp_list)):
                    use_polarized_comb[key + '-' + str(i + 1)] = tmp_list[i]
                    tmp_type[self.rx_comb_index[key + '-' + str(i + 1)] - 1] = 1
                    # if i == 0:
                    #     use_polarized_comb[key] = tmp_list[i]
                    #     tmp_type[self.rx_comb_index[key] - 1] = 1
                    # else:
                    #     use_polarized_comb[key + '-' + str(i + 1)] = tmp_list[i]
                    #     tmp_type[self.rx_comb_index[key + '-' + str(i + 1)] - 1] = 1







        if self.debag:
            ut.UtilFunc.chkprint(tmp_rx3)
            ut.UtilFunc.chkprint(tmp_rx_comb)
            ut.UtilFunc.chkprint(use_polarized_comb)
            ut.UtilFunc.chkprint(tmp_type)


        if tmp_type in self.rx_comb.values():
            for key in self.rx_comb:
                if tmp_type == self.rx_comb[key]:
                    self.type_no = key
            print('>>>    rx Mode is "' + str(self.type_no) + '"')
        else:
            count2 = 0
            for key in self.rx_comb:
                if self.debag:
                        ut.UtilFunc.chkprint(self.rx_comb[key])
                count = 0
                for i in range(0, len(tmp_type)):
                    if self.rx_comb[key][i] - tmp_type[i] >= 0:
                        count += 1
                if self.debag:
                    ut.UtilFunc.chkprint2('count', count)
                    ut.UtilFunc.chklprint(tmp_type)
                if count == len(tmp_type):
                    self.type_no = key
                    count2 += 1
                    print('rx Mode is "' + str(self.type_no) + '"')
                    print('')
                    break
            

            if self.debag:
                ut.UtilFunc.chkprint(count2)
            if count2 == 0:
                ut.UtilFunc.print_err_msg(False, '', "受信機の組み合わせが正しくありません")
        if self.debag: print(ut.pycolor.REVERCE + 'rx Mode is "' + str(self.type_no) + '"' + ut.pycolor.END)

        return use_polarized_comb

    def __sort_array(self, use_polarized_comb):
        '''
        正しいArrayの並びにする
        '''
        rxlist = []

        array_freq_rx_list = [[None,None,None, None, -1, None, None, None, None]] * self.max_array_leng
        self.use_array_list = {}
     
        # array_freq_rx_list = [[None,None,None, None, -1, None, None, None, None]] * self.max_array_leng
        # [受信機名, SideBand, 静止周波数, vexファイルに記載された周波数, 受信機のindex, 受信機名（詳細）, IFの設定, pointing or vlbi]
        for key in use_polarized_comb.keys():
            if self.debag:
                ut.UtilFunc.chkprint(key)
                ut.UtilFunc.chkprint2('self.array_num[' + key + ']', self.array_num[key])
                ut.UtilFunc.chkprint2('use_polarized_comb[' + key + ']', use_polarized_comb[key])
            tmp_freq = use_polarized_comb[key][1]
            
            d = math.fabs(float(1000 * self.static_freq[0]) - float(tmp_freq))
            dcount = 0
            for i in range(1, len(self.static_freq)):
                if math.fabs(1000 * float(self.static_freq[i]) - float(tmp_freq)) < d:
                    d = math.fabs(1000 * float(self.static_freq[i]) - float(tmp_freq))
                    dcount = i

            tmp_freq = 1000 * self.static_freq[dcount]

            if not [key.split('-')[0], use_polarized_comb[key][2][1], tmp_freq / 1000] in rxlist:
                # print([key.split('-')[0], use_polarized_comb[key][0]])
                rxlist.append([key.split('-')[0], use_polarized_comb[key][2][1], tmp_freq / 1000])

            num = rxlist.index([key.split('-')[0], use_polarized_comb[key][2][1], tmp_freq / 1000]) 


            array_freq_rx_list[self.array_num[key] - 1] = copy.copy([key.split('-')[0], use_polarized_comb[key][2][1], tmp_freq / 1000, use_polarized_comb[key][1], num, key, use_polarized_comb[key][2], use_polarized_comb[key][3]])

        tmp_vlbi_array_freq_rx_list = []
        if self.debag:
            ut.UtilFunc.chkprint2('array_freq_rx_list[self.array_num[key] - 1]', array_freq_rx_list[self.array_num[key] - 1] )
        
        for i, lists in enumerate(array_freq_rx_list):
            if not lists[4] == -1:
                if self.debag:ut.UtilFunc.chkprint(lists)
                tmp_vlbi_array_freq_rx_list.append(lists)
        if self.debag:
            ut.UtilFunc.chkprint(tmp_vlbi_array_freq_rx_list)
            print('\n     '.join(map(str, tmp_vlbi_array_freq_rx_list)))

        if self.pointing_flag:
            for i, lists in enumerate(tmp_vlbi_array_freq_rx_list):
                if lists[5] in self.pointing_array_num.keys():
                    tmp_num = self.pointing_array_num[lists[5]]
                    tmp_list = lists
                    if self.debag:ut.UtilFunc.chkprint(tmp_list)


                    if self.debag:
                        ut.UtilFunc.chkprint(array_freq_rx_list[tmp_num-1])
                        ut.UtilFunc.chkprint(tmp_num - 1)
                    array_freq_rx_list[tmp_num-1] = copy.copy(tmp_list)

        if self.debag:
            ut.UtilFunc.chkprint2('array_freq_rx_list', array_freq_rx_list)



        if self.debag:
            ut.UtilFunc.chkprint2('array_freq_rx_list', array_freq_rx_list)

            ut.UtilFunc.chkprint(rxlist)

        return rxlist, array_freq_rx_list

            # ut.UtilFunc.chkprint(pointing_rxlist)
    def __set_rest_freq(self, array_freq_rx_list):
        '''
        RESFREQを設定
        '''

        restf = []
        # ut.UtilFunc.chkprint(array_freq_rx_list)
        tmp_lis = copy.copy(array_freq_rx_list)
        for i, lis in enumerate(array_freq_rx_list):
            tmp_lis[i].append(lis[2])

        # for i, lists in enumerate(array_freq_rx_list):
        #     print('i = ' + str(i))
        #     # tmp_resfreq = self.res_freq[0]
        #     if i + 1 in self.array_num.values() and lists[4] != -1:
        #         val = Decimal(str(float(lists[3] + lists[7] / 2) / 1000)).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
        #         tmp_lis[i].append(float(val))
        #         continue
        #     elif i + 1 in self.pointing_array_num.values():
        #         restf = copy.copy(self.pointing_res_freq)
        #     else:
        #         restf = []


        #     if lists[4] == -1:
        #         tmp_lis[i].append(None)
        #         continue
        #     res = restf[0]
        #     min_d = math.fabs((lists[3] + lists[7] / 2) / 1000 - restf[0])
        #     # print(self.res_freq[1:])
        #     for tmp_resfreq in restf[1:]:
        #         d = math.fabs((lists[3] + lists[7] / 2) / 1000 - tmp_resfreq)
        #         if min_d > d:
        #             res = tmp_resfreq
        #             min_d = d
        #     ut.UtilFunc.chkprint2('res', res)
        #     print(i, tmp_lis[i])
        #     # tmp_lis[i].append(res)
        #     tmp_lis[i].append(tmp_lis[i][2])
        #     print(i, tmp_lis[i])
        return tmp_lis

    def __overwrite_freqsetting(self, array_freq_rx_list, rxlist):
        '''
        各種設定をある固定値に書き換え
        '''
        tmp_list = copy.copy(array_freq_rx_list)
        tmp_array_index = None
        for i, lis in enumerate(rxlist):
            if lis[0] == 'H22R':
                tmp_array_index = i
        if tmp_array_index == None:
            rxlist.append(['H22R', 'USB-L'])
            tmp_array_index = len(rxlist) - 1
        if self.pointing_flag:
            tmp_list[0] = ['H22R', 'USB-L', 22.8, 22480.0, tmp_array_index, 'H22R', [16800.0, 'USB', None], 1024.0, 22.23508]
            tmp_list[1] = ['H22R', 'USB-L', 22.8, 22480.0, tmp_array_index, 'H22R', [16800.0, 'USB', None], 1024.0, 22.23508]
        # for i, lists in enumerate(array_freq_rx_list):
        #     if lists[0] == 'H40':
        #         tmp_list[i][8] = 43.12207
        #         tmp_list[i][9] = 43.12207
        #     # elif  lists[4] != -1: 
        return tmp_list

    def __copy_low2high(self, array_freq_rx_list):
        tmp_array_num = {}
        tmp_lis = copy.copy(array_freq_rx_list)
        for s in self.array_num:
            if s.split('-')[0] in tmp_array_num.keys():
                tmp_array_num[s.split('-')[0]] += 1
            else:
                tmp_array_num[s.split('-')[0]] = 1
        # ut.UtilFunc.chkprint(tmp_array_num)

        for keys in tmp_array_num.keys():

            if tmp_array_num[keys] > 1 and tmp_lis[self.array_num[keys + '-1'] - 1][0] == keys:
                # print(self.array_num[keys + '-1'] - 1)
                # print(tmp_lis[self.array_num[keys + '-1'] - 1])
                # print(tmp_lis[self.array_num[keys + '-1'] - 1][0])
                # ut.UtilFunc.chkprint(keys)
                for i in range(1, tmp_array_num[keys]):
                    j = self.array_num[keys + '-' + str(i + 1)] - 1
                    if tmp_lis[j][0] == None:
                        # print('j=' + str(j))
                        tmp_lis[j] = tmp_lis[self.array_num[keys + '-1'] - 1]
        # print(tmp_lis)
        return tmp_lis

    def __set_pfreq(self, array_list, rxlist):
        arraylst = copy.copy(array_list)
        tmp = []
        index_tmp = None
        for key in self.pointing_array_num.keys():
            for i, s in enumerate(rxlist):
                if key == s[0]:
                    tmp = s
                    index_tmp = i
                    break
            # print(self.pointing_array_num[key])

            arraylst[self.pointing_array_num[key] - 1] = [key, 'USB', tmp[2], self.pfreq[key] * 1000, i, key, [None, 'USB', None], 0, self.pfreq[key]]
            # arraylst[self.pointing_array_num[key] - 1] = [key, 'USB', tmp[2], self.pfreq[key] * 1000, i, key, [None, 'LSB', None], 0, self.pfreq[key]]
            # if self.debag: ut.UtilFunc.chkprint([key, 'USB-L', tmp[2], None, i, key, [None, 'USB', None], None, self.pfreq[key]])

        return arraylst


    def __print_rx_list(self, rxlist, array_freq_rx_list):
        '''
        書き出す情報の表示
        '''


        # def __print_array_list(array_freq_rx_list, rxlist, 'VLBI'):
        print(ut.pycolor.UNDERLINE + "Freqency Setting for " + 'VLBI' + ut.pycolor.END)
        if self.debag:
            ut.UtilFunc.chkprint(array_freq_rx_list)
            ut.UtilFunc.chkprint(rxlist)
            # print('--------------------------------------------------------')
            # print("Array  Freqency[GHz]  rx  Band  VexFileFreq  index　　 LO Set")
        # else:
            # print('-------------------------------------------------')
        print("Array 1stLO[GHz] rxname  Band rx_No CenterFreq[MHz]")
        for i, lists in enumerate(array_freq_rx_list):
            # print(lists)
            # if self.debag:
            #     # print(type(lists[5]))
            #     # print(lists[6])
            #     if lists[6] != None : tmp = ':'.join(map(str,lists[6]))
            #     else: tmp = ''
            #     print('{0:>5}  {1:>13.10}  {2:>8}  {3:>4}  {4:>11.10}  {5:>5}  {6:>9}'.format(i + 1, str(lists[2]),str(lists[0]), str(lists[1]), str(lists[3]), str(lists[4] + 1), tmp))
            # else:
            if lists[4] == -1:
                tmp_num = 'None'
                tmp_cent = 'None'
                first_LO = 'None'
            else:
                tmp_num = lists[4] + 1
                tmp_cent = lists[3] + lists[7] / 2
                first_LO = lists[2] - 6
            if i + 1 in self.pointing_array_num.values():
                print('   {0} {1:>10.10} {2:>6}  {3:>4} {4:>5} {5}'.format(ut.pycolor.RED + str(i + 1).zfill(2) + ut.pycolor.END, str(first_LO),str(lists[0]), str(lists[1]), tmp_num, str(tmp_cent)))
            else:
                print('   {0} {1:>10.10} {2:>6}  {3:>4} {4:>5} {5}'.format(str(i + 1).zfill(2), str(first_LO),str(lists[0]), str(lists[1]), tmp_num, str(tmp_cent)))
        print('(' + ut.pycolor.RED + 'Red array number' + ut.pycolor.END + ' is Pointing)')
        if self.debag:
            print('------------------')
            for i, lists in enumerate(array_freq_rx_list):
                print(str(i + 1).zfill(2) + ': ' + ', '.join(map(str, lists)))

        print(ut.pycolor.UNDERLINE + "rx Setting for " + 'VLBI' + ut.pycolor.END)
        for i, lists in enumerate(rxlist):
            print('{0:>5}  {1:>8}  {2:>4}'.format(i + 1, str(lists[0]),str(lists[1])))
        # print_array_list(array_freq_rx_list, rxlist, 'VLBI')

        return None

    def __make_export_line(self, rxlist, comb_rx_freq, array_freq_rx_list):
        '''
        書き出すパラｰメータを代入
        '''

        out_data = []
        out_data.append("NOBS_VERSION_DEVICE=" + str(self.nobs_version))
        # FE...
        for i in range(0, 8):
            if i < len(rxlist):
                out_data.append('FE' + str(i + 1).zfill(2) + '=' + rxlist[i][0])
            else:
                out_data.append('FE' + str(i + 1).zfill(2) + '=')
        # IF...
        for i in range(0, 8):
            if i < len(rxlist):
                # out_data.append('IF' + str(i + 1).zfill(2) + '=' + rxlist[i][1])
                if rxlist[i][1] == 'USB':
                    out_data.append('IF' + str(i + 1).zfill(2) + '=USB-L')
                elif rxlist[i][1] == 'LSB':
                    out_data.append('IF' + str(i + 1).zfill(2) + '=LSB-L')
            else:
                out_data.append('IF' + str(i + 1).zfill(2) + '=')
        # TRFREQ
        # print(comb_rx_freq)
        # print(rxlist)
        for i in range(0, 8):
            if i < len(rxlist):
                # out_data.append('TRFREQ' + str(i + 1).zfill(2) + '=' + str(self.rx_inf[comb_rx_freq[rxlist[i][0]]]))
                out_data.append('TRFREQ' + str(i + 1).zfill(2) + '=' + str(self.rx_inf[comb_rx_freq[rxlist[i][0]]]))
            else:
                out_data.append('TRFREQ' + str(i + 1).zfill(2) + '=')

        for i in range(0, 8):
            out_data.append('LOFREQ' + str(i + 1).zfill(2) + '=')

        for i in range(0, 8):
            if i < len(rxlist):
                out_data.append('IFFREQ' + str(i + 1).zfill(2) + '=' + str(self.IFFREQ[i]))
            else:
                out_data.append('IFFREQ' + str(i + 1).zfill(2) + '=')

        out_data.append('SYNFENUM=1,3,4,5')

        for i in range(0, self.max_array_leng):
            if i < len(array_freq_rx_list) and array_freq_rx_list[i][4] != -1:
                out_data.append('FEID_IF' + str(i + 1).zfill(2) + '=' + 'FE' + str(array_freq_rx_list[i][4] + 1).zfill(2))
            else:
                out_data.append('FEID_IF' + str(i + 1).zfill(2) + '=')

        for i in range(0, 8):
            out_data.append('V_FE' + str(i + 1).zfill(2) + '=' + 'False')

        for i in range(0, 8):
            out_data.append('V_IF' + str(i + 1).zfill(2) + '=' + 'False')

        for i in range(0, 8):
            if i < len(rxlist):
                out_data.append('V_TRFREQ' + str(i + 1).zfill(2) + '=' + 'True')
            else:
                out_data.append('V_TRFREQ' + str(i + 1).zfill(2) + '=' + 'False')

        for i in range(0, 8):
            if i < len(rxlist):
                if rxlist[i][0] != 'H40':
                    out_data.append('V_IFFREQ' + str(i + 1).zfill(2) + '=' + 'True')
                else:
                    out_data.append('V_IFFREQ' + str(i + 1).zfill(2) + '=' + 'False')
            else:
                out_data.append('V_IFFREQ' + str(i + 1).zfill(2) + '=' + 'False')

        for i in range(0, self.max_array_leng):
            out_data.append('V_FEID_IF' + str(i + 1).zfill(2) + '=' + 'False')

        for i in range(0, self.max_array_leng):
            if i < len(array_freq_rx_list) and array_freq_rx_list[i][4] != -1:
                out_data.append('V_ATT' + str(i + 1).zfill(2) + '=' + 'True')
            else:
                out_data.append('V_ATT' + str(i + 1).zfill(2) + '=' + 'False')

        for i in range(0, self.max_array_leng):
            if i < len(array_freq_rx_list) and array_freq_rx_list[i][4] != -1:
                out_data.append('ATT' + str(i + 1).zfill(2) + '=' + str(self.att[i]))
            else:
                out_data.append('ATT' + str(i + 1).zfill(2) + '=')


        out_data.append('FE_PARAM_FILE=')
        out_data.append('IF_SWBOX_ID=014')
        out_data.append('DEV_NOTE=' + self.DEV_NOTE)

        for i in range(0, 32):
            if i < len(array_freq_rx_list) and array_freq_rx_list[i][4] != -1:
                out_data.append('RSFREQ' + str(i + 1).zfill(2) + '=' + str(Decimal(str((array_freq_rx_list[i][3] + array_freq_rx_list[i][7] / 2) * 1E-3)).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)))
            else:
                out_data.append('RSFREQ' + str(i + 1).zfill(2) + '=')

        for i in range(0, 32):
            if i < len(array_freq_rx_list) and array_freq_rx_list[i][4] != -1:
                out_data.append('USE' + str(i + 1).zfill(2) + '=' + 'True')
            else:
                out_data.append('USE' + str(i + 1).zfill(2) + '=')

        out_data.append('SUBARRAY=True')
        out_data.append('SPWIN=False')
        out_data.append('V_SUBARRAY=True')
        out_data.append('V_SPWIN=False')
        # out_data.append('RES11KHZ=30.52')
        out_data.append('RES11KHZ=30.52')
        out_data.append('RES12KHZ=')
        # out_data.append('RES21KHZ=122.08')
        out_data.append('RES21KHZ=488.28')
        out_data.append('RES22KHZ=')
        out_data.append('V_RES11KHZ=True')
        out_data.append('V_RES12KHZ=False')
        out_data.append('V_RES21KHZ=True')
        out_data.append('V_RES22KHZ=False')

        for i in range(0, 32):
            if i < len(array_freq_rx_list) and array_freq_rx_list[i][4] != -1:
                out_data.append('V_RSFREQ' + str(i + 1).zfill(2) + '=' + 'True')
            else:
                out_data.append('V_RSFREQ' + str(i + 1).zfill(2) + '=' + 'False')

        for i in range(0, self.max_array_leng):
            out_data.append('BEAM_NUM' + str(i + 1).zfill(2) + '=' + '1')
        for i in range(self.max_array_leng, 32):
            out_data.append('BEAM_NUM' + str(i + 1).zfill(2) + '=' + '0')
        out_data.append('N_BEAM=1')


        return out_data

    def convert_vex_to_ndevice(self):
        '''
        vexファイルを変換
        '''
        use_mode                                            = Vex2Ndevice.__read_sched(self)
        mode_bindex, mode_eindex, FreqMode, IFMode, BBCMode = Vex2Ndevice.__read_mode(self)
        unused_variable                                     = Vex2Ndevice.__check_sched_and_mode(self, mode_bindex, mode_eindex, use_mode, FreqMode, IFMode)
        freq_BBC, freq_val, freq_pol, freq_sb, freq_range   = Vex2Ndevice.__read_freq(self, FreqMode)
        BBC_comb                                            = Vex2Ndevice.__read_bbc(self, BBCMode)
        IF_comb                                             = Vex2Ndevice.__read_if(self, IFMode)
        freq_BBC                                            = Vex2Ndevice.__overwrite_bbc_with_if(self, BBC_comb, freq_BBC, IF_comb)
        comb_rx_freq, rx_sb_name, num_of_rx    = Vex2Ndevice.__dist_rx_and_pol(self, freq_val, freq_pol, freq_sb, freq_BBC, freq_range)
        # rx_sb_name                                    = Vex2Ndevice.__overwrite_sideband(self, rx_sb_name)
        # rx_sb_name                                           = Vex2Ndevice.__adjust_bandwidth(self, rx_sb_name)
        # freq_list                                           = Vex2Ndevice.__set_freq(self, rx_sb_name)
        freq_list = rx_sb_name
        # ut.UtilFunc.chkprint(freq_list)
        freq_list                                           = Vex2Ndevice.__adjust_bandwidth(self, freq_list)

        # freq_list                                           = Vex2Ndevice.__adjust_lo_freq(self, freq_list)
        # freq_list                                           = Vex2Ndevice.__change_sb_name(self, freq_list)
        use_polarized_comb                                  = Vex2Ndevice.__check_type(self, num_of_rx, freq_list)
        self.rxlist, self.array_list                        = Vex2Ndevice.__sort_array(self, use_polarized_comb)
        self.array_list                                     = Vex2Ndevice.__set_rest_freq(self, self.array_list)
        # self.array_list                            = Vex2Ndevice.__overwrite_freqsetting(self, self.array_list, self.rxlist)
        self.array_list                                     = Vex2Ndevice.__copy_low2high(self, self.array_list)
        self.array_list                                     = Vex2Ndevice.__set_pfreq(self, self.array_list, self.rxlist)
        unused_variable                                     = Vex2Ndevice.__print_rx_list(self, self.rxlist, self.array_list)
        out_data                                            = Vex2Ndevice.__make_export_line(self, self.rxlist, comb_rx_freq, self.array_list)
        unused_variable                                     = ut.UtilFunc.ask_and_write(self.device_fname, out_data, self.device_file_flag, self.yes)

        self.array_list[0] = self.array_list[3]
        self.array_list[1] = self.array_list[3]

        del unused_variable


        if self.debag:
            for key in self.result_status.keys():
                ut.UtilFunc.chkprint2(key, self.result_status[key])
        
        if all(self.result_status.values()):
            return True
        else:
            ut.UtilFunc.print_warning_msg(self.result_status["MatchScheduleMode"], "スケジュールで指定されているモードの中で野辺山45ｍの周波数設定がされていないものがあります", "$SCHEDのmodeの部分を確認してください")
            ut.UtilFunc.print_warning_msg(self.result_status["GetFreqSettingError"], "$FREQで間違っている可能性がある行があります")

            print(ut.pycolor.END, end = "")
            return False
