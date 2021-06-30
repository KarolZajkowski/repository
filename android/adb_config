from subprocess import Popen, PIPE, STDOUT
import pandas as pd
import re
import time
import sys
import os, shutil

""" Karol Zajkowsi
Easy tool for get data from android getprop in excel file"""


def test_devices():
    command0 = Popen('adb devices', shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output0 = command0.stdout.read()
    output0 = output0.decode('utf-8')
    # print(output0)
    output0 = output0.split('\r\n')
    output0 = [re.split("\t", value) for value in output0 if value != '']
    # print(output0)

    formatted_output_to_dictionary0 = {}
    count = 1
    for i in output0:
        if output0[-1] == output0[0]:
            formatted_output_to_dictionary0[output0[0][0]] = 'No devices'
        else:

            if i != output0[0]:
                formatted_output_to_dictionary0[output0[0][0] + ', Number {}'.format(count)] = i[0]
                count += 1
    print(formatted_output_to_dictionary0)

    commands2 = []
    for key in formatted_output_to_dictionary0.values():
        commands2.append('adb -s {} shell getprop'.format(key))
    # print(commands2)

    number_device = 1
    time_d = time.strftime("%Y_%m_%d")
    writer = pd.ExcelWriter('{}/pandas_device_config_{}.xlsx'.format(str(time_d), str(time_d)), mode='w',
                            engine='xlsxwriter')

    for command in commands2:
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        output = p.stdout.read()
        output = output.decode('utf-8')
        output = output.split('\r\n')
        output.remove('')
        # print(output)

        formated_output_to_dictionary1 = {}
        for i in output:
            formated_output_to_dictionary_temple = {}
            formated_output_to_dictionary_temple[i.split(': ')[0].strip('[]')] = i.split(': ')[1].strip('[]')
            formated_output_to_dictionary1.update(formated_output_to_dictionary_temple)
        print(formated_output_to_dictionary1)
        # print(formated_output_to_dictionary1)

        try:
            """File shutil"""
            # time_d = time.strftime("%Y_%m_%d")
            if os.path.exists(time_d):
                # shutil.rmtree(directory2)
                pass
            else:
                os.makedirs(time_d)

            ro_product_manufacturer = formated_output_to_dictionary1['ro.product.manufacturer']
            ro_product_model = formated_output_to_dictionary1['ro.product.model']
            name = ''.join('Device ' + str(number_device) + ' ' + ro_product_manufacturer + ' ' + ro_product_model)
            number_device += 1

            """adding device ID form ADB"""
            # formated_output_to_dictionary1['ADB device ID'] = command[7:25]
            formated_output_to_dictionary1['ADB device ID'] = re.match(r"(\w+)", command[7:28])[0]
            formated_output_to_dictionary1['Test time'] = time.strftime("%Y/%m/%d %H:%M:%S")

            """write to Excel"""
            df2 = pd.DataFrame(formated_output_to_dictionary1, index=['The properties of device']).T
            # writer = pd.ExcelWriter('{}/pandas_device_config_{}.xlsx'.format(time_d,time_d), mode='a', engine='xlsxwriter')
            df2.to_excel(writer, sheet_name='{}'.format(name))
            writer.save()

            # # TEST 2 not necessary
            # writer2 = pd.ExcelWriter('{}/pandas_device_config_{}.xlsx'.format(str(time_d), 'test_output'), mode='w',
            #                          engine='xlsxwriter')
            # df3 = pd.DataFrame(output)
            # df3.to_excel(writer2, sheet_name='TEST')
            # writer2.save()
            # # TEST 2

            """Format cell"""
            worksheet_object = writer.sheets[name]
            worksheet_object.set_column('A:B', 40)


        except:
            print('Something went wrong...', sys.exc_info())
            print(formated_output_to_dictionary1)


if __name__ == '__main__':
    test_devices()
