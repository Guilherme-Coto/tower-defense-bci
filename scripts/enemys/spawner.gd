extends Node3D

#inimigo para spawnar
const ENEMY = preload("res://scenes/enemies/enemy.tscn")

@onready var spawner: Path3D = $"../EnemyPath"

@export var time_spawn = 0.0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	#mensagem só para saber se isto funciona
	print("Spawner ativo")
	spawn_enemy()

func _process(delta: float) -> void:
	time_spawn += delta
	if time_spawn >= 4:
		spawn_enemy()
		time_spawn = 0
		

func spawn_enemy():
	var new_enemy = ENEMY.instantiate()
	spawner.add_child(	new_enemy)
