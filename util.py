#! /usr/local/bin/Python3
# Python version 3 (and 2)
# Contents: ツール関係
# Since   : Nov, 2019
#           Yuki Hamae
# Update  : Oct, 2020
#           Beta版リリース

import datetime
# import sys
import os
# import re
import traceback
# import math
# import collections
import inspect
import sys


class UtilFunc():
    # @staticmethod
    def str_time_to_time(str_time):
        month = str(datetime.date(int(str_time[0:4]), 1, 1) + datetime.timedelta(days=int(str_time[5:8]) - 1))[5:7]
        day = str(datetime.date(int(str_time[0:4]), 1, 1) + datetime.timedelta(days=int(str_time[5:8]) - 1))[8:10]
        time_list = [str_time[0:4], month, day, str_time[9:11], str_time[12:14], str_time[15:17]]
        return time_list


    def time_plus_or_minus(str_time1, str_time2):
        # ye = (int(str_time1.year) - int(str_time2.year))
        # mo = (int(str_time1.month) - int(str_time2.month))
        # da = (int(str_time1.day) - int(str_time2.day))
        # ho = (int(str_time1.hour) - int(str_time2.hour))
        # mi = (int(str_time1.minute) - int(str_time2.minute))
        # se = (int(str_time1.second) - int(str_time2.second))
        porm = int((str_time1 - str_time2).days)

        if porm >= 0:
            return 1
        else:
            return -1

    def get_parameter(l, x, default=""):  # get parameter val by "l"
        if x in l:
            if not '-' in l[l.index(x) + 1]:
                return l[l.index(x) + 1]
            else:
                raise IndexError
        else:
            return default


    def export_ldata(*args):
        # 第一引数: 書き出しファイルの名前（※リストで渡さない）
        # 第二引数以降: 書き出したいデータ
        try:
            with open(args[0], mode='w') as f:
                for line in args[1:]:
                    f.write('\n'.join([str(s) for s in line]) + "\n")
            print('Export File Name is "' + args[0] + '"')

        except FileNotFoundError as e:
            print(">>>    " + e)
            traceback.print_exc()
            return False

    def ask_and_write(name, outlist, flag = True, yes_or_no = True):
        filename = name

        if flag:
            if yes_or_no:
                while True:
                    if os.path.exists(filename):
                        print(pycolor.YELLOW + filename + " is exists" + pycolor.END)
                        print("Do you overwrite This file?")
                        print("y/n: ", end="")
                        tmp = input().strip()
                        if tmp[0] == "y":
                            break
                        else:
                            print("Enter New file name: ", end="")
                            filename = input().strip()
                    else:
                        break

            status = UtilFunc.export_ldata(filename, outlist)

        else:
            l = len(max(outlist, key=len))
            # print("\nConvert Data is bellow")
            print("-" * l)
            print('\n'.join(outlist))
            print("-" * l)
            status = None
        return status

    def print_err_msg(TF, e, *msg):
        if not isinstance(TF, str):
            if TF:
                print(pycolor.RED + "Error(Python): " + pycolor.END, end = "")
                print(e)
                traceback.print_exc()
            print(pycolor.RED + "Error: " + pycolor.END, end = "")
            print('\n       '.join(msg))
            exit()
    def print_red_msg(TF, *msg):
        if not isinstance(TF, str):
            if TF:
                print(pycolor.RED + "Error(Python): " + pycolor.END, end = "")
                # print(e)
                # traceback.print_exc()
            # print(pycolor.RED + "Error: " + pycolor.END, end = "")
            # print('\n       '.join(msg))
            exit()



    def print_warning_msg(e, *msg):
        if not e:
            print(pycolor.YELLOW + "WARNING: " + pycolor.END, end = "")
            print('\n         '.join(msg))


    def make_sqr_comment(msg, moji = '#'):
        comment = []
        if isinstance(msg, list):
            lst = msg
        else:
            lst = [msg]
        max_len =  max([len(x) for x in lst])
        comment.append(moji * (max_len + 4))
        for s in lst:
            shortage = max_len - len(str(s))
            comment.append(moji + ' ' + str(s) + (' ' * shortage) + ' ' + moji)
        comment.append(moji * (max_len + 4))
        return comment

    ####################
    #  Debag関係の関数  #
    ####################
    def chkprint(*args):
        names = {id(v): k for k, v in inspect.currentframe().f_back.f_locals.items()}
        print(pycolor.PURPLE + str(inspect.currentframe().f_back.f_lineno).zfill(4) + pycolor.END + ":    " + '\n         '.join(names.get(id(arg), '???') + ' = ' + repr(arg) for arg in args))

    def chklprint(*args):
        names = {id(v): k for k, v in inspect.currentframe().f_back.f_locals.items()}
        print(pycolor.PURPLE + str(inspect.currentframe().f_back.f_lineno).zfill(4) + pycolor.END + ":    len(" + '\n         len('.join(names.get(id(arg), '???') + ') = ' + str(len(arg)) for arg in args))

    def chkprint2(val_name, val):
        print(pycolor.PURPLE + str(inspect.currentframe().f_back.f_lineno).zfill(4) + pycolor.END + ":    " + val_name + " = " + str(val))

    def chklprint2(val_name, val):
        print(pycolor.PURPLE + str(inspect.currentframe().f_back.f_lineno).zfill(4) + pycolor.END + ":    len(" + val_name + ") = " + str(len(val)))
    def chkprintstr(val):
        print(pycolor.PURPLE + str(inspect.currentframe().f_back.f_lineno).zfill(4) + pycolor.END  + ":    " + val)
    def chklistprint(val_name, lists):
        print(pycolor.PURPLE + str(inspect.currentframe().f_back.f_lineno).zfill(4) + pycolor.END + ":    " + str(val_name) + ' =\n         ' + '\n         '.join(map(str, lists)))




class pycolor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE = '\033[07m'
    BLINK = '\033[05m'

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        tmp = args[1]
    else:
        tmp = ' '.join(map(str, args[1:]))
    print('\n'.join(UtilFunc.make_sqr_comment(tmp)))