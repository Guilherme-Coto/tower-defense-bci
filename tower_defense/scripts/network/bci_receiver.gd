extends Node

## BciReceiver (Autoload Singleton)
## Listens on UDP port 4242 for real-time rhythm decoding commands from the Python BCI pipeline.
## Commands:
##   - power:0 (FIRE)
##   - power:1 (WATER)
##   - power:2 (WIND)
##   - power:3 (ELECTRICITY)
##   - curar_jogador / heal
##   - kill_enemy
##   - spawn:0..3

signal bci_command_received(command: String)
signal bci_power_received(element_id: int)

const UDP_PORT: int = 4242
var udp_peer := PacketPeerUDP.new()
var is_listening: bool = false

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS # Persists across pause and scene changes
	_start_listener()

func _start_listener() -> void:
	var err = udp_peer.bind(UDP_PORT)
	if err != OK:
		printerr("[BciReceiver] Falha ao abrir porta UDP %d: %d" % [UDP_PORT, err])
		is_listening = false
	else:
		print("[BciReceiver] Servidor UDP ouvindo com sucesso na porta %d" % UDP_PORT)
		is_listening = true

func _process(_delta: float) -> void:
	if not is_listening:
		return
		
	while udp_peer.get_available_packet_count() > 0:
		var packet = udp_peer.get_packet()
		var msg = packet.get_string_from_utf8().strip_edges()
		if msg != "":
			process_bci_command(msg)

func process_bci_command(cmd: String) -> void:
	print("[BciReceiver] Comando recebido: ", cmd)
	bci_command_received.emit(cmd)
	
	var bci_marker = get_tree().get_first_node_in_group("BCI")
	if bci_marker and bci_marker.has_method("write_log"):
		bci_marker.write_log("BCI_UDP_Command: " + cmd)
		
	var ui = get_tree().get_first_node_in_group("UIManager")
	var spawner = get_tree().get_first_node_in_group("spawner")
	
	if cmd.begins_with("power:"):
		var parts = cmd.split(":")
		if parts.size() > 1:
			var elem_id = parts[1].to_int()
			if elem_id >= 0 and elem_id <= 3:
				bci_power_received.emit(elem_id)
				if ui and ui.has_method("active_a_button"):
					ui.active_a_button(elem_id)
				if ui and ui.has_method("notify_bci_switch"):
					ui.notify_bci_switch(elem_id)
	elif cmd == "curar_jogador" or cmd == "heal":
		if ui and ui.has_method("heal"):
			ui.heal()
	elif cmd == "kill_enemy":
		if spawner and spawner.has_method("kill_active_enemy"):
			spawner.kill_active_enemy()
		elif spawner and "spawner" in spawner and spawner.spawner:
			for child in spawner.spawner.get_children():
				if child.has_method("end"):
					child.end()
					break
	elif cmd.begins_with("spawn:"):
		var parts = cmd.split(":")
		if parts.size() > 1:
			var elem_id = parts[1].to_int()
			if spawner and spawner.has_method("spawn_enemy"):
				spawner.spawn_enemy(true, elem_id)
	elif cmd == "blink_box":
		if ui and "box_isblinking" in ui:
			if ui.box_isblinking:
				ui.desactive_box_blink()
			else:
				ui.active_box_blink()
