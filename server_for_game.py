import socket
from threading import Thread
import pickle

class GameRoom:
    def __init__(self, free, name):
        self.is_free: bool = free
        self.name: str = name
        self.clients: list = []
        self.ready_clients_count = 0
        self.used_words: list = []
        self.clients_names: list = []
        self.turn = 0
        self.is_active = False

    def broadcast(self, packet, except_client=None):
        for client in self.clients:
            if client != except_client:
                client.send(pickle.dumps(packet))

    def start_game(self):
        self.broadcast(dict(data="Игра началась.",
                            msgtype='start_game'))

    def exit_room(self, client, client_name, reason=None):
        client_idx = self.clients.index(client)
        self.clients.pop(client_idx)
        self.clients_names.pop(client_idx)
        self.used_words = []
        self.is_free = True
        self.ready_clients_count -= 1
        self.turn = 0
        if reason == 'ban':
            self.broadcast(dict(data=f"Игрок {client_name} был забанен.",
                                msgtype='chat'),
                           client)
            client.send(pickle.dumps(dict(data='Вы были забанены.',
                                          msgtype='banned')))
        else:
            self.broadcast(dict(data=f"Игрок {client_name} покинул игру.",
                                msgtype='chat'),
                           client)
        print(self.is_free)
        if len(self.clients) == 1:
            self.end_game(client)

    def end_game(self, loser):
        self.broadcast(dict(data="Вы выиграли! Игра окончена. "
                                 "Вы можете подключиться к новой игре "
                                 "или дождаться подключения нового клиента.",
                            msgtype='chat'),
                       loser)
        self.is_active = False


class GameServer:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.is_server_active: bool = True
        self.current_rooms_count: int = 0
        self.rooms = [GameRoom(True, 'Room1'),
                      GameRoom(True, 'Room2'),
                      GameRoom(True, 'Room3')]
        self.package_template = {'data': '', 'msgtype': ''}
        self.TIMER: int = 15

    def start(self):
        print("Ожидание подключения игроков...")
        while self.is_server_active:
            client_socket, client_address = self.socket.accept()
            print(f'Подключен {client_address}')
            client_handler_thread = ClientHandler(client_socket, self.rooms)

class ClientHandler(Thread):
    def __init__(self, client, rooms):
        super().__init__()
        self.client = client
        self.rooms = rooms
        self.room: GameRoom | None = None
        self.name = ''

        self.start()

    def run(self):
        while True:
            try:
                data_in_bytes = self.client.recv(1024)
                print('Данные получены')

                if not data_in_bytes:
                    break

                data = pickle.loads(data_in_bytes)

                match data['msgtype']:
                    case 'name':
                        self.name = data['data']
                        print('Имя получено')

                        free_rooms = self.get_free_rooms()
                        free_rooms_names = []
                        for room in free_rooms:
                            free_rooms_names.append(room.name)
                        print(free_rooms_names)
                        self.client.send(pickle.dumps(dict(data=free_rooms_names,
                                                           msgtype='free_rooms')))
                    case 'room':
                        print(f'Комната получена')
                        self.join_room(data['data'])
                    case 'ready':
                        self.room.ready_clients_count += 1
                        if self.room.ready_clients_count == 2:
                            self.room.is_free = False
                            self.room.is_active = True
                            self.room.start_game()
                            print('Начинаем игру')
                            self.room.clients[self.room.turn].send(pickle.dumps(dict(data='Ваша очередь ходить.',
                                                                                     msgtype='your_turn')))
                    case 'city':
                        city = data['data'].strip().lower()
                        if self.is_city_valid(city):
                            self.room.used_words.append(city)
                            self.client.send(pickle.dumps(dict(data=f'Вы: {city}.',
                                                               msgtype='chat')))
                            self.room.broadcast(dict(data=f"{self.name}: {city}",
                                                     msgtype='chat'),
                                                self.client)
                            self.change_turn()
                    case 'ban':
                        client_idx = self.room.clients.index(self.client)
                        opponent_idx = (client_idx + 1) % 2
                        opponent = self.room.clients[opponent_idx]
                        opponent_name = self.room.clients_names[opponent_idx]
                        self.room.exit_room(opponent, opponent_name, 'ban')
                        print('banned')
                    case 'change':
                        print('Смена комнаты')
                        self.room.exit_room(self.client, self.name)
                    case 'exit':
                        self.exit_game(self.room, self.client, self.name)
            except (ConnectionError, OSError):
                print("Игрок отключился.")
                break

    def change_turn(self):
        self.room.turn = (self.room.turn + 1) % 2
        self.room.clients[self.room.turn].send(pickle.dumps(dict(data='Ваша очередь ходить.',
                                                       msgtype='your_turn')))

    def get_free_rooms(self):
        free_rooms = []
        rooms = self.rooms
        for room in rooms:
            if room.is_free:
                free_rooms.append(room)

        return free_rooms

    def exit_game(self, room, player, name):
        packet = dict(data=f"Игрок {name} покинул игру. ",
                      msgtype='chat')
        room.broadcast(packet, player)
        print(f"{name} disconnected")
        cur_player_idx = room.clients.index(player)
        room.clients.pop(cur_player_idx)
        room.clients_names.pop(cur_player_idx)
        room.is_free = True
        room.used_words = []
        room.ready_clients_count -= 1
        room.turn = 0
        room.end_game(player)
        self.client.send(pickle.dumps(dict(data='',
                                           msgtype='end_game')))

    def ban(self, room, opponent, opponent_name):
        pass

    def join_room(self, room_name):
        for room in self.rooms:
            print(room.is_free)
            if room.name == room_name and room.is_free:
                print('Игрок подключился к комнате')
                self.room = room
                room.clients.append(self.client)
                room.clients_names.append(self.name)
                room.broadcast(dict(data=f'Игрок {self.name} присоединился к комнате.',
                                    msgtype='chat'),
                               self.client)
                self.client.send(pickle.dumps(dict(data='',
                                                   msgtype='room_free')))
                break
        else:
            self.client.send(pickle.dumps(dict(data='',
                                               msgtype='room_not_free')))

    def is_city_valid(self, city):
        if city in self.room.used_words:
            packet = dict(data="Такой город уже был. Попробуйте снова.\n",
                          msgtype='try_again')
            self.client.send(pickle.dumps(packet))
            return False

        if self.room.used_words:
            last_word = self.room.used_words[-1]
            if last_word[-1].lower() != city[0]:
                packet = dict(data=f"Город должен начинаться с буквы "
                                   f"{last_word[-1].lower()}. "
                                   f"Попробуйте снова.",
                              msgtype='try_again')
                self.client.send(pickle.dumps(packet))
                return False

        return True


def main():
    game_server = GameServer('127.0.0.1', port=3434)
    game_server.start()


if __name__ == "__main__":
    main()
