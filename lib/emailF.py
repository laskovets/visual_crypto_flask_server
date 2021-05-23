import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_mail(send_from, send_to, subject, text, files=None,
              server="127.0.0.1"):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        part = MIMEApplication(
            f,
            Name=basename('shadow')
        )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename('shadow.png')
        msg.attach(part)

    smtp = smtplib.SMTP('smtp.gmail.com:587')
    smtp.starttls()
    smtp.login('test@gmail.com', 'test')
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
