import sqlite3
import os
import re
import json


""" Karol Zajkowski @ karolzajkowskidigital@gmail.com """


class FolderTree:
    db_dir = []

    def __init__(self, relative_path):
        self.__tempDir = "."
        self.relative_path = relative_path

    def __iter__(self):
        for x in self.relative_path:
            yield x

    @property
    def TempDir(self):
        return self.__tempDir

    @TempDir.setter
    def TempDir(self, newDir):
        if self:
            self.__tempDir = newDir

    @TempDir.deleter
    def TempDir(self):
        self.__tempDir = "."

    def dir(self, relative_path):

        base_path = os.path.isdir(relative_path)
        if base_path:
            temp_list = os.listdir(path=relative_path)

            if len(temp_list) > 0:
                for i in temp_list:
                    new_dir = os.path.join(relative_path, i)
                    self.dir(new_dir)

        else:
            self.TempDir += f"\\{relative_path}"
            if "dbname.db" in self.TempDir:
                # print(self.TempDir)
                self.db_dir.append(self.TempDir)
            del self.TempDir


class DataFromDB:
    dictionary_for_count = {}

    @classmethod
    def importdb(cls, db):
        print(f"\t_" * 17,
              f"\n\tCreating connection SQL db: {db}")
        try:
            connection = sqlite3.connect(db)
            cursor = connection.cursor()

            # # Check tables name
            # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            # print(cursor.fetchall())

            sqlite_select_query = """SELECT *
            FROM 'Case'
            INNER JOIN 'CheckPoint'
            ON 'Case'.'ID' = 'CheckPoint'.'FID_Case';"""

            cursor.execute(sqlite_select_query)
            records = cursor.fetchall()


            r = 1
            for row in records:
                # print(f"Row nr{r}: ", row)
                _, FullName, DurationAllText, _, FID_Case, Result, DurationTestText = row
                print(f"Row nr{r}: ", FullName, DurationAllText, FID_Case, Result, DurationTestText, "\n")

                DurationAll = cls.filtr(DurationAllText)
                DurationTest = cls.filtr(DurationTestText)

                try:
                    if cls.dictionary_for_count[FullName]:
                        cls.dictionary_for_count[FullName]["average_duration"].append(DurationAll)
                        cls.dictionary_for_count[FullName]["average_test_duration"].append(DurationTest)
                        cls.dictionary_for_count[FullName]["pass_ratio"].append(Result)

                except KeyError:
                    temp = {FullName: {
                        "average_duration": [DurationAll],
                        "average_test_duration": [DurationTest],
                        "pass_ratio": [Result]}}
                    cls.dictionary_for_count.update(temp)

                r += 1

        except sqlite3.OperationalError:
            print("\tProblem occurred - SQL closed")

        else:
            # print("\tConnection closed")
            if connection:
                cursor.close()
                connection.close()

        finally:
            print(f"\tProcess closed for {db}\n")

    @staticmethod
    def filtr(text):
        duration_time = re.findall(r"(\d+)", text)
        # print(duration_time)
        if len(duration_time) == 2:
            hours = 0
            minutes = 60 * int(duration_time[0])
            seconds = int(duration_time[1])
        elif len(duration_time) == 3:
            hours = 3600 * int(duration_time[0])
            minutes = 60 * int(duration_time[1])
            seconds = int(duration_time[2])
        else:
            hours = 0
            minutes = 0
            seconds = int(duration_time[-1])

        return hours+minutes+seconds


if __name__ == '__main__':

    relative_path = os.listdir()

    dirs_literate = FolderTree(relative_path)
    for i in dirs_literate:
        dirs_literate.dir(i)

    # # Check point
    # print(len(dirs_literate.db_dir))

    j = 1
    getData = DataFromDB()
    for db in dirs_literate.db_dir:
        getData.importdb(db)
        # print(j, "- done")
        j += 1

    count_dic = getData.dictionary_for_count
    # print("\n\n\n", getData.dictionary_for_count)
    data_to_save = {}
    for keys in count_dic.keys():
        data_to_save.setdefault(keys, {})

        for key_dic, value in count_dic[keys].items():
            all_count = len(value)

            if key_dic == "average_duration" or key_dic == "average_test_duration":
                # print(sum(value)//all_count, value)
                sumed_value = sum(value)

                sum_time = str((sumed_value//all_count))+"min " + \
                           str(int((((sumed_value%all_count)/all_count)*100*60)/100))+"s"
                data_to_save[keys].update({key_dic: sum_time})

            elif key_dic == "pass_ratio":
                dict = {"Passed": 0, "Failed": 0, "No result": 0}
                for rate in value:
                    if rate.lower() == 'passed':
                        dict.update({"Passed": dict["Passed"] + 1})
                    elif rate.lower() == 'failed':
                        dict.update({"Failed": dict["Failed"] + 1})
                    else:
                        # print("No result")
                        dict.update({"No result": dict["No result"] + 1})

                pass_ratio = str(((dict["Passed"]/all_count)*100).__round__(2))+"%"
                fail_ratio = str(((dict["Failed"]/all_count)*100).__round__(2))+"%"
                no_result_ratio = str(((dict["No result"]/all_count)*100).__round__(2))+"%"

                data_to_save[keys].update({key_dic: pass_ratio})
                data_to_save[keys].update({"fail_ratio": fail_ratio})
                data_to_save[keys].update({"no_result_ratio": no_result_ratio})

                # print(dict, all_count, pass_ratio)

    # print(data_to_save)
    with open("output.json", "w") as json_file:
        json.dump(data_to_save, json_file, indent=4)


