import socket
import threading
import pickle

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.isConnected = False
        self.lock = threading.Lock()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        name = input("Введите ваше имя: ")
        self.sock.send(pickle.dumps(name))
        self.isConnected = True
        thread_send = threading.Thread(target=self.send_messages)
        thread_recv = threading.Thread(target=self.receive_messages)
        thread_send.start()
        thread_recv.start()

    def send_messages(self):
        try:
            while self.isConnected:
                message = input()
                self.sock.send(pickle.dumps(message))
                if message.lower() == 'exit':
                    print("Отключение от сервера...")
                    self.isConnected = False
                    self.sock.close()
                    break
        except (ConnectionResetError, ConnectionAbortedError):
            print("Вы были отключены от сервера")

    def receive_messages(self):
        try:
            while self.isConnected:
                received_data = self.sock.recv(4096)
                if not received_data:
                    break
                data = pickle.loads(received_data)
                if type(data) == type(dict):
                    if 'exit' in data.keys() and data['exit']:
                        self.isConnected = False
                        self.sock.close()
                print(data)
        except (ConnectionResetError, ConnectionAbortedError):
            print("Вы были отключены от сервера")


def main():
    client = Client('127.0.0.1', port=3434)
    client.connect()


if __name__ == "__main__":
    main()
