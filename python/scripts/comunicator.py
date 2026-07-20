import time, socket

#configurações da rede do godot
GODOT_IP = "127.0.0.1"
GODOT_PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Conexão com Godot")

try:
    while True:
        input()
        message = "TEST_CONNECTION"
        sock.sendto(message.encode('utf-8'), (GODOT_IP, GODOT_PORT))
        print(f"Mensagem '{message}' enviada com sucesso.")
except KeyboardInterrupt:
    print("Programa encerrado por ordem do utilizador.")
    sock.close()