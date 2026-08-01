import socket, config

class UDPSender:
    def __init__(self,host=config.IP,port=config.PORT):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def send(self, message):
        self.socket.sendto(message.encode(),(self.host, self.port))
        print(f"[UDP] Sent -> {message}")