import os
import email


class Sender(object):
    def __init__(self, server, user=None, passwd=None,
                 port=25, starttls=False, ssl=False, **kwargs):
        """
        """
        self._server = server
        self._user = user
        self._passwd = passwd
        self._port = port
        self._starttls = starttls
        self._ssl = ssl
        self._from_name = kwargs.get('from_name', None)
        self._from_email = kwargs.get('from_email', None)

    def send(self, to, subject, body, attachments=None,
             from_name=None, from_email=None, cc=None, bcc=None):
        """
        :param to: The recipient email. If a list is passed, the message will
        be fired to all of them.
        :param subject: The email's subject.
        :param body: The email's body.
        :param attachments: An optional list of filepaths to be passed as
        attachments.
        :param from_name: The sender name. If passed here, will override the
        one passed in the constructor.
        :param from_email: The sender email. If passed here, will override the
        one passed in the constructor.
        :param cc: A single email or a list. Used as carbon copy, emails passed
        here will receive a carbon copy of the email.
        :param bcc: A single email or a list. Used as blind carbon copy, emails
        passed here will receive a blind carbon copy of the email.
        """

        to = [to] if type(to) in (str, unicode) else to
        attachments = [] if attachments else attachments
        from_name = from_name if from_name else self._from_name
        from_email = from_email if from_email else self._from_email

        msg = email.MIMEMultipart.MIMEMultipart()
        msg['From'] = "{} <{}>".format(from_name, from_email)
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        msg['Date'] = email.Utils.formatdate(localtime=True)

        if cc is not None:
            cc = [cc] if type(cc) in (str, unicode) else cc
            msg['Cc'] = ', '.join(cc)

        if bcc is not None:
            bcc = [bcc] if type(bcc) in (str, unicode) else bcc
            msg['Bcc'] = ', '.join(bcc)

        msg.attach(email.MIMEText.MIMEText(body))

        for f in attachments:
            part = email.MIMEBase.MIMEBase('application', 'octet-stream')
            part.set_payload(open(f, "rb").read())
            email.Encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(f)
            )
            msg.attach(part)
        else:
            msg.set_payload(body)