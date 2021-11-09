from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4.QtNetwork import *


class ProgressBar(QMessageBox):
    def __init__(self, title="Loading"):
        QMessageBox.__init__(self)
        self.setWindowTitle(title)
        bar = QProgressBar(self)
        self.bar = bar
        self.layout().addWidget(bar)
        bar.setRange(0, 100)
        bar.setValue(0)
        self.setWindowModality(Qt.ApplicationModal)
        self.open()

    def setValue(self, value):
        self.bar.setValue(value)

    def setClose(self):
        self.done()


class FileDownloader(ProgressBar):
    def __init__(self, url):
        # http = QPHttp()
        qurl = QUrl(url)
        path = QString(qurl.toPercentEncoding(qurl.path(), "!$&'()*+,;=:/@"))

        tmpDir = QDir.tempPath()
        # TODO: better file selector
        tmpPath = QDir.cleanPath(tmpDir + "/"+"A")
        self.file = QFile(tmpPath)

        port = qurl.port()
        if port < 0:
            port = 80

        self.httpGetId = -1
        self.http = QPHttp(qurl.host(), port)

        self.http.connect(self.http, SIGNAL("stateChanged ( int )"),
                          self.stateChanged)
        self.http.connect(self.http, SIGNAL("requestFinished (int, bool)"),
                          self.requestFinished)
        self.http.connect(self.http, SIGNAL("dataReadProgress ( int , int )"),
                          self.readProgress)
        self.httpGetId = self.http.get(path, self.file)

    def stateChanged(self, state):
        messages = ["Download complete...", "Resolving host name...",
                    "Connecting...", "Host connected. Sending request...",
                    "Downloading data...", "Idle", "Closing connection...",
                    "Error"]
        self.setTitle(messages[state])
        qgis.utils.iface.mainWindow().statusBar().showMessage(messages[state])

    def readProgress(self, done, total):
        self.progress.bar.setMaximum(total)
        self.progress.bar.setValue(done)
        pass

    def requestFinished(self, requestId, state):
        if requestId != self.httpGetId:
            return
        if state:
            return
        self.file.close()
        path = self.file.fileName()
        self.progress.setClose()
        Tools.debug(path)
        self.complete = True
        return


class QPHttp(QHttp):
    def __init__(self, *args):
        QHttp.__init__(self, *args)
        settings = QSettings()
        settings.beginGroup("proxy")
        if settings.value("/proxyEnabled").toBool():
            self.proxy = QNetworkProxy()
            proxyType = settings.value("/proxyType", QVariant(0)).toString()
            if len(args) > 0 and settings.value("/proxyExcludedUrls").toString().contains(args[0]):
                proxyType = "NoProxy"
            if proxyType in ["1", "Socks5Proxy"]:
                self.proxy.setType(QNetworkProxy.Socks5Proxy)
            elif proxyType in ["2", "NoProxy"]:
                self.proxy.setType(QNetworkProxy.NoProxy)
            elif proxyType in ["3", "HttpProxy"]:
                self.proxy.setType(QNetworkProxy.HttpProxy)
            elif proxyType in ["4", "HttpCachingProxy"] and QT_VERSION >= 0X040400:
                self.proxy.setType(QNetworkProxy.HttpCachingProxy)
            elif proxyType in ["5", "FtpCachingProxy"] and QT_VERSION >= 0X040400:
                self.proxy.setType(QNetworkProxy.FtpCachingProxy)
            else:
                self.proxy.setType(QNetworkProxy.DefaultProxy)
            self.proxy.setHostName(settings.value("/proxyHost").toString())
            self.proxy.setPort(settings.value("/proxyPort").toUInt()[0])
            self.proxy.setUser(settings.value("/proxyUser").toString())
            self.proxy.setPassword(settings.value("/proxyPassword").toString())
            self.setProxy(self.proxy)
        settings.endGroup()
        return None
