import sys
import ctypes
from ctypes import wintypes
from typing import Callable, Union, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import  QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QSizePolicy,
    QScrollArea,
)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.connection import ChatUi_Connection, SessionUi_Connection, Setup_Connection
from gui.icon import AspectRatioLabel
from gui.stylesheet import WINDOW_STYLE
from PySide6.QtCore import Qt
from gui.task_runner import test_func


class MainWindow(QMainWindow, ChatUi_Connection, SessionUi_Connection, Setup_Connection):

    agent_reply_signal = Signal(str)

    def __init__(self,model_name:str ="qwen3.8-max",
                model_name_dict:dict = {"qwen3.8-max":"API","qwen3.8-8B":"LOCAL"},
                think_timeout:Union[int,bool] = 120, core_task_func:Callable = test_func):

        super().__init__()

        self.external_model_name = model_name
        self.external_model_name_dict = model_name_dict
        self.external_think_timeout = think_timeout
        self.external_core_func = core_task_func

        self.setWindowTitle("AI Agent")
        self.resize(1280, 720)
        self.setMinimumSize(960, 540)

        self.setup_ui()
        self.init_setting()
        self.setup_palette()

        self.setup_stylesheet()
        self.apply_dark_title_bar()
        self.set_up_connection()
        self.agent_reply_signal.connect(self.on_agent_reply)
     
    # =========================================================
    # 初始化设置
    # =========================================================
    def init_setting(self):
        self.is_thinking = False
        # 当前正在使用的对话id
        self.current_conv_id: Optional[str] = None
        # 加载本地历史会话
        self.refresh_sidebar_conversation_list()

        if self.local_conversations:
            first_conv = self.local_conversations[0]
            self.current_conv_id = first_conv["conv_id"]
            self.load_messages_to_ui(first_conv.get("messages", []))
            self.conversations.setCurrentRow(0)
        else:
            self.current_conv_id = None
            self.clear_chat_display()

    # =========================================================
    # 创建主界面
    # =========================================================
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.root_layout = QVBoxLayout(central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # =====================================================
        # 主体：左侧工作区 + 右侧控制台
        # 不可滑动分割条（可滑动易出现bug）
        # =====================================================
        self.body_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.body_splitter.setChildrenCollapsible(False)
        self.body_splitter.setHandleWidth(1)
        self.body_splitter.setEnabled(True)

        # -----------------------------------------------------
        # 左侧工作区
        # -----------------------------------------------------
        self.sidebar = QWidget()
        self.sidebar.setObjectName("workspaceSidebar")
        self.sidebar.setMinimumWidth(230)
        self.sidebar.setMaximumWidth(260)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(14, 16, 14, 10)
        sidebar_layout.setSpacing(10)

        icon_label = AspectRatioLabel("gui/icon.png", self.sidebar)
        sidebar_layout.addWidget(icon_label)

        self.new_session_button = QPushButton("新建对话")
        self.new_session_button.setObjectName("newChatButton")
        self.new_session_button.setFixedHeight(42)
        sidebar_layout.addWidget(self.new_session_button)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("\U0001F50D")
        self.search_box.setFixedHeight(35)
        sidebar_layout.addWidget(self.search_box)

        self.conversations = QListWidget()
        self.conversations.setObjectName("conversationList")
        self.conversations.setSpacing(2)

        sidebar_layout.addWidget(self.conversations, 1)

        self.body_splitter.addWidget(self.sidebar)

        # -----------------------------------------------------
        # 右侧区域
        # -----------------------------------------------------
        self.right_area = QWidget()
        self.right_area.setObjectName("rightArea")

        right_layout = QVBoxLayout(self.right_area)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # =====================================================
        # 顶部导航工具栏
        # =====================================================
        navigation = QWidget()
        navigation.setObjectName("navigation")
        navigation.setFixedHeight(44)
        navigation_layout = QHBoxLayout(navigation)
        navigation_layout.setContentsMargins(10, 0, 8, 0)
        navigation_layout.setSpacing(2)

        button = QPushButton("Chat")
        button.setObjectName("activeNav") # 当前激活状态
        button.setFlat(True)
        button.setFixedHeight(44)
        navigation_layout.addWidget(button)

        navigation_layout.addStretch()
        right_layout.addWidget(navigation)

        # =====================================================
        # 上方控制台区域
        # =====================================================
        chat_area = QWidget()
        chat_area.setObjectName("chatArea")

        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(20, 10, 12, 12)
        chat_layout.setSpacing(10)

        # 创建滚动区域
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setObjectName("chatScrollArea")
        self.chat_scroll_area.setWidgetResizable(True)

        # 禁止横向滚动，只允许纵向滚动
        self.chat_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.chat_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # 创建真正存放消息的内部容器
        self.chat_display_panel = QWidget()
        self.chat_display_panel.setObjectName("chatDisplayPanel")
        self.chat_display_panel.setStyleSheet("background-color:#101315;")

        self.chat_display_layout = QVBoxLayout(self.chat_display_panel)
        self.chat_display_layout.setContentsMargins(16, 16, 16, 16)
        self.chat_display_layout.setSpacing(14)

        # 初始提示
        self.chat_empty_tip_label = QLabel()
        self.chat_empty_tip_label.setObjectName("chatEmptyTipText")
        self.chat_empty_tip_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.chat_empty_tip_label.setWordWrap(True)

        self.chat_display_layout.addWidget(
            self.chat_empty_tip_label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        # 这个弹簧始终放在最后，后面的消息插入到它前面
        self.chat_display_layout.addStretch(1)

        self.chat_scroll_area.setWidget(self.chat_display_panel)
        chat_layout.addWidget(self.chat_scroll_area, 1)

        # =====================================================
        # 模型信息和工具按钮
        # =====================================================
        model_row = QWidget()
        model_row.setObjectName("modelRow")
        model_layout = QHBoxLayout(model_row)
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.setSpacing(7)
        model_frame = QFrame()
        model_frame.setObjectName("modelFrame")
        model_frame_layout = QHBoxLayout(model_frame)
        model_frame_layout.setContentsMargins(10, 5, 10, 5)
        model_frame_layout.setSpacing(8)
        engine_label = QLabel("MODEL")
        engine_label.setObjectName("smallLabel")
        model_frame_layout.addWidget(engine_label)
        self.model_name = QComboBox()
        self.model_name.setObjectName("modelSelector")
        self.model_name.setMinimumSize(200, 32)

        self.model_name.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )
        for model_name, description in self.external_model_name_dict.items():
            display_text = "  "+ f"{model_name}" + \
                "             " + f"{description}"
            self.model_name.addItem(display_text, model_name)
        model_frame_layout.addWidget(self.model_name)

        model_layout.addWidget(model_frame, 0)

        # 根据外部传入的模型名称，设置下拉框的默认选中项
        target_model = self.external_model_name
        idx = self.model_name.findData(target_model)
        if idx >= 0:
            self.model_name.setCurrentIndex(idx)
        else:
            # 找不到，默认选第0项
            self.model_name.setCurrentIndex(0)

        action_names = [
            "\U0001F3A4",
            "Upload docx",
            "Upload pdf",
            "Upload txt",
        ]
        self.action_buttons = []
        for text in action_names:
            button = QPushButton(text)
            button.setObjectName("actionButton")
            button.setFixedHeight(42)
            button.setFixedWidth(200)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            model_layout.addWidget(button)
            self.action_buttons.append(button)
        chat_layout.addWidget(model_row)

        # =====================================================
        # 输入区域
        # =====================================================
        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(10)

        self.input_box = QTextEdit()
        self.input_box.setObjectName("inputBox")
        self.input_box.setPlaceholderText(
            "Describe the procedure, constraints, "
            "and expected result..."
        )
        self.input_box.setFixedHeight(100)

        input_row.addWidget(self.input_box, 1)

        send_column = QVBoxLayout()
        send_column.setSpacing(8)
        send_column.addStretch()

        self.run_button = QPushButton("Send")
        self.run_button.setObjectName("sendButton")
        self.run_button.setFixedSize(96, 96)
        send_column.addWidget(self.run_button)

        send_column.addStretch()
        input_row.addLayout(send_column)

        chat_layout.addLayout(input_row)

        right_layout.addWidget(chat_area, 1)

        self.body_splitter.addWidget(self.right_area)

        # 左侧约 240 像素，右侧自动填充
        self.body_splitter.setSizes([242, 1198])
        self.body_splitter.setStretchFactor(0, 0)
        self.body_splitter.setStretchFactor(1, 1)

        self.root_layout.addWidget(self.body_splitter, 1)

    # =========================================================
    # 设置调色板
    # =========================================================
    def setup_palette(self):
        QApplication.setStyle("Fusion")

        palette = QPalette()

        palette.setColor(
            QPalette.ColorRole.Window,
            QColor("#101315"),
        )
        palette.setColor(
            QPalette.ColorRole.WindowText,
            QColor("#e8eeee"),
        )
        palette.setColor(
            QPalette.ColorRole.Base,
            QColor("#1a2224"),
        )
        palette.setColor(
            QPalette.ColorRole.AlternateBase,
            QColor("#222c2e"),
        )
        palette.setColor(
            QPalette.ColorRole.Text,
            QColor("#e8eeee"),
        )
        palette.setColor(
            QPalette.ColorRole.Button,
            QColor("#222b2d"),
        )
        palette.setColor(
            QPalette.ColorRole.ButtonText,
            QColor("#e8eeee"),
        )
        palette.setColor(
            QPalette.ColorRole.Highlight,
            QColor("#1fa889"),
        )
        palette.setColor(
            QPalette.ColorRole.HighlightedText,
            QColor("#ffffff"),
        )

        self.setPalette(palette)

    def apply_dark_title_bar(self):
        """
        将 Windows 原生标题栏设置为深色。
        仅 Windows 生效，其他系统直接跳过。
        """
        if sys.platform != "win32":
            return None

        try:
            hwnd = wintypes.HWND(int(self.winId()))

            # Windows 10 1809+ / Windows 11
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_CAPTION_COLOR = 35
            DWMWA_TEXT_COLOR = 36

            dwmapi = ctypes.windll.dwmapi

            # 开启深色标题栏
            dark_mode = ctypes.c_int(1)

            dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(dark_mode),
                ctypes.sizeof(dark_mode),
            )

            # 标题栏背景颜色
            caption_color = ctypes.c_uint32(
                self.colorref("#0b0e10")
            )

            dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR,
                ctypes.byref(caption_color),
                ctypes.sizeof(caption_color),
            )

            # 标题文字颜色
            text_color = ctypes.c_uint32(
                self.colorref("#e8eeee")
            )

            dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_TEXT_COLOR,
                ctypes.byref(text_color),
                ctypes.sizeof(text_color),
            )

        except Exception as error:
            print(f"设置 Windows 标题栏颜色失败：{error}")

    @staticmethod
    def colorref(color: str) -> int:
        """
        将 #RRGGBB 转换成 Windows COLORREF 格式。
        Windows 使用 0x00BBGGRR 顺序。
        """
        color = color.lstrip("#")

        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)

        return red | (green << 8) | (blue << 16)

    # =========================================================
    # 样式表
    # =========================================================
    def setup_stylesheet(self):
        self.setStyleSheet(WINDOW_STYLE)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())