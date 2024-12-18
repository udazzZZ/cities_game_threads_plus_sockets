import threading
import pickle
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow
from gui_for_game import Ui_MainWindow
import socket
from queue import Queue


class GameClient(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.isConnected = True
        self.queue = Queue()

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
        self.queue.put(pickle.dumps(message))

    def receive_messages(self):
        while self.isConnected:
            try:
                received_data = self.sock.recv(4096)
                if not received_data:
                    break
                message = pickle.loads(received_data)
                if isinstance(message, dict) and 'exit' in message and message['exit']:
                    self.message_received.emit("Отключение от сервера...")
                    self.isConnected = False
                    self.sock.close()
                    break

                self.message_received.emit(message)

            except (ConnectionError, OSError):
                print("Вы были отключены от сервера.")
                self.isConnected = False
                self.sock.close()
                break


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setupUi(self)

        self.setWindowTitle("Client")

        self.stackedWidget.setCurrentIndex(0)

        self.client.message_received.connect(self.display_message)
        self.input_0.editingFinished.connect(self.send_name)
        self.input_0.setPlaceholderText("Введите свое имя...")
        self.input_1.editingFinished.connect(self.send_room)
        self.input_2.editingFinished.connect(self.send_chat_message)

        self.send_0.clicked.connect(self.send_name)
        self.send_1.clicked.connect(self.send_room)
        self.new_1.clicked.connect(self.create_room)
        self.send_2.clicked.connect(self.send_chat_message)
        self.change.clicked.connect(self.change_room)
        self.exit.clicked.connect(self.exit_app)
        self.ban.clicked.connect(self.ban_player)

    def send_name(self):
        name = self.input_0.text()
        if name:
            self.client.send_message(name)
            self.setWindowTitle(name)
            self.input_0.clear()
            self.stackedWidget.setCurrentIndex(1)

    def send_room(self):
        room_name = self.input_1.text()
        if room_name:
            self.client.send_message(room_name)
            self.input_1.clear()
            self.output_1.clear()
            self.stackedWidget.setCurrentIndex(2)

    def create_room(self):
        self.client.send_message("new")
        room_name = self.input_1.text()
        if room_name:
            self.client.send_message(room_name)
            self.input_1.clear()
            self.output_1.clear()
            self.stackedWidget.setCurrentIndex(2)

    def send_chat_message(self):
        message = self.input_2.text()
        if message:
            self.client.send_message(message)
            self.input_2.clear()

    def change_room(self):
        self.client.send_message("change")
        self.stackedWidget.setCurrentIndex(1)

    def exit_app(self):
        self.client.send_message("exit")
        self.close()

    def ban_player(self):
        self.client.send_message("ban")

    def display_message(self, message):
        if "new" in message:
            self.stackedWidget.setCurrentIndex(1)
        elif "Вы были забанены." == message:
            self.close()

        current_page_index = self.stackedWidget.currentIndex()

        if current_page_index == 0:
            print(message)
            self.output_0.append(message)
        elif current_page_index == 1:
            self.output_1.append(message)
        elif current_page_index == 2:
            self.output_2.append(message)

    def closeEvent(self, event):
        self.client.sock.close()

def main():
    app = QApplication([])

    host = '127.0.0.1'
    port = 3435
    client = GameClient(host, port)

    main_window = MainWindow(client)
    main_window.show()
    client.start()
    main_window.setFixedSize(363, 482)

    app.exec()


if __name__ == "__main__":
    main()
