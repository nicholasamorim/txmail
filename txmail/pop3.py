from twisted.internet import ssl
from twisted.internet import protocol
from twisted.mail import pop3client
from twisted.application.internet import TCPClient, SSLClient


class POP3Protocol(pop3client.POP3Client):
    def connectionMade(self):
        d = self.login(self.factory._username, self.factory._passwd)
        d.addCallback(self._login_done)

    def _login_done(self, msg):
        print msg

    def handle_WELCOME(self, line):
        print line

    def serverGreeting(self, msg):
        pop3client.POP3Client.serverGreeting(self, msg)
        self.login(self.factory._username, self.factory._passwd)


class POP3ClientFactory(protocol.ClientFactory):
    protocol = POP3Protocol

    def __init__(self, username, passwd):
        self._username = username
        self._passwd = passwd

    def clientConnectionFailed(self, connector, reason):
        print reason


class POP3Client(TCPClient):
    def __init__(self, host, username, passwd, port):
        factory = POP3ClientFactory(username, passwd)
        TCPClient.__init__(self, host, port, factory)


class POP3SSLClient(SSLClient):
    def __init__(self, host, username, passwd, port):
        self.factory = POP3ClientFactory(username, passwd)
        SSLClient.__init__(
            self, host, port, self.factory, ssl.ClientContextFactory())


class POP3ServiceFactory(object):
    """Convenience Factory.
    """
    def __init__(self, host, username, passwd, port=None, ssl=False):
        if port is None and ssl is False:
            self.port = 110
        elif port is None and ssl is True:
            self.port = 995

        self.host = host
        self.username = username
        self.passwd = passwd
        self.ssl = ssl

    @property
    def service(self):
        if self.ssl is False:
            return POP3Client(
                self.host, self.username, self.passwd, self.port)
        else:
            return POP3SSLClient(
                self.host, self.username, self.passwd, self.port)