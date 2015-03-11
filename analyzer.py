#!/usr/bin/python
#analyze power consumption
#ying.tan@tcl.com

import os
import sys

RESULT_FILE = 'consumption_arrange_result.txt'
WAKELOCK_FILTER = 'PowerManagerService: releaseWakeLockInternal:'
WAKEUP_ALARM_FILTER = 'AlarmManager: wakeup alarm'
WAKELOCK_FILTER_INDEX = 82 #line.find(WAKELOCK_FILTER) + len(WAKELOCK_FILTER) + 1
WAKEUP_ALARM_FILTER_INDEX = 65 #line.find(WAKEUP_ALARM_FILTER) + len(WAKEUP_ALARM_FILTER) + 3

class Wakelock_Record:
    def __init__(self):
        self.id = ''
        self.key = ''
        self.total_time = None

class Wakeup_Record:
    def __init__(self):
        self.name = ''
        self.times = 0

def validate_path(filepath):
    filepath_list = []
    if os.path.isdir(filepath):
        for root,dirs,files in os.walk(filepath):
            for path in files:
                if path[:7] == 'sys_log':
                    filepath_list.append(os.path.join(filepath, path))
    else:
        filepath_list.append(filepath)

    return filepath_list

def change_time_to_int(string):
    return int(string [:-3])

def get_wakelock_obj(line):
    #change line into object
    line = line[WAKELOCK_FILTER_INDEX:]
    record = Wakelock_Record()
    record.id = line[5:15] #lock=1120168048
    line = line[16:]
    temp_index = line.find('],') + 3
    record.key = line[:temp_index-2]
    item_list = line[temp_index:].split(' ')
    record.total_time = (item_list[1][11:]) #len('total_time=')
    return record

def get_wakeup_obj(line):
    line = line[WAKEUP_ALARM_FILTER_INDEX:]
    wakeup_list = line.split(' ')
    record = Wakeup_Record()
    record.name = wakeup_list[len(wakeup_list) - 1][:-2]
    record.times +=1
    return record

def display_consumption(sorted_list, time_all, wakeup_record_list):
    string = '*****WAKELOCK_TOTAL_TIME_COUNTING*****\n\n'

    for item in sorted_list:
        percentage = float('%0.4f' % (float(item[1])/float(time_all) * 100))
        string += item[0] + ' total_time: ' + str(item[1]) + 'ms percentage:' + str(percentage) + '%\n'

    string += '\n\n*****WAKEUP ALARM TIMES COUNTING*****\n\n'

    for item in wakeup_record_list:
        string += item[0] + ':' + str(item[1]) + '\n'

    f = open(RESULT_FILE, 'w')
    result = str(string)
    f.write(result)
    f.close()

    print 'Consumption arranged successed!\nResult output in: ' + RESULT_FILE + '\n'

def count_consumption(wakelock_record_list, wakeup_record_list):
    count_dict = {}
    time_all = 0
    for record in wakelock_record_list:
        time_all += change_time_to_int(record.total_time)
        if not count_dict.has_key(record.key):
            count_dict[record.key] = change_time_to_int(record.total_time)
        else:
            count_dict[record.key] += change_time_to_int(record.total_time)


    sorted_list = sorted(count_dict.iteritems(), key=lambda d:d[1], reverse = True )  
    #display the result
    display_consumption(sorted_list, time_all, wakeup_record_list)

def main():
    argv_len = len(sys.argv)
    wakelock_record_list = []
    wakeup_record_dict = {}

    if argv_len < 2:
        print('should input log path!')
    else:
        #should validate log path
        path_list = validate_path(sys.argv[1])
        for log_path in path_list:
            fIn = open(log_path, 'rb')
            for  line in  fIn.readlines():
                wakelock_filter_index = line.find(WAKELOCK_FILTER)
                wakeup_filter_index = line.find(WAKEUP_ALARM_FILTER)
                if wakeup_filter_index > -1:
                    line = line[WAKEUP_ALARM_FILTER_INDEX:]
                    wakeup_list = line.split(' ')
                    name = wakeup_list[len(wakeup_list) - 1][:-2]
                    if wakeup_record_dict.has_key(name):
                        wakeup_record_dict[name] += 1
                    else:
                        wakeup_record_dict[name] = 1
                if wakelock_filter_index > -1:
                    wakelock_record = get_wakelock_obj(line)
                    # print record.total_time
                    #push the object into dict by key
                    wakelock_record_list.append(wakelock_record)

        wakeup_record_list = sorted(wakeup_record_dict.iteritems(), key=lambda d:d[1], reverse = True )

        #count the consumption by key
        sorted_list = count_consumption(wakelock_record_list, wakeup_record_list)

if __name__ == '__main__':
    main()