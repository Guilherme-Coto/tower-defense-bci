extends Node3D

#inimigos para spawnar
const enemy_fire = preload("res://scenes/enemies/enemy_fire.tscn")
const enemy_water = preload("res://scenes/enemies/enemy_water.tscn")
const enemy_wind = preload("res://scenes/enemies/enemy_wind.tscn")
const enemy_electricity= preload("res://scenes/enemies/enemy_electricity.tscn")

@onready var UIManager = get_tree().get_first_node_in_group("UIManager")

@onready var spawner: Path3D = $"../EnemyPath"
@export var time_between_enemies = 3.5
@export var blink_time = 2.0
@export var delay_after_blink = 3.0
@export var auto_spawn = true
@export var reverse_mode = false
@export var random_spawn = false
@export var random_spawn_count = 20

@export var waves = 1

enum SpawnElement { FOGO, AGUA, VENTO, ELETRICIDADE }
@export var spawn_sequence: Array[SpawnElement] = [SpawnElement.FOGO, SpawnElement.AGUA, SpawnElement.VENTO, SpawnElement.ELETRICIDADE]

var enemies_elements = ["Fogo", "Água", "Vento", "Eletricidade"]
const enemies = [enemy_fire, enemy_water, enemy_wind, enemy_electricity]
var index = 0
var is_first_spawn = true

var total_waves = 1
var current_wave = 1

var last_counter_idx = -1
var last_enemy_type = -1

var audio_player: AudioStreamPlayer
var bci: Node

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if AudioSettings:
		delay_after_blink = AudioSettings.get_delay_after_blink()
	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)
	bci = get_tree().get_first_node_in_group("BCI")
	
	if Engine.has_singleton("GameSettings") or get_node_or_null("/root/GameSettings"):
		var gs = get_node_or_null("/root/GameSettings")
		if gs:
			waves = gs.get_waves()
	
	total_waves = waves
	current_wave = 1
	
	if random_spawn:
		var count = waves * 4
		if count <= 0:
			count = random_spawn_count
		spawn_sequence.clear()
		for i in range(count):
			spawn_sequence.append(randi() % 4 as SpawnElement)
		waves = 1
		total_waves = 1
			
	if spawn_sequence.size() > 0:
		if UIManager:
			UIManager.call_deferred("change_next_element", str("Próximo elemento: " + enemies_elements[spawn_sequence[index]]))
			UIManager.call_deferred("update_wave_info", current_wave, total_waves)
		spawn_enemy()

func spawn_enemy(force: bool = false, specific_element: int = -1):
	if waves <= 0 or spawn_sequence.is_empty():
		if bci:
			bci.write_log("Game Finished")
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
		return 
		
	if not auto_spawn and not force:
		return
		
	# Espera o tempo de descanso entre os inimigos
	if auto_spawn:
		UIManager.call_deferred("show_instruction", "Descansa")
		if bci:
			bci.call_deferred("write_log", "Rest")
		if not is_first_spawn:
			await get_tree().create_timer(time_between_enemies).timeout
		else:
			is_first_spawn = false
			await get_tree().create_timer(3.0).timeout
			
		UIManager.call_deferred("hide_instruction")
	
	var current_enemy_type = spawn_sequence[index]
	
	if specific_element != -1:
		current_enemy_type = specific_element
	
	var counter_idx = 0
	if auto_spawn:
		var max_multiplier = -1.0
		for attack_elem in [0, 1, 2, 3]:
			var mult = Weak_System.get_damage_mult(attack_elem, current_enemy_type)
			if mult > max_multiplier:
				max_multiplier = mult
				counter_idx = attack_elem
				
		var track_name = AudioSettings.get_track_name_for_element(counter_idx)
		
		if not reverse_mode:
			print("A tocar música: " + track_name + " (selecionou " + enemies_elements[counter_idx] + " para combater " + enemies_elements[current_enemy_type] + ")")
			if bci:
				bci.call_deferred("write_log", "Start Listen")
			audio_player.stream = AudioSettings.get_track_for_element(counter_idx)
			audio_player.play()
			
			UIManager.call_deferred("show_instruction", "Presta atenção (" + enemies_elements[counter_idx] + ")")
			
			# Toca 5 segundos
			await get_tree().create_timer(5.0).timeout
			audio_player.stop()
			if bci:
				bci.call_deferred("write_log", "End Listen")
			
			# Pisca a caixa
			UIManager.call_deferred("show_instruction", "Olha para o quadrado")
			UIManager.call_deferred("active_box_blink")
			
			# Espera blink_time segundos
			await get_tree().create_timer(blink_time).timeout
			
			UIManager.call_deferred("desactive_box_blink")
			UIManager.call_deferred("hide_instruction")
			
			if delay_after_blink > 0:
				await get_tree().create_timer(delay_after_blink).timeout
				
			UIManager.call_deferred("active_a_button", counter_idx)
			UIManager.call_deferred("show_instruction", "Imagina")
			if bci:
				bci.call_deferred("write_log", "Imagine")
			
		else:
			# Reverse mode: Imagine -> Select
			UIManager.call_deferred("show_instruction", "Próximo inimigo: " + enemies_elements[current_enemy_type])
			await get_tree().create_timer(2.0).timeout
			
			UIManager.call_deferred("show_instruction", "Olha para o quadrado")
			UIManager.call_deferred("active_box_blink")
			
			await get_tree().create_timer(blink_time).timeout
			
			UIManager.call_deferred("desactive_box_blink")
			UIManager.call_deferred("hide_instruction")
			
			if delay_after_blink > 0:
				await get_tree().create_timer(delay_after_blink).timeout
				
			UIManager.call_deferred("active_a_button", counter_idx)
			UIManager.call_deferred("show_instruction", "Pensa na musica")
			if bci:
				bci.call_deferred("write_log", "Imagine")
		
	var new_enemy = enemies[current_enemy_type].instantiate()
	spawner.add_child(new_enemy)
	
	if auto_spawn and reverse_mode:
		last_counter_idx = counter_idx
		last_enemy_type = current_enemy_type
	if index == spawn_sequence.size() - 1:
		waves -= 1
		current_wave += 1
		index = 0
	else:
		index += 1 #aumenta o index
	
	if spawn_sequence.size() > 0:
		if UIManager:
			UIManager.change_next_element(str("Próximo elemento: " + enemies_elements[spawn_sequence[index]]))
			if waves > 0:
				UIManager.update_wave_info(current_wave, total_waves)

func play_music(element_index: int):
	var stream = AudioSettings.get_track_for_element(element_index)
	if stream:
		audio_player.stream = stream
		audio_player.play()
		print("Servidor OZ ativou a música: " + str(element_index) + " (" + AudioSettings.get_track_name_for_element(element_index) + ")")

func stop_music():
	audio_player.stop()

func play_reverse_music_then_spawn():
	if last_counter_idx != -1 and last_enemy_type != -1:
		var track_name = AudioSettings.get_track_name_for_element(last_counter_idx)
		print("A tocar música: " + track_name + " (selecionou " + enemies_elements[last_counter_idx] + " para combater " + enemies_elements[last_enemy_type] + ")")
		if bci:
			bci.call_deferred("write_log", "Start Listen")
		audio_player.stream = AudioSettings.get_track_for_element(last_counter_idx)
		audio_player.play()
		
		UIManager.call_deferred("show_instruction", "Presta atenção (" + enemies_elements[last_counter_idx] + ")")
		
		await get_tree().create_timer(5.0).timeout
		audio_player.stop()
		if bci:
			bci.call_deferred("write_log", "End Listen")
		UIManager.call_deferred("hide_instruction")
	
	spawn_enemy()
