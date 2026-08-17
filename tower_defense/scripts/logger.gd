extends Node3D

const LOGS_DIR = "res://logs"
var current_file_path = ""
var start_time_msec: int = 0
var last_event_time_msec: int = 0

@onready var BCI_marker_send = get_tree().get_first_node_in_group("BCI")

enum MODE { NORMAL, AUTO }
@export var mode_selected : MODE

func _ready():
	start_time_msec = Time.get_ticks_msec()
	last_event_time_msec = start_time_msec
	
	if mode_selected == MODE.NORMAL:	
		_prepare_directory()
		_create_new_log_file()
		write_log("Log system started successfully.")

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

func write_log(message: String):
	if mode_selected == MODE.NORMAL:	
		var current_ticks = Time.get_ticks_msec()
		
		var duration_sec: float = (current_ticks - last_event_time_msec) / 1000.0
		
		last_event_time_msec = current_ticks
		
		if current_file_path != "":
			var file = FileAccess.open(current_file_path, FileAccess.READ_WRITE)
			if file:
				file.seek_end()
				
				var offset_msec = current_ticks - start_time_msec
				var seconds = offset_msec / 1000
				var milliseconds = offset_msec % 1000
				var offset_string = str(seconds) + "." + str(milliseconds).pad_zeros(3) + "s"
				
				file.store_line("[" + offset_string + "] " + message)
				file.close()
				
		BCI_marker_send.send_bci_marker(message, duration_sec)
