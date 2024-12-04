import socket
import threading


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.isConnected = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        name = input("Введите ваше имя: ")
        self.sock.send(name.encode())
        self.isConnected = True
        thread_send = threading.Thread(target=self.send_messages)
        thread_recv = threading.Thread(target=self.receive_messages)
        thread_send.start()
        thread_recv.start()

    def send_messages(self):
        while self.isConnected:
            message = input()
            self.sock.send(message.encode())
            if message.lower() == 'exit':
                print("Отключение от сервера...")
                self.sock.close()
                break

    def receive_messages(self):
        try:
            while self.isConnected:
                data = self.sock.recv(1024)
                print(data.decode())
                if not data:
                    break
        except (ConnectionResetError, ConnectionAbortedError):
            print("Вы были отключены от сервера")


def main():
    client = Client('127.0.0.1', port=3434)
    client.connect()


if __name__ == "__main__":
    main()
