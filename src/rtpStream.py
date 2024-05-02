import socket
from threading import Thread
from multiprocessing import Queue

class RTPStream :
    def __init__(self, addr: str, port: int) -> None:
        self.addr = addr
        self.port = port
        print(f'{addr}:{port}')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.addr, self.port))
        self.data = Queue()
        self.stopped = True
        self.t = Thread(target=self.getData, args=(), daemon=True)

    def __repr__(self) -> str:
        print(f'RTP Stream: {self.url}')

    def start(self):
        self.stopped = False
        self.t.start()

    def stop(self):
        self.stopped = True
        self.t.join()

    def getData(self):
        print(f'[INFO] -- Starting to read data from {self.addr}:{self.port}')
        while True:
            if self.stopped:
                break
            data, addr = self.socket.recvfrom(2048)
            self.data.put(data)