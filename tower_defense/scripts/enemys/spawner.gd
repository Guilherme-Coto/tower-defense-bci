extends Node3D

#inimigos para spawnar
const enemy_fire = preload("res://scenes/enemies/enemy_fire.tscn")
const enemy_water = preload("res://scenes/enemies/enemy_water.tscn")
const enemy_wind = preload("res://scenes/enemies/enemy_wind.tscn")
const enemy_electricity= preload("res://scenes/enemies/enemy_electricity.tscn")

const track_fire = preload("res://assets/musics/Track1_Fur_Elise.wav")
const track_water = preload("res://assets/musics/Track3_Prelude_C_Major.wav")
const track_wind = preload("res://assets/musics/Track5_The_Four_Seasons.wav")
const track_electricity = preload("res://assets/musics/Track6_Waltz_of_the_flowers.wav")
const tracks = [track_fire, track_water, track_wind, track_electricity]

@onready var logger = get_tree().get_first_node_in_group("logger")
@onready var UIManager = get_tree().get_first_node_in_group("UIManager")

@onready var spawner: Path3D = $"../EnemyPath"
@export var time_between_enemies = 5.0
@export var auto_spawn = true


var waves = 1

enum SpawnElement { FOGO, AGUA, VENTO, ELETRICIDADE }
@export var spawn_sequence: Array[SpawnElement] = [SpawnElement.FOGO, SpawnElement.AGUA, SpawnElement.VENTO, SpawnElement.ELETRICIDADE]

var enemies_elements = ["Fogo", "Água", "Vento", "Eletricidade"]
const enemies = [enemy_fire, enemy_water, enemy_wind, enemy_electricity]
var index = 0
var is_first_spawn = true

var audio_player: AudioStreamPlayer

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)
	
	if spawn_sequence.size() > 0:
		UIManager.call_deferred("change_next_element", str("Próximo elemento: " + enemies_elements[spawn_sequence[index]]))
		spawn_enemy()

func spawn_enemy(force: bool = false, specific_element: int = -1):
	if waves <= 0 or spawn_sequence.is_empty():
		logger.write_log("Game Finished")
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
		return 
		
	if not auto_spawn and not force:
		return
		
	# Espera o tempo de descanso entre os inimigos
	if auto_spawn:
		if not is_first_spawn:
			await get_tree().create_timer(time_between_enemies).timeout
		else:
			is_first_spawn = false
			await get_tree().create_timer(3.0).timeout # pequeno delay inicial

		
	var current_enemy_type = spawn_sequence[index]
	if specific_element != -1:
		current_enemy_type = specific_element
	
	if auto_spawn:
		var counter_idx = 0
		var max_multiplier = -1.0
		for attack_elem in [0, 1, 2, 3]:
			var mult = Weak_System.get_damage_mult(attack_elem, current_enemy_type)
			if mult > max_multiplier:
				max_multiplier = mult
				counter_idx = attack_elem
				
		var track_names = ["Track1_Fur_Elise", "Track3_Prelude_C_Major", "Track5_The_Four_Seasons", "Track6_Waltz_of_the_flowers"]
		print("A tocar música: " + track_names[counter_idx] + " (selecionou " + enemies_elements[counter_idx] + " para combater " + enemies_elements[current_enemy_type] + ")")
		audio_player.stream = tracks[counter_idx]
		audio_player.play()
		
		# Toca 5 segundos
		await get_tree().create_timer(5.0).timeout
		audio_player.stop()
		
		# Pisca a caixa apenas enquanto a pessoa pensa
		UIManager.call_deferred("active_box_blink")
		
		# Pensa 5 segundos
		await get_tree().create_timer(5.0).timeout
		
		UIManager.call_deferred("desactive_box_blink")
		
		# Troca automaticamente
		UIManager.call_deferred("active_a_button", counter_idx)
		
	var new_enemy = enemies[current_enemy_type].instantiate()
	spawner.add_child(new_enemy)
	
	if index == spawn_sequence.size() - 1:
		waves -= 1
		index = 0
	else:
		index += 1 #aumenta o index
	
	if spawn_sequence.size() > 0:
		UIManager.change_next_element(str("Próximo elemento: " + enemies_elements[spawn_sequence[index]]))

func play_music(element_index: int):
	if element_index >= 0 and element_index < tracks.size():
		audio_player.stream = tracks[element_index]
		audio_player.play()
		print("Feiticeiro ativou a música: " + str(element_index))

func stop_music():
	audio_player.stop()
