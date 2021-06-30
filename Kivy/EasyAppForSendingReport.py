import kivy
import os
import smtplib
import json
import datetime

kivy.require("1.11.1")
__version__ = "1.0.1"

from kivy.app import App
from kivy.uix.label import Label
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from kivy.storage.jsonstore import JsonStore
from kivy.uix.image import Image
from kivy.uix.image import \
    AsyncImage  # web direction to located png image 'http://kivy.org/logos/kivy-logo-black-64.png'
from jnius import autoclass
from os.path import join

# from android.permissions import request_permissions, Permission
# request a permission from user
# request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.INTERNET])


class GetTextFile(object):
    def __init__(self):
		"""Geting object to send in report"""
        os.chdir(r'/data/data/org.mail.mail_send/')
        self.cwd = os.getcwd()

    def attach_file(self):
        try:
            with open("conf.json", 'r') as json_file:
                data = json.load(json_file)
                print(data)
                return data

        except FileNotFoundError:
            print('There is no file - change direction')


class Gmail(object):
    def __init__(self, email, password, smtp, receiver):
        self.email = email
        self.password = password
        self.server = smtp
        self.port = 465
        self.email_receiver = receiver
        super(Gmail, self).__init__()

    def send_message(self, subject, body, html):
        COMMASPACE = ', '

        mail = MIMEMultipart()
        mail["From"] = self.email
        mail["To"] = COMMASPACE.join(self.email_receiver)
        mail["Subject"] = subject

        part1 = MIMEText(body, "plain")
        part2 = MIMEText(html, "html")

        mail.attach(part1)
        mail.attach(part2)

        with smtplib.SMTP_SSL(self.server, self.port) as session:
            session.ehlo()
            session.login(self.email, self.password)

            text = mail.as_string()
            session.sendmail(self.email, self.email_receiver, text)
            session.quit()


def get_time():
    return datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")


class MyApp(App):
    time = get_time()
    get_json = GetTextFile()

    try:
        get_json = GetTextFile()
        date = get_json.attach_file()

        text = """\

                Warning! A problem with script occurred
        The script was restarted...

    Serial Number of the phone: {}
    Break in loop no.: {}
    AutoRack no.: {}
    Place to run the script: {}
    Timer trigger for restart: {}
    Date and Time when the error occurred: {}

                """.format(date["appDetail"]["serialNumber"], date["count"], date["AutoRack"],
                           date["appDetail"]["direction"], date["maxIntervalBreak"], time)

        html = """\
        <html>
        <head>
        <style>
        .myDiv {
            border: 5px outset red;
            background-color: lightblue;
            text-align: center;
            }
        h1 {color:blue;}
        p {color:brown;}
        </style>
        </head>
          <body>
            <div class="myDiv">
                <h1>Monkey Test Report</h1>
            </div>
            <p>Problem with script occurred<br>
               The script was restarted...<br>

                    Possible need for a reboot


                        <a href="http://www.google.com">KarolZajkowski</a>
            </p>
            <p><strong><span style="color:red">***This is an automatically generated email, 
            please do not replay to this message.***</span></strong></p>
          </body>
        </html>
        """

        email_receiver = date["email"]["email_receiver"]
        email_account = date["email"]["email_account"]
        email_password = date["email"]["email_password"]
        email_smtp = date["email"]["email_SMTP"]

        if email_account != False and email_password != False and email_smtp != False:
            login = email_account
            password = email_password
            smtp = email_smtp

        else:
            login = "test@gmail.com"
            password = ""
            smtp = "smtp.gmail.com"

        subject = date["email"]["Subject"]

        gm = Gmail(login, password, smtp, email_receiver)
        gm.send_message(subject, text, html)

        # listdir = gm.cwd
        def build(self):
            return AsyncImage(source="http://www.icons101.com/icons/4/iOS_7_by_dtafalonso/64/Mail.png")

    except Exception as e:
        # Print any error messages to stdout
        get_json_dir = get_json.cwd

        def build(self):
            print("Exception occured: ", e)
            return Label(text="{:^65}\n{:^65}\n{:^65}".format("Error occurred: {}".format(self.error),



if __name__ == '__main__':
    MyApp().run()
