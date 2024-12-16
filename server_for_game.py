import socket
import threading
import time
from threading import Thread, Condition, Lock
import pickle


class GameRoom:
    def __init__(self, free, number):
        self.is_free = free
        self.number = number
        self.clients = []
        self.used_words = []
        self.admins = []
        self.running = False
        self.clients_names = []
        self.lock = Lock()
        self.game_condition = Condition(self.lock)

    def get_clients_names(self):
        return ' '.join([i for i in self.clients_names])

class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.is_server_active = True
        self.socket = None
        self.users = []
        self.current_rooms_count = 0
        self.rooms = {}

    def launch(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Ожидание подключения игроков...")

        accept_thread = Thread(target=self.accept_incoming_connections)
        accept_thread.start()
        accept_thread.join()

    def accept_incoming_connections(self):
        while self.is_server_active:
            client_socket, client_address = self.socket.accept()
            print(f'Подключен {client_address}')
            self.users.append(client_socket)
            Thread(target=self.recv_name, args=(client_socket, ), daemon=True).start()

    def recv_name(self, client_socket):
        received_name = client_socket.recv(1024)
        name = pickle.loads(received_name)
        self.change(client_socket, name)

    def get_free_rooms(self):
        free_rooms = []
        mes = '\n'
        for keys, room in self.rooms.items():
            if room.is_free:
                free_rooms.append(str(room.number))
                mes += f'Комната номер: {room.number}, клиенты: {room.get_clients_names()}\n'
        return free_rooms, mes

    def exit(self, room, first_player, first_player_name, second_player, second_player_name):
        del self.rooms[room]
        first_player_sock_idx = self.users.index(first_player)
        self.users.pop(first_player_sock_idx)
        first_player.close()
        print(f"{first_player_name} disconnected")
        Thread(target=self.change, args=(second_player, second_player_name)).start()

    def ban(self, room, first_player, first_player_name, second_player):
        second_player.send(pickle.dumps("Вы были забанены."))
        key_exit = {'exit': True}
        second_player.send(pickle.dumps(key_exit))
        second_player_idx = self.rooms[room].clients.index(second_player)
        self.rooms[room].clients.pop(second_player_idx)
        self.rooms[room].clients_names.pop(second_player_idx)
        print(len(self.rooms[room].clients))
        second_player_sock_idx = self.users.index(second_player)
        self.users.pop(second_player_sock_idx)
        second_player.close()
        self.rooms[room].running = False
        self.rooms[room].used_words = []
        Thread(target=self.start_game, args=(room, first_player, True)).start()

    def change(self, client_socket, name):
        not_in_room = True
        while not_in_room:
            free_rooms_count, mes = self.get_free_rooms()

            try:
                client_socket.send(pickle.dumps(f'Доступные комнаты: {mes}'
                                                f'Выберите существующую комнату или создайте новую через команду new.'))
            except ConnectionError:
                print(f"Клиент {name} внезапно разорвал соединение.")
                not_in_room = False
                client_sock_idx = self.users.index(client_socket)
                self.users.pop(client_sock_idx)
                break

            received_room = client_socket.recv(1024)
            room = pickle.loads(received_room).strip()

            if room in free_rooms_count and not (len(self.rooms[room].clients) == 2):
                self.rooms[room].clients.append(client_socket)
                self.rooms[room].clients_names.append(name)
                client_socket.send(pickle.dumps(f"Вы подключились к комнате {room}"))
                cur_room_idx = free_rooms_count.index(room)
                free_rooms_count.pop(cur_room_idx)

                self.start_game(room, client_socket, False)

                not_in_room = False
            elif room == 'new':
                self.current_rooms_count += 1
                client_socket.send(pickle.dumps(f"Вы создали комнату {self.current_rooms_count}"))

                self.rooms[str(self.current_rooms_count)] = GameRoom(True,
                                                                     self.current_rooms_count)
                cur_room = self.rooms[str(self.current_rooms_count)]
                cur_room.clients.append(client_socket)
                cur_room.clients_names.append(name)
                cur_room.admins.append(client_socket)

                self.start_game(str(self.current_rooms_count), client_socket, True)

                not_in_room = False
            else:
                try:
                    client_socket.send(pickle.dumps("Комната не существует или уже занята."))
                except ConnectionError:
                    print(f"Клиент {name} внезапно разорвал соединение.")
                    not_in_room = False
                    client_sock_idx = self.users.index(client_socket)
                    self.users.pop(client_sock_idx)
                    break

    def start_game(self, room, first_player, turn):
        print(threading.active_count())
        while len(self.rooms[room].clients) == 1:
            first_player.send(pickle.dumps("Ждем второго игрока..."))
            time.sleep(5)
            continue

        commands_message = "Список доступных команд: exit, change, ban."
        first_player.send(pickle.dumps(commands_message))
        first_player_name = self.rooms[room].clients_names[self.rooms[room].clients.index(first_player)]
        print(self.rooms[room].clients)

        if turn:
            second_player = self.rooms[room].clients[1]
            second_player_name = self.rooms[room].clients_names[self.rooms[room].clients.index(second_player)]
            print(second_player_name)
            second_player.send(pickle.dumps("Игра началась. Вы ходите вторым."))
        else:
            second_player = self.rooms[room].clients[0]
            second_player_name = self.rooms[room].clients_names[self.rooms[room].clients.index(second_player)]
            print(second_player_name)
            second_player.send(pickle.dumps("Игра началась. Вы ходите первым."))

        self.rooms[room].running = True
        while self.rooms[room].running:
            print('Игра идет')
            if turn:
                start_timer = time.time()
                first_player.send(pickle.dumps("ты ходишь"))

                try:
                    received_city = first_player.recv(1024)
                    city = pickle.loads(received_city)
                    print(city)
                except (ConnectionError, OSError):
                    print(f"Клиент внезапно разорвал соединение.")
                    del self.rooms[room]
                    Thread(target=self.change, args=(second_player, second_player_name)).start()
                    break

                if city == 'exit':
                    self.exit(room, first_player, first_player_name, second_player, second_player_name)
                    break

                if city == 'change':
                    del self.rooms[room]
                    Thread(target=self.change, args=(first_player, first_player_name)).start()
                    Thread(target=self.change, args=(second_player, second_player_name)).start()
                    break

                if city == 'ban':
                    print(threading.active_count())
                    if first_player in self.rooms[room].admins:
                        self.ban(room, first_player, first_player_name, second_player)
                        break
                    else:
                        first_player.send(pickle.dumps("Вы не можете забанить игрока, "
                                                       "так как вы не являетесь администратором."))
                        continue

                if city in self.rooms[room].used_words:
                    first_player.send(pickle.dumps("Такой город уже был. Попробуйте снова.\n"))
                    continue

                if self.rooms[room].used_words:
                    last_word = self.rooms[room].used_words[-1]
                    if last_word[-1].lower() != city[0]:
                        first_player.send(pickle.dumps(f"Город должен начинаться с буквы "
                                                       f"{last_word[-1].lower()}. "
                                                       f"Попробуйте снова."))
                        continue

                end_timer = time.time()
                if end_timer - start_timer > 15:
                    self.end_game(second_player, first_player, room, second_player_name, first_player_name)
                    break

                self.rooms[room].used_words.append(city)
                opponent_name = self.rooms[room].clients_names[self.rooms[room].clients.index(first_player)]
                second_player.send(pickle.dumps(f"{opponent_name}: {city}"))
                turn = not turn
                with self.rooms[room].game_condition:
                    self.rooms[room].game_condition.notify_all()

            else:
                with self.rooms[room].game_condition:
                    first_player.send(pickle.dumps("жди очереди"))
                    self.rooms[room].game_condition.wait()
                    try:
                        first_player.send(pickle.dumps("теперь твоя очередь"))
                    except OSError:
                        break
                turn = not turn

    def end_game(self, winner, loser, room, winner_name, loser_name):
        winner.send(pickle.dumps("Вы выиграли! Игра окончена. Введите команду exit для выхода."))
        loser.send(pickle.dumps("Вы не успели ввести город и проиграли. Игра окончена. "
                                "Введите команду exit для выхода."))
        time.sleep(1)
        del self.rooms[room]
        Thread(target=self.change, args=(winner, winner_name)).start()
        Thread(target=self.change, args=(loser, loser_name)).start()


def main():
    game_server = GameServer('127.0.0.1', port=3453)
    game_server.launch()


if __name__ == "__main__":
    main()
