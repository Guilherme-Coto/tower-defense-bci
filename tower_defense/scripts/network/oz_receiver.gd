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
		if spawner and spawner.has_method("kill_active_enemy"):
			spawner.kill_active_enemy()
		elif spawner and "spawner" in spawner and spawner.spawner:
			for child in spawner.spawner.get_children():
				if child.has_method("end"):
					child.end()
					break
	elif cmd.begins_with("spawn:"):
		var parts = cmd.split(":")
		if parts.size() > 1 and spawner and spawner.has_method("spawn_enemy"):
			spawner.spawn_enemy(true, parts[1].to_int())
	elif cmd == "blink_box":
		if ui and "box_isblinking" in ui:
			if ui.box_isblinking:
				ui.desactive_box_blink()
			else:
				ui.active_box_blink()
	elif cmd.begins_with("music:"):
		var parts = cmd.split(":")
		if parts.size() > 1:
			if parts[1] == "stop":
				if spawner and spawner.has_method("stop_music"):
					spawner.stop_music()
				if ui and ui.has_method("add_text_to_log"):
					ui.add_text_to_log("Feiticeiro: Música parada")
			else:
				var elem_id = parts[1].to_int()
				if spawner and spawner.has_method("play_music"):
					spawner.play_music(elem_id)
				if ui and ui.has_method("add_text_to_log"):
					var elem_names = ["Fogo", "Água", "Vento", "Eletricidade"]
					var el_name = elem_names[elem_id] if elem_id >= 0 and elem_id < elem_names.size() else str(elem_id)
					ui.add_text_to_log("Feiticeiro ativou Música: " + el_name)
	elif cmd == "stop_music":
		if spawner and spawner.has_method("stop_music"):
			spawner.stop_music()
		if ui and ui.has_method("add_text_to_log"):
			ui.add_text_to_log("Feiticeiro: Música parada")
	elif cmd == "music_correct" or cmd == "music_feedback:correct" or cmd == "correct_music":
		if bci and bci.has_method("write_log"):
			bci.write_log("Music_Feedback: CORRECT")
		if ui and ui.has_method("notify_music_feedback"):
			ui.notify_music_feedback(true)
		elif ui and ui.has_method("add_text_to_log"):
			ui.add_text_to_log("Feiticeiro: Música avaliada como CORRETA ✔")
	elif cmd == "music_incorrect" or cmd == "music_feedback:incorrect" or cmd == "incorrect_music":
		if bci and bci.has_method("write_log"):
			bci.write_log("Music_Feedback: INCORRECT")
		if ui and ui.has_method("notify_music_feedback"):
			ui.notify_music_feedback(false)
		elif ui and ui.has_method("add_text_to_log"):
			ui.add_text_to_log("Feiticeiro: Música avaliada como INCORRETA ✖")
