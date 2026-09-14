WINDOW_STYLE = """
QMainWindow {
    background: #101315;
}
QMenuBar {
    background: #0b0e10;
    color: #a9b3b5;
    border-bottom: 1px solid #202a2c;
    padding-left: 10px;
}
QMenuBar::item {
    background: transparent;
    padding: 7px 14px;
}
QMenuBar::item:selected {
    background: #1c2929;
    color: #e5f3ef;
}
QMenu {
    background: #182021;
    color: #e8eeee;
    border: 1px solid #354344;
}
QMenu::item {
    padding: 7px 22px;
}
QMenu::item:selected {
    background: #25413c;
}
QWidget {
    color: #d9e1e0;
    font-size: 13px;
}
#workspaceSidebar {
    background: #151a1c;
    border-right: 1px solid #334042;
}
#rightArea,
#chatArea {
    background: #101315;
}
#navigation {
    background: #111719;
    border-bottom: 1px solid #293536;
}
QPushButton {
    background: #222b2d;
    color: #dfe9e7;
    border: 1px solid #3a494a;
    border-radius: 4px;
    padding: 5px 12px;
}
QPushButton:hover {
    background: #2c393a;
    border-color: #5b7776;
}
QPushButton:pressed {
    background: #182324;
}
QPushButton:disabled {
    background: #1a2021;
    color: #65716f;
    border-color: #293132;
}
#navButton,
#activeNav {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    color: #93a2a2;
    padding: 0 16px;
}
#navButton:hover {
    background: #182324;
    color: #e4efec;
}
#activeNav {
    color: #e7fff8;
    border-bottom: 2px solid #20c39a;
    font-weight: bold;
}
#windowToolButton {
    background: #151c1e;
    border: 1px solid #435253;
    border-radius: 4px;
    padding: 0;
}
#windowToolButton:hover {
    background: #263435;
    border-color: #6a8584;
}
#sidebarTitle {
    color: #d5e1df;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1px;
}
#newChatButton {
    background: #16a985;
    border: none;
    border-radius: 4px;
    color: #ffffff;
    font-weight: bold;
}
#newChatButton:hover {
    background: #20c39a;
}
QLineEdit,
QTextEdit,
QListWidget {
    background: #1a2224;
    color: #e1e9e8;
    border: 1px solid #324143;
    border-radius: 4px;
    selection-background-color: #28594f;
}
QLineEdit:focus,
QTextEdit:focus {
    border-color: #28b997;
}
QLineEdit {
    padding-left: 10px;
}
#conversationList {
    padding: 2px;
    border-radius: 4px;
}
#conversationList::item {
    border-radius: 3px;
    padding: 1px;
}
#conversationList::item:selected {
    background: #203b38;
    border-left: 2px solid #20c39a;
}
#sessionNumber {
    color: #55c1a8;
    font-size: 11px;
    font-weight: bold;
}
#sessionName {
    color: #dce8e5;
    font-weight: bold;
}
#sessionTime {
    color: #778586;
    font-size: 11px;
}
#sessionState {
    color: #7e9290;
    padding-left: 30px;
    font-size: 11px;
}
#welcomeContainer {
    background: transparent;
}
#welcomeText {
    color: #9ab4ae;
    font-size: 20px;
    font-weight: bold;
    padding: 0 0 20px 12px;
}
#referencesButton {
    background: transparent;
    border: 1px solid #735e43;
    color: #d0a96c;
    border-radius: 4px;
}
#referencesButton:hover {
    background: #282319;
}
#modelRow {
    background: transparent;
}
#modelFrame {
    background: #141a1c;
    border: 1px solid #334243;
    border-radius: 4px;
}
#modelFrame QLineEdit {
    background: #1d2929;
    border: none;
    color: #bde7da;
}

#modelFrame QComboBox {
    background: #1d2929;
    border: none;
    color: #bde7da;
}
#modelFrame QScrollArea{
    background: #1d2929;
    border: none;
    color: #bde7da;
}
#smallLabel {
    color: #6f8582;
    font-size: 11px;
    font-weight: bold;
}
#modelDescription {
    color: #81b6a8;
}
#actionButton {
    min-width: 72px;
    background: #1b2527;
    border: 1px solid #354748;
    border-radius: 4px;
}
#actionButton:hover {
    background: #293638;
    border-color: #607b79;
}
#inputBox {
    background: #1a2224;
    border: 1px solid #354748;
    border-radius: 4px;
    padding: 9px;
    color: #e1e9e8;
}
#sendButton {
    background: #d39a46;
    border: none;
    border-radius: 4px;
    color: #17130d;
    font-weight: bold;
}
#sendButton:hover {
    background: #e6ad5b;
}
#pipelineButton {
    background: transparent;
    border: 1px solid #20a8a0;
    border-radius: 4px;
    color: #50d5c4;
}
#pipelineButton:hover {
    background: #153331;
}
#statusBarCustom {
    background: #0d1113;
    border-top: 1px solid #334143;
}
#serverStatus {
    color: #45c6a5;
    font-weight: bold;
}
#bottomModelStatus {
    color: #c09b62;
}
#statusLabel {
    color: #81908e;
}
#verticalLine {
    color: #5c4d39;
    background: #5c4d39;
    max-width: 1px;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #344143;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 13px;
    height: 13px;
    margin: -5px 0;
    border-radius: 6px;
    background: #d39a46;
}
QSlider::handle:horizontal:hover {
    background: #e6ad5b;
}
QSplitter::handle {
    background: #334042;
}
#chatScrollArea {
    background: #101315;
    border: none;
}
#chatScrollArea QWidget#qt_scrollarea_viewport {
    background: #101315;
}
#chatDisplayPanel {
    background: #101315;
}
#chatEmptyTipText {
    color: #9ab4ae;
    background: transparent;
}
QTextBrowser#aiMessage {
    background-color: #182021;
    color: #dfe9e7;
    border: 1px solid #334243;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
}
QTextBrowser#aiMessage:focus {
    border: 1px solid #28b997;
}
QTextBrowser#aiMessage a {
    color: #50d5c4;
}
"""
