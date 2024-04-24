import cv2
from threading import Thread

class VideoStream :
    def __init__(self, url) -> None:
        self.url = url
        self.cap = cv2.VideoCapture(url)
        self.data = None
        self.stopped = True
        self.t = Thread(target=self.getData, args=(), daemon=True)

    def __repr__(self) -> str:
        print(f'Open CV Stream: {self.url}')

    def reconnect(self):
        self.cap.release()
        self.cap = cv2.VideoCapture(self.url)

    def start(self):
        self.stopped = False
        self.t.start()

    def stop(self):
        self.stopped = True
        self.cap.release()
        self.t.join()

    def getData(self):
        print(f'[INFO] -- Starting to read data from {self.url}')
        while True:
            if self.stopped:
                break
            elif not self.cap.isOpened():
                self.reconnect()
                continue
            ret, self.data = self.cap.read()