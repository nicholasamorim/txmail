import re
import email

from twisted.python import log
from twisted.internet import ssl, defer
from twisted.internet import protocol
from twisted.mail import pop3client
from twisted.application.internet import TCPClient, SSLClient

EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+')


class POP3Protocol(pop3client.POP3Client):
    def _login_successful(self, msg):
        if self.factory._debug:
            log.msg('Login was successful!')

        self.listSize().addCallback(self._got_sizes)

    def _got_sizes(self, sizes):
        retrievers = []
        for i in range(len(sizes)):
            d = self.retrieve(i)
            d.addCallback(self._parse_message)
            d.addCallback(self._process_message)

            retrievers.append(d)

        dlist = defer.DeferredList(retrievers)
        dlist.addCallback(self._finished)

        return dlist

    def _parse_message(self, lines):
        """
        """
        parsed_email = email.message_from_string('\n'.join(lines))
        return parsed_email

    def _finished(self, results):
        if self.factory._debug:
            log.msg('_finished: %s' % (results, ))

        self.quit()

    def serverGreeting(self, msg):
        pop3client.POP3Client.serverGreeting(self, msg)
        d = self.login(
            self.factory._username,
            self.factory._passwd)

        d.addCallback(self._login_successful)
        d.addErrback(log.err)

    def _save_on_folder(self, message):
        if self.factory._save_on:
            pass

        return message

    def _call_callback(self, message):
        """
        """
        if self.factory._callback is not None:
            pass

    def _process_message(self, message):
        """
        """
        d = self._save_on_folder(message)
        d.addCallback(self._call_callback)
        return d


class POP3ClientFactory(protocol.ClientFactory):
    protocol = POP3Protocol

    def __init__(self, username, passwd, callback=None, **kwargs):
        self._username = username
        self._passwd = passwd
        self._callback = callback
        self._debug = kwargs.get('debug', False)
        self._save_on = kwargs.get('save_on', False)
        self._delete_on_remote = kwargs.get('delete_on_remote', False)

    def clientConnectionFailed(self, connector, reason):
        print reason


class POP3Client(TCPClient):
    """POP3 non-encrypted client. Usually connects on port 110.
    """
    def __init__(self, host, port, factory):
        TCPClient.__init__(self, host, port, factory)


class POP3SSLClient(SSLClient):
    """POP3 SSL Client. Usually connects on port 995.
    """
    def __init__(self, host, port, factory):
        SSLClient.__init__(
            self, host, port, factory, ssl.ClientContextFactory())


class POP3ServiceFactory(object):
    """Convenience Service Factory. It returns the correct client/service
    based on ssl parameter.
    """
    def __init__(self, host, username, passwd, port=None,
                 ssl=False, callback=None, **kwargs):
        """
        :param host: The POP3 host.
        :param username: The POP3 server username.
        :param passwd: The POP3 user's password.
        :param port: An optional port.
        :param ssl: A boolean. Default is False.
        :param callback: A function to be called everytime a message arrives.
        :param save_on: (kwargs) An optional path to save messages.
        :param delete_on_remote: (kwargs) An optional boolean to delete
        messages on remote after receiving them. Default is False.
        """
        if port is None and ssl is False:
            self.port = 110
        elif port is None and ssl is True:
            self.port = 995

        self.host = host
        self.ssl = ssl
        self.factory = POP3ClientFactory(username, passwd, callback, **kwargs)

    @property
    def service(self):
        """A property factory that returns the right service.
        When using as a service you might do:

        pop3 = POP3ServiceFactory(host, user, passwd, ssl=ssl)
        application.addService(pop3.service)
        """
        if self.ssl is False:
            return POP3Client(
                self.host, self.port, self.factory)
        else:
            return POP3SSLClient(
                self.host, self.port, self.factory)