import socket
import time
from threading import Thread, Timer, Condition, Lock


class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.is_server_active = True
        self.socket = None
        self.users = []
        self.names = []
        self.current_rooms_count = 0
        self.rooms = {}
        self.threads = {}

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
            name = client_socket.recv(1024).decode('UTF-8')
            self.names.append(name)

            unconnected = True
            while unconnected:
                free_rooms_count = []

                for room_number in self.rooms.keys():
                    if self.rooms[room_number]['free']:
                        free_rooms_count.append(room_number)

                client_socket.send(('Выберите комнату или создайте новую (new)\n'
                                    'Доступные комнаты: ' + ', '.join(free_rooms_count)).encode('UTF-8'))
                room = client_socket.recv(1024).decode('UTF-8').strip()

                if room in free_rooms_count and not (len(self.rooms[room]['clients']) == 2):
                    self.rooms[room]['clients'].append(client_socket)

                    thread = Thread(target=self.start_game, args=(room,
                                                                  client_socket,
                                                                  False,
                                                                  self.rooms[room]['condition']))
                    self.threads[client_socket] = thread
                    thread.start()

                    unconnected = False
                elif room == 'new':
                    self.current_rooms_count += 1
                    lock = Lock()
                    game_start_condition = Condition(lock)

                    self.rooms[str(self.current_rooms_count)] = {'free': True,
                                                                 'clients': [client_socket],
                                                                 'used_words': [],
                                                                 'condition': game_start_condition}

                    thread = Thread(target=self.start_game, args=(str(self.current_rooms_count),
                                                                  client_socket,
                                                                  True,
                                                                  game_start_condition))
                    self.threads[client_socket] = thread
                    thread.start()

                    unconnected = False
                else:
                    client_socket.send('Комната не существует или уже занята.'.encode('UTF-8'))

    def start_game(self, room, first_player, turn, condition):
        while len(self.rooms[room]['clients']) == 1:
            continue

        if turn:
            second_player = self.rooms[room]['clients'][1]
        else:
            second_player = self.rooms[room]['clients'][0]

        while self.is_server_active and len(self.rooms[room]['clients']) == 2:
            self.rooms[room]['running'] = True
            while self.rooms[room]['running']:
                if turn:
                    timer = Timer(10.0, self.end_game, (first_player, second_player, room))
                    timer.start()

                    first_player.send("Введите город: ".encode())
                    city = first_player.recv(1024).decode('UTF-8').strip()

                    if city == 'exit':
                        first_player.close()
                        break

                    if city in self.rooms[room]['used_words']:
                        first_player.send("Такой город уже был. Попробуйте снова.\n".encode())
                        continue

                    if self.rooms[room]['used_words'] and self.rooms[room]['used_words'][-1][-1].lower() != city[0]:
                        first_player.send(f"Город должен начинаться с буквы '{self.rooms[room]['used_words'][-1][-1]}'. "
                                          f"Попробуйте снова.\n".encode())
                        continue

                    self.rooms[room]['used_words'].append(city)
                    turn = not turn
                    second_player.send(f"{self.names[self.users.index(first_player)]}: {city}".encode('UTF-8'))
                    with condition:
                        condition.notify()
                    timer.cancel()

                else:
                    with condition:
                        condition.wait()
                    turn = not turn

    def end_game(self, loser, winner, room):
        self.rooms[room]['running'] = False
        loser.send("Вы не успели ввести город и проиграли. Игра окончена.".encode('UTF-8'))
        winner.send("Вы выиграли! Игра окончена.".encode('UTF-8'))
        time.sleep(1)
        self.rooms[room]['clients'].pop(self.rooms[room]['clients'].index(loser))
        self.rooms[room]['clients'].pop(self.rooms[room]['clients'].index(winner))


def main():
    game_server = GameServer('127.0.0.1', port=49537)
    game_server.launch()


if __name__ == "__main__":
    main()
