import os
import email

from cStringIO import StringIO

from OpenSSL.SSL import SSLv3_METHOD

from twisted.internet import defer, reactor
from twisted.mail.smtp import ESMTPSenderFactory
from twisted.internet.ssl import ClientContextFactory


class Sender(object):
    def __init__(self, server, user=None, passwd=None,
                 port=25, starttls=False, ssl=False, **kwargs):
        """A class that sends emails via SMTP and returns a deferred.

        :param server: SMTP server.
        :param user: SMTP user.
        :param passwd: SMTP passwd.
        :param port: SMTP port.
        :param starttls: If True, we will upgrade a plain connection to
        an encrypted connection.
        :param ssl: If True, we'll use SSL to connect.
        :param from_name: An optional sender name. It can also be passed
        to the send method directly. If set here, will be used for all
        emails sent via the `send` method.
        :param from_email: An optional sender email. It can also be passed
        to the send method directly. If set here, will be used for all
        emails sent via the `send` method.
        :param retries: An `int` specifying how many times we should retry
        in case of failue. Default is 5.
        :param timeout: An `int`specifying the timeout. If None, we wait
        forever. Default is None.
        """
        self._server = server
        self._user = user
        self._passwd = passwd
        self._port = port
        self._starttls = starttls
        self._ssl = ssl

        self._from_name = kwargs.get('from_name', None)
        self._from_email = kwargs.get('from_email', None)
        self._noisy = kwargs.get('noisy', False)
        self._retries = kwargs.get('retries', 5)
        self._timeout = kwargs.get('timeout', None)

    def send(self, to, subject, body, attachments=None,
             from_name=None, from_email=None, cc=None, bcc=None, headers=None):
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
        :param headers: An optional dictionary of custom headers.
        """

        to = [to] if type(to) in (str, unicode) else to
        attachments = [] if attachments is None else attachments
        self._from_name = from_name if from_name else self._from_name
        self._from_email = from_email if from_email else self._from_email

        if attachments:
            msg = email.MIMEMultipart.MIMEMultipart()
            msg.attach(email.MIMEText.MIMEText(body))
        else:
            msg = email.MIMENonMultipart.MIMENonMultipart('text', 'plain')
            msg.set_payload(body)

        msg['From'] = "{} <{}>".format(self._from_name, self._from_email)
        self._to = ', '.join(to)
        msg['To'] = self._to

        msg['Subject'] = subject
        msg['Date'] = email.Utils.formatdate(localtime=True)

        if cc is not None:
            cc = [cc] if type(cc) in (str, unicode) else cc
            msg['Cc'] = ', '.join(cc)

        if bcc is not None:
            bcc = [bcc] if type(bcc) in (str, unicode) else bcc
        else:
            bcc = []

        for f in attachments:
            part = email.MIMEBase.MIMEBase('application', 'octet-stream')
            part.set_payload(open(f, "rb").read())
            email.Encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(f)
            )
            msg.attach(part)

        if headers:
            for k, v in headers.iteritems():
                msg.add_header(k, v)

        d = self._send(None, to, msg.as_string())

        for blindrcpt in bcc:
            msg['To'] = blindrcpt
            del msg['Cc']
            d.addCallback(self._send, blindrcpt, msg.as_string())

        return d

    def _get_factory(self, to, message, deferred):
        """
        """
        sender_factory = ESMTPSenderFactory(
            self._user,
            self._passwd,
            self._from_email,
            to,
            message,
            deferred,
            heloFallback=True,
            requireAuthentication=False,
            requireTransportSecurity=self._starttls
        )
        sender_factory.noisy = self._noisy

        return sender_factory

    def _send(self, _, to, message):
        """Internal function used to actually send the email.

        :param _: Callback return, ignored.
        :param to: A list of recipients.
        :param message: The message as string.
        """
        d = defer.Deferred()

        sender_factory = self._get_factory(to, StringIO(message), d)
        args = [self._server, self._port, sender_factory]

        if self._ssl:
            func = reactor.connectSSL

            context_factory = ClientContextFactory()
            context_factory.method = SSLv3_METHOD
            args.append(context_factory)
        else:
            func = reactor.connectTCP

        func(*args)

        return d
