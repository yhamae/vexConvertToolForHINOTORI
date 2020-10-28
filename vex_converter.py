#! /usr/local/bin/Python3
# Contents: 各モジュールで使用するパラメータを読む
#           vexファイルをstartとndevice、tune、datに変換するモジュールを読み込み、実行する
#           vexファイルの中身を取得する
# Usage   : $ Python vex_converter.py [パラメータファイル名] [オプション]
# Since   : Nov, 2019
#           Yuki Hamae


from importlib import machinery
import os
# import sys
import traceback
import argparse
import sys
import datetime
import getpass

import util as ut
from vex2start import Vex2Start
from vex2ndevice import Vex2Ndevice
from vex2dat import Vex2Dat
from vex2tune import Vex2Tune


class VexConverter(Vex2Start, Vex2Ndevice, Vex2Dat, Vex2Tune):
    '''
    vexファイルをstartとndevice、tune、datに変換する
    '''
    def __init__(self):
        Vex2Start.__init__(self)
        Vex2Ndevice.__init__(self)
        Vex2Tune.__init__(self)
        Vex2Dat.__init__(self)
        self.common_error = []
        self.start_error = []
        self.prm_filename = ''
        self.vexdata = {}
        self.version = 'α1.0'

    def reverse_print(self, moji):
        '''
        標準出力で表示させる文字の色を反転させる
        '''
        print('\n' + ut.pycolor.REVERCE + moji + ut.pycolor.END)

    def get_common_var(self):
        '''
        全モジュールで共通のパラメータを取得する
        '''
        try:
            prm = machinery.SourceFileLoader('prm', self.prm_filename).load_module()
        except FileNotFoundError:
            print(ut.pycolor.RED + 'パラメータファイルが見つかりません' + ut.pycolor.END)
            exit()
        except:
            print(ut.pycolor.RED + 'パラメータファイルの書式が間違っています。' + ut.pycolor.END)
            traceback.print_exc()
            exit()
        
        if hasattr(prm, 'yes'): self.yes = prm.yes
        if hasattr(prm, 'vex_file_name'): self.vex_file_name = prm.vex_file_name
        else: 
            self.common_error.append('vex_file_name')
        if hasattr(prm, 'station_name'): self.station_name = prm.station_name
        if hasattr(prm, 'debag'): self.debag = prm.debag
        if hasattr(prm, 'ask_verwrite'): self.yes = prm.ask_verwrite
        

        if len(self.common_error) >= 1:
            for error in self.common_error:
                print('"' + error + '" is not defined in ' + self.prm_filename)
            return False
        else:
            return True

    def get_start_var(self):
        try:
            prm = machinery.SourceFileLoader('prm', self.prm_filename).load_module()
        except FileNotFoundError:
            print(ut.pycolor.RED + 'パラメータファイルが見つかりません' + ut.pycolor.END)
            exit()
        except:
            print(ut.pycolor.RED + 'パラメータファイルの書式が間違っています。' + ut.pycolor.END)
            traceback.print_exc()
            exit()

        if hasattr(prm, 'USER_NAME'):
            self.USER_NAME = prm.USER_NAME 
        else:
            self.USER_NAME = getpass.getuser()
        if hasattr(prm, 'obs_name'): self.obs_name = prm.obs_name         
        if hasattr(prm, 'PROJECT_NAME'): self.PROJECT_NAME = prm.PROJECT_NAME
        if hasattr(prm, 'pointing_start_file_path'): self.pointing_start_file_path = prm.pointing_start_file_path
        if hasattr(prm, 'pointing_start_file'): self.pointing_start_file = prm.pointing_start_file
        if hasattr(prm, 'start_time_flag'): self.start_time_flag = prm.start_time_flag 
        if self.start_time_flag == 'any_start':
            if hasattr(prm, 'any_time'):
                self.any_time = prm.any_time 
            else:
                self.start_error.append()
        if self.start_time_flag == 'after_start':
            if hasattr(prm, 'after_day'):
                self.after_day = prm.after_day
            if hasattr(prm, 'minute_day'):
                self.minute_day = prm.minute_day 
        if hasattr(prm, 'TIME_MOVE_ANTENNA'): self.TIME_MOVE_ANTENNA = prm.TIME_MOVE_ANTENNA
        if hasattr(prm, 'after_mmc'): self.after_mmc = prm.after_mmc  
        if hasattr(prm, 'before_observation'): self.before_observation = prm.before_observation 
        if hasattr(prm, 'time_of_second_move'): self.time_of_second_move = prm.time_of_second_move
        if hasattr(prm, 'start_file_flag'): self.start_file_flag = prm.start_file_flag 
        if hasattr(prm, 'start_file_name'): self.start_file_name = prm.start_file_name
        if hasattr(prm, 'error_flag'): self.error_flag = prm.error_flag 
        if hasattr(prm, 'datalist'): self.datalist = prm.datalist

        if self.start_file_name == '' or self.start_file_name == ' ':
            self.start_file_name = os.path.splitext(self.vex_file_name)[0] + ".start"
        if self.USER_NAME == '':
            self.USER_NAME = os.getlogin()
        if self.obs_name == '':
            self.obs_name = os.path.splitext(self.vex_file_name)[0].split('/')[-1]
        if self.pointing_start_file_path == '':
            self.pointing_start_file_path = '/cosmos3/45m/obstable' + self.USER_NAME
        if self.pointing_start_file_path[-1] != '/':
            self.pointing_start_file_path += '/'
        



        if len(self.start_error) >= 1:
            for error in self.start_error:
                print('"' + error + '" is not defined in ' + self.prm_filename)
            return False
        else:
            return True

    def get_ndevice_var(self):
        try:
            prm = machinery.SourceFileLoader('prm', self.prm_filename).load_module()
        except FileNotFoundError:
            print(ut.pycolor.RED + 'パラメータファイルが見つかりません' + ut.pycolor.END)
            exit()
        except:
            print(ut.pycolor.RED + 'パラメータファイルの書式が間違っています。' + ut.pycolor.END)
            traceback.print_exc()
            exit()

        if hasattr(prm, 'device_fname'): self.device_fname = prm.device_fname
        if hasattr(prm, 'device_file_flag'): self.device_file_flag = prm.device_file_flag
        if hasattr(prm, 'Observation_Name'): self.Observation_Name = prm.Observation_Name
        if hasattr(prm, 'SAM_Att'): self.SAM_Att = prm.SAM_Att
        if hasattr(prm, 'IFFREQ'): self.IFFREQ = prm.IFFREQ
        if hasattr(prm, 'rx_inf'): self.rx_inf = prm.rx_inf
        if hasattr(prm, 'polarized_inf'): self.polarized_inf = prm.polarized_inf
        if hasattr(prm, 'polarized_comb'): self.polarized_comb = prm.polarized_comb
        if hasattr(prm, 'static_freq'): self.static_freq = prm.static_freq
        if hasattr(prm, 'rx_range'): self.rx_range = prm.rx_range
        if hasattr(prm, 'array_num'): self.array_num = prm.array_num
        if hasattr(prm, 'pointing_arraynum'): self.pointing_arraynum = prm.pointing_arraynum
        if hasattr(prm, 'rx_conb'): self.rx_conb = prm.rx_conb
        # if hasattr(prm, ''):

        

        if self.device_fname == '':
            self.device_fname = os.path.splitext(self.vex_file_name)[0] + ".ndevice"

        if self.device_file_flag == "file_date":
            Create_Date = datetime.datetime.today()
            self.device_fname = os.path.splitext(self.device_fname)[0] + "_" + str(Create_Date.year)[:] + "%02d%02d%02d%02d%02d.ndevice" % (int(str(Create_Date.month)), int(str(Create_Date.day)), int(str(Create_Date.hour)),int(str(Create_Date.minute)), int(str(Create_Date.second)))

        return True

    def get_dat_var(self):
        try:
            prm = machinery.SourceFileLoader('prm', self.prm_filename).load_module()
        except FileNotFoundError:
            print(ut.pycolor.RED + 'パラメータファイルが見つかりません' + ut.pycolor.END)
            exit()
        except:
            print(ut.pycolor.RED + 'パラメータファイルの書式が間違っています。' + ut.pycolor.END)
            traceback.print_exc()
            exit()


        if hasattr(prm, 'dat_filename'): self.dat_filename = prm.dat_filename
        if hasattr(prm, 'dat_file_flag'): self.dat_file_flag = prm.dat_file_flag
        if hasattr(prm, 'rx_range_list'): self.rx_range_list = prm.rx_range_list
        if hasattr(prm, 'first_LO'): self.first_LO = prm.first_LO




        if self.dat_filename == '':
            self.dat_filename = os.path.splitext(self.vex_file_name)[0] + ".dat"


        return True

    def get_tune_var(self):
        try:
            prm = machinery.SourceFileLoader('prm', self.prm_filename).load_module()
        except FileNotFoundError:
            print(ut.pycolor.RED + 'パラメータファイルが見つかりません' + ut.pycolor.END)
            exit()
        except:
            print(ut.pycolor.RED + 'パラメータファイルの書式が間違っています。' + ut.pycolor.END)
            traceback.print_exc()
            exit()

        if hasattr(prm, 'tune_file_name'): self.tune_file_name = prm.tune_file_name
        if hasattr(prm, 'tune_file_flag'): self.tune_file_flag = prm.tune_file_flag

        if self.tune_file_name == '':
            self.tune_file_name = os.path.splitext(self.vex_file_name)[0] + ".tune"


        return True

class ReadVex():
    '''
    Vexファイルの読み込み関係
    '''
    def __init__(self):
        self.datalist = []
        self.title_list = ["GLOBAL", "EXPER", "MODE", "STATION", "PROCEDURES", "SITE", "ANTENNA", "DAS","SOURCE", "FREQ", "IF", "BBC", "PHASE_CAL_DETECT", "SCHED"]
        self.title_index = []
        self.detail_error = ''
        self.vexdata = {}


    def read_vex_file(self, vex_filename):
        '''
        vexファイル全体を読む
        '''
        try:
            vex_data = open(vex_filename, "r")
            self.data_list = vex_data.readlines()

            
            self.title_index = [len(self.data_list)]

            # 各$...の行数を取得
            for data in self.data_list:
                # print(data.strip().strip('$'';'))
                if data.strip().strip('$'';'' ') in self.title_list:
                    self.title_index.append(self.data_list.index(data))
            self.title_index.sort()
            return True
        except FileNotFoundError as e:
            ut.UtilFunc.print_err_msg(False, e, vex_filename + ": No such file or dirxtry")
            return False

    def read_section_at_vex(self, section_name):
        '''
        読み込んだvexファイルから特定のsectionの内容を取得
        '''
        if section_name in self.title_list:
            INDEX_START = 0
            INDEX_END = 0
            count = 0
            # print('\n'.join(self.data_list))
            for data in self.data_list:
                # print(data.strip().strip("$"";"))
                if data.strip('$'';'' ''\n') in section_name:
                    # print(data.strip('$'';'' ''\n'))
                    INDEX_START = self.data_list.index(data)
                    INDEX_END = self.title_index[self.title_index.index(INDEX_START)+1]
                    # print(INDEX_START + '-' + INDEX_END)
                    count += 1
            if count == 0:
                print(ut.pycolor.RED + 'section_nameが見つかりません' + ut.pycolor.END)
                self.detail_error = 'Vexファイル内にsection_nameが見つかりません'
                return False
            return self.data_list[INDEX_START:INDEX_END]
        else:
            print(ut.pycolor.RED + 'section_nameが間違っています' + ut.pycolor.END)
            self.detail_error = '引数"section_name"がself.title_listないに見つかりません'
            return False

    def separate_vex_data(self, vex_filename):
        '''
        vexファイルを各sectionごとに分割
        '''
        ReadVex.read_vex_file(self, vex_filename)
        for name in self.title_list:
            self.vexdata[name] = ReadVex.read_section_at_vex(self, name)
        return self.vexdata





if __name__ == "__main__":
    result = {}
    vc = VexConverter()
    all_flag = False
    args_tmp = sys.argv
    descri = 'vexファイルを各種野辺山用観測指示書へ変換するプログラムです。\n実行する際にはパラメータファイルが必用となるので必ず用意してください。\n詳細はGitHubを参照: https://github.com/yhamae/vexConvertToolForHINOTORI'
    usg = 'Python3 vex_converter.py [option]\n(optionに何も設定しない場合、すべての変換が実行される。)'

    parser = argparse.ArgumentParser(prog='vex_converter', usage=usg, description=descri, add_help=True)
    parser.add_argument('-s', '--start', help='.startへの変換を実行する場合使用', action='store_true')
    parser.add_argument('-n', '--ndevice', help='.ndeviceへの変換を実行する場合使用', action='store_true')
    parser.add_argument('-d', '--dat', help='.datへの変換を実行する場合使用', action='store_true')
    parser.add_argument('-t', '--tune', help='.tuneへの変換を実行する場合使用', action='store_true')
    parser.add_argument('-f', '--filename', help='パラメータファイルの名前を指定(デフォルトでは"parameter.inp"に設定)', default = 'parameter.inp')
    parser.add_argument('-v', '--version', help='バージョンを表示', action='store_true')
    if '--debag' in args_tmp:
        parser.add_argument('--debag', help='For Debag(User don\'t use)', action='store_true', default = False)
    args = parser.parse_args()

    if '--debag' in args_tmp:
        vc.debag = args.debag
    else:
        vc.debag = False

    if args.version:
        print('Ver.' + str(vc.version))
        exit()

    if not args.start and not args.ndevice and not  args.dat and not args.tune:
        all_flag = True


    vc.prm_filename = args.filename
    result['get parameter(common)'] = vc.get_common_var()

    rv = ReadVex()
    vc.vexdata = rv.separate_vex_data(vc.vex_file_name)
    if args.start or all_flag:
        result['get parameter(start)'] = vc.get_start_var()


    if args.ndevice or all_flag:
        result['get parameter(ndevice)'] = vc.get_ndevice_var() 
        vc.reverse_print('Convert .vex to .ndevice')
        result['Convert .vex to .ndevice'] = vc.convert_vex_to_ndevice()
    if args.dat or all_flag:
        if not args.ndevice and not all_flag:
            result['get parameter(ndevice)'] = vc.get_ndevice_var()      
            vc.device_file_flag = False
            vc.reverse_print('Convert .vex to .ndevice')
            result['Convert .vex to .ndevice'] = vc.convert_vex_to_ndevice()      
        result['get parameter(dat)'] = vc.get_dat_var()
        vc.reverse_print('Convert .vex to .dat')
        result['Convert .vex to .dat'] = vc.convert_vex_to_dat()
    # Tuneファイルの作成が不要になったためコメントアウト
    # if args.tune or all_flag:
    #     if not args.start and not all_flag:
    #         result['get parameter(start)'] = vc.get_start_var()
    #         vc.start_file_flag = False
    #         vc.reverse_print('Convert .vex to .start')
    #         result['Convert .vex to .start'] = vc.convert_vex_to_start()
    #     result['get parameter(tune)'] = vc.get_tune_var()
    #     vc.reverse_print('Convert .vex to .tune')
    #     result['Convert .vex to .tune'] = vc.convert_vex_to_tune()

    if args.start or all_flag:
        result['get parameter(start)'] = vc.get_start_var()
        vc.reverse_print('Convert .vex to .start')
        result['Convert .vex to .start'] = vc.convert_vex_to_start()



    print('\n' + ut.pycolor.REVERCE + 'Result Status' + ut.pycolor.END)
    max_leng = max([len(moji) for moji in result.keys()])
    for key in result.keys():
        if result[key] == True:
            status = ut.pycolor.GREEN + ut.pycolor.REVERCE + 'Success'.center(9) + ut.pycolor.END
        elif result[key] == None:
            status = ut.pycolor.YELLOW + ut.pycolor.REVERCE + 'Unknown'.center(9) + ut.pycolor.END
        else:
            status = ut.pycolor.RED + ut.pycolor.REVERCE + 'False'.center(9) + ut.pycolor.END
        print(str(key).ljust(max_leng) + ': ' + status)

