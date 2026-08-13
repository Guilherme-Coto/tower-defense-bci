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
@export var time_between_enemies = 20.0

var time_spawn = 3.0
var waves = 1

var enemies_elements = ["Fogo", "Água", "Vento", "Eletricidade"]

const enemies = [enemy_fire, enemy_water, enemy_wind, enemy_electricity]
var index = 0

var audio_player: AudioStreamPlayer

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)
	spawn_enemy()

func spawn_enemy():
	if waves <= 0:
		logger.write_log("Game Finished")
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
		return 
		
	UIManager.call_deferred("active_box_blink")
	
	if logger.mode_selected == logger.MODE.AUTO:
		var counter_idx = 0
		var max_multiplier = -1.0
		for attack_elem in [0, 1, 2, 3]:
			var mult = Weak_System.get_damage_mult(attack_elem, index)
			if mult > max_multiplier:
				max_multiplier = mult
				counter_idx = attack_elem
				
		var track_names = ["Track1_Fur_Elise", "Track3_Prelude_C_Major", "Track5_The_Four_Seasons", "Track6_Waltz_of_the_flowers"]
		print("A tocar música: " + track_names[counter_idx] + " (selecionou " + enemies_elements[counter_idx] + " para combater " + enemies_elements[index] + ")")
		audio_player.stream = tracks[counter_idx]
		audio_player.play()
		
	await get_tree().create_timer(time_spawn).timeout
	
	if logger.mode_selected == logger.MODE.AUTO:
		audio_player.stop()
		
	UIManager.desactive_box_blink()
	
	var new_enemy = enemies[index].instantiate()
	spawner.add_child(	new_enemy)
	
	if index == enemies.size() - 1:
		waves-=1
		index = 0
	else:
		index+=1 #aumenta o index
	
	
	UIManager.change_next_element(str("Próximo elemento: " + enemies_elements[index]))
	
