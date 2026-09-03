extends Node

var udp_peer := PacketPeerUDP.new()
var bridge_host := "127.0.0.1"
var bridge_port := 9000

const LOGS_DIR = "res://logs"
var current_file_path = ""
var start_time_msec: int = 0
var last_event_time_msec: int = 0

enum MODE { NORMAL, AUTO }
@export var mode_selected: MODE = MODE.NORMAL

func _ready():
	start_time_msec = Time.get_ticks_msec()
	last_event_time_msec = start_time_msec
	
	# Connect to the local UDP bridge running from the Python suite
	var err = udp_peer.connect_to_host(bridge_host, bridge_port)
	if err == OK:
		print("BCI UDP Peer connected to ", bridge_host, ":", bridge_port)
	else:
		print("Warning: Could not connect BCI UDP peer to ", bridge_host, ":", bridge_port)

	if mode_selected == MODE.NORMAL:
		_prepare_directory()
		_create_new_log_file()
		write_log("Log system started successfully.")

	# Send an initial marker to verify connection and include level name
	call_deferred("_send_start_marker")

func _prepare_directory():
	if not DirAccess.dir_exists_absolute(LOGS_DIR):
		var err = DirAccess.make_dir_recursive_absolute(LOGS_DIR)
		if err != OK:
			print("Error creating logs directory.")

func _create_new_log_file():
	if mode_selected == MODE.NORMAL:
		var counter = 1
		current_file_path = LOGS_DIR + "/log_" + str(counter) + ".txt"
		
		while FileAccess.file_exists(current_file_path):
			counter += 1
			current_file_path = LOGS_DIR + "/log_" + str(counter) + ".txt"
			
		var file = FileAccess.open(current_file_path, FileAccess.WRITE)
		if file:
			file.store_line("Log Start (Execution " + str(counter) + ")")
			file.close()
		else:
			print("Failed to open log file for writing.")

func _send_start_marker():
	var level_name = "Unknown_Level"
	if get_tree().current_scene and get_tree().current_scene.scene_file_path != "":
		level_name = get_tree().current_scene.scene_file_path.get_file().get_basename()
	elif get_tree().current_scene:
		level_name = get_tree().current_scene.name
	send_bci_marker("Game_Started_" + level_name, 0.0)

func write_log(message: String):
	var current_ticks = Time.get_ticks_msec()
	var duration_sec: float = (current_ticks - last_event_time_msec) / 1000.0
	last_event_time_msec = current_ticks
	
	if mode_selected == MODE.NORMAL and current_file_path != "":
		var file = FileAccess.open(current_file_path, FileAccess.READ_WRITE)
		if file:
			file.seek_end()
			var offset_msec = current_ticks - start_time_msec
			var seconds = offset_msec / 1000
			var milliseconds = offset_msec % 1000
			var offset_string = str(seconds) + "." + str(milliseconds).pad_zeros(3) + "s"
			file.store_line("[" + offset_string + "] " + message)
			file.close()
			
	send_bci_marker(message, duration_sec)

func send_bci_marker(marker_name: String, duration: float = 0.0):
	# Construct the JSON payload required by the bridge
	var payload = {
		"name": marker_name,
		"duration": duration
	}

	# Convert dictionary to JSON string
	var json_string = JSON.stringify(payload)

	# Send the packet over UDP
	udp_peer.put_packet(json_string.to_utf8_buffer())
	print("Sent BCI marker: ", marker_name, " (duration: ", duration, "s)")
