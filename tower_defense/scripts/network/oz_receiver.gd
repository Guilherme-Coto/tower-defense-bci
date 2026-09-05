extends Node

## oz_receiver.gd - Mantido para compatibilidade com scene_oz.tscn
## Se o singleton BciReceiver estiver ativo como Autoload, delega para ele.
## Caso contrário, escuta na porta 4242 de forma segura.

var server := UDPServer.new()
var is_standalone: bool = false

func _ready() -> void:
	if Engine.has_singleton("BciReceiver") or get_node_or_null("/root/BciReceiver"):
		print("[OzReceiver] BciReceiver global detectado. Delegação ativa.")
		return
		
	var err = server.listen(4242)
	if err == OK:
		is_standalone = true
		print("[OzReceiver] Servidor Oz ativo na porta 4242.")
	else:
		print("[OzReceiver] Não foi possível vincular porta 4242: ", err)

func _process(_delta: float) -> void:
	if not is_standalone:
		return
	server.poll()
	if server.is_connection_available():
		var peer: PacketPeerUDP = server.take_connection()
		var packet = peer.get_packet()
		var msg = packet.get_string_from_utf8().strip_edges()
		process_oz_command(msg)

func process_oz_command(cmd: String) -> void:
	var bci = get_tree().get_first_node_in_group("BCI")
	var ui = get_tree().get_first_node_in_group("UIManager")
	var spawner = get_tree().get_first_node_in_group("spawner")
	
	if bci and bci.has_method("write_log"):
		bci.write_log("Wizard of Oz command: " + cmd)
		
	if cmd.begins_with("power:"):
		var parts = cmd.split(":")
		if parts.size() > 1 and ui and ui.has_method("active_a_button"):
			ui.active_a_button(parts[1].to_int())
	elif cmd == "curar_jogador" or cmd == "heal":
		if ui and ui.has_method("heal"):
			ui.heal()
	elif cmd == "kill_enemy":
		if spawner and "spawner" in spawner and spawner.spawner:
			for child in spawner.spawner.get_children():
				if child.has_method("end"):
					child.end()
					break
