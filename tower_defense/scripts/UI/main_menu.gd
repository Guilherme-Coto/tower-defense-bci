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

#quatro elementos
func _on_btn_level_fire_water_wind_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_four_elements.tscn")

func _on_btn_level_reverse_fire_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_reverse_fire.tscn")

func _on_btn_level_reverse_water_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_reverse_water.tscn")
	
func _on_btn_level_reverse_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_reverse_wind.tscn")

func _on_btn_level_reverse_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_reverse_electricity.tscn")

func _on_btn_level_reverse_four_elements_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_reverse_four_elements.tscn")
#funções de mundança de nível
#elemento único
func _on_btn_level_fire_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_fire.tscn")

func _on_btn_level_water_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_water.tscn")

func _on_btn_level_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_wind.tscn")

func _on_btn_level_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_electricity.tscn")

#dois elementos
func _on_btn_level_fire_water_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_fire_water.tscn")

func _on_btn_level_fire_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_fire_wind.tscn")

func _on_btn_level_fire_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_fire_electricity.tscn")

func _on_btn_level_water_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_water_wind.tscn")

func _on_btn_level_water_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_water_electricity.tscn")

func _on_btn_level_wind_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_wind_electricity.tscn")

#três elementos
func _on_btn_level_fire_water_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_fire_water_wind.tscn")

func _on_btn_level_fire_water_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_fire_water_electricity.tscn")

func _on_btn_level_fire_wind_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_fire_wind_electricity.tscn")
	
func _on_btn_level_water_wind_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_water_wind_electricity.tscn")

#feiticeiro de oz
func _on_play_oz_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_oz.tscn")
