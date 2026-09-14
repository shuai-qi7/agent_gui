from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

class AspectRatioLabel(QLabel):
    def __init__(self, pixmap_path: str, parent=None):
        super().__init__(parent)

        self.original_pixmap = QPixmap(pixmap_path)
        self._updating = False

        self.setAlignment(Qt.AlignmentFlag.AlignTop |
                          Qt.AlignmentFlag.AlignHCenter)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        self.update_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        if self.original_pixmap.isNull():
            return

        if self.width() <= 0:
            return

        # 防止 setFixedHeight 触发 resizeEvent 后重复更新
        if self._updating:
            return

        self._updating = True

        scaled_pixmap = self.original_pixmap.scaled(
            self.width(),
            self.original_pixmap.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)

        if self.height() != scaled_pixmap.height():
            self.setFixedHeight(scaled_pixmap.height())

        self._updating = False