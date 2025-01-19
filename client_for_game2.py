import threading
import pickle
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow
from game_window import Ui_MainWindow
from choose_room_window import Ui_RoomWindow
from registration import Ui_Registration
from room_is_not_free_window import Ui_RoomIsNotFree
from banned_window import Ui_BannedWindow
import socket
from queue import Queue


class Communication(QObject):
    message_received = pyqtSignal(str)
    free_rooms_updater = pyqtSignal(list)
    start_game = pyqtSignal(str)
    end_game = pyqtSignal()
    room_free = pyqtSignal()
    room_not_free = pyqtSignal()
    your_turn = pyqtSignal(str)
    try_again = pyqtSignal(str)
    banned = pyqtSignal(str)


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
                    case 'banned':
                        self.comm.banned.emit(data['data'])
                    case 'start_game':
                        self.comm.start_game.emit(data['data'])
                    case 'room_free':
                        self.comm.room_free.emit()
                    case 'room_not_free':
                        self.comm.room_not_free.emit()
                    case 'end_game':
                        self.comm.end_game.emit()
                    case 'your_turn':
                        self.comm.your_turn.emit(data['data'])
                    case 'try_again':
                        self.comm.try_again.emit(data['data'])

            except (ConnectionError, OSError):
                print("Вы были отключены от сервера.")
                self.isConnected = False
                self.sock.close()
                break

class Registration(QMainWindow, Ui_Registration):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.room = None
        self.setupUi(self)
        self.comm = Communication()
        self.client = GameClient('127.0.0.1', 3434, self.comm)

        self.reg_input.setPlaceholderText("Введите свое имя...")
        self.setWindowTitle("Регистрация игрока")

        self.send_name_button.clicked.connect(self.send)
        self.comm.free_rooms_updater.connect(self.get_rooms)
        self.show()

    @pyqtSlot()
    def send(self):
        name = self.reg_input.text()
        self.name = name
        self.client.send_message(dict(data=name,
                                      msgtype='name'))
        self.reg_input.clear()
        self.hide()

    @pyqtSlot(list)
    def get_rooms(self, rooms):
        self.room = Room(self, self.name, self.comm, self.client, rooms)

class Room(QMainWindow, Ui_RoomWindow):
    def __init__(self, reg_window, name: str, comm: Communication, client, rooms):
        super().__init__()
        self.name = name
        self.comm = comm
        self.client = client
        self.rooms = rooms
        self.reg_window = reg_window
        self.game = None
        self.not_free = None
        self.setupUi(self)
        self.setWindowTitle(name)
        self.list_of_rooms.addItems(rooms)
        self.room = ''
        self.show()
        self.button_send.clicked.connect(self.game_start)
        self.comm.room_not_free.connect(self.room_not_free_window)
        self.comm.room_free.connect(self.room_free_window)

    def game_start(self):
        self.room = self.list_of_rooms.currentText()
        self.client.send_message(dict(data=self.room,
                                      msgtype='room'))
        self.hide()

    @pyqtSlot()
    def room_free_window(self):
        self.game = MainWindow(self.reg_window, self, self.comm, self.client, self.name, self.room)

    @pyqtSlot()
    def room_not_free_window(self):
        self.not_free = UiRoomIsNotFree(self)

class UiRoomIsNotFree(QMainWindow, Ui_RoomIsNotFree):
    def __init__(self, room_window):
        super().__init__()
        self.room_window = room_window
        self.setupUi(self)

        self.button_send.clicked.connect(self.return_to_change_room)

        self.show()

    def return_to_change_room(self):
        self.hide()
        self.room_window.show()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, reg_window, choose_room_window, comm, client, name, room):
        super().__init__()
        self.reg_window = reg_window
        self.choose_room_window = choose_room_window
        self.client = client
        self.client_name = name
        self.comm = comm
        self.room = room
        self.ban_window = None
        self.setupUi(self)

        self.send.setEnabled(False)
        self.ban_button.setEnabled(False)

        self.setWindowTitle(self.room)

        self.comm.message_received.connect(self.chat_update)
        self.comm.start_game.connect(self.start_game)
        self.comm.end_game.connect(self.end_game)
        self.comm.your_turn.connect(self.make_move)
        self.comm.try_again.connect(self.try_again)
        self.comm.banned.connect(self.player_is_banned)

        self.send.clicked.connect(self.send_chat_message)
        self.change_button.clicked.connect(self.change_room)
        self.exit_button.clicked.connect(self.exit_app)
        self.ban_button.clicked.connect(self.ban_player)

        self.player_is_ready()

        self.show()

    def player_is_ready(self):
        self.client.send_message(dict(data='',
                                      msgtype='ready'))

    @pyqtSlot(str)
    def start_game(self, data):
        self.output.append(data)

    @pyqtSlot(str)
    def make_move(self, message):
        self.output.append(message)
        self.send.setEnabled(True)
        self.ban_button.setEnabled(True)

    @pyqtSlot(str)
    def try_again(self, message):
        self.output.append(message)
        self.send.setEnabled(True)
        self.ban_button.setEnabled(True)

    def send_chat_message(self):
        message = self.input.text()
        if message:
            self.client.send_message(dict(data=message,
                                          msgtype='city'))
            self.send.setEnabled(False)
            self.send.setEnabled(False)
            self.input.clear()

    def change_room(self):
        self.client.send_message(dict(data='',
                                      msgtype='change'))
        self.output.clear()
        self.hide()
        self.choose_room_window.show()

    @pyqtSlot(str)
    def player_is_banned(self):
        self.hide()
        self.ban_window = BannedWindow()

    def exit_app(self):
        self.client.send_message(dict(data='',
                                      msgtype='exit'))

    @pyqtSlot()
    def end_game(self):
        self.close()

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

class BannedWindow(QMainWindow, Ui_BannedWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.button_send.clicked.connect(self.exit)

        self.show()

    def exit(self):
        self.close()

def main():
    app = QApplication([])

    start_window = Registration()
    start_window.show()

    app.exec()


if __name__ == "__main__":
    main()
