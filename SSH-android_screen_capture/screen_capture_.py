import datetime
import os
import threading
import multiprocessing
from multiprocessing import Process, freeze_support
from tkinter import ttk
import tkinter.messagebox
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import time
from tkinter import *
import paramiko
import tkinter.messagebox
from queue import Queue
import subprocess
import copy
import xlwt
import xlrd
import re
import sys

"""
    =====================================================================

    Android debug bridge - port tuned to remote PC while RDP is forbidden

    Screen from selected machine, from android device will be handed over 
    on separated multiprocess

    Version for Linux Recipient

    ---------------------------------------------------------------------
    - To compile use python +3,9 (query limitation and multiprocess events limitation)
    - to compile use pyinstaller

"""


class PlaceholderEntry(ttk.Entry):
    """ Overwrite ttk.Entry class to entry inserts """

    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, style="Placeholder.TEntry", **kwargs)
        self.placeholder = placeholder

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self["style"] == "Placeholder.TEntry":
            self.delete("0", "end")
            self["style"] = "TEntry"

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = "Placeholder.TEntry"


class Decrypt:
    """ Password descriptor """

    def __init__(self):
        key = b"Zajkowski"
        salt = b"SALT"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        _key = base64.urlsafe_b64encode(kdf.derive(key))
        self.f = Fernet(_key)
        # print(_key)

    def encrypted_function(self, obj):
        message = obj.encode()
        # print("message", message)
        encrypted = self.f.encrypt(message)
        encrypted = encrypted.decode("utf-8")
        # print("encrypted", encrypted)
        return encrypted

    def decrypted(self, obj):
        obj = obj.encode()
        decrypted = self.f.decrypt(obj)
        # print("decrypted", decrypted)
        decrypted = decrypted.decode("utf-8")
        return decrypted

    def list_command(self, dictionary):
        temp_dic = {}
        temp_dic.update(dictionary)

        for i, j in temp_dic.items():
            x = j["Password"]
            decrypted = self.decrypted(x)
            temp_dic[i]["Password"] = decrypted
            # print("temp_dic", temp_dic)

        return temp_dic


class ApplicationConfig(tk.Tk):
    # json_decrypted = {}

    def __init__(self, queue=None, plink_dir=None, scrcpy=None, adb_dir=None, getlog=None, adb_dirs=None):
        self.json_decrypted = {}
        self.encrypted = {}
        self.decode = Decrypt()
        self.adb_dirs = adb_dirs

        try:

            with open("passwords.json", "r") as json_file:
                obj = json.load(json_file)

            self.encrypted.update(obj)

        except FileNotFoundError:
            with open("passwords.json", "w") as json_file:
                json_file.write(json.dumps(self.encrypted, indent=4))

        dict_copy = copy.deepcopy(self.encrypted)
        decrypted_dic = self.decode.list_command(dict_copy)
        self.json_decrypted.update(decrypted_dic)

        self.queue = queue
        self.plink_dir = plink_dir
        self.scrcpy = scrcpy
        self.adb_dir = adb_dir
        self.getlog = getlog
        self.flag_tunnelling = False

        self.root = tk.Tk()
        self.root.title(" SSH connection ")
        self.root.geometry("600x365")

        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        adb_versions = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ADB VERSION...", menu=adb_versions)

        global_adb = list(self.adb_dirs.values())
        print(global_adb)
        text1 = global_adb[0]
        text2 = global_adb[1]
        text3 = global_adb[2]

        # adb v1.0.41 v. 30.0.4-6686687
        adb_versions.add_cascade(label=text1, command=lambda: self.select_adb(value=text1))
        # adb 'v1.0.40 v. 4797878
        adb_versions.add_cascade(label=text2, command=lambda: self.select_adb(value=text2))
        # adb v1.0.39 v. 32ac824b4b59
        adb_versions.add_cascade(label=text3, command=lambda: self.select_adb(value=text3))

        # create tab
        tab_control = ttk.Notebook(self.root)

        self.tab1 = ttk.Frame(tab_control)
        self.tab2 = ttk.Frame(tab_control)
        self.tab3 = ttk.Frame(tab_control)
        self.tab4 = ttk.Frame(tab_control)

        tab_control.add(self.tab1, text=' Configuration ')
        tab_control.add(self.tab2, text=' Start session ')
        tab_control.add(self.tab3, text=' Other tools ')
        tab_control.add(self.tab4, text=' ScreenRecord/LogsCapture ')
        # tab_control.add(self.tab3, text='    Console    ')
        tab_control.pack(padx=5, pady=5, expand=1, fill="both")

        # Tab1(self.tab1) ------------------------------------------------------------
        ip_number = ttk.Label(self.tab1, text="IP address: ", font=("Times New Roman", 15))
        ip_number.grid(row=0, column=0, padx=10, pady=10)

        self.firstEntry = PlaceholderEntry(self.tab1, "IP adress 10.123....", width=45)
        self.firstEntry.grid(row=0, column=1, padx=10, pady=10, sticky="W")

        username = ttk.Label(self.tab1, text="Username: ", font=("Times New Roman", 15))
        username.grid(row=1, column=0, padx=10, pady=10)

        self.secondEatery = PlaceholderEntry(self.tab1, "username", width=45)
        self.secondEatery.grid(row=1, column=1, padx=10, pady=10, sticky="W")

        password = ttk.Label(self.tab1, text="Password: ", font=("Times New Roman", 15))
        password.grid(row=2, column=0, padx=10, pady=10)

        self.thirdEatery = PlaceholderEntry(self.tab1, "1234", show='*', width=45)
        self.thirdEatery.grid(row=2, column=1, padx=10, pady=10, sticky="W")

        port = ttk.Label(self.tab1, text="Port: ", font=("Times New Roman", 15))
        port.grid(row=3, column=0, padx=10, pady=10)

        self.fourthEatery = PlaceholderEntry(self.tab1, "22", width=5)
        self.fourthEatery.grid(row=3, column=1, padx=10, pady=10, sticky="W")

        adb = ttk.Label(self.tab1, text="Direction to\nandroid debug bridge\nwithout 'cd': ")
        adb.grid(row=4, column=0, padx=10, pady=10)

        self.scroll = ScrolledText(self.tab1, width=35, height=5, relief="raised", wrap=tk.WORD)
        self.scroll.grid(row=4, column=1, padx=10, pady=10)
        self.scroll.insert(tk.INSERT, """dir to adb""")

        base = ttk.Button(self.tab1, text=' Add to base ', command=self.show_entry_fields, width=15)
        base.grid(row=3, column=2, padx=10, pady=10)

        # Tab2(self.tab2) ------------------------------------------------------------
        self.item = None
        self.item_text = None
        self.item_sn_selected = dict()

        # Using treeview widget
        self.treev = ttk.Treeview(self.tab2, selectmode='browse')

        # Calling pack method w.r.to treeview
        self.treev.pack(side='left')

        # Constructing vertical scrollbar
        # with treeview
        verscrlbar = ttk.Scrollbar(self.tab2,
                                   orient="vertical",
                                   command=self.treev.yview)

        # Calling pack method w.r.to verical
        # scrollbar
        verscrlbar.pack(side='right', fill='y')

        # Configuring treeview
        self.treev.configure(yscrollcommand=verscrlbar.set, height=50)

        # Defining number of columns
        self.treev["columns"] = ("1", "2", "3")

        # Defining heading
        self.treev['show'] = 'headings'

        # Assigning the width and anchor to  the
        # respective columns
        self.treev.column("1", width=100, anchor='c')
        self.treev.column("2", width=120, anchor='c')
        # self.treev.column("2", width=100, anchor='c')
        # self.treev.column("2", width=100, anchor='se')
        self.treev.column("3", width=346, anchor='w')

        # Assigning the heading names to the
        # respective columns
        self.treev.heading("1", text="IP address")
        self.treev.heading("2", text=" Username ")
        self.treev.heading("3", text="ADB Direction ")

        # Inserting the items and their features to the
        # columns built
        for i, j in self.json_decrypted.items():
            self.treev.insert("", 'end', text=i,
                              values=(i, j["Username"], j["Direction"]))

        self.treev.pack(side='left', anchor='n')
        # select from tree (2nd tab)
        self.treev.bind("<<TreeviewSelect>>", self.ClickOnTree)
        # double click - button 1
        self.treev.bind('<Double-Button-1>', self.double_click)

        start = ttk.Button(self.tab2, text='START', command=self.Messagebox, width=20)
        start.place(relx=0.75, rely=0.9, anchor=tkinter.CENTER)

        delete_button = ttk.Button(self.tab2, text='Delete', command=self.delete_treev, width=20)
        delete_button.place(relx=0.25, rely=0.9, anchor=tkinter.CENTER)

        # Tab3(self.tab3) ------------------------------------------------------------
        ttk.Label(self.tab3,
                  text="To execute function, first select IP address in 'Start session' tab...").place(
            relx=0.62, rely=0.1, anchor=tkinter.CENTER)

        get_excel = ttk.Button(self.tab3, text='Get Dives Excel', command=self.GetExcelInfo, width=20)
        get_excel.place(relx=0.75, rely=0.9, anchor=tkinter.CENTER)

        get_bat = ttk.Button(self.tab3, text='Create getlog.bat to edit', command=self.CreateGetBat, width=25)
        get_bat.place(relx=0.45, rely=0.9, anchor=tkinter.CENTER)

        self.message = "Select IP address..."
        self.label_text = StringVar()
        self.label_text.set(self.message)
        self.label = Label(self.tab3, textvariable=self.label_text)
        self.label.place(relx=0.62, rely=0.2, anchor=tkinter.CENTER)

        # # Using treeview widget
        self.treev_tab3 = ttk.Treeview(self.tab3, selectmode='browse')

        # Calling pack method w.r.to treeview
        self.treev_tab3.pack(side='left')

        # Constructing vertical scrollbar
        # with treeview
        verscrlbar_tab3 = ttk.Scrollbar(self.tab3,
                                        orient="vertical",
                                        command=self.treev_tab3.yview)

        # Calling pack method w.r.to verical
        # scrollbar
        verscrlbar_tab3.pack(side='left', fill='y')
        # verscrlbar_tab3.pack(side='right', fill='y')

        # Configuring treeview yscrollcommand = scrollbar.set
        self.treev_tab3.configure(yscrollcommand=verscrlbar_tab3.set, height=50)

        # Defining number of columns
        self.treev_tab3["columns"] = ("1",)

        # Defining heading
        self.treev_tab3['show'] = 'headings'

        # Assigning the width and anchor to  the
        # respective columns
        self.treev_tab3.column("1", width=100, anchor='c')

        # Assigning the heading names to the
        # respective columns
        self.treev_tab3.heading("1", text="IP address")

        # Inserting the items and their features to the
        # columns built
        for i, j in self.json_decrypted.items():
            # print(i, j)
            self.treev_tab3.insert("", 'end', text=i,
                                   values=(i,))

        self.treev_tab3.pack(side='left', anchor='n')
        # self.treev.bind('<Button-1>', self.selectItem)
        # select from tree (2nd tab)
        self.treev_tab3.bind("<<TreeviewSelect>>", self.ClickOnTree3)
        # double click - button 1
        self.treev_tab3.bind('<Double-Button-1>', self.double_click3)

        # Tab4(self.tab4) ------------------------------------------------------------
        start_record = ttk.Button(self.tab4, text='Start recording selected device...',
                                  command=lambda: self.GetUpdateTreeTab4_2_Start_Process_Recording(
                                      ScreenRecord=True, LogsCapture=False), width=32)
        start_record.place(relx=0.8, rely=0.9, anchor=tkinter.CENTER)

        get_log = ttk.Button(self.tab4, text='Get logs form selected device...',
                             command=lambda: self.GetUpdateTreeTab4_2_Start_Process_Recording(
                                 ScreenRecord=False, LogsCapture=True), width=32)
        get_log.place(relx=0.42, rely=0.9, anchor=tkinter.CENTER)

        # # Using treeview widget
        self.treev_tab4 = ttk.Treeview(self.tab4, selectmode='browse')
        # height - set 2nd tree viewer here
        self.treev_tab4_2 = ttk.Treeview(self.tab4, selectmode='browse', height=12)

        # Calling pack method w.r.to treeview
        self.treev_tab4.pack(side='left')
        # self.treev_tab4_2.pack(side='left')

        # Constructing vertical scrollbar
        # with treeview
        verscrlbar_tab4 = ttk.Scrollbar(self.tab4,
                                        orient="vertical",
                                        command=self.treev_tab4.yview)

        # Calling pack method w.r.to verical
        # scrollbar
        verscrlbar_tab4.pack(side='left', fill='y')

        self.treev_tab4_2.pack(side='left')

        # Configuring treeview yscrollcommand = scrollbar.set
        self.treev_tab4.configure(yscrollcommand=verscrlbar_tab4.set, height=50)

        # Defining number of columns
        self.treev_tab4["columns"] = ("1",)
        self.treev_tab4_2["columns"] = ("1", "2", "3")

        # Defining heading
        self.treev_tab4['show'] = 'headings'
        self.treev_tab4_2['show'] = 'headings'

        # Assigning the width and anchor to  the
        # respective columns
        self.treev_tab4.column("1", width=100, anchor='c')
        self.treev_tab4_2.column("1", width=120, anchor='c')
        self.treev_tab4_2.column("2", width=120, anchor='w')
        self.treev_tab4_2.column("3", width=224, anchor='w')

        # Assigning the heading names to the
        # respective columns
        self.treev_tab4.heading("1", text="Double click")
        self.treev_tab4_2.heading("1", text="Serial Number")
        self.treev_tab4_2.heading("2", text="Model")
        self.treev_tab4_2.heading("3", text="Version")

        # Inserting the items and their features to the
        # columns built
        for i, j in self.json_decrypted.items():
            # print(i, j)
            self.treev_tab4.insert("", 'end', text=i,
                                   values=(i,))

        self.treev_tab4.pack(side='left', anchor='n')
        self.treev_tab4_2.pack(side='left', anchor='n')
        # self.treev.bind('<Button-1>', self.selectItem)
        # select from tree (4th tab)
        self.treev_tab4.bind("<<TreeviewSelect>>", self.ClickOnTree4)
        # double click - button 1
        self.treev_tab4.bind('<Double-Button-1>', self.double_click4)
        # select from tree (4th tab)
        self.treev_tab4_2.bind("<<TreeviewSelect>>", self.ClickOnTree4_2)
        # double click - button 1
        self.treev_tab4_2.bind('<Double-Button-1>', self.double_click4_2)

        # adding icon
        icon = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAJ+klEQVR42qVXaWxU1xk9b5Y3" \
               "++aZsT0mBBuw8YYdg9kc11VpmxASkUhuiNqiqL" \
               "/SJErUH02kLpFo86NEiipRpFT5kyrJDyqiRlQlSlyIIAoCCgQHvICJMRDbeJuxZ595b5Y3PffhJUOTqmqudHXfe" \
               "/PefOee73zLlXB3NNXX13e7XC6vwWCALMuwWCz6ajQaYTKZ9HsxxLV4R0wxllZN05ZnoVDQn6mqql/n83koiqKv4j6VSsVGRkb" \
               "+xVcGpUUAu1988cX9CwsLVmHU4/HA5/PB6" \
               "/XC4XDo02q1wmaz6auYAogAJwCUSiX9j4vFom5IzGw2q680hmg0inA4jEQioT8LBALFI0eO/GliYuLIEoDHXnvttR" \
               "+Pjo5axB87nU4dBF80BYNBR2VlpYfTbzabjcKoJEn6vHfwz7lptSAAiSkAiZlOp3Xjc3Nz6vnz5282NDQUDx069I" \
               "/JycmjywAOHjzYS1pMwgBdsbz7pcFdG5uamlaHQqGqrzP+TUMA+QqA7PHjxwdaWlrw" \
               "+uuv942Pj68AeOONN3QAglK3261PwcS9Q3aFKhsamzeYLBaHBKO5xGdG7lOSNMVqKCo2Gfl7AQh3xONx4YbsqVOnhpqbm3H" \
               "gwIFyAG+++eYyA0sABBNLYyxm8WvuuuYNretXrar2mNb7ZchGIT5BNSmn+JSsqiWiybQZyoLXVsosAchkMksMKGfOnBkWAF" \
               "599dVyAG+99Vbv9evXdQbEzoULBABB95lpb8uO7i3tjoDXoNKg03z3szVuA3evm4F4lCcQ2SBRC3nMR8KRWk9pVvwqXJBMJ" \
               "nUA586du9ba2or9+/f33bp1awXAO++8owMQDAgAIgqEBj6Z9G3u3LGpSfbYoRY1BBwmZGlITF6iwSvrxkUwZnJF2IjIQWri" \
               "6RzmwtFEnTs3rioZTTAwPz+vXLhw4QuhgVdeeaUcwOHDh8tEKACcng621W9saZN9LtgtBjgsRmTJQLagwUBmhP8r+LyxQtZ" \
               "dkc0V4OM7PpsJ4YSKtFJEJBKJrnVmvkwk4uJavXz58mhbWxtefvnlcgDvv/9+79DQkA5AhOBk1h9MeZofdlVXwOeR4XfJUDU" \
               "gltNg5HaXAsHMi7ZKC+zceXHRBUEHdUQggxPMAQkFheTslyFrKkIRqoODgzfb29vx0ksv9d24cWMFwLFjx3qHh4dNwufC/x" \
               "/crtlZ39JQA7sV66psqHCaMRrNIadnP+YBQNdHQJbQU+sAF8zE8yhSjG6rEQ765eZsFjEyQTkobf7kcDwWydLNtx944AG88" \
               "MIL5QAYn70DAwM6AzOqx3ctW7d7Y9sayeO24PuNXsyTzk9vp6GQaiMpMFLd1kIRtS4zeja4MbGgIqUUdCEm+a6NOsjni1iI" \
               "K7oAvaXwaNAcnxobG5vo6OjA888/30cwKwBOnjzZS3p0AP+85dnoqF7f7vb70LzGhR9tDmAsouLiHaZXukGiES0j8rqmg6mh" \
               "EHWNkIbpmKo/N5Mlm9mAuRi/YRRkY7ORzlBqgNlvSmjgmWeeKQdw+vTpZQB/6Xf0rGtYf38g6IPTIaOjzo3ZVAEjkRzy1ICWY" \
               "d6nAsW0ywZ8r9GNrWsd+OhKDNl8QQfACgEPXRGOKcikUxTgXPqR9dlzU1NTM5s2bcLTTz9dDoDh0UuFmkQtOHDK+uiq++/zt" \
               "dVX4jstflR6LBieVjAwmaGouPOi+ERaBCDhhy0eNIasOHppgSwYoDH/MzPB7zQhElUQTyQxMz2b/0lH7iSFGBYA9u3b13f16" \
               "tUVAP39/ToDQli//sD4uGr2uqpDFXiyqwad69zwMeiPD8Xx3sUYIqkitJIEk5GKp5HWVTbea7gdVuGySHxXgt0koS4gk4Es7" \
               "sxEkU9GC892aydYcec3b96MvXv3lgOgcV2EIhP+7kM8PKU6g7LTjdY6D1YHHKirtEI2m3ByJIVYRiPVgJtZp6fBgYV0AWdvp" \
               "Bl6BoSTOawNmnC/16QzMz2fwcXrs0jOR5TnurWPWRNinZ2d6O3t7WPYrwAgGh2AcMGhT7D9cti2XrI4sLqSSchhwVxKw4YaB" \
               "8bCeagFCRVkpGWVBb96JIBPv0iTmTgCLiMUKt9nl9ASsmBflx9DE2m8feImstFw9NkHtdOMiMTWrVuxZ8+ecgAMD10DQoQfj" \
               "5pq370gdZesLoS4e6fdgmuzeVR5rZwWDE5S6ZqEdUEZ29facG1KxSS1ITFBNYfMLFIamqplPNHhxWc34jh6dhKNrtjonlZti" \
               "IUpvWXLFuzevbscACtTL3WgA8ibvJafv5t8XDE6ZR9rQMhvpwiZZFh6NoRsTERGXJlQsdpnhsdmwAhZKdE44wM1HiOe3OQAE" \
               "yEFCvTfTGBkbA6//C5OrnZmowSQ3bZtG3bt2tV35cqVFQAMj97PP/9cByDqwMGP8x0fXC21yOwF61e58MVcAZkCExCNN1DxR" \
               "mpFxH4kreHGvADH4kQBNtWY4KcLttdamBElvHd+Hr5CbOr3j5rP0v+lXC6nChfs3LmzHABL5TIDAoDR6jU/9efEI3cSBXcdU" \
               "3GqwAwZZ+0nz2aK8QctTvy0y4W/XUqjbziDHDNk22ozFpgjsqyKOxus8LJAnBuI5v/wmOFElV1JsTcssTHNLwGgvRUALJXLA" \
               "CoqKkQ/iM8Gb1b87LD1YYvNbqyiqsfCRRpiR2y6y8IvHvLiKl3z189ScNIVVlI+Gcuhkn1CyG3GHf72XOO1s0891D7OSohYL" \
               "CYYKO7YsQM9PT3lAPjjfwAQRentI301vz0R7PIE77PmVAXzGaZh0u93y2iosfCePYKb1Y+0X5nK6bRXuWyITM0UHw0M9v/mu" \
               "T2joh3jBvXumN2z1tXVBc5yAAwPHYAIQ1GO2Q2TamZ0jqPHTlT+8XimfcH5YEAtWUixyrachijC8VgBIa42ZkA1Z4RcVFERO" \
               "zu/b1txeO8Tu6a5oRI7ZY0JSDCgAxAMbN++vRwA1dl76dKlZQ34/X7RCRuI3jQ7OyszTzg/PD1U07+wtmbOvNGVM1UYHXY7M" \
               "mwSzFIeueS8FsgPpLYGbt15rKdxin1fqqqqKk8W82zXS8L/iwyUuru7QR30Xbx48ZsBCAbYmkn8QBIgZmZmZApVZrjaxm6PO" \
               "yfnsvaUCrnEmmCXS/lqnyXbsPa+ZG1tbaa6ujrHc0SOTBZ40CnxcFISBxMBQJwT/mcAwhWLna3EDyXuRGKLbaCQDWIV4MTvd" \
               "FuJhjQypvH0JNaSoJ7eE13bUkv+XwHsFhpgJpTvBSA08W2GOLLdC4CJSGNT8hE7sL8vAWiiMDrpLwuLkdiZmS86uVq5e8O3A" \
               "cANsYWBQkGnuJm8ECHFqPCINsDnA189Y4lzmBl3O2w7p2fxmUEv/v/fEC4QANLCE5yZxfvc4vXX/rEwKHi3Lq7fioFFg+K8r" \
               "iyu2ld//DfrbnmAyt9PggAAAABJRU5ErkJggg== "

        img = base64.b64decode(icon)
        img = PhotoImage(data=img)

        self.root.wm_iconphoto(True, img)
        self.root.mainloop()

        super(tk.Tk, self).__init__()

    @property
    def Adb_dir(self):
        return self.__adb_dir

    @Adb_dir.setter
    def Adb_dir(self, value):
        self.__adb_dir = value

    def select_adb(self, value):
        for android_debug_dir, text in self.adb_dirs.items():
            if text == value:
                subprocess.call(f"{android_debug_dir} kill-server", creationflags=subprocess.CREATE_NO_WINDOW)
                tk.messagebox.showinfo("ADB VERSION", "You selected android debug bridge in \n" + text +
                                       " in global tool.")
                self.adb_dir = android_debug_dir

                split_path = os.path.split(android_debug_dir)
                newPathOfScrypy = os.path.join(split_path[0], "scrcpy-noconsole.exe")
                newPathOfPlink = os.path.join(split_path[0], "plink.exe")
                # print("\n\tnewPathOfScrypy: ", newPathOfScrypy)
                # print("\n\tnewPathOfPlink: ", newPathOfPlink)
                # print("\n\tandroid_debug_dir: ", android_debug_dir)
                self.scrcpy = newPathOfScrypy
                self.plink_dir = newPathOfPlink

    def show_entry_fields(self):
        IP = self.firstEntry.get(),
        Username = self.secondEatery.get(),
        Password = self.thirdEatery.get(),
        Port = self.fourthEatery.get(),
        Direction = self.scroll.get('1.0', tk.END)

        self.json_decrypted[IP[0]] = {'Username': Username[0],
                                      'Password': Password[0],
                                      'Port': Port[0],
                                      'Direction': Direction.strip()}

        # print("\n\n\n\nPassword from console", Password[0])
        # print("1. json_decrypted: ", self.json_decrypted)
        password_decode = self.decode.encrypted_function(Password[0])
        # print("4. password_decode: ", password_decode)

        self.encrypted[IP[0]] = {'Username': Username[0],
                                 'Password': password_decode,
                                 'Port': Port[0],
                                 'Direction': Direction.strip()}

        # print("\nencrypted: ", self.json_decrypted)
        # print("json_decrypted: ", self.encrypted)

        self.treev.insert("", 'end', text=IP[0],
                          values=(IP[0], Username[0], Direction.strip()))

        self.treev_tab3.insert("", 'end', text=IP[0],
                               values=(IP[0],))

        with open("passwords.json", "w") as json_file:
            json_file.write(json.dumps(self.encrypted, indent=4))

    def delete_treev(self):
        """ Delete element from tree"""
        MsgBox = tk.messagebox.askquestion('Deleting...', 'Do you want to delete selected row?', icon="question")
        if MsgBox == 'yes':
            try:
                self.treev.delete(self.item)
                self.treev_tab3.delete(self.item)

                del self.json_decrypted[self.item_text]
                del self.encrypted[self.item_text]

                with open("passwords.json", "w") as json_file:
                    json_file.write(json.dumps(self.encrypted, indent=4))

            except Exception:
                tk.messagebox.showinfo('Warning...', 'Select new row')
        else:
            tk.messagebox.showinfo('Info...', 'Row not deleted')

    def ClickOnTree(self, event):
        """ Select element on 2nd tab (form list) """
        try:
            for item in self.treev.selection():
                item_text = self.treev.item(item, "text")

            print("Selected value: ", item_text)
        except ValueError:
            tk.messagebox.showinfo('Warning...', 'Wrong value')

        finally:
            self.item_text = item_text
            return self.item_text

    def ClickOnTree3(self, event):
        """ Select element on 3rd tab (form list) """
        try:
            for item in self.treev_tab3.selection():
                item_text = self.treev_tab3.item(item, "text")

            print("Selected value: ", item_text)
        except ValueError:
            tk.messagebox.showinfo('Warning...', 'Wrong value')

        finally:

            self.item_text = item_text
            self.message = "Selected address: " + item_text
            self.label_text.set(self.message)
            return self.label_text, self.item_text

    def ClickOnTree4(self, event):
        """ Select element on 4th tab (form list) """
        try:
            for item in self.treev_tab4.selection():
                item_text = self.treev_tab4.item(item, "text")

            print("Selected value: ", item_text)
        except ValueError:
            tk.messagebox.showinfo('Warning...', 'Wrong value')

        finally:
            self.item_text = item_text
            return self.item_text

    def ClickOnTree4_2(self, event):
        """ Select element on 4th tab (form list) """
        try:
            for item in self.treev_tab4_2.selection():
                item_values = self.treev_tab4_2.item(item, "values")
                item_text = self.treev_tab4_2.item(item, "text")

            # print("Selected text: ", item_text)
            # print("Selected value: ", item_values)

            item_sn_selected = dict()
            temp = {"serial_number": [item_values[0]], "IP": item_text}
            item_sn_selected.update(temp)

        except ValueError:
            tk.messagebox.showinfo('Warning...', 'Wrong value')

        finally:
            self.item_sn_selected = item_sn_selected
            return self.item_sn_selected

    def double_click(self, event):
        """ Set the double click status flag - in this case start process = START button"""
        self.Messagebox()

    # event double click for second event
    def double_click3(self, event):
        """ Set the double click status flag - in this case in 3rd tab"""
        self.GetExcelInfo()

    def double_click4(self, event):
        """ Set the double click status flag - in this case 4th tab"""
        self.flag_tunnelling = False
        self.GetUpdateTreeTab4()

    def double_click4_2(self, event):
        """ Set the double click status flag - in this case 4th tab"""
        self.GetUpdateTreeTab4_2_Start_Process_Recording()

    def Messagebox(self):
        """ Start process = START button """
        # add here trigger to close this program and open new process

        MsgBox = tk.messagebox.askquestion('Starting threading...', 'Do you want to connect ?', icon="question")
        if MsgBox == 'yes':
            # print("New window !")

            ip, user, password, port, direction = self.item_text, \
                                                  self.json_decrypted[self.item_text]["Username"], \
                                                  self.json_decrypted[self.item_text]["Password"], \
                                                  self.json_decrypted[self.item_text]["Port"], \
                                                  self.json_decrypted[self.item_text]["Direction"]

            ssh_connection = ShellHandler2(ip, user, password, port, direction)
            serial_number = set(ssh_connection.sn)
            if len(serial_number) == 0:
                del ssh_connection
                print("On this xBox there is no samples viable on adb... ")
                tk.messagebox.showinfo('Info!', 'On this xBox there is no any sample viable on adb...')

            else:
                """ Starting progress bar """
                p = Process(target=progress_bar, args=(25000,))
                p.start()

                temp = {"serial_number": serial_number, "IP": self.item_text,
                        "ScreenRecord": False, "LogsCapture": False}

                self.json_decrypted[self.item_text].update(temp)
                self.queue.put(self.json_decrypted[self.item_text])

                self.root.destroy()
                del ssh_connection

        else:
            tk.messagebox.showinfo('Welcome Back', 'Welcome back to the App')

    def GetUpdateTreeTab4(self):
        """ GetExcelInfo button """
        # add here trigger to close this program and open new process
        # cleaning all data from treev in tab 4 -2nd
        self.treev_tab4_2.delete(*self.treev_tab4_2.get_children())

        try:
            ip, user, password, port, direction = self.item_text, \
                                                  self.json_decrypted[self.item_text]["Username"], \
                                                  self.json_decrypted[self.item_text]["Password"], \
                                                  self.json_decrypted[self.item_text]["Port"], \
                                                  self.json_decrypted[self.item_text]["Direction"]

            ssh_connection = ShellHandler2(ip, user, password, port, direction)
            serial_number = set(ssh_connection.sn)
            if len(serial_number) == 0:
                del ssh_connection
                print("On this xBox there is no samples viable on adb... ")
                tk.messagebox.showinfo('Info!', 'On this xBox there is no any sample viable on adb...')

            else:

                ssh_connection.read_devices(self.treev_tab4_2)

        except KeyError:
            tk.messagebox.showinfo('Warning...', 'No selected IP in "Start session" tab')

    def GetUpdateTreeTab4_2_Start_Process_Recording(self, ScreenRecord=False, LogsCapture=False):
        """ GetExcelInfo button """
        # add here trigger to close this program and open new process

        try:

            if len(self.item_sn_selected) == 0:
                print("On this xBox there is no samples viable on adb... ")
                tk.messagebox.showinfo('Info!', 'On this xBox there is no any sample viable on adb...')

            else:

                """ Starting progress bar """
                p = Process(target=progress_bar, args=(25000,))
                p.start()

                logs_var = {"ScreenRecord": ScreenRecord, "LogsCapture": LogsCapture}
                self.item_sn_selected.update(logs_var)
                temp = self.item_sn_selected

                print(self.json_decrypted[self.item_text])
                self.json_decrypted[self.item_text].update(temp)
                print(self.json_decrypted[self.item_text])

                ip, user, password, port, direction, serial_number, ScreenRecord, LogsCapture = \
                self.json_decrypted[self.item_text]["IP"], \
                self.json_decrypted[self.item_text]["Username"], \
                self.json_decrypted[self.item_text]["Password"], \
                self.json_decrypted[self.item_text]["Port"], \
                self.json_decrypted[self.item_text]["Direction"], \
                self.json_decrypted[self.item_text]["serial_number"], \
                self.json_decrypted[self.item_text]["ScreenRecord"], \
                self.json_decrypted[self.item_text]["LogsCapture"]

                print("\n\n\tADB dicrection: ", {self.adb_dir})
                command = f'{self.plink_dir} -ssh -N -C -L 5037:localhost:5037 -R 27183:localhost:27183 {user}@{ip} -pw {password}'
                proc_start = ServerStart()

                print(" \nConfigure port connection in ssh protocol... ")
                if self.flag_tunnelling == False:
                    start_server = Process(target=proc_start.start, args=(command,))
                    start_server.start()
                    self.flag_tunnelling = True

                time.sleep(1)
                # event = multiprocessing.Event()
                print("Checking adb verion: ", self.adb_dir)

                process_start_ssh_mirror = StartConnectionWithSample()

                if ScreenRecord == True:
                    start_scrcpy = Process(target=process_start_ssh_mirror.start_ssh_mirror_recording,
                                           args=(serial_number, self.scrcpy))

                elif LogsCapture == True:
                    start_scrcpy = Process(target=process_start_ssh_mirror.get_log,
                                           args=(serial_number, self.adb_dir, self.getlog))

                else:
                    start_scrcpy = Process(target=process_start_ssh_mirror.start_ssh_mirror,
                                           args=(serial_number, self.scrcpy))

                start_scrcpy.start()

        except KeyError:
            tk.messagebox.showinfo('Warning...', 'No selected IP in "Start session" tab')

    def CreateGetBat(self):
        with open(self.getlog, "r") as f:
            variables = f.readlines()

        with open("getlog.bat", "w") as f:
            f.writelines(variables)

    def GetExcelInfo(self):
        """ GetExcelInfo button """
        # add here trigger to close this program and open new process
        try:
            ip, user, password, port, direction = self.item_text, \
                                                  self.json_decrypted[self.item_text]["Username"], \
                                                  self.json_decrypted[self.item_text]["Password"], \
                                                  self.json_decrypted[self.item_text]["Port"], \
                                                  self.json_decrypted[self.item_text]["Direction"]

            MsgBox = tk.messagebox.askquestion('Getting an excel... ', f'Do you want get information from {ip}?',
                                               icon="question")
            if MsgBox == 'yes':

                self.message = "Please wait... Creating excel..."
                self.label_text.set(self.message)

                ssh_connection = ShellHandler2(ip, user, password, port, direction)
                dict__ = ssh_connection.read_devices()

                if os.path.exists('OutputSampleList.xls'):

                    workbook = xlrd.open_workbook('OutputSampleList.xls')
                    sheet = workbook.sheet_by_index(0)

                    out_dictionary = {}
                    for i in range(1, sheet.nrows):
                        data = [sheet.cell_value(i, col) for col in range(sheet.ncols)]

                        _, sn, model, marketing, product, version, imei1, imei2, \
                        date, board_platform_model, board_chiptyp_name, xbox = data

                        out_dictionary.setdefault(sn, (model, marketing, product, version, [imei1, imei2], date,
                                                       board_platform_model, board_chiptyp_name, xbox))

                    dict__.update(out_dictionary)

                    workbook = xlwt.Workbook()
                    sheet = workbook.add_sheet('SampleList')

                    sheet.write(0, 0, 'LP')
                    sheet.write(0, 1, 'Serial Number')
                    sheet.write(0, 2, 'Manufacture')
                    sheet.write(0, 3, 'Marketing Info')
                    sheet.write(0, 4, 'Product Info')
                    sheet.write(0, 5, 'Software version')
                    sheet.write(0, 6, 'IMEI 1')
                    sheet.write(0, 7, 'IMEI 2')
                    sheet.write(0, 8, 'Date dd/mm/yy')
                    sheet.write(0, 9, 'Board Platform')
                    sheet.write(0, 10, 'Board Chiptyp')
                    sheet.write(0, 11, 'IP Address')

                    sheet.col(0).width = 6 * 256
                    sheet.col(1).width = 20 * 256
                    sheet.col(2).width = 14 * 256
                    sheet.col(3).width = 20 * 256
                    sheet.col(4).width = 13 * 256
                    sheet.col(5).width = 40 * 256
                    sheet.col(6).width = 20 * 256
                    sheet.col(7).width = 20 * 256
                    sheet.col(8).width = 14 * 256
                    sheet.col(9).width = 13 * 256
                    sheet.col(10).width = 13 * 256
                    sheet.col(11).width = 20 * 256

                    index = 0
                    for i, key, value in zip(range(1, int(len(dict__) + 1)), dict__.keys(), dict__.values()):
                        model, marketing, product, version, imei, date, board_platform_model, board_chiptyp_name, xbox \
                            = value

                        sheet.write(i, index, str(i))
                        sheet.write(i, index + 1, key)
                        sheet.write(i, index + 2, model)
                        sheet.write(i, index + 3, marketing)
                        sheet.write(i, index + 4, product)
                        sheet.write(i, index + 5, version)
                        sheet.write(i, index + 6, imei[0])
                        sheet.write(i, index + 7, imei[1])
                        sheet.write(i, index + 8, date)
                        sheet.write(i, index + 9, board_platform_model)
                        sheet.write(i, index + 10, board_chiptyp_name)
                        sheet.write(i, index + 11, xbox)

                else:

                    workbook = xlwt.Workbook()
                    sheet = workbook.add_sheet('SampleList')

                    sheet.write(0, 0, 'LP')
                    sheet.write(0, 1, 'Serial Number')
                    sheet.write(0, 2, 'Manufacture')
                    sheet.write(0, 3, 'Marketing Info')
                    sheet.write(0, 4, 'Product Info')
                    sheet.write(0, 5, 'Software version')
                    sheet.write(0, 6, 'IMEI 1')
                    sheet.write(0, 7, 'IMEI 2')
                    sheet.write(0, 8, 'Date dd/mm/yy')
                    sheet.write(0, 9, 'Board Platform')
                    sheet.write(0, 10, 'Board Chiptyp')
                    sheet.write(0, 11, 'IP Address')

                    sheet.col(0).width = 6 * 256
                    sheet.col(1).width = 20 * 256
                    sheet.col(2).width = 14 * 256
                    sheet.col(3).width = 20 * 256
                    sheet.col(4).width = 13 * 256
                    sheet.col(5).width = 40 * 256
                    sheet.col(6).width = 20 * 256
                    sheet.col(7).width = 20 * 256
                    sheet.col(8).width = 14 * 256
                    sheet.col(9).width = 13 * 256
                    sheet.col(10).width = 13 * 256
                    sheet.col(11).width = 20 * 256

                    index = 0
                    for i, key, value in zip(range(1, int(len(dict__) + 1)), dict__.keys(), dict__.values()):
                        # print(i, key, value)

                        model, marketing, product, version, imei, date, board_platform_model, board_chiptyp_name, xbox \
                            = value

                        sheet.write(i, index, str(i))
                        sheet.write(i, index + 1, key)
                        sheet.write(i, index + 2, model)
                        sheet.write(i, index + 3, marketing)
                        sheet.write(i, index + 4, product)
                        sheet.write(i, index + 5, version)
                        sheet.write(i, index + 6, imei[0])
                        sheet.write(i, index + 7, imei[1])
                        sheet.write(i, index + 8, date)
                        sheet.write(i, index + 9, board_platform_model)
                        sheet.write(i, index + 10, board_chiptyp_name)
                        sheet.write(i, index + 11, xbox)

                workbook.save('OutputSampleList.xls')
                print("\nProcess ended. Excel created...")

                del ssh_connection

                self.message = "Excel created!"
                self.label_text.set(self.message)

                # p.terminate()

            else:
                tk.messagebox.showinfo('Welcome Back', 'Welcome back to the App')

        except KeyError:
            tk.messagebox.showinfo('Warning...', 'No selected IP in "Start session" tab')


def progress_bar(interval):
    my_pb = ProgressbarApp(interval)

    for i in range(interval):
        my_pb.update(i)

    my_pb.close()


class ShellHandler2:
    """ Paramiko - connecting with the host & reading the output """

    def __init__(self, host, user, psw, port, direction=None):
        self.host = host

        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(host, username=user, password=psw, port=port, look_for_keys=False, allow_agent=False)

        except OSError:
            print("there is no connection")
            time.sleep(20)

        self.direction = direction
        self.dictionary_devices = {}
        self.sn = []

        self.execute2()

    def __del__(self):
        self.ssh.close()

    def execute2(self, cmd="./adb devices", sn=None, mp_guere=None):
        """ Reading the devices form connected ssh machine """

        # Check if connection is made previously.
        if (self.ssh):

            stdin, stdout, stderr = self.ssh.exec_command(
                "cd {} && {}".format(self.direction, cmd))
            stdin.flush()

            while not stdout.channel.exit_status_ready():

                if "./adb devices" in cmd:

                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"

                    while prevdata:
                        # Retrieve the next 1024 bytes.
                        prevdata = stdout.channel.recv(1024)
                        # print("Prevdata: ", prevdata)
                        alldata += prevdata

                    d_list = alldata.decode("utf-8").split("\n")
                    # print("\n\t\td_list", d_list)
                    for line in d_list:
                        print("\t", line)
                        if "device" in line and "List" not in line:
                            self.dictionary_devices.setdefault(line.split("\t")[0], {})
                            self.sn.append(line.split("\t")[0])

        else:
            print("Connection not opened.")

    def read_devices(self, tree_list=None):
        temple_dic = {}
        time_now = self.timeFormat()

        if tree_list != None:
            print("\n\n\tTree...")

            for serial_number in self.sn:
                print("Serial_number: ", serial_number)

                marketing_info = ""
                sv_info = ""

                command = {
                    'marketing_info': f'cd {self.direction} && ./adb -s {serial_number} '
                                      f'shell getprop ro.config.marketing_name',
                    'sv_info': f'cd {self.direction} && ./adb -s {serial_number} '
                               f'shell getprop ro.product.model',
                }

                for key, value in command.items():
                    stdin, stdout, stderr = self.ssh.exec_command(value)

                    stdout = stdout.readlines()
                    # print("stdout all paramiko: ", stdout)

                    for line in stdout:
                        if line != "":
                            print("Line: ", line.strip())
                            line = line.strip()

                            if key == "manufacture_info":
                                pass
                            elif key == "marketing_info":
                                marketing_info = line
                            elif key == "product_model_info":
                                pass
                            elif key == "sv_info":
                                sv_info = line
                            elif key == "serial_nr_info":
                                pass
                            elif key == "board_platform_model":
                                pass
                            elif key == "board_chiptyp_name":
                                pass

                        else:
                            # print("blink line: ", line)
                            pass

                tree_list.insert("", 'end', text=self.host,
                                 values=(serial_number, marketing_info, sv_info))

        else:
            print("\n\n\tNo tree here... ")
            for serial_number in self.sn:
                print("Serial_number: ", serial_number)

                manufacture_info = ""
                marketing_info = ""
                product_model_info = ""
                sv_info = ""
                serial_nr_info = ""
                board_platform_model = ""
                board_chiptyp_name = ""

                command = {
                    'manufacture_info': f'cd {self.direction} && ./adb -s {serial_number} '
                                        f'shell getprop ro.product.manufacturer',
                    'marketing_info': f'cd {self.direction} && ./adb -s {serial_number} '
                                      f'shell getprop ro.config.marketing_name',
                    'product_model_info': f'cd {self.direction} && ./adb -s {serial_number} '
                                          f'shell getprop ro.product.model',
                    'sv_info': f'cd {self.direction} && ./adb -s {serial_number} '
                               f'shell getprop ro.hw.oemName',
                    'serial_nr_info': f'cd {self.direction} && ./adb -s {serial_number} '
                                      f'shell getprop ro.boot.serialno',
                    'board_platform_model': f'cd {self.direction} && ./adb -s {serial_number} '
                                            f'shell getprop ro.board.platform',
                    'board_chiptyp_name': f'cd {self.direction} && ./adb -s {serial_number} '
                                          f'shell getprop ro.board.chiptype',
                }

                for key, value in command.items():
                    stdin, stdout, stderr = self.ssh.exec_command(value)

                    stdout = stdout.readlines()
                    # print("stdout all paramiko: ", stdout)

                    for line in stdout:
                        if line != "":
                            print("Line: ", line.strip())
                            line = line.strip()

                            if key == "manufacture_info":
                                manufacture_info = line
                            elif key == "marketing_info":
                                marketing_info = line
                            elif key == "product_model_info":
                                product_model_info = line
                            elif key == "sv_info":
                                sv_info = line
                            elif key == "serial_nr_info":
                                serial_nr_info = line
                            elif key == "board_platform_model":
                                board_platform_model = line
                            elif key == "board_chiptyp_name":
                                board_chiptyp_name = line

                        else:
                            # print("blink line: ", line)
                            pass

                imei_list = []
                for i in range(0, 2):
                    if i == 2:
                        imei = f'cd {self.direction} && ./adb -s {serial_number} shell service call iphonesubinfo {i}'
                    else:
                        imei = f'cd {self.direction} && ./adb -s {serial_number} shell service call iphonesubinfo 3 i32 {i}'

                    stdin, stdout, stderr = self.ssh.exec_command(imei)
                    output = stdout.read()

                    output = output.decode("utf-8")
                    # print(output)

                    read = re.findall(r"(\d+)\.", output)
                    imei_ = ''.join(read)
                    print("IMEI: ", imei_)
                    imei_list.append(imei_)

                temple_dic[serial_nr_info] = (
                    manufacture_info, marketing_info, product_model_info, sv_info, imei_list, time_now,
                    board_platform_model, board_chiptyp_name, self.host)

            return temple_dic

    @staticmethod
    def timeFormat():
        return datetime.datetime.now().strftime("%d/%m/%Y")


class AndroidMirrorHandler(tk.Tk):
    """ Just Bar - no in use """

    def __init__(self):
        self.window = tk.Tk()
        frame = tk.Frame()
        frame.pack()

        start = ttk.Button(self.window, text='C', command=self.Messagebox, width=20)
        start.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.window.mainloop()
        super(tk.Tk, self).__init__()


class ServerStart(Process):
    """ After connected to server - if key does't exist it will swipe the rest... """

    def __init__(self):
        super(Process, self).__init__()

    def analyze(self, proc):
        for line in iter(proc.stdout.readline, b''):
            line = str(line.decode('utf-8', errors='ignore'))
            print(line)

            if 'If you trust this host, enter "y" to add the key to' in line:
                proc.stdin.write(b"y\n")
                proc.stdin.flush()

            elif 'Store key in cache? (y/n) Using username "pwrcbenchmark".' in line:
                proc.stdin.write(b"y\n")
                proc.stdin.flush()

    def start(self, command, event_tk_inside=None):
        """ Reading output and output error - could be not infinity loop
        if screen will disconnect use while and terminate multiprocess """

        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, )
        # creationflags=subprocess.CREATE_NO_WINDOW)

        proc.stdin.flush()

        t = threading.Thread(target=self.analyze, args=(proc,))
        t.start()

        # event createt for tkinter - no in use, maybe in future
        if event_tk_inside != None:
            while True:
                time.sleep(5)
                print("line 1555")
                if event_tk_inside.is_set():
                    print("\nTaring to kill subprocess... ")
                    proc.kill()
                    print("\nSuccess! Process closed! ")
                    event_tk_inside.clear()
                    return False

        else:
            t.join()
            print("Process joined - subprocess... ")


class ProgressbarApp(threading.Thread):
    """ Progress Bar """

    def __init__(self, max_value: int):
        self.max_value = max_value

        self.root = None
        self.pb = None

        threading.Thread.__init__(self)
        self.lock = threading.Lock()  # (1)
        self.lock.acquire()  # (2)
        self.start()

        # (1) Makes sure progressbar is fully loaded before executing anything
        with self.lock:
            return

    def close(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)

        self.pb = ttk.Progressbar(self.root, orient='horizontal', length=400, mode='determinate')
        self.pb['value'] = 0
        self.pb['maximum'] = self.max_value
        self.pb.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP)

        self.lock.release()  # (2) Will release lock when finished
        self.root.mainloop()

    def update(self, value: int):
        self.pb['value'] = value


class StartConnectionWithSample(Process):
    """ ADB mirror """

    def __init__(self):
        super(Process, self).__init__()

    def start_ssh_mirror(self, serial_number, scrcpy, event=None):
        """ Adding process of multi-stream-opening-adb-mirror on ssh connection in one process """
        nr = 1
        poll_list = []

        # serial_number = set(serial_number)
        # print(serial_number)
        for sn in serial_number:
            # time.sleep(0.5)

            print(f"\tLP {nr} - Running now ssh tunnel for: {sn}...")
            sn_command = f"{scrcpy} -s {sn} -b2M -m800 --max-fps 15 -w --window-title {sn}"

            p = subprocess.Popen(sn_command, )  # creationflags=subprocess.CREATE_NO_WINDOW)
            # # use a new console to not flood the test output
            # creationflags=subprocess.CREATE_NEW_CONSOLE,
            # # use a shell to hide the console window (SW_HIDE)
            # shell=True)

            poll_list.append(p)

            nr += 1
            time.sleep(0.5)

        while True:
            try:
                if len(poll_list) != 0:

                    for p in poll_list:
                        # check that process is alive
                        poll = p.poll()
                        if poll is None:
                            time.sleep(5)
                            # p.subprocess is alive

                        else:
                            print("\nClosed one of available windows of android monitor...")
                            poll_list.remove(p)
                            if len(poll_list) == 0:
                                print("\nProcess of mirroring devices - ended!\n"
                                      "All windows are closed!")

                                # here is set event for terminate process
                                if event == None:
                                    print("\nNon event here...")
                                    return False

                                else:
                                    print("\nEvent is set here...")
                                    event.set()
                                    return False

            except KeyboardInterrupt:
                sys.exit()
                return False

    @staticmethod
    def get_actual_time():
        return datetime.datetime.now().strftime("hh%H_mm%M_ss%S__dd%d_mm%m_yy%y")

    def get_log(self, serial_number, adb_dir=None, getlog=None):
        """ Adding process of multi-stream-opening-adb-mirror on ssh connection in one process """
        actual_dir = os.getcwd()
        join_get_log_dir = actual_dir + "\\getlog.bat"
        print(join_get_log_dir)

        nr = 1
        time_string = self.get_actual_time()

        # serial_number = set(serial_number)
        # print(serial_number)

        for sn in serial_number:
            if os.path.exists(f"reports\\{sn}"):
                print("Path not exist - report")

            else:
                actual_dir = os.getcwd()
                actual_dir = os.path.join(actual_dir, "reports", sn)
                print("actual_dir", actual_dir)
                os.makedirs(actual_dir)
                print("Path exist - report")

            # time.sleep(0.5)
            print(f"\tLP {nr} - Geting logs from: {sn}...")
            nr += 1

            if os.path.exists(join_get_log_dir):
                print("\nGetlog.bat Exist in main folder! ")
                p = subprocess.Popen(["start", "cmd", "/k",
                                      f"{join_get_log_dir} reports\\{sn}\\{time_string} {sn} {adb_dir}"],
                                     shell=True)
                p.wait()

            else:
                print("\nGetlog.bat not exist in main folder using compiled one!")
                p = subprocess.Popen(["start", "cmd", "/k", f"{getlog} reports\\{sn}\\{time_string} {sn} {adb_dir}"],
                                     shell=True)
                p.wait()

    def start_ssh_mirror_recording(self, serial_number, scrcpy, event=None):
        """ Adding process of multi-stream-opening-adb-mirror on ssh connection in one process """
        nr = 1
        poll_list = []
        time_string = self.get_actual_time()

        # serial_number = set(serial_number)
        # print(serial_number)
        for sn in serial_number:
            if os.path.exists(f"reports\\{sn}"):
                print("Path not exist - report")

            else:
                actual_dir = os.getcwd()
                actual_dir = os.path.join(actual_dir, "reports", sn)
                print("actual_dir", actual_dir)
                os.makedirs(actual_dir)
                print("Path exist - report")

            # time.sleep(0.5)
            print(f"\tLP {nr} - Running now ssh tunnel for: {sn}...")
            sn_command = f"{scrcpy} -s {sn} -b2M -m800 --max-fps 15 -w --window-title {sn}" \
                         f" --record reports\\{sn}\\{sn}_{time_string}.mp4"

            p = subprocess.Popen(sn_command, )  # creationflags=subprocess.CREATE_NO_WINDOW)
            # # use a new console to not flood the test output
            # creationflags=subprocess.CREATE_NEW_CONSOLE,
            # # use a shell to hide the console window (SW_HIDE)
            # shell=True)

            poll_list.append(p)

            nr += 1
            time.sleep(0.5)

        while True:
            # print("one")
            try:
                if len(poll_list) != 0:

                    for p in poll_list:
                        # check that process is alive
                        poll = p.poll()
                        if poll is None:
                            time.sleep(5)
                            # p.subprocess is alive

                        else:
                            print("\nClosed one of available windows of android monitor...")
                            poll_list.remove(p)
                            if len(poll_list) == 0:
                                print("\nProcess of mirroring devices - ended!\n"
                                      "All windows are closed!")
                                # here is set event for terminate process
                                if event == None:
                                    print("\nNon event here...")
                                    return False

                                else:
                                    print("\nEvent is set here...\nClosing ")
                                    event.set()
                                    return False

            except KeyboardInterrupt:
                sys.exit()


class ReadTeamFiles:
    paths = {}

    def __init__(self, func):
        self.func = func

    def __call__(self, dir):
        get_path = self.resource_path(dir)
        path = self.func(get_path)
        return path

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
            # print("Try", base_path)

        except Exception:
            base_path = os.path.abspath(".")
            # print("Exception", base_path)

        return os.path.join(base_path, relative_path)


def kill_server(adb):
    subprocess.Popen(f"{adb} kill-server", creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(2)


if __name__ == '__main__':
    print("Python version: ", sys.version)

    # scrcpy main dir - direction must be this same adb version

    adb39_32ac824b4b59_dir = "zajkowskiSSH_adb39_32ac824b4b59\\adb.exe"
    adb40_4797878_dir = "zajkowskiSSH_adb40_4797878\\adb.exe"  # 1.0.40 Version 4797878
    adb41_30_0_4_dir = "zajkowskiSSH_adb41_30_0_4\\adb.exe"
    plink_dir = "zajkowskiSSH_adb40_4797878\\plink.exe"
    scrcpy_dir = "zajkowskiSSH_adb40_4797878\\scrcpy-noconsole.exe"
    getlog_dir = "zajkowskiSSH_adb40_4797878\\getlog.bat"


    # Overwrite function to get actual path in compiled file
    @ReadTeamFiles
    def print_file(dir):
        print(f"Getting new {dir}...")
        return dir


    adb40_4797878 = print_file(adb40_4797878_dir)
    adb39_32ac824b4b59 = print_file(adb39_32ac824b4b59_dir)
    adb41_30_0_4 = print_file(adb41_30_0_4_dir)
    plink = print_file(plink_dir)
    scrcpy = print_file(scrcpy_dir)
    getlog = print_file(getlog_dir)
    # Main adb
    adb = adb40_4797878

    adb_dir = {adb41_30_0_4: 'v1.0.41 v. 30.0.4-6686687',
               adb40_4797878: 'v1.0.40 v. 4797878',
               adb39_32ac824b4b59: 'v1.0.39 v. 32ac824b4b59'}

    print("\n\nadb: ", adb, "\nPlink:", plink, "\nscrcpy:", scrcpy, "\ngetlog:", getlog)

    freeze_support()
    process_jobs = []

    kill_adb_server = Process(target=kill_server, args=(adb,))
    kill_adb_server.start()
    time.sleep(2)

    q = Queue()
    ApplicationConfig(q, plink, scrcpy, adb, getlog, adb_dir)

    data = {}
    while not q.empty():

        quere = q.get()
        # print("\nQueue", quere)
        data.update(quere)

        ip, user, password, port, direction, serial_number, ScreenRecord, LogsCapture = data["IP"], \
                                                                                        data["Username"], \
                                                                                        data["Password"], \
                                                                                        data["Port"], \
                                                                                        data["Direction"], \
                                                                                        data["serial_number"], \
                                                                                        data["ScreenRecord"], \
                                                                                        data["LogsCapture"]

        command = f'{plink} -ssh -N -C -L 5037:localhost:5037 -R 27183:localhost:27183 {user}@{ip} -pw {password}'
        proc_start = ServerStart()

        print(" \nConfigure port connection in ssh protocol... ")
        start_server = Process(target=proc_start.start, args=(command,))
        process_jobs.append(start_server)
        start_server.start()

        time.sleep(1)
        event = multiprocessing.Event()

        process_start_ssh_mirror = StartConnectionWithSample()

        if ScreenRecord == True:
            start_scrcpy = Process(target=process_start_ssh_mirror.start_ssh_mirror_recording,
                                   args=(serial_number, scrcpy, event))

        elif LogsCapture == True:
            start_scrcpy = Process(target=process_start_ssh_mirror.get_log,
                                   args=(serial_number,))

        else:
            start_scrcpy = Process(target=process_start_ssh_mirror.start_ssh_mirror,
                                   args=(serial_number, scrcpy, event))

        start_scrcpy.start()
        # process_jobs.append(start_server)
        process_jobs.append(start_scrcpy)

        for i in process_jobs[1::]:
            # for i in process_jobs:
            print("\nJoing the finished process to the main process")
            i.join()

        while True:
            if event.is_set():
                print("\nExiting all child processess..")
                # for i in process_jobs[::1]:
                for i in reversed(process_jobs):
                    try:

                        # Terminate each process
                        i.terminate()
                        print("\n\tProcess is alive? - after terminate: ", i.is_alive())

                        i.kill()
                        print("\n\tProcess is alive? - after kill process: ", i.is_alive())

                        i.close()
                        print("\n\tProcess is alive? - after close process: ", i.is_alive())

                    except ValueError:
                        print("\nProcess is closed - trying to close all process...")
                # Terminating main process
                sys.exit(1)
            time.sleep(3)

