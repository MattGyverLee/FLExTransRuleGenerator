from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class WebBridge(QObject):
    message_received = pyqtSignal(str)

    @pyqtSlot(str)
    def receive_message(self, msg: str):
        self.message_received.emit(msg)
