import socket
import threading
import time
from threading import Thread, Condition, Lock
import pickle


class GameRoom:
    def __init__(self, free, name):
        self.is_free: bool = free
        self.name: str = name
        self.clients: list = []
        self.used_words: list = []
        self.admins: list = []
        self.clients_names: list = []
        self.lock: Lock = Lock()
        self.game_condition: Condition = Condition(self.lock)

    def get_clients_names(self):
        return ' '.join([i for i in self.clients_names])

    def broadcast(self, except_client, mes):
        for client in self.clients:
            if client != except_client:
                client.send(pickle.dumps(mes))


class GameServer:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.is_server_active: bool = True
        self.current_rooms_count: int = 0
        self.rooms: dict = {}
        self.TIMER: int = 15
        self.lock: Lock = Lock()
        self.banned_players: list = []

    def start(self):
        print("Ожидание подключения игроков...")
        while self.is_server_active:
            client_socket, client_address = self.socket.accept()
            print(f'Подключен {client_address}')
            Thread(target=self.recv_name, args=(client_socket,)).start()

    def recv_name(self, client_socket):
        client_socket.send(pickle.dumps("Введите свое имя."))
        received_name = client_socket.recv(1024)
        name = pickle.loads(received_name)
        self.change(client_socket, name)

    def get_free_rooms(self):
        free_rooms = []
        mes = '\n'
        for keys, room in self.rooms.items():
            if room.is_free:
                free_rooms.append(room.name)
                mes += f'Комната: {room.name}, клиенты: {room.get_clients_names()}\n'
        return free_rooms, mes

    def exit(self, room, player, opponent, name, opponent_name):
        room.broadcast(player, f"Игрок {name} покинул игру. "
                               f"Вы будете перенаправлены в меню смены комнаты.")
        print(f"{name} disconnected")
        del self.rooms[room.name]
        Thread(target=self.change, args=(opponent, opponent_name)).start()

    def ban(self, room, opponent, opponent_name):
        self.banned_players.append(opponent_name)
        opponent.send(pickle.dumps("Вы были забанены."))
        key_exit = {'exit': True}
        opponent.send(pickle.dumps(key_exit))
        opponent_idx = room.clients.index(opponent)
        room.clients.pop(opponent_idx)
        room.clients_names.pop(opponent_idx)
        room.used_words = []
        room.is_free = True
        Thread(target=self.start_game, args=(room, )).start()

    def change(self, client_socket, name):
        not_in_room = True
        while not_in_room:
            free_rooms_count, mes = self.get_free_rooms()

            try:
                client_socket.send(pickle.dumps(f'Доступные комнаты: {mes}'
                                                f'Выберите существующую комнату или создайте новую через команду new.'))
            except ConnectionError:
                print(f"Клиент {name} внезапно разорвал соединение.")
                break

            received_room = client_socket.recv(1024)
            room = pickle.loads(received_room).strip()

            if room in free_rooms_count and self.rooms[room].is_free:
                if name in self.banned_players:
                    client_socket.send(pickle.dumps("Вы были забанены на этом сервере, "
                                                    "поэтому не можете подключаться к существующим комнатам."))
                    continue

                with self.lock:
                    cur_room = self.rooms[room]
                    cur_room.clients.append(client_socket)
                    cur_room.clients_names.append(name)
                    client_socket.send(pickle.dumps(f"Вы подключились к комнате {room}"))
                    cur_room_idx = free_rooms_count.index(room)
                    free_rooms_count.pop(cur_room_idx)
                    cur_room.is_free = False

                not_in_room = False

            elif room == 'new':
                client_socket.send(pickle.dumps(f"Введите название комнаты: "))
                new_room_name = pickle.loads(client_socket.recv(1024))
                self.current_rooms_count += 1
                client_socket.send(pickle.dumps(f"Вы создали комнату {new_room_name}"))

                with self.lock:
                    self.rooms[new_room_name] = GameRoom(True, new_room_name)
                    cur_room = self.rooms[new_room_name]
                    cur_room.clients.append(client_socket)
                    cur_room.clients_names.append(name)
                    cur_room.admins.append(client_socket)

                client_socket.send(pickle.dumps(f"Ждем второго игрока..."))
                threading.Thread(target=self.start_game, args=(cur_room,)).start()

                not_in_room = False

            else:
                try:
                    client_socket.send(pickle.dumps("Комната не существует или уже занята."))
                except ConnectionError:
                    print(f"Клиент {name} внезапно разорвал соединение.")
                    break

    def start_game(self, cur_room):
        if cur_room.is_free:
            for client in cur_room.clients:
                client.send(pickle.dumps(f"Ожидание соперника..."))
        while cur_room.is_free:
            continue

        commands_message = ("Игра началась.\n"
                            "Список доступных команд: exit, change, ban.")
        for client in cur_room.clients:
            client.send(pickle.dumps(commands_message))

        turn = 0
        game_running = True

        while game_running:
            print('Игра идет.')
            cur_player = cur_room.clients[turn]
            cur_player_name = cur_room.clients_names[turn]
            opponent = cur_room.clients[(turn + 1) % 2]
            opponent_name = cur_room.clients_names[(turn + 1) % 2]

            while True:
                start_timer = time.time()
                cur_player.send(pickle.dumps("Вы ходите."))

                received_data = cur_player.recv(1024)
                data = pickle.loads(received_data).strip()

                if data == 'exit':
                    self.exit(cur_room, cur_player, opponent, cur_player_name, opponent_name)
                    game_running = False
                    break

                elif data == 'change':
                    del self.rooms[cur_room.name]
                    game_running = False
                    Thread(target=self.change, args=(cur_player, cur_player_name)).start()
                    Thread(target=self.change, args=(opponent, opponent_name)).start()
                    break

                elif data == 'ban':
                    if cur_player in cur_room.admins:
                        self.ban(cur_room, opponent, opponent_name)
                        game_running = False
                        break
                    else:
                        cur_player.send(pickle.dumps("Вы не можете забанить игрока, "
                                                     "так как не являетесь администратором. "
                                                     "Введите другую команду или город."))
                        continue

                else:
                    city = data

                    if city in cur_room.used_words:
                        cur_player.send(pickle.dumps("Такой город уже был. Попробуйте снова.\n"))
                        continue

                    if cur_room.used_words:
                        last_word = cur_room.used_words[-1]
                        if last_word[-1].lower() != city[0]:
                            cur_player.send(pickle.dumps(f"Город должен начинаться с буквы "
                                                         f"{last_word[-1].lower()}. "
                                                         f"Попробуйте снова."))
                            continue

                    end_timer = time.time()
                    if end_timer - start_timer > self.TIMER:
                        self.end_game(opponent, cur_player, cur_room, opponent_name, cur_player_name)
                        game_running = False
                        break

                    cur_room.used_words.append(city)
                    opponent.send(pickle.dumps(f"{cur_player_name}: {city}"))
                    turn = (turn + 1) % 2
                    break

    def end_game(self, winner, loser, room, winner_name, loser_name):
        winner.send(pickle.dumps("Вы выиграли! Игра окончена. "
                                 "Вы можете подключиться к новой игре."))
        loser.send(pickle.dumps("Вы не успели ввести город и проиграли. Игра окончена. "
                                "Вы можете подключиться к новой игре."))
        time.sleep(5)
        del self.rooms[room.name]
        Thread(target=self.change, args=(winner, winner_name)).start()
        Thread(target=self.change, args=(loser, loser_name)).start()


def main():
    game_server = GameServer('127.0.0.1', port=3435)
    game_server.start()


if __name__ == "__main__":
    main()
