import cv2 as cv
import numpy as np
import socket as s
import struct as st
import threading as t

class Receiver:
    def __init__(self, server_ip, server_port):
        self.server = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.server.bind((server_ip, server_port))
        self.server.listen()
        print(f'SERVER LISTENING ON {server_ip}:{server_port}')

    def receive_dimensions(self, connection):
        stream = b""
        payload_size = st.calcsize("Q")
        while len(stream) < payload_size:
            packet = connection.recv(4096)
            if packet is None:
                break
            stream = stream + packet
        message_size = st.unpack("Q", stream[:payload_size])[0]
        message = stream[payload_size:]
        while len(message) < message_size:
            message = message + connection.recv(4096)
        excess = message[message_size:]
        message = message[:message_size]
        img_h, img_w = np.frombuffer(message, dtype='int32').tolist()
        return img_h, img_w, excess

    def communicate(self, connection, address):
        print(f'{address} CONNECTED TO SERVER')
        img_h, img_w, stream = self.receive_dimensions(connection)
        payload_size = st.calcsize("Q")
        while True:
            while len(stream) < payload_size:
                packet = connection.recv(4096)
                if packet is None:
                    break
                stream = stream + packet
            frame_size = stream[:payload_size]
            frame = stream[payload_size:]
            frame_size = st.unpack("Q", frame_size)[0]
            while len(frame) < frame_size:
                frame = frame + connection.recv(4096)
            stream = frame[frame_size:]
            frame = frame[:frame_size]
            frame = np.frombuffer(frame, dtype='uint8').reshape([img_h, img_w, -1])
            cv.imshow('Frame', frame)
            if cv.waitKey(1) == 27:
                break
        connection.close()

    def connect_to_a_client(self):
        connection, address = self.server.accept()
        client_thread = t.Thread(target=self.communicate, args=((connection, address)))
        client_thread.start()

if __name__ == '__main__':
    server_ip = '192.168.0.87'
    server_port = 8554
    server = Receiver(server_ip, server_port)
    server.connect_to_a_client()
