from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
from PyQt4.QtWebKit import *
from ..gis.qgis.tools import Tools
from ..gis.qgis.ui.progressbar import ProgressBar

import qgis.utils
import time


def getProxy():
    # Adaption by source of "Plugin Installer - Version 1.0.10"
    proxy = None
    settings = QSettings()
    settings.beginGroup("proxy")
    if settings.value("/proxyEnabled").toBool():
        proxy = QNetworkProxy()
        proxyType = settings.value("/proxyType", QVariant(0)).toString()
        # if len(args)>0 and settings.value("/proxyExcludedUrls").toString().contains(args[0]):
        #  proxyType = "NoProxy"
        if proxyType in ["1", "Socks5Proxy"]:
            proxy.setType(QNetworkProxy.Socks5Proxy)
        elif proxyType in ["2", "NoProxy"]:
            proxy.setType(QNetworkProxy.NoProxy)
        elif proxyType in ["3", "HttpProxy"]:
            proxy.setType(QNetworkProxy.HttpProxy)
        elif proxyType in ["4", "HttpCachingProxy"] and QT_VERSION >= 0X040400:
            proxy.setType(QNetworkProxy.HttpCachingProxy)
        elif proxyType in ["5", "FtpCachingProxy"] and QT_VERSION >= 0X040400:
            proxy.setType(QNetworkProxy.FtpCachingProxy)
        else:
            proxy.setType(QNetworkProxy.DefaultProxy)
        proxy.setHostName(settings.value("/proxyHost").toString())
        proxy.setPort(settings.value("/proxyPort").toUInt()[0])
        proxy.setUser(settings.value("/proxyUser").toString())
        proxy.setPassword(settings.value("/proxyPassword").toString())
    settings.endGroup()
    return proxy


class OLWebPage(QWebPage):
    def __init__(self, parent=None):
        QWebPage.__init__(self, parent)
        self.__manager = None   # Need persist for PROXY
        # Set Proxy in webpage
        proxy = getProxy()
        if proxy is not None:
            self.__manager = QNetworkAccessManager()
            self.__manager.setProxy(proxy)
            self.setNetworkAccessManager(self.__manager)

    def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
        qDebug("%s[%d]: %s" % (sourceID, lineNumber, message))


class LoadXML():
    def __init__(self, url=None):
        self.complete = False
        web = OLWebPage()
        self.frame = web.mainFrame()
        self.frame.load(QUrl(url))
        web.connect(web, SIGNAL("loadFinished(bool)"), self.loadingComplete)
        Tools.debug(url)

    def loadingComplete(self, bool):
        Tools.debug("Load OK"+str(len(self.frame.toHtml())))
        Tools.debug(self.frame.toHtml())
        self.xml = self.frame.toHtml()
        Tools.debug("XML OK")

    def isComplete(self):
        return self.complete

    def getXML(self):
        if self.isComplete():
            return self.xml
        else:
            return None


class LoadXmlByHttp():
    def __init__(self, url=None):
        self.complete = False

        url = QUrl(url)
        path = QString(url.toPercentEncoding(url.path(), "!$&'()*+,;=:/@"))

        tmpDir = QDir.tempPath()
        tmpPath = QDir.cleanPath(tmpDir+"/"+"A")
        self.file = QFile(tmpPath)

        port = url.port()
        if port < 0:
            port = 80

        self.httpGetId = -1
        self.http = QPHttp(url.host(), port)

        self.http.connect(self.http, SIGNAL("stateChanged ( int )"), self.stateChanged)
        self.http.connect(self.http, SIGNAL("requestFinished (int, bool)"), self.requestFinished)
        self.http.connect(self.http, SIGNAL("dataReadProgress ( int , int )"), self.readProgress)
        self.httpGetId = self.http.get(path, self.file)
        # self.progress = ProgressBar()
        Tools.debug("Loading index")
        while True:
            if self.complete:
                return
            Tools.debug("Tick")

    def stateChanged(self, state):
        Tools.debug("state")
        messages = ["Downloaded...", "Resolving host name...", "Connecting...", "Host connected. Sending request...", "Downloading data...", "Idle", "Closing connection...", "Error"]
        qgis.utils.iface.mainWindow().statusBar().showMessage(messages[state])
        Tools.debug(messages[state])

    def readProgress(self, done, total):
        Tools.debug("progress")
        message = str(done) + "/" + str(total)
        qgis.utils.iface.mainWindow().statusBar().showMessage(message)
        # self.progress.bar.setMaximum(total)
        # self.progress.bar.setValue(done)
        Tools.debug(message)

    def requestFinished(self, requestId, state):
        if requestId != self.httpGetId:
            return
        # self.buttonBox.setEnabled(False)
        if state:
            # self.mResult = self.http.errorString()
            # self.reject()
            return
        self.file.close()
        path = self.file.fileName()
        self.progress.setClose()
        Tools.debug(path)
        self.complete = True
        return

        QPHttpfile
        pluginDir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins"
        tmpPath = self.file.fileName()
        # make sure that the parent directory exists
        if not QDir(pluginDir).exists():
            QDir().mkpath(pluginDir)
        # if the target directory already exists as a link, remove the link without resolving:
        QFile(pluginDir+QString(QDir.separator())+self.plugin["localdir"]).remove()
        try:
            un = unzip()
            un.extract(unicode(tmpPath), unicode(pluginDir))    # test extract. If fails, then exception will be raised and no removing occurs
            # removing old plugin files if exist
            removeDir(QDir.cleanPath(pluginDir + "/"+self.plugin["localdir"]))    # remove old plugin if exists
            un.extract(unicode(tmpPath), unicode(pluginDir))    # final extract.
        except:
            self.mResult = self.tr("Failed to unzip the plugin package. Probably it's broken or missing from the repository. You may also want to make sure that you have write permission to the plugin directory:") + "\n" + pluginDir
            self.reject()
            return
        try:
            # cleaning: removing the temporary zip file
            QFile(tmpPath).remove()
        except:
            pass

    def loadingComplete(self, bool):
        Tools.debug("Load OK" + str(len(self.frame.toHtml())))
        Tools.debug(self.frame.toHtml())
        self.xml = self.frame.toHtml()
        Tools.debug("XML OK")

    def isComplete(self):
        return self.complete

    def getXML(self):
        if self.isComplete():
            return self.xml
        else:
            return None


class LoadXmlByRequests():
    def __init__(self, url=None, username=None, password=None):
        Tools.debug(url)
        self.complete = False
        settings = QSettings()
        settings.beginGroup("proxy")
        if settings.value("/proxyEnabled").toBool():
            purl = settings.value("/proxyHost").toString()
            pport = str(settings.value("/proxyPort").toUInt()[0])
            puser = settings.value("/proxyUser").toString()
            ppass = settings.value("/proxyPassword").toString()
        puser = puser.replace("corporateict\\", "")

        proxy = str("http://"+puser+":"+ppass+"@"+purl+":"+pport)
        Tools.debug(proxy)
        proxies = {"http": str(proxy)}  # ,"https": str(proxy)}

        auth = None
        if username is not None and password is not None:
            auth = HTTPBasicAuth(username, password)
        # verbs= requests.options(url, proxies=proxies)
        # for v in verbs.headers['allow']:
        #   Tools.debug(v)
        text = requests.get(url, proxies=proxies, auth=auth)
        Tools.debug(text.content)
        return

        url = QUrl(url)
        path = QString(url.toPercentEncoding(url.path(), "!$&'()*+,;=:/@"))

        tmpDir = QDir.tempPath()
        tmpPath = QDir.cleanPath(tmpDir+"/"+"A")
        self.file = QFile(tmpPath)

        port = url.port()
        if port < 0:
            port = 80

        self.httpGetId = -1
        self.http = QPHttp(url.host(), port)

        self.http.connect(self.http, SIGNAL("stateChanged ( int )"), self.stateChanged)
        self.http.connect(self.http, SIGNAL("requestFinished (int, bool)"), self.requestFinished)
        self.http.connect(self.http, SIGNAL("dataReadProgress ( int , int )"), self.readProgress)
        self.httpGetId = self.http.get(path, self.file)
        self.progress = ProgressBar()
        # count = 0
        # while not self.complete:
            # Tools.debug("Loading index")
            # count += 1
            # bar=self.progress.bar
            # bar.setValue(count)
            # bar.setMaximum(count+1)
            # qgis.utils.iface.mainWindow().statusBar().showMessage(str(count))
            # time.sleep(1)
            # pass

    def stateChanged(self, state):
        messages = ["Downloaded...", "Resolving host name...", "Connecting...", "Host connected. Sending request...", "Downloading data...", "Idle", "Closing connection...", "Error"]
        self.progress.setTitle(messages[state])
        qgis.utils.iface.mainWindow().statusBar().showMessage(messages[state])

    def readProgress(self, done, total):
        self.progress.bar.setMaximum(total)
        self.progress.bar.setValue(done)
        pass

    def requestFinished(self, requestId, state):
        if requestId != self.httpGetId:
            return
        # self.buttonBox.setEnabled(False)
        if state:
            # self.mResult = self.http.errorString()
            # self.reject()
            return
        self.file.close()
        path = self.file.fileName()
        self.progress.setClose()
        Tools.debug(path)
        self.complete = True
        return
        QPHttpfile
        pluginDir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins"
        tmpPath = self.file.fileName()
        # make sure that the parent directory exists
        if not QDir(pluginDir).exists():
            QDir().mkpath(pluginDir)
        # if the target directory already exists as a link, remove the link without resolving:
        QFile(pluginDir+QString(QDir.separator())+self.plugin["localdir"]).remove()
        try:
            un = unzip()
            un.extract(unicode(tmpPath), unicode(pluginDir))    # test extract. If fails, then exception will be raised and no removing occurs
            # removing old plugin files if exist
            removeDir(QDir.cleanPath(pluginDir+"/"+self.plugin["localdir"]))    # remove old plugin if exists
            un.extract(unicode(tmpPath), unicode(pluginDir))    # final extract.
        except:
            self.mResult = self.tr("Failed to unzip the plugin package. Probably it's broken or missing from the repository. You may also want to make sure that you have write permission to the plugin directory:") + "\n" + pluginDir
            self.reject()
            return
        try:
            # cleaning: removing the temporary zip file
            QFile(tmpPath).remove()
        except:
            pass

    def loadingComplete(self, bool):
        Tools.debug("Load OK" + str(len(self.frame.toHtml())))
        Tools.debug(self.frame.toHtml())
        self.xml = self.frame.toHtml()
        Tools.debug("XML OK")

    def isComplete(self):
        return self.complete

    def getXML(self):
        if self.isComplete():
            return self.xml
        else:
            return None


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
