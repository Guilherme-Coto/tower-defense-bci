from flask import Flask, render_template_string, request, jsonify
import socket
import datetime

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
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feiticeiro de Oz - BCI Tower Defense</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            flex-direction: column;
            gap: 14px;
            padding: 20px;
            background: #1e1e2e;
            color: #cdd6f4;
            margin: 0;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        h2 { text-align: center; margin: 0 0 4px 0; color: #f5e0dc; font-size: 22px; }
        h3 { text-align: center; margin: 12px 0 6px 0; color: #bac2de; font-size: 16px; text-transform: uppercase; letter-spacing: 0.8px; }
        
        #status-bar {
            background: #313244;
            border: 1px solid #45475a;
            border-radius: 10px;
            padding: 10px 14px;
            text-align: center;
            font-size: 14px;
            color: #a6adc8;
            min-height: 20px;
            transition: all 0.2s ease;
        }
        #status-bar.active {
            border-color: #89b4fa;
            color: #cdd6f4;
            background: #45475a;
        }
        
        .section-card {
            background: #252538;
            border-radius: 14px;
            padding: 14px;
            border: 1px solid #313244;
        }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        
        button {
            padding: 14px 10px;
            font-size: 15px;
            border: none;
            border-radius: 12px;
            font-weight: bold;
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
            transition: transform 0.1s, opacity 0.15s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        button:active { transform: scale(0.96); opacity: 0.85; }
        
        .green { background: #a6e3a1; color: #11111b; }
        .yellow { background: #f9e2af; color: #11111b; }
        .red { background: #f38ba8; color: #11111b; }
        .blue { background: #89b4fa; color: #11111b; }
        .purple { background: #cba6f7; color: #11111b; }
        .dark-btn { background: #45475a; color: #cdd6f4; }
        
        .btn-feedback-correct {
            background: #40a02b;
            color: #ffffff;
            font-size: 16px;
            padding: 16px 10px;
            border: 2px solid #a6e3a1;
            box-shadow: 0 4px 12px rgba(64, 160, 43, 0.3);
        }
        .btn-feedback-incorrect {
            background: #d20f39;
            color: #ffffff;
            font-size: 16px;
            padding: 16px 10px;
            border: 2px solid #f38ba8;
            box-shadow: 0 4px 12px rgba(210, 15, 57, 0.3);
        }
        
        .full-width { grid-column: span 2; }
    </style>
</head>
<body>
    <h2>Feiticeiro de Oz</h2>
    <div id="status-bar">Pronto. Aguardando comandos...</div>
    
    <!-- Validação da Música / Eventos de Feedback -->
    <div class="section-card" style="border: 2px solid #89b4fa;">
        <h3 style="color: #89b4fa; margin-top: 2px;">Validação da Música (Evento)</h3>
        <div class="grid">
            <button class="btn-feedback-correct" onclick="send('music_correct', 'Música marcada como CORRETA')">
                <span></span> Música Correta
            </button>
            <button class="btn-feedback-incorrect" onclick="send('music_incorrect', 'Música marcada como INCORRETA')">
                <span></span> Música Incorreta
            </button>
        </div>
    </div>

    <!-- Tocar Música -->
    <div class="section-card">
        <h3>Tocar uma Música</h3>
        <div class="grid">
            <button class="red" onclick="send('music:0', 'Música Fogo iniciada')">Música Fogo</button>
            <button class="blue" onclick="send('music:1', 'Música Água iniciada')">Música Água</button>
            <button class="green" onclick="send('music:2', 'Música Vento iniciada')">Música Vento</button>
            <button class="yellow" onclick="send('music:3', 'Música Elétrica iniciada')">Música Elétrica</button>
            <button class="dark-btn full-width" onclick="send('stop_music', 'Música parada')">Parar Música</button>
        </div>
    </div>

    <!-- Interações do Jogo -->
    <div class="section-card">
        <h3>Interações</h3>
        <div class="grid">
            <button class="purple full-width" onclick="send('blink_box', 'Piscar Caixa alternado')">Piscar Caixa (On/Off)</button>
            <button class="green" onclick="send('curar_jogador', 'Jogador Curado')">Curar</button>
            <button class="red" onclick="send('kill_enemy', 'Inimigo Eliminado')">Disparar</button>
        </div>
    </div>

    <!-- Troca Manual de Poder -->
    <div class="section-card">
        <h3>🛡️ Trocar de Poder</h3>
        <div class="grid">
            <button class="red" onclick="send('power:0', 'Poder Fogo selecionado')">Fogo</button>
            <button class="blue" onclick="send('power:1', 'Poder Água selecionado')">Água</button>
            <button class="green" onclick="send('power:2', 'Poder Vento selecionado')">Vento</button>
            <button class="yellow" onclick="send('power:3', 'Poder Elétrico selecionado')">Eletricidade</button>
        </div>
    </div>

    <!-- Spawn de Inimigos -->
    <div class="section-card">
        <h3>👾 Spawn de Inimigo</h3>
        <div class="grid">
            <button class="red" onclick="send('spawn:0', 'Inimigo Fogo invocado')">Spawn Fogo</button>
            <button class="blue" onclick="send('spawn:1', 'Inimigo Água invocado')">Spawn Água</button>
            <button class="green" onclick="send('spawn:2', 'Inimigo Vento invocado')">Spawn Vento</button>
            <button class="yellow" onclick="send('spawn:3', 'Inimigo Elétrico invocado')">Spawn Elétrica</button>
        </div>
    </div>

    <script>
        function send(cmd, desc) {
            const label = desc || cmd;
            const statusBar = document.getElementById('status-bar');
            const now = new Date().toLocaleTimeString();
            
            statusBar.classList.add('active');
            statusBar.innerText = `[${now}] A enviar: ${label}...`;
            
            fetch('/action?cmd=' + encodeURIComponent(cmd))
                .then(response => {
                    if (response.ok) {
                        statusBar.innerText = `[${now}] Enviado com sucesso: ${label}`;
                    } else {
                        statusBar.innerText = `[${now}] Erro ao enviar: ${label}`;
                    }
                })
                .catch(err => {
                    statusBar.innerText = `[${now}] Falha de rede: ${err}`;
                });
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
    cmd = request.args.get('cmd', '').strip()
    if cmd:
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        sock.sendto(cmd.encode('utf-8'), (GODOT_IP, GODOT_PORT))
        print(f"[{now_str}] [OZ Server] Comando UDP enviado: '{cmd}' -> {GODOT_IP}:{GODOT_PORT}")
        return jsonify({"status": "ok", "command": cmd, "timestamp": now_str}), 200
    return jsonify({"status": "error", "message": "No command specified"}), 400

@app.route('/music_feedback')
def music_feedback():
    """
    Endpoint dedicado para feedback da música.
    Exemplos:
      /music_feedback?correct=1
      /music_feedback?correct=0
      /music_feedback?status=correct
      /music_feedback?status=incorrect
    """
    correct_param = request.args.get('correct')
    status_param = request.args.get('status', '').lower()
    
    is_correct = False
    if correct_param in ['1', 'true', 'True']:
        is_correct = True
    elif status_param in ['correct', 'certo', 'correto']:
        is_correct = True
        
    cmd = "music_correct" if is_correct else "music_incorrect"
    sock.sendto(cmd.encode('utf-8'), (GODOT_IP, GODOT_PORT))
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now_str}] [OZ Server] Music Feedback enviado: {cmd} (is_correct={is_correct})")
    return jsonify({"status": "ok", "is_correct": is_correct, "command": cmd, "timestamp": now_str}), 200

if __name__ == '__main__':
    # host='0.0.0.0' torna o servidor visível para outros aparelhos na rede Wi-Fi
    print("==================================================")
    print(" Feiticeiro de Oz - Servidor Web Ativo")
    print(f" A enviar comandos UDP para {GODOT_IP}:{GODOT_PORT}")
    print(" Aceda via browser: http://localhost:5000")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000)