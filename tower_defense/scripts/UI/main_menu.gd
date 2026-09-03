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
@onready var blink_time_slider = $OptionsMenu/VBoxOptions/GridGameplay/HBoxBlinkTime/BlinkTimeSlider
@onready var blink_time_spin_box = $OptionsMenu/VBoxOptions/GridGameplay/HBoxBlinkTime/SpinBoxBlinkTime
@onready var enemy_health_slider = $OptionsMenu/VBoxOptions/GridGameplay/HBoxEnemyHealth/EnemyHealthSlider
@onready var enemy_health_spin_box = $OptionsMenu/VBoxOptions/GridGameplay/HBoxEnemyHealth/SpinBoxEnemyHealth
@onready var delay_blink_slider = $OptionsMenu/VBoxOptions/GridGameplay/HBoxDelayBlink/DelayBlinkSlider
@onready var delay_blink_spin_box = $OptionsMenu/VBoxOptions/GridGameplay/HBoxDelayBlink/SpinBoxDelayBlink

@onready var camera_3d: Camera3D = get_node_or_null("SubViewportContainer/SubViewport/Camera3D")

var cam_transform_menu: Transform3D

# Posição e rotação exata da câmara de jogo (onde o jogador joga)
var cam_transform_game: Transform3D = Transform3D(
	Vector3(-1, 0, 0),
	Vector3(0, 0.86506176, 0.50166535),
	Vector3(0, 0.50166535, -0.86506176),
	Vector3(1.0698649, 2.3351312, -8.175171)
)

var cam_tween: Tween
var current_page = 0 # 0 = Recall, 1 = Inverse

func _ready() -> void:
	if camera_3d:
		cam_transform_menu = camera_3d.transform
	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)
	_update_carousel_page(0)
	_setup_options_ui()

func _tween_camera(target_transform: Transform3D, duration: float = 1.3) -> void:
	if not camera_3d:
		return
	if cam_tween and cam_tween.is_valid():
		cam_tween.kill()
	
	cam_tween = create_tween().set_parallel(true)
	cam_tween.set_trans(Tween.TRANS_CUBIC)
	cam_tween.set_ease(Tween.EASE_IN_OUT)
	
	# Transição suave de posição
	cam_tween.tween_property(camera_3d, "position", target_transform.origin, duration)
	
	# Transição suave de rotação (slerp com quaternions para evitar gimbal lock)
	var start_quat = camera_3d.quaternion
	var end_quat = target_transform.basis.get_rotation_quaternion()
	cam_tween.tween_method(func(weight: float):
		if is_instance_valid(camera_3d):
			camera_3d.quaternion = start_quat.slerp(end_quat, weight)
	, 0.0, 1.0, duration)

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
	
	# Inicializar configurações de jogabilidade / BCI
	if blink_time_slider and blink_time_spin_box:
		var cur_blink = AudioSettings.get_box_blink_time()
		blink_time_slider.value = cur_blink
		blink_time_spin_box.value = cur_blink
		
	if enemy_health_slider and enemy_health_spin_box:
		var cur_hp = AudioSettings.get_enemy_health()
		enemy_health_slider.value = cur_hp
		enemy_health_spin_box.value = cur_hp
		
	if delay_blink_slider and delay_blink_spin_box:
		var cur_delay = AudioSettings.get_delay_after_blink()
		delay_blink_slider.value = cur_delay
		delay_blink_spin_box.value = cur_delay

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
			btn_tab_recall.modulate = Color(1.0, 1.0, 1.0, 1.0)
		if btn_tab_inverse:
			btn_tab_inverse.disabled = false
			btn_tab_inverse.modulate = Color(0.75, 0.75, 0.8, 0.85)
	else:
		if page_recall:
			page_recall.visible = false
		if page_inverse:
			page_inverse.visible = true
		if btn_tab_recall:
			btn_tab_recall.disabled = false
			btn_tab_recall.modulate = Color(0.75, 0.75, 0.8, 0.85)
		if btn_tab_inverse:
			btn_tab_inverse.disabled = true
			btn_tab_inverse.modulate = Color(1.0, 1.0, 1.0, 1.0)

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
	_tween_camera(cam_transform_game, 1.3)

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
	_tween_camera(cam_transform_menu, 1.3)

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

func _on_blink_time_slider_value_changed(value: float) -> void:
	if blink_time_spin_box and blink_time_spin_box.value != value:
		blink_time_spin_box.value = value
	AudioSettings.set_box_blink_time(value)

func _on_blink_time_spin_box_value_changed(value: float) -> void:
	if blink_time_slider and blink_time_slider.value != value:
		blink_time_slider.value = value
	AudioSettings.set_box_blink_time(value)

func _on_enemy_health_slider_value_changed(value: float) -> void:
	if enemy_health_spin_box and enemy_health_spin_box.value != value:
		enemy_health_spin_box.value = value
	AudioSettings.set_enemy_health(value)

func _on_enemy_health_spin_box_value_changed(value: float) -> void:
	if enemy_health_slider and enemy_health_slider.value != value:
		enemy_health_slider.value = value
	AudioSettings.set_enemy_health(value)

func _on_delay_blink_slider_value_changed(value: float) -> void:
	if delay_blink_spin_box and delay_blink_spin_box.value != value:
		delay_blink_spin_box.value = value
	AudioSettings.set_delay_after_blink(value)

func _on_delay_blink_spin_box_value_changed(value: float) -> void:
	if delay_blink_slider and delay_blink_slider.value != value:
		delay_blink_slider.value = value
	AudioSettings.set_delay_after_blink(value)

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
	_tween_camera(cam_transform_menu, 1.3)

#quatro elementos
func _on_btn_level_fire_water_wind_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/scene_four_elements.tscn")

#funções de mudança de nível -> Imagine
func _on_btn_level_reverse_fire_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_imagine/one_element/scene_reverse_fire.tscn")
func _on_btn_level_reverse_water_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_imagine/one_element/scene_reverse_water.tscn")
func _on_btn_level_reverse_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_imagine/one_element/scene_reverse_wind.tscn")
func _on_btn_level_reverse_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_imagine/one_element/scene_reverse_electricity.tscn")

func _on_btn_level_random_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/scene_random.tscn")

func _on_btn_level_reverse_four_elements_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_imagine/scene_reverse_four_elements.tscn")
func _on_btn_level_reverse_random_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_imagine/scene_reverse_random.tscn")

#funções de mundança de nível -> recall
#elemento único
func _on_btn_level_fire_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/one_element/scene_fire.tscn")

func _on_btn_level_water_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/one_element/scene_water.tscn")

func _on_btn_level_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/one_element/scene_wind.tscn")

func _on_btn_level_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/one_element/scene_electricity.tscn")

#dois elementos
func _on_btn_level_fire_water_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/two_elements/scene_fire_water.tscn")
func _on_btn_level_fire_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/two_elements/scene_fire_wind.tscn")
func _on_btn_level_fire_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/two_elements/scene_fire_electricity.tscn")
func _on_btn_level_water_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/two_elements/scene_water_wind.tscn")

func _on_btn_level_water_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/two_elements/scene_water_electricity.tscn")
func _on_btn_level_wind_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/two_elements/scene_wind_electricity.tscn")

#três elementos
func _on_btn_level_fire_water_wind_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/three_elements/scene_fire_water_wind.tscn")
func _on_btn_level_fire_water_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/three_elements/scene_fire_water_electricity.tscn")
func _on_btn_level_fire_wind_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/three_elements/scene_fire_wind_electricity.tscn")	
func _on_btn_level_water_wind_electricity_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scenes_recall/three_elements/scene_water_wind_electricity.tscn")

#feiticeiro de oz
func _on_play_oz_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/game_scenes/scene_oz.tscn")
