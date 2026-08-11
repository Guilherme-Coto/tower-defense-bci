extends Node3D

const LOGS_DIR = "res://logs"
var current_file_path = ""
var start_time_msec: int = 0

func _ready():
	start_time_msec = Time.get_ticks_msec()
	
	_prepare_directory()
	_create_new_log_file()
	write_log("Log system started successfully.")

func _prepare_directory():
	if not DirAccess.dir_exists_absolute(LOGS_DIR):
		var err = DirAccess.make_dir_recursive_absolute(LOGS_DIR)
		if err != OK:
			print("Error creating logs directory.")

func _create_new_log_file():
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
	if current_file_path == "":
		return
		
	var file = FileAccess.open(current_file_path, FileAccess.READ_WRITE)
	if file:
		file.seek_end()
		
		var current_ticks = Time.get_ticks_msec()
		var offset_msec = current_ticks - start_time_msec
		var seconds = offset_msec / 1000
		var milliseconds = offset_msec % 1000
		var offset_string = str(seconds) + "." + str(milliseconds).pad_zeros(3) + "s"
		
		file.store_line("[" + offset_string + "] " + message)
		file.close()
