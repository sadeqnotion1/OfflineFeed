import QtQuick
import QtQuick.Controls
import "../themes"

// Container for the master-detail Settings navigation stack
Rectangle {
    id: root
    color: Theme.bg

    StackView {
        id: settingsStack
        anchors.fill: parent
        clip: true

        initialItem: SettingsRoot {
            onSectionSelected: function(sectionId) {
                if (sectionId === "account") {
                    settingsStack.push(accountComponent)
                } else if (sectionId === "notifications") {
                    settingsStack.push(notificationsComponent)
                } else if (sectionId === "privacy") {
                    settingsStack.push(privacyComponent)
                } else if (sectionId === "feed") {
                    settingsStack.push(feedComponent)
                } else if (sectionId === "sources") {
                    settingsStack.push(sourcesComponent)
                } else if (sectionId === "folders") {
                    settingsStack.push(foldersComponent)
                } else if (sectionId === "advanced") {
                    settingsStack.push(advancedComponent)
                } else if (sectionId === "appearance") {
                    settingsStack.push(appearanceComponent)
                } else if (sectionId === "language") {
                    settingsStack.push(languageComponent)
                } else if (sectionId === "help") {
                    settingsStack.push(helpComponent)
                }
            }
        }
    }

    Component { id: accountComponent; SettingsAccount {} }
    Component { id: notificationsComponent; SettingsNotifications {} }
    Component { id: privacyComponent; SettingsPrivacy {} }
    Component { id: feedComponent; SettingsFeed {} }
    Component { id: sourcesComponent; SettingsSources {} }
    Component { id: foldersComponent; SettingsFolders {} }
    Component { id: advancedComponent; SettingsAdvanced {} }
    Component { id: appearanceComponent; SettingsAppearance {} }
    Component { id: languageComponent; SettingsLanguage {} }
    Component { id: helpComponent; SettingsHelp {} }
}
