import sys
import threading
import pickle
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow
from gui_for_client_pages import Ui_MainWindow
import socket


class GameClient(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.isConnected = True

    def start(self):
        threading.Thread(target=self.receive_messages).start()

    def send_message(self, message):
        try:
            self.sock.send(pickle.dumps(message))
        except (ConnectionError, OSError):
            print("Ошибка при отправке сообщения.")

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
        self.lineEdit.editingFinished.connect(self.send_name)
        self.lineEdit_2.editingFinished.connect(self.send_room)
        self.lineEdit_3.editingFinished.connect(self.send_chat_message)

        self.pushButton.clicked.connect(self.send_name)
        self.pushButton_2.clicked.connect(self.send_room)
        self.pushButton_3.clicked.connect(self.create_room)
        self.pushButton_4.clicked.connect(self.send_chat_message)
        self.pushButton_5.clicked.connect(self.change_room)
        self.pushButton_6.clicked.connect(self.exit_app)
        self.pushButton_7.clicked.connect(self.ban_player)

    def send_name(self):
        name = self.lineEdit.text()
        if name:
            self.client.send_message(name)
            self.lineEdit.clear()
            self.stackedWidget.setCurrentIndex(1)

    def send_room(self):
        room_name = self.lineEdit_2.text()
        if room_name:
            self.client.send_message(room_name)
            self.lineEdit_2.clear()
            self.textEdit_3.clear()
            self.stackedWidget.setCurrentIndex(2)

    def create_room(self):
        self.client.send_message("new")
        room_name = self.lineEdit_2.text()
        if room_name:
            self.client.send_message(room_name)
            self.lineEdit_2.clear()
            self.textEdit_3.clear()
            self.stackedWidget.setCurrentIndex(2)

    def send_chat_message(self):
        message = self.lineEdit_3.text()
        if message:
            self.client.send_message(message)
            self.lineEdit_3.clear()

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
            # self.textEdit_2.clear()
            self.stackedWidget.setCurrentIndex(1)
        elif "Вы были забанены." == message:
            self.close()

        current_page_index = self.stackedWidget.currentIndex()

        if current_page_index == 0:
            print(message)
            self.textEdit.append(message)
        elif current_page_index == 1:
            self.textEdit_2.append(message)
        elif current_page_index == 2:
            self.textEdit_3.append(message)


def main():
    app = QApplication(sys.argv)

    host = '127.0.0.1'
    port = 3435
    client = GameClient(host, port)
    client.start()

    main_window = MainWindow(client)
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()
