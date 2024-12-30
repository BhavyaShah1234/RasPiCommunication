import os
import socket as s
import struct as st

class FileSender:
    def __init__(self, server_ip, server_port):
        self.client = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.client.connect((server_ip, server_port))
        print(f'CLIENT CONNECTED')

    def send_file(self, file_path):
        filename = bytes(os.path.basename(file_path), "utf-8")
        self.client.send(st.pack("Q", len(filename)) + filename)
        content = open(file_path, 'rb').read()
        self.client.send(st.pack("Q", len(content)) + content)

if __name__ == '__main__':
    server_ip = '192.168.0.87'
    server_port = 8554
    sender = FileSender(server_ip, server_port)
    sender.send_file('portal/green1.jpg')
