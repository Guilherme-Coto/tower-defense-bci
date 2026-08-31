extends Control

var music_index = 0
var audio_player: AudioStreamPlayer

@onready var menu = $Menu
@onready var level_selector = $LevelSelector
@onready var page_recall = $LevelSelector/CarouselContainer/PageRecall
@onready var page_inverse = $LevelSelector/CarouselContainer/PageInverse
@onready var btn_tab_recall = $LevelSelector/PageNavHBox/btn_tab_recall
@onready var btn_tab_inverse = $LevelSelector/PageNavHBox/btn_tab_inverse

# Opções
@onready var options_menu = $OptionsMenu
@onready var volume_slider = $OptionsMenu/VBoxOptions/HBoxVolume/VolumeSlider
@onready var lbl_vol_value = $OptionsMenu/VBoxOptions/HBoxVolume/lbl_vol_value
@onready var opt_fire = $OptionsMenu/VBoxOptions/GridElements/opt_fire
@onready var opt_water = $OptionsMenu/VBoxOptions/GridElements/opt_water
@onready var opt_wind = $OptionsMenu/VBoxOptions/GridElements/opt_wind
@onready var opt_electricity = $OptionsMenu/VBoxOptions/GridElements/opt_electricity

var current_page = 0 # 0 = Recall, 1 = Inverse

func _ready() -> void:
	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)
	_update_carousel_page(0)
	_setup_options_ui()

func _setup_options_ui() -> void:
	if not volume_slider or not opt_fire:
		return
	
	# Inicializar slider de volume
	var cur_vol = AudioSettings.get_master_volume_percent()
	volume_slider.value = cur_vol
	lbl_vol_value.text = str(int(cur_vol)) + "%"
	
	# Preencher OptionButtons dos elementos
	_populate_element_dropdown(opt_fire, 0)
	_populate_element_dropdown(opt_water, 1)
	_populate_element_dropdown(opt_wind, 2)
	_populate_element_dropdown(opt_electricity, 3)

func _populate_element_dropdown(opt_btn: OptionButton, element_idx: int) -> void:
	opt_btn.clear()
	var current_track_id = AudioSettings.get_track_id_for_element(element_idx)
	var selected_idx = 0
	
	for i in range(AudioSettings.AVAILABLE_TRACKS.size()):
		var track = AudioSettings.AVAILABLE_TRACKS[i]
		var track_id = track["id"]
		var track_name = track["name"]
		opt_btn.add_item(track_name, track_id)
		if track_id == current_track_id:
			selected_idx = opt_btn.get_item_count() - 1
			
	opt_btn.selected = selected_idx

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
	if options_menu:
		options_menu.visible = false
	_update_carousel_page(0)

func _on_play_auto_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/cena_auto.tscn")

func _on_play_options_pressed() -> void:
	options_menu.visible = true
	menu.visible = false
	level_selector.visible = false
	_setup_options_ui()

func _on_btn_options_back_pressed() -> void:
	if audio_player.playing:
		audio_player.stop()
	options_menu.visible = false
	menu.visible = true

func _on_volume_slider_value_changed(value: float) -> void:
	AudioSettings.set_master_volume_percent(value)
	lbl_vol_value.text = str(int(value)) + "%"

func _on_btn_test_sound_pressed() -> void:
	if audio_player.playing:
		audio_player.stop()
	var stream = AudioSettings.get_track_for_element(0)
	if stream:
		audio_player.stream = stream
		audio_player.play()

func _on_opt_fire_item_selected(index: int) -> void:
	var track_id = opt_fire.get_item_id(index)
	AudioSettings.set_element_track(0, track_id)

func _on_opt_water_item_selected(index: int) -> void:
	var track_id = opt_water.get_item_id(index)
	AudioSettings.set_element_track(1, track_id)

func _on_opt_wind_item_selected(index: int) -> void:
	var track_id = opt_wind.get_item_id(index)
	AudioSettings.set_element_track(2, track_id)

func _on_opt_electricity_item_selected(index: int) -> void:
	var track_id = opt_electricity.get_item_id(index)
	AudioSettings.set_element_track(3, track_id)

func _on_btn_reset_defaults_pressed() -> void:
	AudioSettings.reset_to_defaults()
	_setup_options_ui()

func _play_track(index: int) -> void:
	if audio_player.playing:
		audio_player.stop()
	var stream = AudioSettings.get_track_for_element(index)
	if stream:
		audio_player.stream = stream
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
