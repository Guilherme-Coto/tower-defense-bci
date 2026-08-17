extends Control

#tracks dos elementos
const track_fire = preload("res://assets/musics/Track1_Fur_Elise.wav")
const track_water = preload("res://assets/musics/Track3_Prelude_C_Major.wav")
const track_wind = preload("res://assets/musics/Track5_The_Four_Seasons.wav")
const track_electricity = preload("res://assets/musics/Track6_Waltz_of_the_flowers.wav")

const tracks = [track_fire, track_water, track_wind, track_electricity]

var music_index = 0
var audio_player: AudioStreamPlayer

@onready var menu = $Menu
@onready var level_selector = $LevelSelector

func _ready() -> void:
	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)

func _on_play_pressed() -> void:
	level_selector.visible = true
	menu.visible = false
	#get_tree().change_scene_to_file("res://scenes/cena_1.tscn")

func _on_play_auto_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/cena_auto.tscn")

func _play_track(index: int) -> void:
	if audio_player.playing:
		audio_player.stop()
	audio_player.stream = tracks[index]
	audio_player.play()

func _on_btn_music_fire_pressed() -> void:
	_play_track(0)

func _on_btn_music_water_pressed() -> void:
	_play_track(1)

func _on_btn_music_wind_pressed() -> void:
	_play_track(2)

func _on_btn_music_electricity_pressed() -> void:
	_play_track(3)

func _on_btn_back_pressed() -> void:
	level_selector.visible = false
	menu.visible = true
