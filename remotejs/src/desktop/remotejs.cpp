/*
Copyright (c) 2010 Sencha Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#include <QtGui>
#include <QtWebKit>

#define LOG_FILTER "RemoteJS"
#define TARGET_ACTIVITY "com.sencha.remotejs/.RemoteJS"

class RemoteConsole: public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool isAdbAvailable READ isAdbAvailable)
    Q_PROPERTY(QStringList deviceList READ getDeviceList)
    Q_PROPERTY(QString targetDevice READ targetDevice WRITE setTargetDevice)
    Q_PROPERTY(QString adbPath READ adbPath WRITE setAdbPath)

public:
    explicit RemoteConsole(QObject *parent = 0);
    ~RemoteConsole();

    bool isAdbAvailable() const;
    QString targetDevice() const;

signals:
    void aboutToQuit();
    void dataAvailable(const QString &data);
    void disconnected();

public slots:
    void evaluateJavaScript(const QString &script);
    QStringList getDeviceList();
    QString installDeviceTool();
    void openUrl(const QString &url);
    void readAdbData();
    void setAdbPath(const QString &adbPath);
    QString adbPath() const;
    void setTargetDevice(const QString &device);
    QString chooseAdbPath();
    void captureWindow();
    void saveBuffer();

private:
    QProcess m_adbConnection;
    QString m_adbData;
    QString m_adbPath;
    QString m_targetDevice;
    QImage m_buffer;
    QProgressDialog *m_progress;

    void adbExecute(const QString &command) const;
    QString adbQuery(const QString &command) const;
    QString readProcess(const QString &command, int timeout = 30000) const;
    QString readProcess(QProcess &process, const QString &command, int timeout = 30000) const;
};

RemoteConsole::RemoteConsole(QObject *parent)
    : QObject(parent)
    , m_progress(0)
{
    connect(&m_adbConnection, SIGNAL(readyRead()), this, SLOT(readAdbData()));
    connect(&m_adbConnection, SIGNAL(finished(int, QProcess::ExitStatus)), SIGNAL(disconnected()));
    connect(qApp, SIGNAL(aboutToQuit()), SIGNAL(aboutToQuit()));
}

RemoteConsole::~RemoteConsole()
{
    m_adbConnection.close();
}

QString RemoteConsole::installDeviceTool()
{
    QFile temp(QDir::temp().absoluteFilePath("RemoteJS.apk"));
    if (!temp.open(QFile::WriteOnly))
        return QLatin1String("Unable to open temp file: ") + temp.fileName();
    QFile tool(":/RemoteJS.apk");
    if (!tool.open(QFile::ReadOnly))
        return QLatin1String("Unable to open tool from the resource subsystem");
    QByteArray rd;
    while (!tool.atEnd()) {
        rd = tool.read(8192);
        temp.write(rd);
    }
    tool.close();
    temp.close();

    adbQuery("uninstall com.sencha.remotejs");
    QString ret = adbQuery("install " + temp.fileName());

    temp.remove();

    return ret.trimmed().split(QLatin1Char('\n')).last().remove(QLatin1Char('\r'));
}

void RemoteConsole::readAdbData()
{
    m_adbData += m_adbConnection.readAll();
    int pos = m_adbData.indexOf(QLatin1Char('\n'));
    while (pos >= 0) {
        QString output = m_adbData.left(pos);

        m_adbData.remove(0, pos + 1);
        pos = m_adbData.indexOf(QLatin1Char('\n'));

        if (!output.contains(QRegExp(QLatin1String("[A-Z]/") + LOG_FILTER)))
            continue;

        bool info = output[0] == 'I';

        output.remove(QRegExp(QLatin1String("[A-Z]/") + LOG_FILTER
                              + QLatin1String("(\\b)*\\((\\s)*(\\d)+\\): ")));
        output.remove(QRegExp(QLatin1String("Console: ")));
        output.remove(QRegExp(QLatin1String(":(\\d)+(\\b)*")));
        output.remove('\r');

        if (info) {
            if (output.startsWith("Buffer START")) {
                QStringList items = output.split(' ', QString::SkipEmptyParts);
                if (items.count() == 4) {
                    int width = items[2].toInt();
                    int height = items[3].toInt();
                    m_buffer = QImage(width, height, QImage::Format_ARGB32);
                    m_buffer.fill(qRgb(255, 255, 255));
                    delete m_progress;
                    m_progress  = new QProgressDialog;
                    m_progress->setWindowModality(Qt::WindowModal);
                    m_progress->setCancelButton(0);
                    m_progress->setWindowTitle("Getting the screen capture...");
                    m_progress->show();
                    m_progress->setMinimumWidth(400);
                    qobject_cast<QWidget*>(parent())->hide();
                }
            } else if (output == "Buffer END") {
                delete m_progress;
                m_progress = 0;
                qobject_cast<QWidget*>(parent())->show();
                QTimer::singleShot(0, this, SLOT(saveBuffer()));
            } else {
                QStringList items = output.split(' ', QString::SkipEmptyParts);
                if (m_progress && items.count() == 5) {
                    int x = items.at(0).toInt();
                    int y = items.at(1).toInt();
                    int r = items.at(2).toInt();
                    int g = items.at(3).toInt();
                    int b = items.at(4).toInt();
                    m_buffer.setPixel(x, y, qRgb(r, g, b));
                    if (m_buffer.height())
                        m_progress->setValue((y + 1) * 100 / m_buffer.height());
                }
            }
        } else {
            emit dataAvailable(output);
        }
    }
}

void RemoteConsole::adbExecute(const QString &command) const
{
    qApp->setOverrideCursor(Qt::WaitCursor);
    QString device;
    if (!m_targetDevice.isEmpty())
        device = QLatin1String(" -s ") + m_targetDevice;
    QProcess::execute(m_adbPath + device + ' ' + command);
    qApp->restoreOverrideCursor();
}

QString RemoteConsole::adbQuery(const QString &command) const
{
    qApp->setOverrideCursor(Qt::WaitCursor);
    QString device;
    if (!m_targetDevice.isEmpty())
        device = QLatin1String(" -s ") + m_targetDevice;
    QString result = readProcess(m_adbPath + device + ' ' + command);
    qApp->restoreOverrideCursor();
    return result;
}

QString RemoteConsole::readProcess(const QString &command, int timeout) const
{
    QProcess process;
    return readProcess(process, command, timeout);
}

QString RemoteConsole::readProcess(QProcess &process, const QString &command,
                                   int timeout) const
{
    qApp->setOverrideCursor(Qt::WaitCursor);
    process.start(command);
    process.waitForFinished(timeout);
    QString output = process.readAll();
    process.close();
    qApp->restoreOverrideCursor();
    return output;
}

bool RemoteConsole::isAdbAvailable() const
{
    QString version = adbQuery(QLatin1String("version"));
    return version.startsWith(QLatin1String("Android Debug Bridge"));
}

QStringList RemoteConsole::getDeviceList()
{
    QString devices = adbQuery(QLatin1String("devices"));
    devices.remove(QRegExp(QLatin1String("List of devices attached\\s+")));

    QStringList temp = devices.split('\n', QString::SkipEmptyParts);
    QStringList list;
    QRegExp re(QLatin1String("\\tdevice"));
    foreach (QString str, temp) {
        if (str.contains(re))
            list << str.remove(re);
    }

    return list;
}

void RemoteConsole::setAdbPath(const QString &adbPath)
{
    m_adbPath = adbPath;
}

QString RemoteConsole::adbPath() const
{
    return m_adbPath;
}

QString RemoteConsole::targetDevice() const
{
    return m_targetDevice;
}

void RemoteConsole::setTargetDevice(const QString &device)
{
    qApp->setOverrideCursor(Qt::WaitCursor);
    m_targetDevice = device;
    bool enabled = !m_targetDevice.isEmpty();
    if (enabled) {
        QString adbDevice = m_adbPath + QLatin1String(" -s ") + m_targetDevice;
        QProcess::execute(adbDevice + QLatin1String(" logcat -c")); // flush log
        m_adbConnection.start(adbDevice + QLatin1String(" logcat ") + LOG_FILTER
                              + QLatin1String(":V *:S"));
    }
    qApp->restoreOverrideCursor();
}

QString RemoteConsole::chooseAdbPath()
{
    return QFileDialog::getOpenFileName(0, QLatin1String("Select the adb executable"), m_adbPath);
}

void RemoteConsole::openUrl(const QString &address)
{
    QString location = QUrl::fromUserInput(address).toEncoded().toBase64();
    QString command = QLatin1String(" shell am start -a android.intent.action.VIEW -n ")
                      + TARGET_ACTIVITY + QLatin1String(" -d '") + location + QLatin1String("'");
    adbExecute(command);
}

void RemoteConsole::evaluateJavaScript(const QString &script)
{
    QString expression = QByteArray("javascript:(function() { " + script.toLatin1()
                         + "; })()").toBase64();
    QString command = QLatin1String(" shell am start -a android.intent.action.VIEW -n ")
                      + TARGET_ACTIVITY + QLatin1String(" -d '") + expression + QLatin1String("'");
    adbExecute(command);
}

void RemoteConsole::captureWindow()
{
    QString command = QLatin1String(" shell am start -a com.sencha.remotejs.ACTION_CAPTURE -n ")
                      + TARGET_ACTIVITY;
    adbExecute(command);
}

void RemoteConsole::saveBuffer()
{
    QString name = QFileDialog::getSaveFileName(0, QLatin1String("Save Capture"),
                                                QString(), "Images (*.png *.jpg)");
    if (name.isEmpty())
        return;
    m_buffer.save(name);
}

static QString readFileContents(const QString &fileName)
{
    QFile file(fileName);
    file.open(QFile::ReadOnly);
    QString contents = file.readAll();
    file.close();
    return contents;
}

int main(int argc, char *argv[])
{
    QApplication::setGraphicsSystem("raster");
    QApplication application(argc, argv);

#ifdef Q_OS_MAC
    QWebSettings::globalSettings()->setFontFamily(QWebSettings::FixedFont, "Monaco");
#endif

    QWebView webView;
    RemoteConsole remoteConsole(&webView);
    webView.settings()->setAttribute(QWebSettings::LocalStorageEnabled, true);
    webView.settings()->setLocalStoragePath(QDesktopServices::storageLocation(QDesktopServices::DataLocation));
    webView.page()->mainFrame()->setHtml(readFileContents(":/interface.html"));
    webView.page()->mainFrame()->addToJavaScriptWindowObject("remoteConsole", &remoteConsole);
    webView.setRenderHints(QPainter::Antialiasing | QPainter::TextAntialiasing | QPainter::SmoothPixmapTransform);
    webView.setWindowTitle("RemoteJS - Remote JavaScript Console for Android");
    webView.show();

    return application.exec();
}

#include "remotejs.moc"
