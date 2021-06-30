import sys
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os, shutil
import time

"""Karol Zajkowski
Old script for getting data scraping from tested page used in manual test to speed up tests"""

class Soup:
    page1 = {}
    page2 = {}
    page3 = {}
    page4 = {}

    def func(self):
        try:
            """1st page"""
            html = requests.get("http://eurd-test.lge.com/sanity/").content
            # print(html)
            unicode_str = html.decode("utf8")
            print(unicode_str)
            encoded_str = unicode_str.encode("ascii", 'ignore')
            news_soup = BeautifulSoup(encoded_str, 'html.parser')
            a_text = news_soup.find_all('a')
            print("a_text", a_text)

            for a in a_text:
                print(a)
                self.page1[''.join(re.sub(r'<.+?>', r'', str(a)))]= \
                    ''.join(str(a.get('href')).replace('.','http://eurd-test.lge.com/sanity', 1) if
                            '.' in str(a.get('href'))[0] else str(a.get('href')))
            print("\n\nSoup.page1", Soup.page1)

            """2nd page #107 - Alexa websites"""
            d = list(self.page1.items())
            new_page = d[-1][-1]

            html_new = requests.get(new_page).content
            unicode_str_new = html_new.decode("utf8")
            encoded_str_new = unicode_str_new.encode("ascii", 'ignore')
            news_soup_1 = BeautifulSoup(encoded_str_new, 'html.parser')
            a_text_new = news_soup_1.find_all('a')

            # gets all page from xml in list comprehension
            self.page2[str(d[-1][0])] = [''.join('http://eurd-test.lge.com/sanity/'+str(b.get('href'))) for b in a_text_new]

            for a, b in self.page2.items():
                for key in b:

                    html_Second = requests.get(str(key)).content
                    unicode_str_Second = html_Second.decode("utf8")
                    encoded_str_Second = unicode_str_Second.encode("ascii", 'ignore')
                    news_soup_Second = BeautifulSoup(encoded_str_Second, 'html.parser')
                    a_text_Second = news_soup_Second.find_all('a')

                    self.page3[''.join(str(key))] = [''.join(str(c.get('href'))) for c in a_text_Second]

            """3rd page #106 - Critical Websites"""
            g = list(self.page1.items())
            new_page2 = g[-2][-1]

            html_new2 = requests.get(new_page2).content
            unicode_str_new2 = html_new2.decode("utf8")
            encoded_str_new2 = unicode_str_new2.encode("ascii", 'ignore')
            news_soup_2 = BeautifulSoup(encoded_str_new2, 'html.parser')
            a_text_new2 = news_soup_2.find_all('a')

            self.page4[str(g[-2][0])] = [''.join(str(b.get('href'))) for b in a_text_new2]
            self.page0 = list(self.page1.items())

            """write to Excel"""
            def pandas_excel(dictionery_base):
                """File shutil"""
                time_d = time.strftime("%Y_%m_%d")
                if os.path.exists(time_d):
                    # shutil.rmtree(directory2)
                    pass
                else:
                    os.makedirs(time_d)

                df2 = pd.DataFrame(dictionery_base[0])
                df3 = pd.DataFrame(dictionery_base[1]).T
                df4 = pd.DataFrame(dictionery_base[2])
                df5 = pd.DataFrame(dictionery_base[3], columns =['Name', 'Uniform Resource Locator'])

                writer = pd.ExcelWriter('{}/eurd_test_lge_com.xlsx'.format(time_d), engine='xlsxwriter')
                df2.to_excel(writer, sheet_name='{}'.format('#107 - Alexa websites'))
                df3.to_excel(writer, sheet_name='{}'.format('Deeper #107 - Alexa websites'))
                df4.to_excel(writer, sheet_name='{}'.format('#106 - Critical Websites'))
                df5.to_excel(writer, sheet_name='{}'.format('Messaging Server'))
                """Format cell"""
                worksheet_object2 = writer.sheets['#107 - Alexa websites']
                worksheet_object2.set_column('B:B', 45)
                worksheet_object3 = writer.sheets['Deeper #107 - Alexa websites']
                worksheet_object3.set_column('A:G', 45)
                worksheet_object4 = writer.sheets['#106 - Critical Websites']
                worksheet_object4.set_column('B:B', 40)
                worksheet_object5 = writer.sheets['Messaging Server']
                worksheet_object5.set_column('B:C', 60)

                writer.save()

            base = [self.page2, self.page3, self.page4, self.page0]
            pandas_excel(base)

        except:
            print('Something went wrong...', sys.exc_info())


if __name__ == '__main__':
    instance = Soup()
    Soup.func(instance)

