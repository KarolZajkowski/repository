from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import json
from GetEngine.engine import Decrypt


class EmailSend(object):
    def __init__(self, email_account_login, email_account_mail,
                 email_password, email_smtp, email_port):

        self.login_name = email_account_login
        self.mail_sender = email_account_mail
        self.password = email_password
        self.smtp = email_smtp
        self.port = email_port
        # super(EmailSend, self).__init__()

    def mail_builder(self, *args, **kwargs):
        text = """\

                        Crypto has been sold/buy for ....
                Auto mail

            {:>} {:>}
            {:>} {:>}
            {:>} {:>}
            {:>} {:>}
            {:>} {:>}
            {:>} {:>}

                        """.format("test1", 1,
                                   "test2", 2,
                                   "test3", 3,
                                   "test4", 4,
                                   "test5", 5,
                                   "test6", 6)

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
                            <h1>    BitBay- trade status    </h1>
                        </div>
                        <p>         All summary in attached excel        <br>
                        <p><br>  
                        <p>Platform hyperlink: <a href="https://app.bitbay.net/">BitBay</a><br> 
                        </p>
                        <p><strong><span style="color:red">***This is an automatically generated email, 
                        please do not replay to this message.***</span></strong></p>
                    </body>
                </html>
                """

        return text, html

    def send_email(self, email_receiver, subject):
        COMASPACE = ', '

        mail = MIMEMultipart()
        mail["From"] = self.mail_sender
        mail["To"] = COMASPACE.join(email_receiver)
        mail["Subject"] = subject
        text, html = self.mail_builder()

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        mail.attach(part2)  # first html
        mail.attach(part1)

        with smtplib.SMTP(host=self.smtp, port=self.port) as session:
            session.starttls()
            session.ehlo()

            session.login(self.login_name, self.password)

            text = mail.as_string()

            session.sendmail(self.mail_sender, email_receiver, text)
            print("Mail have been sanded!")

            session.quit()


if __name__ == '__main__':
    encode_decrypt = Decrypt()
    # dict_acc = {
    # "email_account_login": "test89kmz@gmail.com",
    # "email_account_mail": "test89kmz@gmail.com",
    # "email_password": "",
    # "email_smtp": "smtp.gmail.com",
    # "email_port": 587}
    #
    # data_for_update = encode_descrypt.encrypted_function(dict_acc["email_password"])
    # print(data_for_update, dict_acc)
    #
    # dict_acc["email_password"] = data_for_update
    # with open("..\\other\\session.json", "w") as f:
    #     json.dump(dict_acc, f, indent=4)
    #
    # print(dict_acc)

    with open("..\\other\\session.json", "r") as f:
        data = json.load(f)
        print(data)

    data_for_load = encode_decrypt.decrypted(data["email_password"])
    data["email_password"] = data_for_load
    # print("data ", data)

    email_account_login = data["email_account_login"]
    email_account_mail = data["email_account_mail"]
    email_password = data["email_password"]
    email_smtp = data["email_smtp"]
    email_port = data["email_port"]

    send_email = EmailSend(email_account_login, email_account_mail, email_password, email_smtp, email_port)
    send_email.send_email(['kmz1989@gmail.com'], "Bank Summary")