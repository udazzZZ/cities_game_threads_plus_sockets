import socket
from threading import Thread, Condition, Lock
import pickle


class GameRoom:
    def __init__(self, free, name):
        self.is_free: bool = free
        self.name: str = name
        self.clients: list = []
        self.used_words: list = []
        self.clients_names: list = []
        self.lock: Lock = Lock()
        self.turn = 0
        self.is_active = False

    def get_clients_names(self):
        return ' '.join([i for i in self.clients_names])

    def broadcast(self, packet, except_client=None):
        for client in self.clients:
            if client != except_client:
                client.send(pickle.dumps(packet))

    def start_game(self):
        if self.is_active:
            self.broadcast(dict(data="Игра началась.",
                                msgtype='start_game'))
        self.clients[0].send(pickle.dumps(dict(data='',
                                               msgtype='start_game')))

    def exit_room(self, client, client_name, reason=None):
        self.broadcast(dict(data=f"Игрок {client_name} покинул игру.",
                            msgtype='chat'))
        if len(self.clients) < 2:
            self.end_game(client)

    def end_game(self, loser):
        self.broadcast(dict(data="Вы выиграли! Игра окончена. "
                                 "Вы можете подключиться к новой игре.",
                            msgtype='chat'),
                       loser)


class GameServer:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.is_server_active: bool = True
        self.current_rooms_count: int = 0
        self.rooms = {GameRoom(True, 'Room1'),
                      GameRoom(True, 'Room2'),
                      GameRoom(True, 'Room3')}
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
        self.room = None
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
                        self.client.send(pickle.dumps(dict(data=free_rooms_names,
                                                           msgtype='free_rooms')))
                    case 'room':
                        print(f'Комната получена')
                        self.join_room(data['data'])

                        if len(self.room.clients) == 2:
                            self.room.is_free = False
                            self.room.is_active = True
                            self.room.start_game()
                            print('Начинаем игру')
                    case 'city':
                        city = data['data'].strip().lower()
                        if self.is_city_valid(city):
                            self.room.used_words.append(city)
                            self.client.send(pickle.dumps(dict(data=f'Вы: {city}.',
                                                               msgtype='chat')))
                            self.room.broadcast(dict(data=f"{self.name}: {city}",
                                                     msgtype='chat'),
                                                self.client)
                    case 'ban':
                        pass
                    case 'change':
                        self.room.exit_room(self.client, self.name)
                    case 'exit':
                        self.exit_game(self.room, self.client, self.name)
                    case 'time_out':
                        self.room.remove_client(self, 'time_out')
            except (ConnectionError, OSError):
                print("Игрок отключился.")
                break

    def get_free_rooms(self):
        free_rooms = []
        rooms = self.rooms
        for room in rooms:
            if room.is_free:
                free_rooms.append(room)

        return free_rooms

    @staticmethod
    def exit_game(room, player, name):
        packet = dict(data=f"Игрок {name} покинул игру. "
                           f"Вы будете перенаправлены в меню смены комнаты.",
                      msgtype='chat')
        room.broadcast(packet, player)
        print(f"{name} disconnected")
        cur_player_idx = room.clients.index(player)
        room.clients.pop(cur_player_idx)
        room.clients_names.pop(cur_player_idx)
        room.is_free = True

    def ban(self, room, opponent, opponent_name):
        packet = dict(data="Вы были забанены.",
                      msgtype='ban')
        opponent.send(pickle.dumps(packet))
        opponent_idx = room.clients.index(opponent)
        room.clients.pop(opponent_idx)
        room.clients_names.pop(opponent_idx)
        room.used_words = []
        room.is_free = True
        Thread(target=self.start_game, args=(room, )).start()

    def join_room(self, room_name):
        for room in self.rooms:
            if room.name == room_name:
                self.room = room
                room.clients.append(self.client)
                room.clients_names.append(self.name)
                print(f"{self.name} joined the room {room.name}.")

    def start_game(self, cur_room):
        pass

    def is_city_valid(self, city):
        if city in self.room.used_words:
            packet = dict(data="Такой город уже был. Попробуйте снова.\n",
                          msgtype='chat')
            self.client.send(pickle.dumps(packet))
            return False

        if self.room.used_words:
            last_word = self.room.used_words[-1]
            if last_word[-1].lower() != city[0]:
                packet = dict(data=f"Город должен начинаться с буквы "
                                   f"{last_word[-1].lower()}. "
                                   f"Попробуйте снова.",
                              msgtype='chat')
                self.client.send(pickle.dumps(packet))
                return False

        return True


def main():
    game_server = GameServer('127.0.0.1', port=3435)
    game_server.start()


if __name__ == "__main__":
    main()
