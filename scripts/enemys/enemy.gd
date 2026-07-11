extends PathFollow3D

const bullet = preload("res://scenes/bullet.tscn") # Cria esta cena no Passo 3!

@onready var shoot_point = $ShootPoint
@onready var tower = get_tree().get_first_node_in_group("tower")

@export var speed = 1.0
@export var element : Weak_System.ELEMENT

var health = 100.0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	print("Inimigo spawnado")

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	progress += speed * delta
	if health <= 0:
		end()


func receive_damage(damage: float, attack_element: Weak_System.ELEMENT):
	#retira vida do inimigo
	health -= damage * Weak_System.get_damage_mult(attack_element, element)
	print("Vida deste inimigo: ", health)

#função de disparar
func shoot():
	var new_shoot = bullet.instantiate()
	get_tree().root.add_child(new_shoot) 
	
	new_shoot.global_position = shoot_point.global_position	
	new_shoot.set_target(tower)

func end():
	queue_free()
