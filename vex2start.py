# Python version 3 (and 2)
# Contents: vexファイルをstartに変換するスクリプト
# Since   : Feb, 2019
#           Takeru Kawaguchi
# Update  : Nov, 2019
#           クラス化、一部を修正
#           Yuki Hamae
# Update  : Oct, 2020
#           Beta版リリース

import datetime
import sys
import os

import util as ut




class Vex2Start():
    def __init__(self):
        self.vex_fname = ''
        self.USER_NAME = ''
        self.PROJECT_NAME = 'proj1'
        self.station_name = 'Ny'
        self.start_time_flag = ''
        self.any_time = ''
        self.after_day = ''
        self.minute_day = ''
        self.TIME_MOVE_ANTENNA = ''
        self.vex_file_name = ''
        self.after_mmc = ''
        self.before_observation = ''
        self.time_of_second_move = ''
        self.start_file_flag = ''
        self.start_file_name = ''
        self.error_flag = ''
        self.datalist = ''
        self.obs_name = ''
        self.startfile = []
        self.pointing_start_file = ''
        self.pointing_start_file_path = ''
        self.startfile_mode = {'vlbi': True, 'pointing': False}

        # rxt = {}
        # sam45 = {}

        # rxt[obs_freq] = [] * 16
        # rxt[freq_if1] = [] * 16
        # rxt[rx_name] = [] * 16
        # rxt[rx_num] = 2
        # rxt[use_flg] = [0, 0, 0]

    


    def __get_device_setting(self, array_list, rxlist):
        pass        


    def __get_pointing_startfile(self, startfile_name):
        '''
        no use
        '''
        return_data = {'pointing_info':[], }
        data = open(startfile_name, "r")
        for line in data:
            if line.startswith('% SRC_NAME='):
                return_data['pointing_info'].append(line.strip('\n'))
            if line.startswith('% SRC_COMMENT='):
                return_data['pointing_info'].append(line.strip('\n'))
            # if line.startswith(''):
            #     return_data[key1].append(line.strip('\n'))
        return return_data




    def convert_vex_to_start(self):

        # print(Vex2Start.__get_pointing_startfile(self, self.pointing_start_file_path + self.PROJECT_NAME + self.pointing_start_file))
        vex_data = open(self.vex_file_name, "r")
        self.datalist = vex_data.readlines()
        # print(self.vex_file_name)
        Create_Date = datetime.datetime.today()

        #各$のindexを抜き出す。
        title_list = ["$GLOBAL;", "$EXPER;", "$MODE;", "$STATION;", "$PROCEDURES;", "$SITE;", "$ANTENNA;", "$DAS;", "$SOURCE;", "$FREQ;", "$IF;", "$BBC;", "$PHASE_CAL_DETECT;", "$SCHED;"]
        title_index = [len(self.datalist)]
        #$を見つけて、indexをtitle_indexに収納、
        for data in self.datalist:
            if data.strip() in title_list:
                title_index.append(self.datalist.index(data))
        title_index.sort()



        #-------------------------------------------------#
        #  GLOBAL
        #-------------------------------------------------#
        #$GLOBALを分解する。
        GLOBAL_INDEX_START = 0
        GLOBAL_INDEX_END = 0
        for data in self.datalist:
            if data.strip() in "$GLOBAL;":
                GLOBAL_INDEX_START = self.datalist.index(data)
                GLOBAL_INDEX_END = title_index[title_index.index(GLOBAL_INDEX_START)+1]
        #print GLOBAL_INDEX_START, GLOBAL_INDEX_END

        GLOBAL_DATA = self.datalist[GLOBAL_INDEX_START:GLOBAL_INDEX_END]
        #print GLOBAL_DATA  #この中に$GLOBAL;の中身が書いてある。


        Observation_Name = ""
        #何に入れるかは別として、ここに$EXPERの観測ネームがある。
        for data in GLOBAL_DATA:
            if "$EXPER" in data.split():
                Observation_Name = data.split()[-1]
                #print Observation_Name


        #-------------------------------------------------#
        #  EXPER
        #-------------------------------------------------#
        #$EXPERを分解する。
        OBSERVATION_START_TIME = 0
        EXPER_INDEX_START = 0
        EXPER_INDEX_END = 0
        for data in self.datalist:
            if data.strip() in "$EXPER;":
                EXPER_INDEX_START = self.datalist.index(data)
                EXPER_INDEX_END = title_index[title_index.index(EXPER_INDEX_START)+1]
        #print EXPER_INDEX_START, EXPER_INDEX_END

        EXPER_DATA = self.datalist[EXPER_INDEX_START:EXPER_INDEX_END]
        #print EXPER_DATA  #この中に$EXPER;の中身が書いてある。



        #何に入れるかは別として、ここに$EXPERの観測ネームがある。
        for data in EXPER_DATA:
            if  "exper_nominal_start" in data[5:24]:
                OBSERVATION_START_TIME = data[25:-1]
                #print OBSERVATION_START_TIME



        #-------------------------------------------------#
        #  SOURCE
        #-------------------------------------------------#
        #$SOURCEを分解する。
        SOURCE_INDEX_START = 0
        SOURCE_INDEX_END = 0
        for data in self.datalist:
            if data.strip() in "$SOURCE;":
                SOURCE_INDEX_START = self.datalist.index(data)
                SOURCE_INDEX_END = title_index[title_index.index(SOURCE_INDEX_START)+1]
        #print SOURCE_INDEX_START, SOURCE_INDEX_END

        SOURCE_DATA = self.datalist[SOURCE_INDEX_START+1:SOURCE_INDEX_END]
        #print SOURCE_DATA

        count = 0
        SOURCE_Start_index = []
        SOURCE_End_index = []
        for data in SOURCE_DATA:
            if "def" == data.strip()[0:3]:
                SOURCE_Start_index.append(count)
            elif "enddef" == data.strip()[0:6]:
                SOURCE_End_index.append(count)
            count += 1
        SOURCE_Start_index.sort()
        SOURCE_End_index.sort()


        SOURCE_LIST = []

        for i in range(len(SOURCE_Start_index)):
            SOURCE_TEXT = ""
            tmpSOURCE = SOURCE_DATA[SOURCE_Start_index[i]:SOURCE_End_index[i]]
            for data in tmpSOURCE:
                if "*" != data[0]:
                    SOURCE_TEXT = SOURCE_TEXT + data

            tmpSOURCE = SOURCE_TEXT.split(';')
            for data in tmpSOURCE:
                #観測天体名
                if "source_name=" in ''.join(data.split()):
                    SOURCE_LIST.append([])
                    SOURCE_LIST[i].append(''.join(data.split())[12:])
                    #print ''.join(data.split()).strip('source_name=')
                if "ra=" in ''.join(data.split()):
                    SOURCE_LIST[i].append(''.join(data.split())[3:])
                    #print ''.join(data.split()).strip('ra=')
                if "dec=" in ''.join(data.split()):
                    SOURCE_LIST[i].append(''.join(data.split())[4:])
                    #print ''.join(data.split()).strip('ra=')
                if "ref_coord_frame=" in ''.join(data.split()):
                    SOURCE_LIST[i].append(''.join(data.split())[16:])




        #-------------------------------------------------#
        #  FREQ
        #-------------------------------------------------#
        #$FREQを分解する。
        FREQ_INDEX_START = 0
        FREQ_INDEX_END = 0
        for data in self.datalist:
            if data.strip() in "$FREQ;":
                FREQ_INDEX_START = self.datalist.index(data)
                FREQ_INDEX_END = title_index[title_index.index(FREQ_INDEX_START)+1]
        #print FREQ_INDEX_START, FREQ_INDEX_END

        FREQ_DATA = self.datalist[FREQ_INDEX_START:FREQ_INDEX_END]
        #print FREQ_DATA  #この中に$FREQ;の中身が書いてある。

        for data in FREQ_DATA:
            #周波数
            if "chan_def" in data.split():
                #print data.split()[2], "=", data.split()[3], "MHz"
                #print data.split()[5], "=", data.split()[6], "MHz"
                #print data.split()[8], "=", data.split()[10], data.split()[12], data.split()[13]
                pass


        #-------------------------------------------------#
        #  STATION - Don't use
        #-------------------------------------------------#
        """
        #$STATIONを分解する。
        STATION_INDEX_START = 0
        STATION_INDEX_END = 0
        for data in self.datalist:
            if data.strip() in "$STATION;":
                STATION_INDEX_START = self.datalist.index(data)
                STATION_INDEX_END = title_index[title_index.index(STATION_INDEX_START)+1]
        #print STATION_INDEX_START, STATION_INDEX_END
        STATION_DATA = self.datalist[STATION_INDEX_START+1:STATION_INDEX_END]
        #print STATION_DATA
        count = 0
        STATION_index = []
        for data in STATION_DATA:
            if "*" in data.strip():
                STATION_index.append(count)
            count += 1
        STATION_index.sort()
        STATION_LIST = []
        for i in range(len(STATION_index)-1):
            tmpSTATION = STATION_DATA[STATION_index[i]:STATION_index[i+1]]
            for data in tmpSTATION:
                #望遠鏡
                if "$SITE" in data.split():
                    #print data.split()[-1][:-1]
                    pass
                if "$ANTENNA" in data.split():
                    #print data.split()[-1][:-1]
                    pass
                if "$DAS" in data.split():
                    #print data.split()[-1][:-1]
                    pass
        """
        #-------------------------------------------------#
        #  SCHED
        #-------------------------------------------------#
        #$SCHEDを分解する。
        SCHED_INDEX_START = 0
        SCHED_INDEX_END = 0
        for data in self.datalist:
            if data.strip() in "$SCHED;":
                SCHED_INDEX_START = self.datalist.index(data)
                SCHED_INDEX_END = title_index[title_index.index(SCHED_INDEX_START)+1]


        SCHED_DATA = self.datalist[SCHED_INDEX_START:SCHED_INDEX_END]
        #print SCHED_DATA  #この中に$SCHED;の中身が書いてある。
        count = 0
        SCHED_Start_index = []
        SCHED_End_index = []
        for data in SCHED_DATA:
            if "scan" == data.strip()[0:4]:
                SCHED_Start_index.append(count)
            elif "endscan" == data.strip()[0:7]:
                SCHED_End_index.append(count)
            count += 1
        SCHED_Start_index.sort()
        SCHED_End_index.sort()



        self.station_name_ANT = ""
        SCHED_LIST = []
        for i in range(len(SCHED_Start_index)):
            SCHED_TEXT = ""
            tmpSCHED = SCHED_DATA[SCHED_Start_index[i]:SCHED_End_index[i]]
            for data in tmpSCHED:
                if "*" != data[0]:
                    SCHED_TEXT = SCHED_TEXT + data


            self.station_name_ANT = "station=" + self.station_name
            tmpSCHED = SCHED_TEXT.split(';')
            for data in tmpSCHED:
                if self.station_name_ANT in ''.join(data.split()):
                    SCHED_LIST[i][3] = ''.join(data.split())[8:]
                if "scan" in ''.join(data.split())[0:5]:
                    SCHED_LIST.append([0, 0, 0, 0])
                if "start=" in ''.join(data.split()):
                    #SCHED_LIST.append([])
                    SCHED_LIST[i][0] = ''.join(data.split())[6:]
                    #print ''.join(data.split()).strip('start=')
                if "mode=" in ''.join(data.split()):
                    SCHED_LIST[i][1] = ''.join(data.split())[5:]
                    #print ''.join(data.split()).strip('mode=')
                if "source=" in ''.join(data.split()):
                    SCHED_LIST[i][2] = ''.join(data.split())[7:]
                    #print ''.join(data.split()).strip('source=')
                if "source1=" in ''.join(data.split()):
                    SCHED_LIST[i][2] = ''.join(data.split())[8:]
                    #print ''.join(data.split()).strip('source1=')

                    #print ''.join(data.split()).strip('station=Vm')

        #-------------------------------------------------#
        #  MODE
        #-------------------------------------------------#
        #$MDOEを分解する。
        MODE_INDEX_START = 0
        MODE_INDEX_END = 0
        for data in self.datalist:
            if data.strip() in "$MODE;":
                MODE_INDEX_START = self.datalist.index(data)
                MODE_INDEX_END = title_index[title_index.index(MODE_INDEX_START)+1]
        #print MODE_INDEX_START, MODE_INDEX_END

        MODE_DATA = self.datalist[MODE_INDEX_START+1:MODE_INDEX_END]
        #print MODE_DATA

        count = 0
        MODE_Start_index = []
        MODE_End_index = []
        for data in MODE_DATA:
            if "def" == data.strip()[0:3]:
                MODE_Start_index.append(count)
            elif "enddef" == data.strip()[0:6]:
                MODE_End_index.append(count)
            count += 1
        MODE_Start_index.sort()
        MODE_End_index.sort()


        MODE_LIST = []

        for i in range(len(MODE_Start_index)):
            MODE_TEXT = ""
            tmpMODE = MODE_DATA[MODE_Start_index[i]:MODE_End_index[i]]
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


        #-------------------------------------------------#
        #  PROCEDURES
        #-------------------------------------------------#
        #$PROCEDURESを分解する。
        PROCEDURES_INDEX_START = 0
        PROCEDURES_INDEX_END = 0
        for data in self.datalist:
            if data.strip() in "$PROCEDURES;":
                PROCEDURES_INDEX_START = self.datalist.index(data)
                PROCEDURES_INDEX_END = title_index[title_index.index(PROCEDURES_INDEX_START)+1]
        #print PROCEDURES_INDEX_START, PROCEDURES_INDEX_END

        PROCEDURES_DATA = self.datalist[PROCEDURES_INDEX_START+1:PROCEDURES_INDEX_END]
        #print PROCEDURES_DATA

        count = 0
        PROCEDURES_Start_index = []
        PROCEDURES_End_index = []
        for data in PROCEDURES_DATA:
            if "def" == data.strip()[0:3]:
                PROCEDURES_Start_index.append(count)
            elif "enddef" == data.strip()[0:6]:
                PROCEDURES_End_index.append(count)
            count += 1
        PROCEDURES_Start_index.sort()
        PROCEDURES_End_index.sort()


        PROCEDURES_LIST = []

        for i in range(len(PROCEDURES_Start_index)):
            PROCEDURES_TEXT = ""
            tmpPROCEDURES = PROCEDURES_DATA[PROCEDURES_Start_index[i]:PROCEDURES_End_index[i]]
            for data in tmpPROCEDURES:
                if "*" != data[0]:
                    PROCEDURES_TEXT = PROCEDURES_TEXT + data

            tmpPROCEDURES = PROCEDURES_TEXT.split(';')
            count = 0
            for data in tmpPROCEDURES:
                if "def" in ''.join(data.split()):
                    PROCEDURES_LIST.append([])
                    PROCEDURES_LIST[i].append(data.split()[1])
                if "preob_cal=" in ''.join(data.split()):
                    preob_txt = ''.join(data.split()).replace('=', ':').split(':')
                    if preob_txt[1] == "on" and preob_txt[3] =="R_SKY":
                        PROCEDURES_LIST[i].append(preob_txt[2][:-3])
                        count += 1
            if count == 0:
                PROCEDURES_LIST[i].append(0)



        #-------------------------------------------------#
        #  書き出す部分
        #-------------------------------------------------#
        offset_time = SCHED_LIST[0][0]
        start_offset_time = ut.UtilFunc.str_time_to_time(offset_time)
        start_offset_time = datetime.datetime(int(start_offset_time[0]), int(start_offset_time[1]), int(start_offset_time[2]), int(start_offset_time[3]), int(start_offset_time[4]), int(start_offset_time[5]))
        end_offset_time = start_offset_time - datetime.timedelta(seconds=10000)


        if self.start_file_flag == "file_date":
            self.start_file_name = Observation_Name[:-1] + "_" + self.station_name + "_" + str(Create_Date.year)[2:] + "%02d%02d%02d%02d%02d.start" %(int(str(Create_Date.month)), int(str(Create_Date.day)), int(str(Create_Date.hour)), int(str(Create_Date.minute)), int(str(Create_Date.second)))
        else:
            pass
        # start_file = open(self.start_file_name, "w")


        #-------------------------------------------------#
        #  write title
        #-------------------------------------------------#
        scan = 0
        SOURCE_NAME_SAMPLE = SCHED_LIST[scan][2]

        for i in range(len(SOURCE_LIST)):
            if SOURCE_NAME_SAMPLE == SOURCE_LIST[i][0]:
                SOURCE_NUMBER = i
        SOURCE_NUMBER = 0
        right_ascension = float(SOURCE_LIST[SOURCE_NUMBER][1][0:2]) * 15 + float(SOURCE_LIST[SOURCE_NUMBER][1][3:5]) * (15/60.0) + float(SOURCE_LIST[SOURCE_NUMBER][1][6:8]) * (15/3600.0) + 0.01 * float(SOURCE_LIST[SOURCE_NUMBER][1][9:11]) * (15/3600.0)

#        if SOURCE_LIST[SOURCE_NUMBER][2][0] == "+" or SOURCE_LIST[SOURCE_NUMBER][2][0] == "-":
#            declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0
#        else:
#            declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:2]) + float(SOURCE_LIST[SOURCE_NUMBER][2][3:5]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][6:10]) / 3600.0

        if SOURCE_LIST[SOURCE_NUMBER][2][0] == "-":
            declination = -1.0*(float(SOURCE_LIST[SOURCE_NUMBER][2][1:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0)
        elif SOURCE_LIST[SOURCE_NUMBER][2][0] == "+":
            declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0
        else:
            declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:2]) + float(SOURCE_LIST[SOURCE_NUMBER][2][3:5]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][6:10]) / 3600.0
            
        start_head = [
                    "WS COSMOS INSTRUCTION FILE",
                    "Generated from VLBI Schedule (" + self.vex_file_name + ')', 
                    "Conversion Software ver." + self.version, 
                    "Creation Date : %04d/%02d/%02d %02d:%02d:%02d" %(Create_Date.year, Create_Date.month, Create_Date.day, Create_Date.hour, Create_Date.minute, Create_Date.second)
                    ]
        # self.startfile.append("#---------------------------------------------------")
        # self.startfile.append("# WS COSMOS INSTRUCTION FILE")
        # self.startfile.append("# Generated from VLBI Schedule (" + self.vex_file_name + ')')
        # self.startfile.append("# Conversion Software ver." + self.version)
        # # self.startfile.append("#------------------- made by " + "H.Imai" + "")
        # self.startfile.append("# Creation Date : %04d/%02d/%02d %02d:%02d:%02d\n" %(Create_Date.year, Create_Date.month, Create_Date.day, Create_Date.hour, Create_Date.minute, Create_Date.second))
        # self.startfile.append("#---------------------------------------------------")
        # self.startfile.append("")
        # self.startfile.append('# ' + '-' * max([len(x) + 2 for x in start_head]))
        self.startfile.extend(ut.UtilFunc.make_sqr_comment(start_head))
        # self.startfile.append('# ' + '-' * max([len(x) + 2 for x in start_head]))
        # self.startfile.append('')
        # self.startfile.append('')

        #-------------------------------------------------#
        #  write OBSTABLE
        #-------------------------------------------------#
        self.startfile.append("#-------- OBSTABLE Information Table --------")
        # if self.startfile_mode['pointing']:


        self.startfile.append("% OBSERVER=" + self.USER_NAME + "")
        #self.startfile.append("% GROUP=" + os.getlogin() + "")
        self.startfile.append("% GROUP=" + self.USER_NAME + "")
        #self.startfile.append("% PROJECT=vlbi")
        self.startfile.append("% PROJECT=" + self.PROJECT_NAME + "")
        self.startfile.append("% OBS_NAME=" + self.obs_name + "")
        self.startfile.append("% MMC_CMD1=MCL")
        self.startfile.append("% MMC_CMD2=MOP")
        self.startfile.append("% MMC_CMD3=")
        self.startfile.append("% MMC_CMD4=")
        self.startfile.append("% ON_TINTEG=10")
        self.startfile.append("% OFF_TINTEG=10")
        self.startfile.append("% CALIB_TINTEG=10")

        # # self.startfile.append('% information of .device')
        # self.startfile.append('% CHAPTER=')
        # self.startfile.append('% SRC_NAME=' + SOURCE_LIST[SOURCE_NUMBER][0])
        # self.startfile.append('% SRC_COMMENT=' + SOURCE_LIST[SOURCE_NUMBER][0])
        # self.startfile.append('% SW_MODE=POS')
        # self.startfile.append('% POS_ANGLE=0')
        # self.startfile.append('% EPOCH=J2000')
        # self.startfile.append('% VELO=24000.0')
        # self.startfile.append('% VDEF=RAD')
        # self.startfile.append('% VREF=LSR')
        # if self.startfile_mode['pointing']:
        #     self.startfile.append('% OBS_MODE=POINTING')
        # if self.startfile_mode['vlbi']:
        #     self.startfile.append('% OBS_MODE=NORMAL')
        # if self.startfile_mode['pointing']:
        #     self.startfile.append('% SCAN_TYPE=5POINTS ')
        # if self.startfile_mode['vlbi']:
        #     self.startfile.append('% SCAN_TYPE=CENTER ')
        # for i, s in enumerate(self.array_list):
        #     if s[0] != None:
        #         tmp_val = '{:E}'.format(s[2] * 1E+9).split('E+')
        #         tmp = str(float(tmp_val[0])) + 'E' + tmp_val[1]
        #         self.startfile.append('% OBS_FREQ' + str(i + 1) + '=' + tmp)
        #     else:
        #         self.startfile.append('% OBS_FREQ' + str(i + 1) + '=0') 
        # for i in range(16, 24):
        #     self.startfile.append('% OBS_FREQ' + str(i + 1) + '=0') 


        # for i, s in enumerate(self.array_list):
        #     if s[0] != None:
        #         tmp_val = '{:.1E}'.format(self.IFFREQ[i] * 1E+9).split('E+')
        #         tmp = tmp_val[0] + 'E' + tmp_val[1]
        #         self.startfile.append('% FREQ_IF' + str(i + 1) + '=' + tmp)
        #     else:
        #         self.startfile.append('% FREQ_IF' + str(i + 1) + '=0') 
        # for i in range(16, 24):
        #     self.startfile.append('% FREQ_IF' + str(i + 1) + '=0') 


        # for i, s in enumerate(self.array_list):
        #     if s[0] != None:
        #         if s[0] in self.change_name_prm.keys():
        #             name = self.change_name_prm[s[0]]
        #         else:
        #             name = s[0]
        #         self.startfile.append('% FE' + str(i + 1) + '=' + name)
        #     else:
        #         self.startfile.append('% FE' + str(i + 1) + '=') 
        # for i in range(16, 24):
        #     self.startfile.append('% FE' + str(i + 1) + '=') 



        # self.startfile.append("% MMC_CMD1=MCL")
        # self.startfile.append("% MMC_CMD2=MOP")
        # self.startfile.append("% MMC_CMD3=")
        # self.startfile.append("% MMC_CMD4=")
        # self.startfile.append('% ON_NTOTAL=6')
        # self.startfile.append('% ON_NSEQUENCE=6')
        # self.startfile.append('% ON_TINTEG=10')
        # self.startfile.append('% ON_COORD_SYS=AZEL')
        # self.startfile.append('% ON1=(0.002778,0.000000)')
        # self.startfile.append('% ON2=(0.000000,0.000000)')
        # self.startfile.append('% ON3=(-0.002778,0.000000)')
        # self.startfile.append('% ON4=(0.000000,0.002778)')
        # self.startfile.append('% ON5=(0.000000,0.000000)')
        # self.startfile.append('% ON6=(0.000000,-0.002778)')
        # self.startfile.append('% OFF_NUSED=1')
        # self.startfile.append('% OFF_TINTEG=10')
        # self.startfile.append('% OFF_COORD_SYS=AZEL')
        # self.startfile.append('% OFF1=(0.050000,0.000000)')
        # self.startfile.append('% OFF2=(0.0,0.0)')
        # self.startfile.append('% OFF3=(0.0,0.0)')
        # self.startfile.append('% OFF4=(0.0,0.0)')
        # self.startfile.append('% OFF5=(0.0,0.0)')
        # self.startfile.append('% OFF6=(0.0,0.0)')
        # self.startfile.append('% OFF7=(0.0,0.0)')
        # self.startfile.append('% OFF8=(0.0,0.0)')
        # self.startfile.append('% OFF9=(0.0,0.0)')
        # self.startfile.append('% NSEQUENCE=100')
        # self.startfile.append('% CALIB_TINTEG=10')
        # self.startfile.append('% CALIB_UNIT=SEQUENCE')
        # self.startfile.append('% PATTERN=1***1***')
        # self.startfile.append('% CALIB_INTERVAL=100')
        
        # if self.startfile_mode['pointing']:
        #     self.startfile.append('% OBS_TYPE=SAM45_LIN')
        #     for i, s in enumerate(self.array_list):
        #         if s[0] != None:
        #             tmp_val = '{:E}'.format(s[8] * 1E+9).split('E+')
        #             tmp = str(float(tmp_val[0])) + 'E' + tmp_val[1]
        #             self.startfile.append('% SAM45_FREQ' + str(i + 1) + '=' + tmp)
        #         else:
        #             self.startfile.append('% SAM45_FREQ' + str(i + 1) + '=0') 
        #     for i in range(len(self.array_list), 32):
        #         self.startfile.append('% SAM45_FREQ' + str(i + 1) + '=0') 




        # self.startfile.append('############################')
        # self.startfile.append('# Change LO Switch for H40 #')
        # self.startfile.append('############################')
        self.startfile.extend(ut.UtilFunc.make_sqr_comment('Change LO Switch for H40'))
        self.startfile.append('OPEN MLPPS')
        self.startfile.append('SET KEYWORD \'OK\'')
        self.startfile.append('SET ERR_KEYWORD \'Error\'')
        self.startfile.append('SEND MLPPS \'/usr/bin/python /cosmos3/45m/nro/bin/losw_h40.py\'')
        self.startfile.append('WAIT MLPPS')
        self.startfile.append('SLEEP 1')
        self.startfile.append('CLOSE MLPPS')
        if self.startfile_mode['pointing']:
            self.startfile.append('################')
            self.startfile.append('# Group Tracks #')
            self.startfile.append('################')
            self.startfile.append('GROUP GRPTRK ANT RXT SAM45 SYNTHE_L SYNTHE_K ')
        self.startfile.append('###########################')
        self.startfile.append('# GROUP SYNTHE CONTROLLER #')
        self.startfile.append('###########################')
        self.startfile.append('GROUP SYNTHE SYNTHE_L SYNTHE_K')

        #-------------------------------------------------#
        #  write GROUP OF DEVICES
        #-------------------------------------------------#
        self.startfile.append("#-------- DEFINE GROUP OF DEVICES --------")
        self.startfile.append("GROUP GRPTRK ANT RXT SYNTHE_L SYNTHE_K VLBI")
        # self.startfile.append("")

        #-------------------------------------------------#
        #  write OPEN DEVICES
        #-------------------------------------------------#
        self.startfile.append("#-------- OPEN DEVICES --------")
        self.startfile.append("OPEN ANT")
        self.startfile.append('OPEN RXT')
        self.startfile.append('OPEN IFATT')
        self.startfile.append('OPEN SYNTHE')
        if self.startfile_mode['pointing']:
            self.startfile.append('OPEN SAM45')
        # self.startfile.append('OPEN MRG')
        self.startfile.append("OPEN MMC")
        self.startfile.append("OPEN VLBI")
        # self.startfile.append("")
        self.startfile.append('###########################')
        self.startfile.append('# Set Tracking Parameters #')
        self.startfile.append('###########################')
        



        self.startfile.append('SET GRPTRK TRK_TYPE \'RADEC\'')
        self.startfile.append('SET GRPTRK SRC_NAME \'' + SOURCE_LIST[SOURCE_NUMBER][0] + '\'')
        self.startfile.append('SET GRPTRK SRC_POS ( %.5f, %.5f)' %(right_ascension, declination))
        self.startfile.append('SET GRPTRK EPOCH \'J2000\'')
        self.startfile.append('SET GRPTRK SCAN_COOD \'AZEL\'')
        self.startfile.append('SET ANT SCAN_COOD_OFF \'AZEL\'')
        self.startfile.append('SET ANT 2BEAM_MODE 0')
        self.startfile.append('SET ANT POINTING \'H40\'')
        self.startfile.append('SET ANT OTF_MODE \'OFF\'')
        # self.startfile.append('######################')
        # self.startfile.append('# Set MRG Parameters #')
        # self.startfile.append('######################')
        # self.startfile.append('SET MRG GROUP \'' + self.USER_NAME + '\'')
        # self.startfile.append('SET MRG PROJECT \'' + self.PROJECT_NAME + '\'')
        # self.startfile.append('SET MRG BK_TYPE \'SAMZ\'')
        # self.startfile.append('SET MRG SP_MODE \'OFF\'')
        # self.startfile.append('SET MRG OTF_MODE \'OFF\'')
        # self.startfile.append('SET MRG OFF_HOLD \'ON\'')
        # self.startfile.append('################################')
        # self.startfile.append('# Set Synthesizer SYNTHE_L Parameters #')
        # self.startfile.append('################################')
        self.startfile.extend(ut.UtilFunc.make_sqr_comment('Set Synthesizer SYNTHE_L Parameters'))
        self.startfile.append('SET SYNTHE_L VELO 24000.0')
        self.startfile.append('SET SYNTHE_L VDEF \'RAD\'')
        self.startfile.append('SET SYNTHE_L VREF \'LSR\'')
        self.startfile.append('SET SYNTHE_L INTERVAL 600')
        self.startfile.append('SET SYNTHE_L DOPPLER_TRK \'OFF\'')
        self.startfile.append('SET SYNTHE_L OBS_FREQ 2.28E10')
        self.startfile.append('SET SYNTHE_L FREQ_IF1 6.0E9')
        self.startfile.append('SET SYNTHE_L FREQ_SW \'OFF\'')
        self.startfile.append('SET SYNTHE_L FREQ_INTVAL 0.0')
        self.startfile.append('SET SYNTHE_L RX_NAME \'H22\'')
        self.startfile.append('SET SYNTHE_L NMA_FLAG 0')
        self.startfile.append('SET SYNTHE_L SIDBD_TYP \'USB\'')
        self.startfile.append('SET SYNTHE_L SCAN_COOD_OFF \'AZEL\'')
        # self.startfile.append('################################')
        # self.startfile.append('# Set Synthesizer SYNTHE_K Parameters #')
        # self.startfile.append('################################')
        self.startfile.extend(ut.UtilFunc.make_sqr_comment('Set Synthesizer SYNTHE_K Parameters'))
        self.startfile.append('SET SYNTHE_K VELO 24000.0')
        self.startfile.append('SET SYNTHE_K VDEF \'RAD\'')
        self.startfile.append('SET SYNTHE_K VREF \'LSR\'')
        self.startfile.append('SET SYNTHE_K INTERVAL 600')
        self.startfile.append('SET SYNTHE_K DOPPLER_TRK \'OFF\'')
        self.startfile.append('SET SYNTHE_K OBS_FREQ 4.32E10')
        self.startfile.append('SET SYNTHE_K FREQ_IF1 6.0E9')
        self.startfile.append('SET SYNTHE_K FREQ_SW \'OFF\'')
        self.startfile.append('SET SYNTHE_K FREQ_INTVAL 0.0')
        self.startfile.append('SET SYNTHE_K RX_NAME \'H40\'')
        self.startfile.append('SET SYNTHE_K NMA_FLAG 0')
        self.startfile.append('SET SYNTHE_K SIDBD_TYP \'USB\'')
        self.startfile.append('SET SYNTHE_K SCAN_COOD_OFF \'AZEL\'')
        self.startfile.append('######################')
        self.startfile.append('# Set RXT Parameters #')
        self.startfile.append('######################')
        self.startfile.append('SET RXT SETUP_FILE \'' + self.dat_filename.split('/')[-1] + '\'')
        self.startfile.append('SET RXT VELO 24000.0')
        self.startfile.append('SET RXT VDEF \'RAD\'')
        self.startfile.append('SET RXT VREF \'LSR\'')
        tmp = ''
        for i in range(0, 8):
            if i < len(self.rxlist):
                # tmp += '{:E}'.format(self.rxlist[i][2] * 1E+9)
                tmp_val = '{:E}'.format(self.rxlist[i][2] * 1E+9).split('E+')
                tmp += str(float(tmp_val[0])) + 'E' + tmp_val[1]
            else:
                tmp += '0.0'
            if i != 7:
                tmp += ','
        self.startfile.append('SET RXT OBS_FREQ (' + tmp + ')')
        tmp = ''
        for i in range(0, 8):
            if i < len(self.rxlist):
                # tmp += '{:E}'.format(self.IFFREQ[i] * 1E+9)
                tmp_val = '{:.1E}'.format(self.IFFREQ[i] * 1E+9).split('E+')
                tmp += str(tmp_val[0]) + 'E' + tmp_val[1]
            else:
                tmp += '0.0'
            if i != 7:
                tmp += ','
        self.startfile.append('SET RXT FREQ_IF1  (' + tmp + ')')
        tmp = ''
        tmp_rx_lst = []
        for i in range(0, 8):
            if i < len(self.rxlist):
                if self.rxlist[i][0][0:2] not in 'TZ' and self.rxlist[i][0][0:3] not in tmp_rx_lst:
                    # tmp += self.rxlist[i][0][0:3]
                    tmp_rx_lst.append(self.rxlist[i][0][0:3])
                # else:
                    # tmp += ','
            # if i != 7:
                # tmp += ','
        for i in range(0, 8):
            if i < len(tmp_rx_lst):
                tmp += tmp_rx_lst[i]
            if i != 7:
                tmp += ','
        self.startfile.append('SET RXT RX_NAME \'' + tmp + '\'')
        self.startfile.append('SET RXT RX_NUM 2')
        self.startfile.append('SET RXT USE_FLG (0,0,0)')
        self.startfile.append('EXECUTE RXT')
        self.startfile.append('####################')
        self.startfile.append('# Set IF Parameters #')
        self.startfile.append('#####################')
        self.startfile.append('SET IFATT DESTINATION ‘SAM45’')
        if self.startfile_mode['pointing']:
            self.startfile.append('#####################')
            self.startfile.append('# Set IF Parameters #')
            self.startfile.append('#####################')
            self.startfile.append('SET IFATT DESTINATION \'SAM45\'')

        
            self.startfile.append('##################')
            self.startfile.append('# SAM Parameters #')
            self.startfile.append('##################')
            self.startfile.append('SET SAM45 INTEG_TIME 10')
            self.startfile.append('SET SAM45 OBS_MODE \'POINTING\'')
            self.startfile.append('SET SAM45 CALB_INT 100')
            self.startfile.append('SET SAM45 SEQ_PTN \'1***1***\'')
            self.startfile.append('SET SAM45 OBS_USER \'vlbi3bz\'')
            self.startfile.append('SET SAM45 OBS_FILE \'tst-pt5\'')
            self.startfile.append('SET SAM45 GROUP \'vlbi3bz\'')
            self.startfile.append('SET SAM45 PROJECT \'proj1\'')
            self.startfile.append('SET SAM45 VELO 24000.0')
            self.startfile.append('SET SAM45 VDEF \'RAD\'')
            self.startfile.append('SET SAM45 VREF \'LSR\'')
            self.startfile.append('SET SAM45 IPTIM 0.1')
            self.startfile.append('SET SAM45 MAP_POS 0 ')
            self.startfile.append('SET SAM45 SW_MODE \'POS\'')
            self.startfile.append('SET SAM45 FREQ_SW 0')
            self.startfile.append('SET SAM45 FREQ_INTVAL (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')
            self.startfile.append('SET SAM45 MULT_MODE \'OFF\'')
            self.startfile.append('SET SAM45 MULT_OFF 0.0 ')
            self.startfile.append('SET SAM45 MULT_NUM (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')
            tmp = ''
            for i in range(0, 32):
                if i < len(self.array_list) and self.array_list[i][0] != None:
                    tmp += 'USB'
                if i + 1 != 32:
                    tmp += ','
            self.startfile.append('SET SAM45 SIDBD_TYP \'' + tmp + '\'')
            self.startfile.append('SET SAM45 REF_NUM (12,12,12,12,12,12,11,11,0,0,3,3,0,0,5,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')

            tmp = ''
            for i in range(0, 32):
                if i < len(self.array_list):
                    if self.array_list[i][0] != None:
                        tmp_val = '{:E}'.format(self.array_list[i][3] * 1E+6).split('E+')
                        tmp += str(float(tmp_val[0]))+ 'E' + tmp_val[1]
                    else:
                        tmp += '0.0'
                if i + 1 != 32:
                    tmp += ','
            self.startfile.append('SET SAM45 REST_FREQ (' + tmp + ')')

            tmp = ''
            for i in range(0, 32):
                if i < len(self.array_list):
                    if self.array_list[i][0] != None:
                        tmp_val = '{:E}'.format(self.array_list[i][2] * 1E+9).split('E+')
                        tmp += str(float(tmp_val[0])) + 'E' + tmp_val[1]
                    else:
                        tmp += '0.0'
                if i + 1 != 32:
                    tmp += ','
            self.startfile.append('SET SAM45 OBS_FREQ (' + tmp + ')')

            tmp = ''
            for i in range(0, 32):
                if i < len(self.array_list):
                    if self.array_list[i][0] != None:
                        tmp_val = '{:.1E}'.format(self.IFFREQ[i] * 1E+9).split('E+')
                        tmp += tmp_val[0] + 'E' + tmp_val[1]
                    else:
                        tmp += '0.0'
                if i + 1 != 32:
                    tmp += ','
            self.startfile.append('SET SAM45 FREQ_IF1 (' + tmp + ')')

            tmp = ''
            for i in range(0, 32):
                if i < len(self.array_list) and self.array_list[i][0] != None:
                        tmp += self.array_list[i][0]
                if i + 1 != 32:
                    tmp += ','
            self.startfile.append('SET SAM45 RX_NAME \'' + tmp + '\'')

            self.startfile.append('SET SAM45 OBS_BAND (1.25E8,1.25E8,1.25E8,1.25E8,1.25E8,1.25E8,1.25E8,1.25E8,0,0,2.0E9,2.0E9,0,0,2.0E9,2.0E9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')

            tmp = ''
            for i in range(0, 32):
                if i < len(self.array_list) and self.array_list[i][0] != None:
                    tmp += '1'
                else:
                    tmp += '0'
                if i + 1 != 32:
                    tmp += ','
            self.startfile.append('SET SAM45 ARRAY (' + tmp + ')')

            self.startfile.append('SET SAM45 OTF_MODE \'OFF\'')
            
            tmp = ''
            for i in range(0, 32):
                if i < len(self.array_list) and self.array_list[i][0] != None:
                    tmp += str(self.att[i])
                else:
                    tmp += '0'
                if i + 1 != 32:
                    tmp += ','
            self.startfile.append('SET SAM45 IFATT (' + tmp + ')')


            self.startfile.append('SET SAM45 FQDAT_F0 (2.225E10,2.225E10,2.2041E10,2.223508E10,2.2041E10,2.223508E10,4.3342E10,4.282054E10,0,0,8.69E10,8.85E10,0,0,8.69E10,8.85E10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')
            self.startfile.append('SET SAM45 FQDAT_FQ (2.218752E10,2.231248E10,2.218752E10,2.231248E10,2.197852E10,2.210348E10,2.21726E10,2.229756E10,2.197852E10,2.210348E10,2.21726E10,2.229756E10,4.327952E10,4.340448E10,4.275805E10,4.288302E10,0,0,0,0,8.590024E10,8.789976E10,8.750024E10,8.949976E10,0,0,0,0,8.590024E10,8.789976E10,8.750024E10,8.949976E10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')
            self.startfile.append('SET SAM45 FQDAT_CH (4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,0,0,0,0,4096,1,4096,1,0,0,0,0,4096,1,4096,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')
            self.startfile.append('SET SAM45 TRK_TYPE \'RADEC\'')
            self.startfile.append('SET SAM45 SRC_NAME \'R-Cas\'')
            self.startfile.append('SET SAM45 SRC_POS (359.603637,51.388806)')
            self.startfile.append('SET SAM45 EPOCH \'J2000\'')
            self.startfile.append('SET SAM45 SCAN_COOD \'AZEL\'')
            tmp = ''
            for i in range(0, 32):
                if i < len(self.array_list) and self.array_list[i][0] != None:
                    tmp += '1'
                else:
                    tmp += '0'
                if i + 1 != 32:
                    tmp += ','
            self.startfile.append('SET SAM45 CH_BIND (' + tmp + ')')
            self.startfile.append('SET SAM45 CH_RANGE (1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')
            self.startfile.append('SET SAM45 QL_AUTOSTOP \'OFF\'')
            self.startfile.append('SET SAM45 QL_RMSARY \'A01\'')
            self.startfile.append('SET SAM45 QL_RMSLIMIT 0.0001')
            self.startfile.append('SET SAM45 QL_POINTMODE \'SEQ\'')
            self.startfile.append('SET SAM45 QL_POINTNUM 1')
            self.startfile.append('SET SAM45 BIN_NUM 1')
            self.startfile.append('SET SAM45 SUB_ARRAY \'ON\'')
            self.startfile.append('SET SAM45 MISC_FLAGS_LFS \'ON,ON\'')
            self.startfile.append('SET SAM45 MISC_FLAGS_MULT \'BEFORE,BEFORE\'')
            self.startfile.append('SET SAM45 INPUT_MODE \'XX&YY,XX&YY\'')
            self.startfile.append('SET SAM45 N_SPEC_WINDOW_SUB1 1')
            self.startfile.append('SET SAM45 FREQ_PROF_SYNTH_SUB1 \'OFF,OFF\'')
            self.startfile.append('SET SAM45 WIN_FUNC_ID_SUB1 \'NONE,NONE\'')
            self.startfile.append('SET SAM45 START_CHAN_SUB1 (245760,0)')
            self.startfile.append('SET SAM45 END_CHAN_SUB1 (278527,0)')
            self.startfile.append('SET SAM45 CHAN_AVG_SUB1 (8,0)')
            self.startfile.append('SET SAM45 N_SPEC_WINDOW_SUB2 1')
            self.startfile.append('SET SAM45 START_CHAN_SUB2 (0,0)')
            self.startfile.append('SET SAM45 END_CHAN_SUB2 (524287,0)')
            self.startfile.append('SET SAM45 CHAN_AVG_SUB2 (128,0)')
            self.startfile.append('SET SAM45 MAKE_HFS_TABLE \'OFF,OFF\'')
            self.startfile.append('SET SAM45 MISC_FLAGS_HFS \'OFF,OFF\'')
            self.startfile.append('SET SAM45 BUT_SCALE \'BUT_SCALE_10_sub1.def,BUT_SCALE_10_sub2.def\'')
            self.startfile.append('DECIDE MANAGER LOG_ID')






        self.startfile.append('#############################')
        self.startfile.append('# Initialize MMC Parameters #')
        self.startfile.append('#############################')
        self.startfile.append('EXECUTE MMC CMD(AOF)')
        self.startfile.append('EXECUTE MMC CMD(OPN)')
        self.startfile.append('EXECUTE MMC CMD(SKY)')
        self.startfile.append('EXECUTE MMC CMD(MOP)')
        self.startfile.append('WAIT MMC')
        self.startfile.append('####################################')
        self.startfile.append('# Moving the antenna to the target #')
        self.startfile.append('####################################')
        self.startfile.append('EXECUTE SYNTHE ACTION(CREATE)')
        self.startfile.append('EXECUTE SYNTHE OFFSET(0.000000,0.000000) TYPE(ZERO)')
        self.startfile.append('EXECUTE ANT OFFSET(0.050000,0.000000) TYPE(ZERO)')
        self.startfile.append('WAIT_READY ANT')
        # self.startfile.append('WAIT RXT')
        # if self.startfile_mode['pointing']:
        # self.startfile.append('EXECUTE SAM45 ACTION(CREATE)')
        self.startfile.append('###############################')
        self.startfile.append('# Preliminary setup for SAM45 #')
        self.startfile.append('###############################')
        self.startfile.append('EXECUTE RXT ACTION(LEVEL1ST)')
        self.startfile.append('WAIT RXT')
        self.startfile.append('EXECUTE SAM45 TYPE(PRE)')
        self.startfile.append('WAIT SAM45')
        self.startfile.append('EXECUTE RXT ACTION(LEVEL2ND)')
        self.startfile.append('WAIT RXT')


        
        # self.startfile.append('##############')
        # self.startfile.append('# Zero Point #')
        # self.startfile.append('##############')
        # self.startfile.append('WAIT MMC')
        # if self.startfile_mode['pointing']:
        #     self.startfile.append('SET SAM45 INTEG_TIME 1')
        #     self.startfile.append('EXECUTE SAM45 TYPE(ZERO)')
        #     self.startfile.append('WAIT SAM45')
        # self.startfile.append('INTERRUPT ANT SYNTHE')
        # # self.startfile.append('EXECUTE MRG')


        # self.startfile.append('#############')
        # self.startfile.append('# CALIB (R) #')
        # self.startfile.append('#############')
        # if self.startfile_mode['pointing']:
        #     self.startfile.append('SET SAM45 INTEG_TIME 10')
        # self.startfile.append('EXECUTE MMC CMD(MCL)')
        # tmp = ''
        tmp = ''
        for i in range(0, 16):
            if i < len(self.array_list) and self.array_list[i][0] != None:
                tmp += str(self.att[i])
            else:
                tmp += '0'
            if i + 1 != 16:
                tmp += ','
        self.startfile.append('EXECUTE IFATT CMD(' + tmp + ')')

        # self.startfile.append('EXECUTE ANT OFFSET(0.050000,0.000000) TYPE(R)')
        # self.startfile.append('WAIT_READY ANT')
        self.startfile.append('WAIT IFATT')
        # self.startfile.append('WAIT MMC')
        # if self.startfile_mode['pointing']:
        #     self.startfile.append('EXECUTE SAM45 TYPE(R)')
        #     self.startfile.append('WAIT SAM45')
        # self.startfile.append('INTERRUPT ANT')
        # self.startfile.append('EXECUTE IFATT CMD(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)')
        # self.startfile.append('###############')
        # self.startfile.append('# CALIB (SKY) #')
        # self.startfile.append('###############')
        # self.startfile.append('EXECUTE MMC CMD(MOP)')
        # self.startfile.append('EXECUTE ANT OFFSET(0.050000,0.000000) TYPE(SKY)')
        # self.startfile.append('WAIT_READY ANT')
        # self.startfile.append('WAIT MMC')
        # self.startfile.append('WAIT IFATT')
        # if self.startfile_mode['pointing']:
        #     self.startfile.append('EXECUTE SAM45 TYPE(SKY)')
        #     self.startfile.append('WAIT SAM45')
        # self.startfile.append('INTERRUPT ANT')
        
        # for i in range(0, 16):
        #     if i < len(self.array_list) and self.array_list[i][0] != None:
        #         tmp += str(self.att[i])
        #     else:
        #         tmp += '0'
        #     if i + 1 != 16:
        #         tmp += ','
        # self.startfile.append('EXECUTE IFATT CMD(' + tmp + ')')


        if self.startfile_mode['vlbi']:
            counter = 0
            #SCHEDの名前からSOURCEを探索
            for scan in range(len(SCHED_Start_index)):
            #----------------------------------------------------------
                if SCHED_LIST[scan][3] == 0:
                    print("#############################")
                    print("######## TIME ERR0R #########")
                    print("#        scan%d SKIP        #" %(scan+1))
                    print("#############################")

                    self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                    self.startfile.append("#-------- TIME ERROR --------")
                    self.startfile.append("#-------- SKIP SKED%04d --------\n\n" %(scan+1))
                    continue
                #------------------------------------#
                #---------- original start ----------#
                #------------------------------------#
                if self.start_time_flag == "original_start":
                    offset_time = SCHED_LIST[scan][0]
                    start_offset_time = ut.UtilFunc.str_time_to_time(offset_time)
                    start_offset_time = datetime.datetime(int(start_offset_time[0]), int(start_offset_time[1]), int(start_offset_time[2]), int(start_offset_time[3]), int(start_offset_time[4]), int(start_offset_time[5]))
                    start_offset_time = start_offset_time + datetime.timedelta(hours=9)

                    #ほぼscan == 0 は関係ない
                    if scan == 0:
                        end_offset_time = end_offset_time + datetime.timedelta(seconds=self.TIME_MOVE_ANTENNA)
                    else:
                        end_offset_time = end_offset_time + datetime.timedelta(seconds=self.time_of_second_move)



                    WAIT_MMC_TIME = 0
                    #print MODE_LIST
                    for m in MODE_LIST:
                        if SCHED_LIST[scan][1] == m[0]:
                            for p in PROCEDURES_LIST:
                                if m[1] == p[0]:
                                    WAIT_MMC_TIME = int(p[1])



                    #observation start time
                    if WAIT_MMC_TIME > 0:
                        OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=self.before_observation+WAIT_MMC_TIME+self.after_mmc)
                    else:
                        OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=self.before_observation)



                    #時間のERROR判定
                    if (ut.UtilFunc.time_plus_or_minus(OBSERVATION_BEFORE_TIME, end_offset_time) > 0):
                        pass
                    else:
                        if WAIT_MMC_TIME > 0:
                            OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=WAIT_MMC_TIME+self.after_mmc)
                        else:
                            OBSERVATION_BEFORE_TIME = start_offset_time



                        if (ut.UtilFunc.time_plus_or_minus(OBSERVATION_BEFORE_TIME, end_offset_time) > 0):
                            pass
                        else:
                            if self.error_flag == "skip_flag":
                                print("#############################")
                                print("######## TIME ERR0R #########")
                                print("#        scan%d SKIP        #" %(scan+1))
                                print("#############################")

                                self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                                self.startfile.append("#-------- TIME ERROR --------")
                                self.startfile.append("#-------- SKIP SKED%04d --------\n\n" %(scan+1))
                                continue

                            else:
                                print("#############################")
                                print("######## TIME ERR0R #########")
                                print("#        scan%d STOP        #" %(scan+1))
                                print("#############################")
                                sys.exit()





                    if scan == 0:
                        CURRENT_TIME = OBSERVATION_BEFORE_TIME - datetime.timedelta(seconds=self.TIME_MOVE_ANTENNA)


                    end_sec = int(SCHED_LIST[scan][3].split(':')[2].strip('sec'))
                    end_offset_time = start_offset_time + datetime.timedelta(seconds=end_sec)


                    #ファイルに書き込み部
                    SOURCE_NAME_SAMPLE = SCHED_LIST[scan][2]
                    self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                    self.startfile.append("EXECUTE MMC CMD(AOF)")
                    self.startfile.append("EXECUTE MMC CMD(OPN)")
                    self.startfile.append("SET ANT TRK_TYPE \'RADEC\'")

                    SOURCE_NUMBER = 0
                    for i in range(len(SOURCE_LIST)):
                        if SOURCE_NAME_SAMPLE == SOURCE_LIST[i][0]:
                            SOURCE_NUMBER = i
                    #print SOURCE_NAME_SAMPLE, ":", SOURCE_LIST[SOURCE_NUMBER][0]


                    right_ascension = float(SOURCE_LIST[SOURCE_NUMBER][1][0:2]) * 15 + float(SOURCE_LIST[SOURCE_NUMBER][1][3:5]) * (15/60.0) + float(SOURCE_LIST[SOURCE_NUMBER][1][6:8]) * (15/3600.0) + 0.01 * float(SOURCE_LIST[SOURCE_NUMBER][1][9:11]) * (15/3600.0)

#                    if SOURCE_LIST[SOURCE_NUMBER][2][0] == "+" or SOURCE_LIST[SOURCE_NUMBER][2][0] == "-":
#                        declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0
#                    else:
#                        declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:2]) + float(SOURCE_LIST[SOURCE_NUMBER][2][3:5]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][6:10]) / 3600.0


                    if SOURCE_LIST[SOURCE_NUMBER][2][0] == "-":
                        declination = -1.0*(float(SOURCE_LIST[SOURCE_NUMBER][2][1:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0)
                    elif SOURCE_LIST[SOURCE_NUMBER][2][0] == "+":
                        declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0
                    else:
                        declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:2]) + float(SOURCE_LIST[SOURCE_NUMBER][2][3:5]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][6:10]) / 3600.0


                    #ファイル書き込み部
                    self.startfile.append("SET GRPTRK SRC_NAME \'" + SOURCE_LIST[SOURCE_NUMBER][0] + "\'")
                    self.startfile.append("SET GRPTRK SRC_POS ( %.5f, %.5f)\n" %(right_ascension, declination))
                    self.startfile.append("SET ANT SCAN_COOD \'RADEC\'")
                    self.startfile.append("SET ANT SCAN_COOD_OFF \'RADEC\'")
                    self.startfile.append("SET VLBI OBS_MODE \'NORMAL\'")
                    self.startfile.append("SET VLBI SCHDULE \'SKED%03d\'\n" %(scan+1))
                    self.startfile.append("SET GRPTRK EPOCH \'" + SOURCE_LIST[SOURCE_NUMBER][3] + "'")


                    self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, OBSERVATION_BEFORE_TIME.year, OBSERVATION_BEFORE_TIME.month, OBSERVATION_BEFORE_TIME.day, OBSERVATION_BEFORE_TIME.hour, OBSERVATION_BEFORE_TIME.minute, OBSERVATION_BEFORE_TIME.second))

                    CURRENT_TIME = OBSERVATION_BEFORE_TIME
                    self.startfile.append("WAIT_READY ANT")


                    if WAIT_MMC_TIME > 0:
                        self.startfile.append("EXECUTE MMC CMD(MCL)")
                        NEXT_TIME = CURRENT_TIME + datetime.timedelta(seconds=WAIT_MMC_TIME)
                        self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, NEXT_TIME.year, NEXT_TIME.month, NEXT_TIME.day, NEXT_TIME.hour, NEXT_TIME.minute, NEXT_TIME.second))

                        CURRENT_TIME = NEXT_TIME + datetime.timedelta(seconds=self.after_mmc)
                        #end_offset_time = CURRENT_TIME + datetime.timedelta(seconds=end_sec+30)
                        self.startfile.append("WAIT_READY ANT")
                        self.startfile.append("WAIT MMC")
                        self.startfile.append("EXECUTE MMC CMD(MOP)")
                        self.startfile.append("WAIT MMC")





                    self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, end_offset_time.year, end_offset_time.month, end_offset_time.day, end_offset_time.hour, end_offset_time.minute, end_offset_time.second))
                    self.startfile.append("WAIT ANT VLBI")
                    self.startfile.append("")
                    CURRENT_TIME = end_offset_time



                #------------------------------#
                #---------- any time ----------#
                #------------------------------#
                if self.start_time_flag == "any_start":
                    if scan == 0:
                        start_offset_time = ut.UtilFunc.str_time_to_time(self.any_time)
                        start_offset_time = datetime.datetime(int(start_offset_time[0]), int(start_offset_time[1]), int(start_offset_time[2]), int(start_offset_time[3]), int(start_offset_time[4]), int(start_offset_time[5]))
                        start_offset_time = start_offset_time + datetime.timedelta(hours=9)
                        critetia_time = start_offset_time



                    offset_time = SCHED_LIST[scan][0]
                    start_offset_time = ut.UtilFunc.str_time_to_time(offset_time)
                    start_offset_time = datetime.datetime(int(start_offset_time[0]), int(start_offset_time[1]), int(start_offset_time[2]), int(start_offset_time[3]), int(start_offset_time[4]), int(start_offset_time[5]))
                    start_offset_time = start_offset_time + datetime.timedelta(hours=9)
                    end_offset_time = end_offset_time + datetime.timedelta(seconds=self.time_of_second_move)


                    if ut.UtilFunc.time_plus_or_minus(critetia_time, start_offset_time) > 0:
                        print("#############################")
                        print("######## TIME ERR0R #########")
                        print("#        scan%d SKIP        #" %(scan+1))
                        print("#############################")
                        self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                        self.startfile.append("#-------- TIME ERROR --------")
                        self.startfile.append("#-------- SKIP SKED%04d --------\n\n" %(scan+1))


                        continue
                    else:
                        counter += 1

                    WAIT_MMC_TIME = 0
                    #print MODE_LIST
                    for m in MODE_LIST:
                        if SCHED_LIST[scan][1] == m[0]:
                            for p in PROCEDURES_LIST:
                                if m[1] == p[0]:
                                    WAIT_MMC_TIME = int(p[1])



                    #observation start time
                    if WAIT_MMC_TIME > 0:
                        OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=self.before_observation+WAIT_MMC_TIME+self.after_mmc)
                    else:
                        OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=self.before_observation)



                    #時間のERROR判定
                    if (ut.UtilFunc.time_plus_or_minus(OBSERVATION_BEFORE_TIME, end_offset_time) > 0):
                        pass
                    else:
                        if WAIT_MMC_TIME > 0:
                            OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=WAIT_MMC_TIME+self.after_mmc)
                        else:
                            OBSERVATION_BEFORE_TIME = start_offset_time



                        if (ut.UtilFunc.time_plus_or_minus(OBSERVATION_BEFORE_TIME, end_offset_time) > 0):
                            pass
                        else:
                            if self.error_flag == "skip_flag":
                                print("#############################")
                                print("######## TIME ERR0R #########")
                                print("#        scan%d SKIP        #" %(scan+1))
                                print("#############################")

                                self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                                self.startfile.append("#-------- TIME ERROR --------")
                                self.startfile.append("#-------- SKIP SKED%04d --------\n\n" %(scan+1))
                                continue

                            else:
                                print("#############################")
                                print("######## TIME ERR0R #########")
                                print("#        scan%d STOP        #" %(scan+1))
                                print("#############################")
                                sys.exit()




                    if counter == 1:
                        CURRENT_TIME = OBSERVATION_BEFORE_TIME - datetime.timedelta(seconds=self.TIME_MOVE_ANTENNA)


                    end_sec = int(SCHED_LIST[scan][3].split(':')[2].strip('sec'))
                    end_offset_time = start_offset_time + datetime.timedelta(seconds=end_sec)


                    #ファイルに書き込み部
                    SOURCE_NAME_SAMPLE = SCHED_LIST[scan][2]
                    self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                    self.startfile.append("EXECUTE MMC CMD(AOF)")
                    self.startfile.append("EXECUTE MMC CMD(OPN)")
                    self.startfile.append("SET ANT TRK_TYPE \'RADEC\'")

                    SOURCE_NUMBER = 0
                    for i in range(len(SOURCE_LIST)):
                        if SOURCE_NAME_SAMPLE == SOURCE_LIST[i][0]:
                            SOURCE_NUMBER = i
                    #print SOURCE_NAME_SAMPLE, ":", SOURCE_LIST[SOURCE_NUMBER][0]


                    right_ascension = float(SOURCE_LIST[SOURCE_NUMBER][1][0:2]) * 15 + float(SOURCE_LIST[SOURCE_NUMBER][1][3:5]) * (15/60.0) + float(SOURCE_LIST[SOURCE_NUMBER][1][6:8]) * (15/3600.0) + 0.01 * float(SOURCE_LIST[SOURCE_NUMBER][1][9:11]) * (15/3600.0)

                    if SOURCE_LIST[SOURCE_NUMBER][2][0] == "+" or SOURCE_LIST[SOURCE_NUMBER][2][0] == "-":
                        declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0
                    else:
                        declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:2]) + float(SOURCE_LIST[SOURCE_NUMBER][2][3:5]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][6:10]) / 3600.0

                    #ファイル書き込み部
                    self.startfile.append("SET GRPTRK SRC_NAME \'" + SOURCE_LIST[SOURCE_NUMBER][0] + "\'")
                    self.startfile.append("SET GRPTRK SRC_POS ( %.5f, %.5f)\n" %(right_ascension, declination))
                    self.startfile.append("SET ANT SCAN_COOD \'RADEC\'")
                    self.startfile.append("SET ANT SCAN_COOD_OFF \'RADEC\'")
                    self.startfile.append("SET VLBI OBS_MODE \'NORMAL\'")
                    self.startfile.append("SET VLBI SCHDULE \'SKED%03d\'\n" %(scan+1))
                    self.startfile.append("SET GRPTRK EPOCH \'" + SOURCE_LIST[SOURCE_NUMBER][3] + "'")


                    self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, OBSERVATION_BEFORE_TIME.year, OBSERVATION_BEFORE_TIME.month, OBSERVATION_BEFORE_TIME.day, OBSERVATION_BEFORE_TIME.hour, OBSERVATION_BEFORE_TIME.minute, OBSERVATION_BEFORE_TIME.second))

                    CURRENT_TIME = OBSERVATION_BEFORE_TIME
                    self.startfile.append("WAIT_READY ANT")


                    if WAIT_MMC_TIME > 0:
                        self.startfile.append("EXECUTE MMC CMD(MCL)")
                        NEXT_TIME = CURRENT_TIME + datetime.timedelta(seconds=WAIT_MMC_TIME)
                        self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, NEXT_TIME.year, NEXT_TIME.month, NEXT_TIME.day, NEXT_TIME.hour, NEXT_TIME.minute, NEXT_TIME.second))

                        CURRENT_TIME = NEXT_TIME + datetime.timedelta(seconds=self.after_mmc)
                        #end_offset_time = CURRENT_TIME + datetime.timedelta(seconds=end_sec+30)
                        self.startfile.append("WAIT_READY ANT")
                        self.startfile.append("WAIT MMC")
                        self.startfile.append("EXECUTE MMC CMD(MOP)")
                        self.startfile.append("WAIT MMC")





                    self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, end_offset_time.year, end_offset_time.month, end_offset_time.day, end_offset_time.hour, end_offset_time.minute, end_offset_time.second))
                    self.startfile.append("WAIT ANT VLBI")
                    self.startfile.append("")
                    CURRENT_TIME = end_offset_time
                    critetia_time = CURRENT_TIME




                #------------------------------#
                #---------- after time ----------#
                #------------------------------#
                if self.start_time_flag == "after_start":
                    if scan == 0:
                        start_offset_time = datetime.datetime.today() + datetime.timedelta(days=self.after_day, hours=self.after_hours, minutes=self.minute_minutes)
                        critetia_time = start_offset_time


                    offset_time = SCHED_LIST[scan][0]
                    start_offset_time = ut.UtilFunc.str_time_to_time(offset_time)
                    start_offset_time = datetime.datetime(int(start_offset_time[0]), int(start_offset_time[1]), int(start_offset_time[2]), int(start_offset_time[3]), int(start_offset_time[4]), int(start_offset_time[5]))
                    start_offset_time = start_offset_time + datetime.timedelta(hours=9)
                    end_offset_time = end_offset_time + datetime.timedelta(seconds=self.time_of_second_move)

                    counter = 0
                    if ut.UtilFunc.time_plus_or_minus(critetia_time, start_offset_time) > 0:
                        print("#############################")
                        print("######## TIME ERR0R #########")
                        print("#        scan%d SKIP        #" %(scan+1))
                        print("#############################")
                        self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                        self.startfile.append("#-------- TIME ERROR --------")
                        self.startfile.append("#-------- SKIP SKED%04d --------\n\n" %(scan+1))
                        continue
                    else:
                        counter += 1

                    WAIT_MMC_TIME = 0
                    #print MODE_LIST
                    for m in MODE_LIST:
                        if SCHED_LIST[scan][1] == m[0]:
                            for p in PROCEDURES_LIST:
                                if m[1] == p[0]:
                                    WAIT_MMC_TIME = int(p[1])



                    #observation start time
                    if WAIT_MMC_TIME > 0:
                        OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=self.before_observation+WAIT_MMC_TIME+self.after_mmc)
                    else:
                        OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=self.before_observation)



                    #時間のERROR判定
                    if (ut.UtilFunc.time_plus_or_minus(OBSERVATION_BEFORE_TIME, end_offset_time) > 0):
                        pass
                    else:
                        if WAIT_MMC_TIME > 0:
                            OBSERVATION_BEFORE_TIME = start_offset_time - datetime.timedelta(seconds=WAIT_MMC_TIME+self.after_mmc)
                        else:
                            OBSERVATION_BEFORE_TIME = start_offset_time



                        if (ut.UtilFunc.time_plus_or_minus(OBSERVATION_BEFORE_TIME, end_offset_time) > 0):
                            pass
                        else:
                            if self.error_flag == "skip_flag":
                                print("#############################")
                                print("######## TIME ERR0R #########")
                                print("#        scan%d SKIP        #" %(scan+1))
                                print("#############################")

                                self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                                self.startfile.append("#-------- TIME ERROR --------")
                                self.startfile.append("#-------- SKIP SKED%04d --------\n\n" %(scan+1))
                                continue

                            else:
                                print("#############################")
                                print("######## TIME ERR0R #########")
                                print("#        scan%d STOP        #" %(scan+1))
                                print("#############################")
                                sys.exit()





                    if counter == 1:
                        CURRENT_TIME = OBSERVATION_BEFORE_TIME - datetime.timedelta(seconds=self.TIME_MOVE_ANTENNA)


                    end_sec = int(SCHED_LIST[scan][3].split(':')[2].strip('sec'))
                    end_offset_time = start_offset_time + datetime.timedelta(seconds=end_sec)


                    #ファイルに書き込み部
                    SOURCE_NAME_SAMPLE = SCHED_LIST[scan][2]
                    self.startfile.append("#-------- PARAMS for SKED%04d --------\n" %(scan+1))
                    self.startfile.append("EXECUTE MMC CMD(AOF)")
                    self.startfile.append("EXECUTE MMC CMD(OPN)")
                    self.startfile.append("SET ANT TRK_TYPE \'RADEC\'")

                    SOURCE_NUMBER = 0
                    for i in range(len(SOURCE_LIST)):
                        if SOURCE_NAME_SAMPLE == SOURCE_LIST[i][0]:
                            SOURCE_NUMBER = i
                    #print SOURCE_NAME_SAMPLE, ":", SOURCE_LIST[SOURCE_NUMBER][0]


                    right_ascension = float(SOURCE_LIST[SOURCE_NUMBER][1][0:2]) * 15 + float(SOURCE_LIST[SOURCE_NUMBER][1][3:5]) * (15/60.0) + float(SOURCE_LIST[SOURCE_NUMBER][1][6:8]) * (15/3600.0) + 0.01 * float(SOURCE_LIST[SOURCE_NUMBER][1][9:11]) * (15/3600.0)

                    # if SOURCE_LIST[SOURCE_NUMBER][2][0] == "+" or SOURCE_LIST[SOURCE_NUMBER][2][0] == "-":
                    #     declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0
                    # else:
                    #     declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:2]) + float(SOURCE_LIST[SOURCE_NUMBER][2][3:5]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][6:10]) / 3600.0
                    if SOURCE_LIST[SOURCE_NUMBER][2][0] == "-":
                        declination = -1.0*(float(SOURCE_LIST[SOURCE_NUMBER][2][1:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0)
                    elif SOURCE_LIST[SOURCE_NUMBER][2][0] == "+":
                        declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:3]) + float(SOURCE_LIST[SOURCE_NUMBER][2][4:6]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][7:11]) / 3600.0
                    else:
                        declination = float(SOURCE_LIST[SOURCE_NUMBER][2][0:2]) + float(SOURCE_LIST[SOURCE_NUMBER][2][3:5]) / 60.0 + float(SOURCE_LIST[SOURCE_NUMBER][2][6:10]) / 3600.0

                    #ファイル書き込み部
                    self.startfile.append("SET GRPTRK SRC_NAME \'" + SOURCE_LIST[SOURCE_NUMBER][0] + "\'")
                    self.startfile.append("SET GRPTRK SRC_POS ( %.5f, %.5f)\n" %(right_ascension, declination))
                    self.startfile.append("SET ANT SCAN_COOD \'RADEC\'")
                    self.startfile.append("SET ANT SCAN_COOD_OFF \'RADEC\'")
                    self.startfile.append("SET VLBI OBS_MODE \'NORMAL\'")
                    self.startfile.append("SET VLBI SCHDULE \'SKED%03d\'\n" %(scan+1))
                    self.startfile.append("SET GRPTRK EPOCH \'" + SOURCE_LIST[SOURCE_NUMBER][3] + "'")


                    self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, OBSERVATION_BEFORE_TIME.year, OBSERVATION_BEFORE_TIME.month, OBSERVATION_BEFORE_TIME.day, OBSERVATION_BEFORE_TIME.hour, OBSERVATION_BEFORE_TIME.minute, OBSERVATION_BEFORE_TIME.second))

                    CURRENT_TIME = OBSERVATION_BEFORE_TIME
                    self.startfile.append("WAIT_READY ANT")


                    if WAIT_MMC_TIME > 0:
                        self.startfile.append("EXECUTE MMC CMD(MCL)")
                        NEXT_TIME = CURRENT_TIME + datetime.timedelta(seconds=WAIT_MMC_TIME)
                        self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, NEXT_TIME.year, NEXT_TIME.month, NEXT_TIME.day, NEXT_TIME.hour, NEXT_TIME.minute, NEXT_TIME.second))

                        CURRENT_TIME = NEXT_TIME + datetime.timedelta(seconds=self.after_mmc)
                        #end_offset_time = CURRENT_TIME + datetime.timedelta(seconds=end_sec+30)
                        self.startfile.append("WAIT_READY ANT")
                        self.startfile.append("WAIT MMC")
                        self.startfile.append("EXECUTE MMC CMD(MOP)")
                        self.startfile.append("WAIT MMC")





                    self.startfile.append("EXECUTE ANT OFFSET(0,0) TIME_RANGE(%04d/%02d/%02d %02d:%02d:%02d - %04d/%02d/%02d %02d:%02d:%02d) TYPE(ON)\n" %(CURRENT_TIME.year, CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.hour, CURRENT_TIME.minute, CURRENT_TIME.second, end_offset_time.year, end_offset_time.month, end_offset_time.day, end_offset_time.hour, end_offset_time.minute, end_offset_time.second))
                    self.startfile.append("WAIT ANT VLBI")
                    self.startfile.append("")
                    CURRENT_TIME = end_offset_time

        self.startfile.append("WAIT ANT")
        self.startfile.append("WAIT MMC")
        self.startfile.append("WAIT VLBI")
        self.startfile.append("WAIT RXT")
        self.startfile.append("WAIT IFATT") 
        self.startfile.append("CLOSE IFATT")
        self.startfile.append("CLOSE RXT")
        # self.startfile.append("CLOSE IFATT")
        self.startfile.append("CLOSE ANT")
        self.startfile.append("CLOSE MMC")
        self.startfile.append("CLOSE VLBI")

        ut.UtilFunc.ask_and_write(self.start_file_name, self.startfile, self.start_file_flag, self.yes)


        #-------------------------------------------------#
        #  alert parameter
        #-------------------------------------------------#
        print("USER NAME              : " + self.USER_NAME)
        print("CREATE Date            :", end=' ')
        print(Create_Date)
        print("ANTENNA NAME           : " + self.station_name)
        print(".VEX FILE NAME         : " + self.vex_file_name)
        print(".START FILE NAME       : " + self.start_file_name)

        return True



if __name__ == "__main__":
    vs = Vex2Start()
    vs.prm_filename = 'parm.py'
    vs.get_var()
    vs.vex2start()