import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


## FILE TO SEND AND ITS PATH
def sendEmail(
    receivers,subject,message, sender='anne.leemans@regioplan.nl',
    bcc=False, bccers='', attachment=False, filepath='',filename=''):

    '''This defenition gives the possibiliy to automatically send emails'''

    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receivers
        msg['Subject'] = subject
        if bcc==True:
            msg['bcc'] = bccers 
        body = message

        msg.attach(MIMEText(body, 'plain'))

        if attachment==True:
            SourcePathName   = filepath+filename
            ## ATTACHMENT PART OF THE CODE IS HERE
            attachment = open(SourcePathName, 'rb')
            part = MIMEBase('application', "octet-stream")
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(part)

        server = smtplib.SMTP('smtp.office365.com', 587)  ### put your relevant SMTP here
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login('anne.leemans@regioplan.nl', 'Henk2200quid!')  ### if applicable
        server.send_message(msg)
        server.quit()
        print('Email send to: '+receivers)
    
    except Exception as e:
        print('Email to '+receivers+' could not be send')
        print('The following error occured:')
        print(e)

