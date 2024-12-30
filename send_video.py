import cv2 as cv
import numpy as np
import socket as s
import struct as st

class Streamer:
    def __init__(self, camera_id, server_ip, server_port):
        self.camera_id = camera_id
        self.client = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.client.connect((server_ip, server_port))
        print(f'CLIENT CONNECTED')

    def send_message(self, message):
        message_size = st.pack("Q", len(message))
        self.client.send(message_size + message)

    def stream(self):
        camera = cv.VideoCapture(self.camera_id)
        img_h = int(camera.get(cv.CAP_PROP_FRAME_HEIGHT))
        img_w = int(camera.get(cv.CAP_PROP_FRAME_WIDTH))
        self.send_message(np.array([img_h, img_w], dtype='int32').tobytes())
        while camera.isOpened():
            ret, frame = camera.read()
            if not ret:
                break
            self.send_message(frame.tobytes())
        camera.release()
        self.client.close()

if __name__ == '__main__':
    server_ip = '192.168.0.87'
    server_port = 8554
    camera_id = 0
    streamer = Streamer(camera_id, server_ip, server_port)
    streamer.stream()
