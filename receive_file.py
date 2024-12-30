import os
import socket as s
import struct as st
import threading as t

class Receiver:
    def __init__(self, server_ip, server_port):
        self.server = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.server.bind((server_ip, server_port))
        self.server.listen()
        print(f'SERVER LISTENING ON {server_ip}:{server_port}')

    def receive_filename(self, connection):
        payload_size = st.calcsize("Q")
        message = b""
        while len(message) < payload_size:
            packet = connection.recv(1024)
            if packet is None:
                break
            message = message + packet
        filename_size = message[:payload_size]
        filename = message[payload_size:]
        filename_size = st.unpack("Q", filename_size)[0]
        while len(filename) < filename_size:
            packet = connection.recv(1024)
            if packet is None:
                break
            filename = filename + packet
        excess = filename[filename_size:]
        filename = filename[:filename_size].decode("utf-8")
        return filename, excess

    def receive_content(self, filename, content, connection):
        file = open(os.path.join('portal', filename), 'wb')
        payload_size = st.calcsize("Q")
        while len(content) < payload_size:
            packet = connection.recv(1024)
            if packet is None:
                break
            content = content + packet
        content_size = content[:payload_size]
        content = content[payload_size:]
        content_size = st.unpack("Q", content_size)[0]
        while len(content) < content_size:
            packet = connection.recv(1024)
            if packet is None:
                break
            content = content + packet
        content = content[:content_size]
        file.write(content)
        file.close()

    def receive_file(self, connection, address):
        print(f'{address} CONNECTED TO SERVER')
        filename, content = self.receive_filename(connection)
        self.receive_content(filename, content, connection)

    def connect_to_a_client(self):
        connection, address = self.server.accept()
        client_thread = t.Thread(target=self.receive_file, args=((connection, address)))
        client_thread.start()

if __name__ == '__main__':
    server_ip = '192.168.0.87'
    server_port = 8554
    receiver = Receiver(server_ip, server_port)
    receiver.connect_to_a_client()
