import threading
import pickle
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow
from game_window import Ui_MainWindow
from choose_room_window import Ui_RoomWindow
from registration import Ui_Registration
import socket
from queue import Queue


class Communication(QObject):
    message_received = pyqtSignal(str)
    free_rooms_updater = pyqtSignal(list)
    start_game = pyqtSignal(str)
    end_game = pyqtSignal()


class GameClient(QObject):

    def __init__(self, host, port, comm):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.isConnected = True
        self.queue = Queue()
        self.comm = comm

        threading.Thread(target=self.receive_messages, daemon=True).start()
        threading.Thread(target=self.send_msg, daemon=True).start()

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

    def send_message(self, packet):
        self.queue.put(pickle.dumps(packet), block=False)

    def receive_messages(self):
        while self.isConnected:
            try:
                data_in_bytes = self.sock.recv(4096)
                if not data_in_bytes:
                    print(data_in_bytes)
                    break
                data = pickle.loads(data_in_bytes)
                print(data)

                match data['msgtype']:
                    case 'chat':
                        self.comm.message_received.emit(data['data'])
                    case 'free_rooms':
                        self.comm.free_rooms_updater.emit(data['data'])
                    case 'ban':
                        pass
                    case 'start_game':
                        self.comm.start_game.emit(data['data'])
                    case 'room_not_free':
                        print('комната какого-то хуя не свободна')
                    case 'end_game':
                        self.comm.end_game.emit()

            except (ConnectionError, OSError):
                print("Вы были отключены от сервера.")
                self.isConnected = False
                self.sock.close()
                break

class Registration(QMainWindow, Ui_Registration):
    def __init__(self):
        super().__init__()
        self.room = None
        self.setupUi(self)
        self.comm = Communication()
        self.client = GameClient('127.0.0.1', 3434, self.comm)

        self.reg_input.setPlaceholderText("Введите свое имя...")
        self.setWindowTitle("Регистрация игрока")

        self.send_name_button.clicked.connect(self.send)
        self.show()

    @pyqtSlot()
    def send(self):
        name = self.reg_input.text()
        self.client.send_message(dict(data=name,
                                      msgtype='name'))
        self.reg_input.clear()
        self.hide()

        self.room = Room(self, name, self.comm, self.client)

class Room(QMainWindow, Ui_RoomWindow):
    def __init__(self, reg_window, name: str, comm: Communication, client):
        super().__init__()
        self.name = name
        self.comm = comm
        self.client = client
        self.reg_window = reg_window
        self.game = None
        self.setupUi(self)
        self.setWindowTitle(name)
        self.list_of_rooms.addItems(['Room1', 'Room2', 'Room3'])
        self.room = ''
        self.show()
        self.button_send.clicked.connect(self.game_start)
        self.comm.free_rooms_updater.connect(self.update_rooms)

    def game_start(self):
        self.room = self.list_of_rooms.currentText()
        self.client.send_message(dict(data=self.room,
                                      msgtype='room'))
        self.hide()
        self.game = MainWindow(self.reg_window, self, self.comm, self.client, self.name, self.room)

    def update_rooms(self, rooms):
        self.list_of_rooms.clear()
        self.list_of_rooms.addItems(rooms)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, reg_window, choose_room_window, comm, client, name, room):
        super().__init__()
        self.reg_window = reg_window
        self.choose_room_window = choose_room_window
        self.client = client
        self.client_name = name
        self.comm = comm
        self.room = room
        self.setupUi(self)

        self.send.setEnabled(False)
        self.ban_button.setEnabled(False)

        self.setWindowTitle(self.room)

        self.comm.message_received.connect(self.chat_update)
        self.comm.start_game.connect(self.start_game)
        self.comm.end_game.connect(self.end_game)

        self.send.clicked.connect(self.send_chat_message)
        self.change_button.clicked.connect(self.change_room)
        self.exit_button.clicked.connect(self.exit_app)
        self.ban_button.clicked.connect(self.ban_player)

        self.show()

    @pyqtSlot(str)
    def start_game(self, data):
        self.output.append(data)
        self.send.setEnabled(True)
        self.ban_button.setEnabled(True)

    @pyqtSlot()
    def send_chat_message(self):
        message = self.input.text()
        if message:
            self.client.send_message(dict(data=message,
                                          msgtype='city'))
            self.input.clear()

    @pyqtSlot()
    def change_room(self):
        self.client.send_message(dict(data='',
                                      msgtype='change'))
        self.output.clear()
        self.hide()
        self.choose_room_window.show()

    @pyqtSlot()
    def exit_app(self):
        self.client.send_message(dict(data='',
                                      msgtype='exit'))

    @pyqtSlot()
    def end_game(self):
        self.close()

    @pyqtSlot()
    def ban_player(self):
        self.client.send_message(dict(data='',
                                      msgtype='ban'))

    @pyqtSlot(str)
    def chat_update(self, message):
        print(message)
        self.output.append(message)

    @pyqtSlot()
    def closeEvent(self, event):
        self.exit_app()

def main():
    app = QApplication([])

    start_window = Registration()
    start_window.show()

    app.exec()


if __name__ == "__main__":
    main()
