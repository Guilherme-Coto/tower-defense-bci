extends Node

var udp_peer = PacketPeerUDP.new()

var python_ip = "127.0.0.1" #ip local
var python_port_send = 5005 #porta para enviar a resposta
var python_port_receive = 5006 #porta para receber a resposta

var socket_send = PacketPeerUDP.new()
var socket_receive = PacketPeerUDP.new()

@onready var UIManager = get_tree().get_first_node_in_group("UIManager")

var responses = {
	"TRIGGER_FIRE" : Weak_System.ELEMENT.Fire,
	"TRIGGER_WATER" : Weak_System.ELEMENT.Water,
	"TRIGGER_WIND" : Weak_System.ELEMENT.Wind,
	"TRIGGER_EARTH" : Weak_System.ELEMENT.Earth
}

func _ready():
	socket_send.connect_to_host(python_ip, python_port_send)
	print("LSL no jogo ligado.")
	
	if socket_receive.bind(python_port_receive) == OK:
			print("Jogo à escuta na porta", python_port_receive)
	else:
		print("Erro ao abrir a porta:", python_port_receive)
		
#função que envia dados
func send_marker(nome_do_evento: String):
	var pacote = nome_do_evento.to_utf8_buffer()
	socket_send.put_packet(pacote)
	print("Dados enviados:", nome_do_evento)

func _process(_delta):
	if socket_receive.get_available_packet_count() > 0:
		var response = socket_receive.get_packet().get_string_from_utf8()
		print("Elemento:",response)
		if response in responses.keys():
			UIManager.on_button_power_clicket(responses[response])
