from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from typing import Optional

from gui.connection.chat_store import (
    load_all_conversations,
    create_new_conversation,
    get_conversation_by_id,
    append_message,
)

class SessionUi_Connection:

    def add_session_item(
        self,
        list_index: int,
        conv_id: str,
        session_name: str,
        session_time: str,
    ):
        """创建左侧会话列表项，并把 conv_id 保存到 item 中。"""

        item = QListWidgetItem()

        # 关键：保存当前会话 ID，点击时通过这个 ID 找回历史记录
        item.setData(Qt.ItemDataRole.UserRole, conv_id)

        self.conversations.addItem(item)

        item_widget = QWidget()
        item_widget.setObjectName("sessionItem")

        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(10, 8, 8, 8)
        item_layout.setSpacing(4)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        number_label = QLabel(str(list_index + 1))
        number_label.setObjectName("sessionNumber")
        number_label.setFixedWidth(22)
        header_layout.addWidget(number_label)

        name_label = QLabel(session_name)
        name_label.setObjectName("sessionName")
        header_layout.addWidget(name_label, 1)

        time_label = QLabel(session_time)
        time_label.setObjectName("sessionTime")
        header_layout.addWidget(time_label)

        item_layout.addLayout(header_layout)

        state_label = QLabel(
            "当前对话" if conv_id == self.current_conv_id else "Saved session"
        )
        state_label.setObjectName("sessionState")
        item_layout.addWidget(state_label)

        item.setSizeHint(item_widget.sizeHint())
        self.conversations.setItemWidget(item, item_widget)

    def refresh_sidebar_conversation_list(self):
        """从 JSON 重新读取并刷新左侧会话列表。"""
        self.conversations.clear()
        self.local_conversations = load_all_conversations()

        for index, conv in enumerate(self.local_conversations):
            self.add_session_item(
                list_index=index,
                conv_id=conv["conv_id"],
                session_name=conv.get("title", "Untitled experiment"),
                session_time=conv.get("create_time", ""),
            )

    def on_new_session_clicked(self):
        """新建会话：保存新会话、切换当前 ID、清空右侧窗口。"""
        # 如果当前正在思考，不建议切换会话
        if self.is_thinking:
            return

        new_conv = create_new_conversation(title="Untitled experiment")
        self.current_conv_id = new_conv["conv_id"]

        self.refresh_sidebar_conversation_list()
        self.clear_chat_display()
        self.input_box.clear()
        self.input_box.setFocus()

        # 让新会话在左侧自动选中
        for row in range(self.conversations.count()):
            item = self.conversations.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == self.current_conv_id:
                self.conversations.setCurrentRow(row)
                break

    def clear_chat_display(self):
        """删除右侧聊天消息，但保留初始提示和底部弹簧。"""
        # 当前布局最后一个通常是 stretch，倒数第二个是初始提示。
        # 这里保留所有非消息控件的简单做法是：删除布局中的所有控件，重新创建。
        while self.chat_display_layout.count():
            item = self.chat_display_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        # 重新创建空提示
        self.chat_empty_tip_label = QLabel("新建一个对话，开始聊天")
        self.chat_empty_tip_label.setObjectName("chatEmptyTipText")
        self.chat_empty_tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chat_empty_tip_label.setWordWrap(True)
        self.chat_display_layout.addWidget(
            self.chat_empty_tip_label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        # 重新添加底部弹簧
        self.chat_display_layout.addStretch(1)

    def on_sidebar_item_click(self):
        """点击左侧历史会话，加载其消息。"""
        selected_item = self.conversations.currentItem()
        if selected_item is None:
            return

        conv_id = selected_item.data(Qt.ItemDataRole.UserRole)
        if not conv_id:
            return

        conv_data = get_conversation_by_id(conv_id)
        if conv_data is None:
            return

        self.current_conv_id = conv_id
        self.load_messages_to_ui(conv_data.get("messages", []))

    def load_messages_to_ui(self, msg_list: list):
        """把历史消息重新渲染到右侧聊天区域。"""
        self.clear_chat_display()

        for msg in msg_list:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "user":
                self.add_user_message(content)
            elif role in ("agent", "assistant"):
                self.add_ai_message(content)

        # 有历史消息时删除空提示
        if msg_list:
            self.remove_empty_tip()

        self.scroll_to_bottom()