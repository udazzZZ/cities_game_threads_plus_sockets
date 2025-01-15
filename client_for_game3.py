import threading
import pickle
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton
from gui_for_game import Ui_MainWindow
import socket
from queue import Queue


class Communication(QObject):
    message_received = pyqtSignal(str)


class GameClient(QObject):

    def __init__(self, host, port, comm):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.isConnected = True
        self.queue = Queue()
        self.comm = comm

    def start(self):
        threading.Thread(target=self.receive_messages).start()
        threading.Thread(target=self.send_msg).start()

    def send_msg(self):
        while self.isConnected:
            try:
                msg = self.queue.get(block=True)
                self.sock.send(msg)
            except (ConnectionError, OSError):
                print("Вы были отключены от сервера.")
                self.isConnected = False
                self.sock.close()
                break

    def send_message(self, message):
        self.queue.put(pickle.dumps(message), block=False)

    def receive_messages(self):
        while self.isConnected:
            try:
                received_data = self.sock.recv(4096)
                if not received_data:
                    break
                message = pickle.loads(received_data)
                print(message)
                if isinstance(message, dict) and 'exit' in message and message['exit']:
                    self.comm.message_received.emit("Отключение от сервера...")
                    self.isConnected = False
                    self.sock.close()
                    break

                self.comm.message_received.emit(message)

            except (ConnectionError, OSError):
                print("Вы были отключены от сервера.")
                self.isConnected = False
                self.sock.close()
                break

class StartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game_room_with_chat = None
        self.comm = Communication()
        self.client = GameClient('127.0.0.1', 3435, self.comm)
        self.client.start()

        self.setGeometry(300, 300, 0, 0)
        #
        layout = QVBoxLayout()
        self.input_room = QLineEdit()
        self.input_room.setPlaceholderText("Введите свое имя...")
        send = QPushButton('send')
        layout.addWidget(self.input_room)
        layout.addWidget(send)
        self.setLayout(layout)
        #
        send.clicked.connect(self.send)
        self.show()

    @pyqtSlot()
    def send(self):
        name = self.input_room.text()
        self.client.send_message(name)
        self.input_room.clear()
        self.hide()

        self.game_room_with_chat = MainWindow(self, self.client, name)
        self.game_room_with_chat.setFixedSize(363, 482)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, start_window, client, name):
        super().__init__()
        self.start_window = start_window
        self.client = client
        self.client_name = name
        self.setupUi(self)

        self.setWindowTitle(name)

        self.stackedWidget.setCurrentIndex(1)

        self.client.comm.message_received.connect(self.display_message)
        self.input_1.editingFinished.connect(self.send_room)
        self.input_2.editingFinished.connect(self.send_chat_message)
        self.send_1.clicked.connect(self.send_room)
        self.new_1.clicked.connect(self.create_room)
        self.send_2.clicked.connect(self.send_chat_message)
        self.change.clicked.connect(self.change_room)
        self.exit.clicked.connect(self.exit_app)
        self.ban.clicked.connect(self.ban_player)

        self.show()

    @pyqtSlot()
    def send_room(self):
        room_name = self.input_1.text()
        if room_name:
            self.client.send_message(room_name)
            self.input_1.clear()
            self.stackedWidget.setCurrentIndex(2)

    @pyqtSlot()
    def create_room(self):
        self.client.send_message("new")
        room_name = self.input_1.text()
        if room_name:
            self.client.send_message(room_name)
            self.input_1.clear()
            self.stackedWidget.setCurrentIndex(2)

    @pyqtSlot()
    def send_chat_message(self):
        message = self.input_2.text()
        if message:
            self.client.send_message(message)
            self.input_2.clear()

    @pyqtSlot()
    def change_room(self):
        self.client.send_message("change")
        self.stackedWidget.setCurrentIndex(1)

    @pyqtSlot()
    def exit_app(self):
        self.client.send_message("exit")
        self.close()

    @pyqtSlot()
    def ban_player(self):
        self.client.send_message("ban")

    @pyqtSlot(str)
    def display_message(self, message):

        current_page_index = self.stackedWidget.currentIndex()

        if current_page_index == 1:
            self.output_1.append(message)
        elif current_page_index == 2:
            self.output_2.append(message)

    @pyqtSlot()
    def closeEvent(self, event):
        self.client.sock.close()

def main():
    app = QApplication([])

    host = '127.0.0.1'
    port = 3435

    start_window = StartWidget()
    start_window.show()

    app.exec()


if __name__ == "__main__":
    main()
