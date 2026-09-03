extends Node

var server := UDPServer.new()

@onready var spawner = get_tree().get_first_node_in_group("spawner")
@onready var UIManager = get_tree().get_first_node_in_group("UIManager")
@onready var bci = get_tree().get_first_node_in_group("BCI")
@onready var light = $"../DirectionalLight3D"

func _ready():
	var err = server.listen(4242)
	if err != OK:
		print("Erro ao iniciar servidor UDP Oz na porta 4242: ", err)
	else:
		print("Servidor Oz na porta 4242.")

func _process(_delta):
	server.poll()
	if server.is_connection_available():
		var peer: PacketPeerUDP = server.take_connection()
		var packet = peer.get_packet()
		var msg = packet.get_string_from_utf8()
		process_oz_command(msg)

func process_oz_command(cmd: String):
	print("Feiticeiro de Oz enviou: ", cmd)
	if bci:
		bci.write_log("Wizard of Oz command: " + cmd)
		
	if cmd.begins_with("music:"):
		var parts = cmd.split(":")
		if parts.size() > 1:
			if spawner:
				spawner.play_music(parts[1].to_int())
	elif cmd == "blink_box":
		if UIManager:
			if UIManager.box_isblinking:
				UIManager.desactive_box_blink()
			else:
				UIManager.active_box_blink()
	elif cmd.begins_with("power:"):
		var parts = cmd.split(":")
		if parts.size() > 1:
			if UIManager:
				UIManager.active_a_button(parts[1].to_int())
	elif cmd.begins_with("spawn:"):
		var parts = cmd.split(":")
		if parts.size() > 1:
			var elem_id = parts[1].to_int()
			if spawner:
				spawner.spawn_enemy(true, elem_id)
	elif cmd == "curar_jogador":
		if UIManager:
			UIManager.heal()
	elif cmd == "kill_enemy":
		if spawner and spawner.spawner:
			for child in spawner.spawner.get_children():
				if child.has_method("end"):
					child.end()
					break
