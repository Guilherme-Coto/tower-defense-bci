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
@onready var page_recall = $LevelSelector/CarouselContainer/PageRecall
@onready var page_inverse = $LevelSelector/CarouselContainer/PageInverse
@onready var btn_tab_recall = $LevelSelector/PageNavHBox/btn_tab_recall
@onready var btn_tab_inverse = $LevelSelector/PageNavHBox/btn_tab_inverse

var current_page = 0 # 0 = Recall, 1 = Inverse

func _ready() -> void:
	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)
	_update_carousel_page(0)

func _update_carousel_page(page_idx: int) -> void:
	current_page = page_idx
	if current_page == 0:
		if page_recall:
			page_recall.visible = true
		if page_inverse:
			page_inverse.visible = false
		if btn_tab_recall:
			btn_tab_recall.disabled = true
		if btn_tab_inverse:
			btn_tab_inverse.disabled = false
	else:
		if page_recall:
			page_recall.visible = false
		if page_inverse:
			page_inverse.visible = true
		if btn_tab_recall:
			btn_tab_recall.disabled = false
		if btn_tab_inverse:
			btn_tab_inverse.disabled = true

func _on_btn_tab_recall_pressed() -> void:
	_update_carousel_page(0)

func _on_btn_tab_inverse_pressed() -> void:
	_update_carousel_page(1)

func _on_play_pressed() -> void:
	level_selector.visible = true
	menu.visible = false
	_update_carousel_page(0)

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

func _on_btn_level_random_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_random.tscn")

func _on_btn_level_reverse_four_elements_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_reverse_four_elements.tscn")

func _on_btn_level_reverse_random_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_reverse_random.tscn")

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
