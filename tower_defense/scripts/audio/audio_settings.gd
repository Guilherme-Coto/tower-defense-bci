extends Node

# Singleton de Áudio e Configurações
# Gere o volume global do jogo e a associação de músicas a cada elemento

enum Element {
	FIRE = 0,
	WATER = 1,
	WIND = 2,
	ELECTRICITY = 3
}

const AVAILABLE_TRACKS = [
	{
		"id": 0,
		"name": "Für Elise",
		"file_name": "Track1_Fur_Elise",
		"path": "res://assets/musics/Track1_Fur_Elise.wav"
	},
	{
		"id": 1,
		"name": "The Entertainer",
		"file_name": "Track2_The_Entertainer",
		"path": "res://assets/musics/Track2_The_Entertainer.wav"
	},
	{
		"id": 2,
		"name": "Prelude in C Major",
		"file_name": "Track3_Prelude_C_Major",
		"path": "res://assets/musics/Track3_Prelude_C_Major.wav"
	},
	{
		"id": 3,
		"name": "Eine kleine Nachtmusik",
		"file_name": "Track4_Eine_kleine_Nachtmusik",
		"path": "res://assets/musics/Track4_Eine_kleine_Nachtmusik.wav"
	},
	{
		"id": 4,
		"name": "The Four Seasons",
		"file_name": "Track5_The_Four_Seasons",
		"path": "res://assets/musics/Track5_The_Four_Seasons.wav"
	},
	{
		"id": 5,
		"name": "Waltz of the Flowers",
		"file_name": "Track6_Waltz_of_the_flowers",
		"path": "res://assets/musics/Track6_Waltz_of_the_flowers.wav"
	}
]

var track_streams: Dictionary = {}

# Mapeamento padrão dos elementos
# 0: Fogo -> Für Elise (ID 0)
# 1: Água -> Prelude in C Major (ID 2)
# 2: Vento -> The Four Seasons (ID 4)
# 3: Eletricidade -> Waltz of the Flowers (ID 5)
const DEFAULT_ELEMENT_TRACKS = {
	0: 0,
	1: 2,
	2: 4,
	3: 5
}

var element_tracks: Dictionary = {
	0: 0,
	1: 2,
	2: 4,
	3: 5
}

var master_volume_percent: float = 100.0

const SAVE_PATH = "user://audio_settings.cfg"

func _ready() -> void:
	# Carregar streams de áudio
	for track in AVAILABLE_TRACKS:
		var stream = load(track["path"])
		track_streams[track["id"]] = stream
	load_settings()
	apply_master_volume()

func get_track_for_element(element_idx: int) -> AudioStream:
	var track_id = get_track_id_for_element(element_idx)
	if track_streams.has(track_id):
		return track_streams[track_id]
	return null

func get_track_id_for_element(element_idx: int) -> int:
	return element_tracks.get(element_idx, DEFAULT_ELEMENT_TRACKS.get(element_idx, 0))

func get_track_name_for_element(element_idx: int) -> String:
	var track_id = get_track_id_for_element(element_idx)
	if track_id >= 0 and track_id < AVAILABLE_TRACKS.size():
		return AVAILABLE_TRACKS[track_id]["file_name"]
	return "Unknown_Track"

func get_track_display_name_for_element(element_idx: int) -> String:
	var track_id = get_track_id_for_element(element_idx)
	if track_id >= 0 and track_id < AVAILABLE_TRACKS.size():
		return AVAILABLE_TRACKS[track_id]["name"]
	return "Unknown Track"

func set_element_track(element_idx: int, track_id: int) -> bool:
	if not element_tracks.has(element_idx):
		return false
	
	if track_id < 0 or track_id >= AVAILABLE_TRACKS.size():
		return false
		
	element_tracks[element_idx] = track_id
	save_settings()
	return true

func set_master_volume_percent(percent: float) -> void:
	master_volume_percent = clamp(percent, 0.0, 100.0)
	apply_master_volume()
	save_settings()

func get_master_volume_percent() -> float:
	return master_volume_percent

func apply_master_volume() -> void:
	var bus_idx = AudioServer.get_bus_index("Master")
	if bus_idx != -1:
		if master_volume_percent <= 0.0:
			AudioServer.set_bus_mute(bus_idx, true)
			AudioServer.set_bus_volume_db(bus_idx, -80.0)
		else:
			AudioServer.set_bus_mute(bus_idx, false)
			var linear = master_volume_percent / 100.0
			var db = linear_to_db(linear)
			AudioServer.set_bus_volume_db(bus_idx, db)

func reset_to_defaults() -> void:
	element_tracks = DEFAULT_ELEMENT_TRACKS.duplicate()
	master_volume_percent = 100.0
	apply_master_volume()
	save_settings()

func save_settings() -> void:
	var config = ConfigFile.new()
	config.set_value("audio", "master_volume", master_volume_percent)
	config.set_value("elements", "fire_track", element_tracks[0])
	config.set_value("elements", "water_track", element_tracks[1])
	config.set_value("elements", "wind_track", element_tracks[2])
	config.set_value("elements", "electricity_track", element_tracks[3])
	config.save(SAVE_PATH)

func load_settings() -> void:
	var config = ConfigFile.new()
	var err = config.load(SAVE_PATH)
	if err == OK:
		master_volume_percent = config.get_value("audio", "master_volume", 100.0)
		element_tracks[0] = config.get_value("elements", "fire_track", DEFAULT_ELEMENT_TRACKS[0])
		element_tracks[1] = config.get_value("elements", "water_track", DEFAULT_ELEMENT_TRACKS[1])
		element_tracks[2] = config.get_value("elements", "wind_track", DEFAULT_ELEMENT_TRACKS[2])
		element_tracks[3] = config.get_value("elements", "electricity_track", DEFAULT_ELEMENT_TRACKS[3])
