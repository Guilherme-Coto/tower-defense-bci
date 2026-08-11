extends Node3D

#inimigos para spawnar
const enemy_fire = preload("res://scenes/enemies/enemy_fire.tscn")
const enemy_water = preload("res://scenes/enemies/enemy_water.tscn")
const enemy_wind = preload("res://scenes/enemies/enemy_wind.tscn")
const enemy_electricity= preload("res://scenes/enemies/enemy_electricity.tscn")

@onready var logger = get_tree().get_first_node_in_group("logger")
@onready var UIManager = get_tree().get_first_node_in_group("UIManager")

@onready var spawner: Path3D = $"../EnemyPath"
@export var time_between_enemies = 20.0

var time_spawn = 3.0
var waves = 1

const enemies = [enemy_fire, enemy_water, enemy_wind, enemy_electricity]
var index = 0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	spawn_enemy()

func spawn_enemy():
	if waves <= 0:
		logger.write_log("Game Finished")
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
		return 
		
	UIManager.call_deferred("active_box_blink")
	await get_tree().create_timer(time_spawn).timeout
	UIManager.desactive_box_blink()
	
	var new_enemy = enemies[index].instantiate()
	spawner.add_child(	new_enemy)
	
	if index == enemies.size() - 1:
		waves-=1
		index = 0
	else:
		index+=1 #aumenta o index
	
