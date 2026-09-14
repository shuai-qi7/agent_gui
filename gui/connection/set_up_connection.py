from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QScrollArea, QTextEdit, QPushButton, QListWidget
from typing import Optional

class Setup_Connection:
    # 类型提示
    chat_empty_tip_label: Optional[QLabel]
    chat_display_layout: QVBoxLayout
    chat_scroll_area: QScrollArea
    input_box: QTextEdit
    run_button: QPushButton
    conversations: QListWidget
    is_thinking: bool
    current_thinking_widget: Optional[QWidget] 
    new_session_button: QPushButton

    def send_message(self) -> None: ...
    def on_new_session_clicked(self) -> None: ...
    def on_sidebar_item_click(self, item: QListWidgetItem) -> None: ...
    
    def set_up_connection(self):
        self.run_button.clicked.connect(self.send_message)
        # 在 setup_ui 里面，创建完 self.new_session_button 之后添加：
        self.new_session_button.clicked.connect(self.on_new_session_clicked)
        # 绑定左侧列表点击事件
        self.conversations.itemClicked.connect(self.on_sidebar_item_click)