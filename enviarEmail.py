import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


fromaddr = "willian.bezerra.ext@sascar.com.br"
toaddr = "w.silva@msn.com"

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Teste envio email python"

body = "Teste de envio de email em python"

msg.attach(MIMEText(body, 'plain'))

filename = "*.sql"
attachment = open("csv2db.sql", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

s = smtplib.SMTP('correio.sascar.com.br', 25)
s.starttls()
s.login(fromaddr, "SENHA_DO_EMAIL")
text = msg.as_string()
s.sendmail(fromaddr, toaddr, text)
s.quit()
print("Sucesso ao enviar o email")
