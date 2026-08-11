extends Node3D

#inimigos para spawnar
const enemy_fire = preload("res://scenes/enemies/enemy_fire.tscn")
const enemy_water = preload("res://scenes/enemies/enemy_water.tscn")
const enemy_wind = preload("res://scenes/enemies/enemy_wind.tscn")
const enemy_electricity= preload("res://scenes/enemies/enemy_electricity.tscn")

@onready var spawner: Path3D = $"../EnemyPath"
@export var time_between_enemies = 20.0

var time_spawn = 0.0

const enemies = [enemy_fire, enemy_water, enemy_wind, enemy_electricity]
var index = 0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	#mensagem só para saber se isto funciona
	spawn_enemy()

func _process(delta: float) -> void:
	time_spawn += delta
	if time_spawn >= time_between_enemies:
		spawn_enemy()
		time_spawn = 0
		

func spawn_enemy():
	var new_enemy = enemies[index].instantiate()
	spawner.add_child(	new_enemy)
	
	if index == enemies.size() - 1:
		index = 0
	else:
		index+=1 #aumenta o index
