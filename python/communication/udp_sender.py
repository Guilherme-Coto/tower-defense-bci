import socket

class UDPSender:
    def __init__(self,host="127.0.0.1",port=5005):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def send(self, message):
        self.socket.sendto(message.encode(),(self.host, self.port))
        print(f"[UDP] Sent -> {message}")