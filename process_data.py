import os
import numpy as np
import csv
import re
import pandas as pd
from random import sample
from random import randint

'''
    For the given path, get the List of all files in the directory tree 
'''

program_dict = {'blackscholes': 0, 'dedup': 1, 'streamcluster': 2, 'swaptions': 3, 'freqmine': 4, 'fluidanimate': 5}


def getListOfFiles(dirName, subset, train):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)

    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        if dirName == '../data' and train and program_dict[entry] not in subset:
            continue
        if dirName == '../data' and not train and program_dict[entry] in subset:
            continue
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath, subset, train)
        else:
            allFiles.append(fullPath)

    return allFiles


def merge_data(processed_file, merged_file):
    df = pd.read_csv(processed_file)
    merge_dict = {}
    for key in df.keys():
        merge_dict[key] = []
        count = 0
        for file in df['Filename']:
            if "mem" in file and key == 'Normalized time avg':
                merge_dict[key].append(df[key].values[count])
            elif re.search("x86.", file) and key != 'Normalized time avg':
                merge_dict[key].append(df[key].values[count])
            count = count + 1

    df_merge = pd.DataFrame(data=merge_dict)
    df_merge.to_csv(path_or_buf='./{}'.format(merged_file), index=False)


def main():
    dirName = '../data'

    # Get the list of all files in directory tree at given path

    subset = sample([i for i in range(5)], 4)
    listOfTrainFiles = getListOfFiles(dirName, subset, True)
    listOfTestFiles = getListOfFiles(dirName, subset, False)
    run_number = str(randint(0, 10000))
    train_data_folder = 'train_{}'.format(run_number)
    test_data_folder = 'test_{}'.format(run_number)
    if not os.path.exists(train_data_folder):
        os.mkdir(test_data_folder)
        os.mkdir(train_data_folder)
    row = ['Filename', 'Normalized integer', 'Normalized floating', 'Normalized control', 'Cycles',
           'Normalized time avg',
           'Ratio Memory', 'Ratio branches', 'Ratio call', 'Phase']
    config_train_files = ['{}/processed_config_{}_4_40.csv'.format(train_data_folder, 'train'),
                          '{}/processed_config_{}_4_60.csv'.format(train_data_folder, 'train'),
                          '{}/processed_config_{}_4_80.csv'.format(train_data_folder, 'train'),
                          '{}/processed_config_{}_4_100.csv'.format(train_data_folder, 'train'),
                          '{}/processed_config_{}_8_40.csv'.format(train_data_folder, 'train'),
                          '{}/processed_config_{}_8_60.csv'.format(train_data_folder, 'train'),
                          '{}/processed_config_{}_8_80.csv'.format(train_data_folder, 'train'),
                          '{}/processed_config_{}_8_100.csv'.format(train_data_folder, 'train')]
    config_test_files = ['{}/processed_config_{}_4_40.csv'.format(test_data_folder, 'test'),
                         '{}/processed_config_{}_4_60.csv'.format(test_data_folder, 'test'),
                         '{}/processed_config_{}_4_80.csv'.format(test_data_folder, 'test'),
                         '{}/processed_config_{}_4_100.csv'.format(test_data_folder, 'test'),
                         '{}/processed_config_{}_8_40.csv'.format(test_data_folder, 'test'),
                         '{}/processed_config_{}_8_60.csv'.format(test_data_folder, 'test'),
                         '{}/processed_config_{}_8_80.csv'.format(test_data_folder, 'test'),
                         '{}/processed_config_{}_8_100.csv'.format(test_data_folder, 'test')]

    merged_train_files = ['{}/merged_config_{}_4_40.csv'.format(train_data_folder, 'train'),
                          '{}/merged_config_{}_4_60.csv'.format(train_data_folder, 'train'),
                          '{}/merged_config_{}_4_80.csv'.format(train_data_folder, 'train'),
                          '{}/merged_config_{}_4_100.csv'.format(train_data_folder, 'train'),
                          '{}/merged_config_{}_8_40.csv'.format(train_data_folder, 'train'),
                          '{}/merged_config_{}_8_60.csv'.format(train_data_folder, 'train'),
                          '{}/merged_config_{}_8_80.csv'.format(train_data_folder, 'train'),
                          '{}/merged_config_{}_8_100.csv'.format(train_data_folder, 'train')]
    merged_test_files = ['{}/merged_config_{}_4_40.csv'.format(test_data_folder, 'test'),
                         '{}/merged_config_{}_4_60.csv'.format(test_data_folder, 'test'),
                         '{}/merged_config_{}_4_80.csv'.format(test_data_folder, 'test'),
                         '{}/merged_config_{}_4_100.csv'.format(test_data_folder, 'test'),
                         '{}/merged_config_{}_8_40.csv'.format(test_data_folder, 'test'),
                         '{}/merged_config_{}_8_60.csv'.format(test_data_folder, 'test'),
                         '{}/merged_config_{}_8_80.csv'.format(test_data_folder, 'test'),
                         '{}/merged_config_{}_8_100.csv'.format(test_data_folder, 'test')]

    create_data(config_train_files, listOfTrainFiles, merged_train_files, row, 'train', run_number)
    create_data(config_test_files, listOfTestFiles, merged_test_files, row, 'test', run_number)

    write_best_config(merged_train_files, run_number)


def create_data(config_files, listOfTrainFiles, merged_files, row, phase, run_number):
    for config, merge_file in zip(config_files, merged_files):
        with open(config, "w", newline='') as processed_file:
            writer = csv.writer(processed_file)
            writer.writerow(row)
        processed_file.close()
    folder = '{}{}{}'.format(phase, '_', run_number)
    for elem in listOfTrainFiles:

        file = open(elem, "r")
        if '4core-100cache' in file.name:
            process_file(file, '{}/processed_config_{}_4_100.csv'.format(folder, phase))
        if '4core-80cache' in file.name:
            process_file(file, '{}/processed_config_{}_4_80.csv'.format(folder, phase))
        if '4core-60cache' in file.name:
            process_file(file, '{}/processed_config_{}_4_60.csv'.format(folder, phase))
        if '4core-40cache' in file.name:
            process_file(file, '{}/processed_config_{}_4_40.csv'.format(folder, phase))
        if '8core-100cache' in file.name:
            process_file(file, '{}/processed_config_{}_8_100.csv'.format(folder, phase))
        if '8core-80cache' in file.name:
            process_file(file, '{}/processed_config_{}_8_80.csv'.format(folder, phase))
        if '8core-60cache' in file.name:
            process_file(file, '{}/processed_config_{}_8_60.csv'.format(folder, phase))
        if '8core-40cache' in file.name:
            process_file(file, '{}/processed_config_{}_8_40.csv'.format(folder, phase))
        file.close()
    for processed_file, merge_file in zip(config_files, merged_files):
        if not os.path.isfile(merge_file):
            merge_data(processed_file, merge_file)


def getNumberofRows(config_files):
    number_of_rows = [pd.read_csv(config_file).get('Cycles').count() for config_file in config_files]
    return min(number_of_rows)


def write_best_config(config_files, run_number):
    number_of_rows = getNumberofRows(config_files)
    data = np.zeros([8, number_of_rows], dtype=np.int)
    for config, j in zip(config_files, range(8)):
        df = pd.read_csv(config)
        for i in range(number_of_rows):
            data[j:j + 1, i:i + 1] = df.get('Cycles')[i]
    config_exists = os.path.isfile('train_{}/best_config_file.csv'.format(run_number))
    if not config_exists:
        with open('train_{}/best_config_file.csv'.format(run_number), "w", newline="") as best_config:
            writer = csv.writer(best_config)
            writer.writerow(['Best Configuration', 'Previous Best Configuration'])
        best_config.close()

        for i in range(number_of_rows):
            cycles_arr = np.array(
                [data[0:1, i:i + 1][0][0], data[1:2, i:i + 1][0][0], data[2:3, i:i + 1][0][0], data[3:4, i:i + 1][0][0],
                 data[4:5, i:i + 1][0][0], data[5:6, i:i + 1][0][0], data[6:7, i:i + 1][0][0],
                 data[7:8, i:i + 1][0][0]])
            sorted_cycles_arr = sorted(cycles_arr)
            with open("train_{}/best_config_file.csv".format(run_number), "a", newline="") as best_config:
                writer = csv.writer(best_config)
                print(cycles_arr)

                print(np.where(cycles_arr == sorted(cycles_arr)[-2])[0][0])
                if sorted_cycles_arr[0] == sorted_cycles_arr[1]:
                    best_configs = [l for l, k in enumerate(cycles_arr) if k == min(cycles_arr)]
                    writer.writerow([best_configs[0], best_configs[1]])
                else:
                    writer.writerow([np.where(cycles_arr == sorted_cycles_arr[0])[0][0],
                                     np.where(cycles_arr == sorted_cycles_arr[1])[0][0]])
            best_config.close()


def process_file(file, processing_file):
    integers = np.array([])
    floating = np.array([])
    cntrl = np.array([])
    cycles = np.array([])
    time_data = np.array([])
    memory = np.array([])
    logic = np.array([])
    branches = np.array([])
    jump = np.array([])
    call = np.array([])
    integers_sum = 0
    floating_sum = 0
    cntrl_sum = 0
    cycles_sum = 0
    time_avg = 0
    memory_sum = 0
    logic_sum = 0
    branches_sum = 0
    jump_sum = 0
    call_sum = 0
    feature1 = 0
    feature2 = 0
    feature3 = 0
    feature4 = 0
    feature5 = 0
    feature6 = 0
    feature7 = 0
    timeSeries = False
    for line in file:
        if timeSeries and "BlockSize = " in line:
            timeSeries = False
        if timeSeries:
            time_data = np.append(time_data, int(line.split(" ")[1]))
        if "Busy stats" in line:
            timeSeries = True

        if " = " in line:
            if "Commit.Integer" in line:
                integers = np.append(integers, int(line.split("= ")[-1].strip()))
            if "Commit.FloatingPoint" in line:
                floating = np.append(floating, int(line.split("= ")[-1].strip()))
            if "Commit.Ctrl" in line:
                cntrl = np.append(cntrl, int(line.split("= ")[-1].strip()))
            if "Cycles = " in line:
                if re.search('^Cycles = ', line):
                    cycles = np.append(cycles, int(line.split("= ")[-1].strip()))
            if "Commit.Memory" in line:
                memory = np.append(memory, int(line.split("= ")[-1].strip()))
            if "Commit.Logic" in line:
                logic = np.append(logic, int(line.split("= ")[-1].strip()))
            if "Commit.Branches" in line:
                branches = np.append(branches, int(line.split("= ")[-1].strip()))
            if "Commit.Uop.jump" in line:
                jump = np.append(jump, int(line.split("= ")[-1].strip()))
            if ("Commit.Uop.call" in line) or ("Commit.Uop.syscall" in line):
                call = np.append(call, int(line.split("= ")[-1].strip()))

    if integers.size != 0:
        integers_sum = int(np.sum(integers))
    if floating.size > 0:
        floating_sum = int(np.sum(floating))
    if cntrl.size > 0:
        cntrl_sum = int(np.sum(cntrl))
    if cycles.size > 0:
        cycles_sum = int(np.sum(cycles))
    if time_data.size > 0:
        time_avg = int(np.average(time_data))
    if memory.size > 0:
        memory_sum = int(np.sum(memory))
    if logic.size > 0:
        logic_sum = int(np.sum(logic))
    if branches.size > 0:
        branches_sum = int(np.sum(branches))
    if jump.size > 0:
        jump_sum = int(np.sum(jump))
    if call.size > 0:
        call_sum = int(np.sum(call))
    feature1 = integers_sum / 500000
    feature2 = floating_sum / 500000
    feature3 = cntrl_sum / 500000
    feature4 = time_avg / 4096
    phase = file.name.split("\\")[-1].split("-")[-2]
    if integers_sum > 0:
        feature5 = memory_sum / (integers_sum + floating_sum + cntrl_sum + logic_sum)
        feature6 = (branches_sum - jump_sum) / jump_sum
        feature7 = call_sum / cntrl_sum
    row = [file.name.strip(), feature1, feature2, feature3, cycles_sum, feature4, feature5, feature6, feature7, phase]
    with open(processing_file, "a", newline='') as processed_file:
        writer = csv.writer(processed_file)
        writer.writerow(row)
    processed_file.close()


if __name__ == '__main__':
    main()
