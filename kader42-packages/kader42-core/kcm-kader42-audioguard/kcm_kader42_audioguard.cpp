#include <KPluginFactory>
#include <KQuickConfigModule>
#include <QDir>
#include <QFile>
#include <QProcess>
#include <QStandardPaths>
#include <QTextStream>

class Kader42AudioGuardKcm : public KQuickConfigModule
{
    Q_OBJECT

public:
    explicit Kader42AudioGuardKcm(QObject *parent, const KPluginMetaData &data)
        : KQuickConfigModule(parent, data)
    {
        setButtons(NoAdditionalButton);
    }

    Q_INVOKABLE bool isServiceActive() const
    {
        return QProcess::execute(
                   QStringLiteral("systemctl"),
                   {QStringLiteral("--user"),
                    QStringLiteral("is-active"),
                    QStringLiteral("--quiet"),
                    QStringLiteral("kader42-audio-guard.service")})
            == 0;
    }

    Q_INVOKABLE void setServiceEnabled(bool enabled)
    {
        QProcess::execute(
            QStringLiteral("systemctl"),
            {QStringLiteral("--user"),
             enabled ? QStringLiteral("enable") : QStringLiteral("disable"),
             QStringLiteral("--now"),
             QStringLiteral("kader42-audio-guard.service")});
    }

    Q_INVOKABLE bool notificationsEnabled() const
    {
        const QString userCfg =
            QStandardPaths::writableLocation(QStandardPaths::ConfigLocation)
            + QStringLiteral("/kader42/audio-guard.conf");

        for (const QString &path : {userCfg, QStringLiteral("/etc/kader42/audio-guard.conf")}) {
            QFile file(path);
            if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
                QTextStream in(&file);
                while (!in.atEnd()) {
                    const QString line = in.readLine().trimmed();
                    if (line.startsWith(QStringLiteral("notifications="))) {
                        const QString val = line.mid(14).trimmed().toLower();
                        return val != QStringLiteral("false")
                            && val != QStringLiteral("0")
                            && val != QStringLiteral("no");
                    }
                }
            }
        }
        return true;
    }

    Q_INVOKABLE void setNotificationsEnabled(bool enabled)
    {
        const QString dirPath =
            QStandardPaths::writableLocation(QStandardPaths::ConfigLocation)
            + QStringLiteral("/kader42");
        QDir().mkpath(dirPath);

        QFile file(dirPath + QStringLiteral("/audio-guard.conf"));
        if (file.open(QIODevice::WriteOnly | QIODevice::Truncate | QIODevice::Text)) {
            QTextStream out(&file);
            out << "notifications=" << (enabled ? "true" : "false") << '\n';
        }
    }

    Q_INVOKABLE void testNotify()
    {
        QProcess::startDetached(
            QStringLiteral("/usr/bin/kader42-audio-guard"),
            {QStringLiteral("--test-notify")});
    }

    Q_INVOKABLE bool repairAudio()
    {
        return QProcess::execute(
                   QStringLiteral("/usr/bin/kader42-audio-guard"),
                   {QStringLiteral("--repair")})
            == 0;
    }
};

K_PLUGIN_CLASS_WITH_JSON(Kader42AudioGuardKcm, "kcm_kader42_audioguard.json")

#include "kcm_kader42_audioguard.moc"
