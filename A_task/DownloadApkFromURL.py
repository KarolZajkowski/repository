import json
import openpyxl
import pandas as pd
import requests
import glob
import re
import time
import multiprocessing
from multiprocessing import freeze_support
import os
from functools import partial
import tqdm
import sys
import colorama
import io
import copy
import datetime
import pickle
import xlrd
from shutil import copy2

"""APK download tool - gets and download apk from url located in excel tab, 
column in separated process (pull in multiple threads)
"""


class GetData:
    @staticmethod
    def get_data():
        return datetime.datetime.now().strftime("dd%d_mm%m_yyyyy%Y")


class DataPickle:
    data = []

    @staticmethod
    def save_to_file(path, data):
        path = path + ".data"
        with open(path, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def read_from_file(cls, path):
        db = dict()

        try:
            with open(path, 'rb') as f:
                db = pickle.load(f)

        except FileNotFoundError:
            print("\nThere is no database in data file...")

        finally:
            cls.data.append(db)
            return db


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
        print("Exception", base_path)

    return os.path.join(base_path, relative_path)


def spiting_an_excel_bat(main_data, excel_report_dir, tab_name):

    try:
        request_excel_to_split = [i for i in excel_report_dir if tab_name in i]

        excel_name_no = 0
        if len(request_excel_to_split) == 0:
            request_excel_to_split_single_file = input("\n\tType name of excel folder with test requested apps for"
                                                       " spited to single SN: ")
            request_excel_to_split.append(request_excel_to_split_single_file)

        elif len(request_excel_to_split) >= 2:
            try:
                dic_with_excel = {}
                i = 0
                for excel in request_excel_to_split:
                    print(f"\tExcel file no.{i}\t  Name:", excel, "\t-Type number or file name")
                    dic_with_excel[excel] = str(i)
                    i += 1

                get_data_base_to_compare = input("\n\tSelect excel data to open file: ")

                for key, value in dic_with_excel.items():

                    if value == str(get_data_base_to_compare):
                        print("\nSelected Number: ", key, "\tName: ", value)
                        excel_name_no = int(value)
                        break

                if excel_name_no != 0 and type(excel_name_no) == int():
                    print("excel_name_no ", excel_name_no)
                    excel_name_no = int(dic_with_excel[get_data_base_to_compare])

            except KeyError:
                print("\n\tWrong value/name for selected excel - "
                      "open tool one more time and select one more time correctly name")
                time.sleep(10)
                sys.exit()

        else:
            print("Requested excel file under test", request_excel_to_split[excel_name_no])
            time.sleep(1)

        try:
            workbook = xlrd.open_workbook(request_excel_to_split[excel_name_no])
            sheet = workbook.sheet_names()
            print("\n\nSheet available in request excel: ", sheet)

            tab_index = int()
            for index, tab in enumerate(sheet):
                if tab_name in tab:
                    tab_index = index
                    print(f"\tChosen {tab}\n\n")
                    break

            df_report = pd.read_excel(request_excel_to_split[excel_name_no], sheet_name=tab_index, index_col=1,
                                      header=0, )
                                      
            all_data_for_testing = []

            for key in df_report.T.keys():
                all_data_for_testing.append(key)

        except IndexError:
            all_data_for_testing = []

        print("All data length for testing:", len(all_data_for_testing))

        all_data_from_base = list()
        if len(excel_dir) != 0:
            for excel in excel_dir:
                new_name_excel = excel.replace(".xls", "").replace(" ", "").replace(")", "").replace("(", "")

                df = pd.read_excel(excel, sheet_name=0, index_col=0, header=0)

                header = df.head().keys()
                for key_name in df.T.keys():
                    all_data_from_base.append(key_name)

        else:
            dic_ = {}
            i = 1
            for file in main_data.keys():
                print(f"\tFile no.{i}\t  Name:", file, "\t-Type number or name file")
                dic_[str(i)] = file

                i += 1

            # print(dic_)
            if len(dic_) == 0:
                print("\nThere is no any base with apps available on this PC. "
                      "\nDownload app_excel from url"
                      "and after that download app...")
                time.sleep(10)
                sys.exit()

            get_data_base_to_compare = input("\n\tSelect data file to read base data file with downloaded apps: ")
            for key, value in dic_.items():
                if key == str(get_data_base_to_compare):
                    print("\nSelected Number: ", key, "\tName: ", value)
                    excel_name = value
                    break

                else:
                    excel_name = get_data_base_to_compare

            for row in main_data[excel_name].keys():
                all_data_from_base.append(row)

            new_name_excel = excel_name.replace("data\\", "").replace(".data", "")

        print("all_data_from_base: ", all_data_from_base)
        print("all_data_from_base len: ", len(all_data_from_base))
        print("all_data_from_base len: ", len(set(all_data_from_base)))

        excel_file = new_name_excel + "_excel_" + time_now
        bat_file = new_name_excel + "_bat_" + time_now
        if os.path.exists(excel_file) and os.path.exists(bat_file):
            print("\n\nPath exist... ", excel_file, " and ", bat_file)

        else:
            os.makedirs(excel_file)
            os.makedirs(bat_file)

        all_data = []
        with open(f"{bat_file}\\install_package_{new_name_excel}_all_apps.bat", 'w') as f:
            f.write("@echo off")
            f.write("\nadb wait-for-device")
            f.write("\nfor /F \"skip=1\" %%i in ('adb devices') do (")
            f.write("\n	echo %%i")

            print("Just application for retest! No more except, just retest app in bat folder to install...")
            time.sleep(2)

            for key_all_data_for_testing in all_data_for_testing:
                for key_all_data_from_base in all_data_from_base:

                    if key_all_data_for_testing == key_all_data_from_base:
                        print(f"\n\t\tPackage name: {key_all_data_for_testing} - application found!")
                        f.write(f"\n	adb -s %%i install ..\\{new_name_excel}\\{key_all_data_for_testing}.apk")
                        all_data.append(key_all_data_for_testing)
            f.write("\n)")
            f.write("\npause")

        new_count_ = len(all_data)
        print("counted all (all in base): ", new_count_)

        samples = input("\nType how many samples will be in use: ")
        samples = int(samples)

        division_ = int(new_count_ / samples)
        print("division: ", division_)

        range_from_, range_to_ = 0, division_

        j = 1
        for i in range(0, samples):
            writer = pd.ExcelWriter(f'{excel_file}\\{new_name_excel}_{j}.xlsx')

            with open(f"{bat_file}\\install_package_{new_name_excel}_{j}.bat", 'w') as f:
                f.write("@echo on")
                f.write("\nadb wait-for-device")
                f.write("\nadb devices")
                f.write("\nset /p sn=\"sn:\"")
                f.write("\necho %sn% in use")

                data_range = all_data[range_from_:range_to_]

                range_from_header = str(int(range_from_) + 1)
                range_to_header = str(int(range_to_) + 1)

                if j == samples:

                    for key_all_data_for_testing in data_range:
                        f.write(f"\nadb -s %sn% install ..\\{new_name_excel}\\{key_all_data_for_testing}.apk")

                    print("LP", i + 1, "\tRange from:", range_from_header, "\tRange to:", range_to_header)

                else:
                    for key_all_data_for_testing in data_range:
                        f.write(f"\nadb -s %sn% install ..\\{new_name_excel}\\{key_all_data_for_testing}.apk")

                    print("LP", i + 1, "\tRange from:", range_from_header, "\tRange to:", range_to_header)

                f.write("\n")
                f.write("\n\necho -----  %sn%  ----- ")
                f.write("\n\necho Success - all apps installed! ")
                f.write("\npause")

                df_range = pd.DataFrame(data_range, columns=[f'Total Rank {range_from_header}-{range_to_header}'])
                df_range.to_excel(writer, sheet_name="Sheet1", index=False)
                writer.save()

                j += 1

                range_to_ += division_
                range_from_ += division_

    except IndexError:
        print("\nNo base excel file"
              "should be inside to split an excel...")
        time.sleep(30)
        sys.exit()

    else:
        print("\tProcess finished - spited apps added...")
        time.sleep(30)
        sys.exit()


def get_download_app(data_url):
    package_name, _, _, file_path_url, package_dir = data_url

    print("\n\nURL: ", file_path_url, "\nPackage direction: ", package_dir)

    r = requests.get(file_path_url, allow_redirects=True)
    io.open(package_dir, 'wb').write(r.content)

    print("\n\n\t"+"\x1b[6;30;42m" + "Finished downloading package: ", package_name + "\x1b[0m")


def main_process(main_data, excel_report_dir, tab_name):
    print("\n\nThe Main process of downloading apps...")
    print("Physically available processors: ", multiprocessing.cpu_count())

    try:
        cpu = input("\n\n\tHow many CPU you would like to use? \n\tType and enter:  ")
        cpu = int(cpu)
    except ValueError:
        print("Wrong value for CPU input...\n\tType integer!")
        time.sleep(7)
        sys.exit()

    request_excel_to_split = [i for i in excel_report_dir if tab_name in i]
    retest_excel = [i for i in excel_report_dir if tab_name not in i]

    if len(retest_excel) != 0:
        if len(retest_excel) == 1:
            tab_index = 0
            print(f"\nSelected excel {retest_excel[0]} for retests...")
            time.sleep(1)

        else:
            tab_index = int()
            temp_excels_report = {}
            for index, excel_name in enumerate(retest_excel):
                print(f"\tFile no.{index}\t  Name:", excel_name, "\t-Type number or name file")
                temp_excels_report[excel_name] = str(index)

            selected_file = input("\nPlease select number or name of excel for retest: ")

            for key, value in temp_excels_report.items():

                if value == str(selected_file):
                    print("\nSelected Number: ", key, "\tName: ", value)
                    tab_index = int(value)
                    print(f"\nSelected excel {retest_excel[tab_index]} for retests...")
                    break

            if tab_index != 0 and type(tab_index) == int():
                tab_index = int(temp_excels_report[selected_file])
                print(f"\nSelected excel {retest_excel[tab_index]} for retests...")

        try:
            df_report = pd.read_excel(excel_report_dir[tab_index], sheet_name="Test Results", index_col=1, header=2, )
            data_unpass = {}
            sorting_by_pass = df_report.loc[df_report["column name"] == "unpass"]

            for key, values in sorting_by_pass.T.items():
                data_unpass.setdefault(key, values[2])

        except IndexError:
            print("\n\tSomething went wrong... "
                  "Apps for retests are taken form tab named 'Test Results' "
                  "and filtered on column named 'column name'")
            time.sleep(5)
            sys.exit()

        except xlrd.biffh.XLRDError:
            print("\n\tSomething went wrong... "
                  "Apps for retests are taken form tab named 'Test Results' "
                  "and filtered on column named 'column name'")
            time.sleep(5)
            sys.exit()


    else:
        data_unpass = False

    print("data unpass: ", data_unpass)

    all_db = dict()
    print(request_excel_to_split)

    if len(excel_dir) == 0:
        pass


    else:
        for excel in excel_dir:
            new_name_excel = excel.replace(".xls", "").replace(" ", "").replace(")", "").replace("(", "")
            print("\n\n\tFile selected: ", new_name_excel)

            all_db = dict()

            try:
                temp_d = main_data[f'data\\{new_name_excel}.data']
                all_db.update(temp_d)

            except TypeError:
                print(f"\nType Error occurred. Check if data for data\\{new_name_excel}.data exist")

            except KeyError:
                print(f"\nKey Error occurred. Check if data for data\\{new_name_excel}.data exist")

            df = pd.read_excel(excel, sheet_name=0, index_col=0, header=0)

            header = df.head().keys()
            for count, value in enumerate(header):
                if value == "app name":
                    app_name = count
                elif value == "version":
                    version = count

                elif value == "file path":
                    file_path = count

            count = int(df["file path"].count())
            print("count all: ", count)

            if os.path.exists(new_name_excel):
                print("\n\nPath exist... ", new_name_excel)

            else:
                os.makedirs(new_name_excel)
                print("\n\nPath created... ", new_name_excel)

            data_for_download = {}

            for key, values in df.T.items():

                package_name_dir = new_name_excel + "\\" + key + ".apk"
                package_tuple = (values[app_name], values[version], values[file_path], package_name_dir)

                try:
                    if all_db[key]:
                        print("\nPackage exist in base: ", all_db[key])

                        if all_db[key][1] == package_tuple[1]:
                            print("Same version here: ", package_tuple[1], "\n\n")

                        else:
                            print("\tNot this same version here!\n\n",
                                  all_db[key][1], "!=", package_tuple[1])
                            all_db[key] = package_tuple
                            data_for_download[key] = package_tuple

                except KeyError:

                    all_db.setdefault(key, package_tuple)
                    data_for_download.setdefault(key, package_tuple)

            if not data_unpass:
                print("No data for retest here - skipped")
                # pass

            else:
                temp = {}
                for key, value in data_unpass.items():
                    try:
                        if all_db[key]:

                            if all_db[key][1] == value:
                                print("Same version here: ", value, "\n\n")

                            else:
                                print("\tNot this same version here!\n\n", all_db[key][1], "!=", value)
                                temp[key] = all_db[key]

                    except KeyError:
                        print(f"There is no this package name in base! Must be wrong retested file "
                              f"- no downloaded before apps. \tPackage name: {key}")

                data_for_download.clear()
                data_for_download.update(temp)

            print("All data after compare retested app: ", data_for_download)


            path_data_pickle = f"{data_dir}\\{new_name_excel}"
            with open(f"{path_data_pickle}.json", "w") as json_file:
                json_file.write(json.dumps(all_db, indent=4))

            save_data = DataPickle()
            save_data.save_to_file(path_data_pickle, all_db)

            list_url = []
            for key_pack, value_package in data_for_download.items():
                temp = (key_pack, value_package[0], value_package[1], value_package[2], value_package[3])
                list_url.append(temp)

            print("\n\n\nCout difference: ", len(list_url))

            print(f"\n\n\tStarting process for project {new_name_excel}...")
            start_time = time.time()

            pool = multiprocessing.Pool(cpu)

            result = pool.map(func=get_download_app, iterable=list_url)
            pool.close()
            pool.join()

            end_time = time.time()
            print(f"\nAll apps downloaded for {new_name_excel}- took (s): ",
                  end_time - start_time, "\n\t Process can be closed...")
            time.sleep(2)

        print("Process finished - all data downloaded! ")
        time.sleep(6000)
        sys.exit()


if __name__ == '__main__':
    freeze_support()
    time_now = GetData.get_data()

    actual_dir = os.getcwd()
    data_dir = os.path.join(actual_dir, "data")

    excel_dir = glob.glob("*.xls")
    excel_report_dir = glob.glob("*.xlsx")
	tab_name = input("Type excel tab name: ")

    print("\n\n {:^3}     {:^60}".format("___", "_" * 60))
    print("|{:^3}|   |{:^60}|".format("1", "Do you want, to split task for multi devices"))
    print("|{:^3}|   |{:^60}|".format(" ", "install bat file & excel file)? '1', 'True' or 'yes' if yes"))
    print("|{:^3}|   |{:^60}|".format("___", "_"*60))
    print("|{:^3}|   |{:^60}|".format("2", "Downloaded tool for apk files... Type 'download' or '2'"))
    print("|{:^3}|   |{:^60}|".format("___", "_"*60))
    print("|{:^3}|   |{:^60}|".format("3", "Get Guide for this tool. Type '3' or enter"))
    print("|{:^3}|   |{:^60}|".format("___", "_"*60))

    input_command = str(input("\n\tType value for selected process...: "))

    main_data = {}
    if os.path.exists(data_dir):
        main_data_base = glob.glob("data\\*.data")
        read_data = DataPickle()

        for path_data_pickle in main_data_base:
            try:
                main_data_to_update = read_data.read_from_file(path_data_pickle)

            except TypeError:
                main_data_to_update = dict()

            finally:
                temp = {path_data_pickle: main_data_to_update}
                main_data.update(temp)

    else:
        os.mkdir(data_dir)

    if input_command.lower() == "true" or input_command.lower() == "yes" or input_command.lower() == "1":

        spiting_an_excel_bat(main_data, excel_report_dir, tab_name)

    elif input_command.lower() == "download" or input_command.lower() == "2":
        main_process(main_data, excel_report_dir, tab_name)

    else:
        dir = os.getcwd()
        folder_presentation = "path/for/prezentation"
        presentation = resource_path(folder_presentation)
        copy2(presentation, dir)
        print("\n\n\tFile created!")
        time.sleep(5)



