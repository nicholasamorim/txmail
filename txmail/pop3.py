from twisted.application import service
from twisted.internet import ssl
from twisted.internet import protocol
from twisted.mail.pop3 import POP3Client
from twisted.application.internet import TCPClient, SSLClient


class POP3Protocol(POP3Client):
    def connectionMade(self):
        print 'made!'

    def handle_WELCOME(self, line):
        print line

    def serverGreeting(self, msg):
        print 'ever called'
        POP3Client.serverGreeting(self, msg)
        self.login(self.factory._username, self.factory._passwd)


class POP3Factory(protocol.ClientFactory):
    protocol = POP3Protocol

    def __init__(self, username, passwd):
        self._username = username
        self._passwd = passwd

    def clientConnectionFailed(self, connector, reason):
        print reason


class _POP3Client(TCPClient):
    def __init__(self, host, username, passwd, port):
        factory = POP3Factory(username, passwd)
        TCPClient.__init__(self, host, port, factory)


class _POP3SSLClient(SSLClient):
    def __init__(self, host, username, passwd, port):
        factory = POP3Factory(username, passwd)
        SSLClient.__init__(
            self, host, port, factory, ssl.ClientContextFactory())


class POP3Service(service.Service):
    def __init__(self, host, username, passwd, port=None, ssl=False):
        if port is None and ssl is False:
            self.port = 110
        elif port is None and ssl is True:
            self.port = 995

        self.host = host
        self.username = username
        self.passwd = passwd
        self.ssl = ssl

    def startService(self):
        service.Service.startService(self)
        if self.ssl is False:
            _POP3Client(self.host, self.username, self.passwd, self.port)
        else:
            _POP3SSLClient(self.host, self.username, self.passwd, self.port)