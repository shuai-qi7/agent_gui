from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
    QTextBrowser,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QScrollArea, QTextEdit, QPushButton, QListWidget
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.task_runner import AgentWorker
from PySide6.QtCore import QThreadPool
from gui.connection.chat_store import (
    append_message,
    create_new_conversation,
    get_conversation_by_id,
    update_conversation_title,
)

class ChatUi_Connection:
    # 类型提示
    chat_empty_tip_label: Optional[QLabel]
    chat_display_layout: QVBoxLayout
    chat_scroll_area: QScrollArea
    input_box: QTextEdit
    run_button: QPushButton
    conversations: QListWidget
    is_thinking: bool
    current_thinking_widget: Optional[QWidget] 
    
    def remove_empty_tip(self):
        """第一次显示消息时，删除初始提示。"""
        if self.chat_empty_tip_label is not None:
            self.chat_empty_tip_label.deleteLater()
            self.chat_empty_tip_label = None

    def add_user_message(self, text: str):
        """向显示区添加一条用户消息。"""
        self.remove_empty_tip()

        # 每一条消息使用一个独立的横向容器
        message_row = QWidget()

        row_layout = QHBoxLayout(message_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        # 左侧增加弹簧，让用户消息靠右
        row_layout.addStretch(1)

        message_label = QLabel(text)
        message_label.setObjectName("userMessage")
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(650)

        # 允许鼠标选择并复制消息
        message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        row_layout.addWidget(message_label)

        user_avatar = QLabel("用户")
        user_avatar.setObjectName("userAvatar")
        user_avatar.setFixedSize(42, 42)
        user_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row_layout.addWidget(user_avatar)

        # count() - 1 表示插入到底部弹簧前面
        insert_position = self.chat_display_layout.count() - 1
        self.chat_display_layout.insertWidget(
            insert_position,
            message_row,
        )

        self.scroll_to_bottom()
    
    def add_ai_message(self, text: str):
        """添加一条支持 Markdown 的 AI 回复。"""
        self.remove_empty_tip()

        message_row = QWidget()
        message_row.setObjectName("aiMessageRow")
        message_row.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        row_layout = QHBoxLayout(message_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        # AI 头像
        ai_avatar = QLabel("AI")
        ai_avatar.setObjectName("aiAvatar")
        ai_avatar.setFixedSize(42, 42)
        ai_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row_layout.addWidget(
            ai_avatar,
            0,
            Qt.AlignmentFlag.AlignTop,
        )

        # 用 QWidget 包裹名称和消息，避免嵌套布局出现异常宽度分配
        content_widget = QWidget()
        content_widget.setObjectName("aiMessageContent")
        content_widget.setMaximumWidth(760)
        content_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)

        ai_name = QLabel("AI Agent")
        ai_name.setObjectName("aiName")
        content_layout.addWidget(ai_name)

        # Markdown 浏览器
        message_browser = QTextBrowser()
        message_browser.setObjectName("aiMessage")
        message_browser.setReadOnly(True)
        message_browser.setOpenExternalLinks(True)
        message_browser.setMarkdown(text)

        # 整个聊天区域负责滚动，消息内部不显示滚动条
        message_browser.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        message_browser.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        message_browser.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        # 不要再限制成 300~500px
        message_browser.setMinimumWidth(0)
        message_browser.setMaximumWidth(16777215)

        content_layout.addWidget(message_browser)

        # 内容区域最多 760px，并紧跟在头像右边
        row_layout.addWidget(
            content_widget,
            1,
            Qt.AlignmentFlag.AlignTop,
        )
        row_layout.addStretch(1)

        insert_position = self.chat_display_layout.count() - 1
        self.chat_display_layout.insertWidget(
            insert_position,
            message_row,
        )

        def adjust_message_height():
            # 按浏览器实际宽度重新计算 Markdown 文档高度
            document_width = max(100, message_browser.viewport().width())
            message_browser.document().setTextWidth(document_width)

            document_height = message_browser.document().size().height()

            # 额外空间用于边框、padding 和 QTextBrowser viewport
            message_browser.setFixedHeight(
                max(55, int(document_height) + 24)
            )

            message_row.adjustSize()
            self.scroll_to_bottom()

        # 等 Qt 完成宽度布局后再计算高度
        QTimer.singleShot(0, adjust_message_height)

    def finish_fake_reply(
        self,
        reply_text: str,
        thinking_widget: QWidget,
    ):
        """删除思考状态，然后显示模拟回复。"""
        thinking_widget.deleteLater()

        reply = (
            f"{reply_text}\n\n"
        )

        self.add_ai_message(reply)

    def send_message(self):
        """读取输入框内容，保存用户消息，并调用智能体。"""
        user_text = self.input_box.toPlainText().strip()

        if not user_text:
            return

        if self.is_thinking:
            return

        # 如果程序启动后还没有当前会话，自动创建一个
        if not self.current_conv_id:
            new_conv = create_new_conversation(title=user_text[:20])
            self.current_conv_id = new_conv["conv_id"]
            self.refresh_sidebar_conversation_list()

        # 先保存用户消息
        append_message(
            self.current_conv_id,
            "user",
            user_text,
        )

        self.is_thinking = True
        self.run_button.setEnabled(False)
        self.run_button.setText("思考中...")
        self.input_box.clear()

        # 更新右侧界面
        self.add_user_message(user_text)
        thinking_widget = self.add_ai_thinking()
        self.current_thinking_widget = thinking_widget

        worker = AgentWorker(user_text)
        worker.signals.agent_reply_signal.connect(self.on_agent_reply)
        QThreadPool.globalInstance().start(worker)
        if len(user_text) > 20:
            title = user_text[:20] + "..."
        else:
            title = user_text

        current_conv = get_conversation_by_id(self.current_conv_id)
        if current_conv and current_conv.get("title") == "Untitled experiment":
            update_conversation_title(self.current_conv_id, title)

    def on_agent_reply(self, reply_text: str):
        """接收 AI 回复，保存到当前会话并更新界面。"""
        tw = self.current_thinking_widget
        if tw is not None:
            tw.deleteLater()
            self.current_thinking_widget = None

        # 保存 AI 回复
        if self.current_conv_id:
            append_message(
                self.current_conv_id,
                "agent",
                reply_text,
            )

        # 显示 AI 回复
        self.add_ai_message(reply_text)

        self.is_thinking = False
        self.run_button.setEnabled(True)
        self.run_button.setText("Send")
        self.input_box.setFocus()

        # 刷新左侧列表，例如更新时间、标题等
        self.refresh_sidebar_conversation_list()

    def complete_send(
        self,
        reply_text: str,
        thinking_widget: QWidget,
    ):
        """agent任务执行完成，渲染回答，恢复UI按钮状态"""
        self.finish_fake_reply(reply_text, thinking_widget)
        self.is_thinking = False
        self.run_button.setEnabled(True)
        self.run_button.setText("Send")
        self.input_box.setFocus()

    def scroll_to_bottom(self):
        """在布局更新后自动滚动到最下面。"""
        def do_scroll():
            scroll_bar = self.chat_scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

        # 等待 Qt 完成布局计算后再滚动
        QTimer.singleShot(0, do_scroll)

    def add_ai_thinking(self):
        """添加 AI 思考状态，并返回这个状态控件。"""
        self.remove_empty_tip()

        thinking_widget = QWidget()
        thinking_widget.setObjectName("thinkingWidget")

        row_layout = QHBoxLayout(thinking_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        # AI 头像
        ai_avatar = QLabel("AI")
        ai_avatar.setObjectName("aiAvatar")
        ai_avatar.setFixedSize(42, 42)
        ai_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row_layout.addWidget(ai_avatar)

        # 右侧文字使用纵向布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)

        ai_name = QLabel("AI Agent")
        ai_name.setObjectName("aiName")
        content_layout.addWidget(ai_name)

        thinking_label = QLabel("思考中，预计需要几分钟...")
        thinking_label.setObjectName("thinkingLabel")
        content_layout.addWidget(thinking_label)

        row_layout.addLayout(content_layout)
        row_layout.addStretch(1)

        insert_position = self.chat_display_layout.count() - 1
        self.chat_display_layout.insertWidget(
            insert_position,
            thinking_widget,
        )

        self.scroll_to_bottom()

        # 返回控件，十秒后需要删除它
        return thinking_widget