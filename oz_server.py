from flask import Flask, render_template_string, request
import socket

app = Flask(__name__)

# Configuração da ligação local com o Godot
GODOT_IP = "127.0.0.1"
GODOT_PORT = 4242
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Interface web responsiva para o ecrã do telemóvel
HTML_UI = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feiticeiro de Oz</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; display: flex; flex-direction: column; gap: 14px; padding: 24px; background: #2b2f33; color: #cdd6f4; margin: 0; }
        h2 { text-align: center; margin-bottom: 5px; }
        h3 { text-align: center; margin: 10px 0 5px 0; color: #a6adc8; font-size: 18px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        button { padding: 14px; font-size: 15px; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; -webkit-tap-highlight-color: transparent; }
        button:active { transform: scale(0.97); }
        .green { background: #6aa84f; color: #11111b; }
        .yellow { background: #ffd966; color: #11111b; }
        .red { background: #f81b36; color: #11111b; }
        .blue { background: #00aef2; color: #11111b; }
        .purple { background: #CC7EBD; color: #11111b; }
        .full-width { grid-column: span 2; }
    </style>
</head>
<body>
    <h2>Controlo remoto do Tower Defense</h2>
    
    <h3>Tocar uma Música</h3>
    <div class="grid">
        <button class="red" onclick="send('music:0')">Música Fogo</button>
        <button class="blue" onclick="send('music:1')">Música Água</button>
        <button class="green" onclick="send('music:2')">Música Vento</button>
        <button class="yellow" onclick="send('music:3')">Música Elétrica</button>
    </div>

    <h3> Interações</h3>
    <div class="grid">
        <button class="purple full-width" onclick="send('blink_box')">Piscar Caixa (On/Off)</button>
        <button class="green" onclick="send('curar_jogador')">Curar</button>
        <button class="red" onclick="send('kill_enemy')">Disparar</button>
    </div>

    <h3>Trocar de Poder</h3>
    <div class="grid">
        <button class="red" onclick="send('power:0')">Fogo</button>
        <button class="blue" onclick="send('power:1')">Água</button>
        <button class="green" onclick="send('power:2')">Vento</button>
        <button class="yellow" onclick="send('power:3')">Eletricidade</button>
    </div>

    <h3>Spawn de um Inimigo</h3>
    <div class="grid">
        <button class="red" onclick="send('spawn:0')">Spawn Fogo</button>
        <button class="blue" onclick="send('spawn:1')">Spawn Água</button>
        <button class="green" onclick="send('spawn:2')">Spawn Vento</button>
        <button class="yellow" onclick="send('spawn:3')">Spawn Elétrica</button>
    </div>

    <script>
        function send(cmd) {
            fetch('/action?cmd=' + encodeURIComponent(cmd));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/action')
def acao():
    cmd = request.args.get('cmd', '')
    if cmd:
        sock.sendto(cmd.encode('utf-8'), (GODOT_IP, GODOT_PORT))
        print(f"[OZ] Action send: {cmd}")
    return ('', 204)

if __name__ == '__main__':
    # host='0.0.0.0' torna o servidor visível para outros aparelhos na rede Wi-Fi
    app.run(host='0.0.0.0', port=5000)