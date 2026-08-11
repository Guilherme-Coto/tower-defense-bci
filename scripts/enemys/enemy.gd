extends PathFollow3D

const bullet = preload("res://scenes/bullet.tscn") # Cria esta cena no Passo 3!

@onready var shoot_point = $ShootPoint
@onready var tower = get_tree().get_first_node_in_group("tower")
@onready var UIManager = get_tree().get_first_node_in_group("UIManager")
@onready var spawner = get_tree().get_first_node_in_group("spawner")

@export var speed = 1.0
@export var element : Weak_System.ELEMENT
@onready var timer_attack = $TimerAttack

@export var attack_range: float = 3.0

var health = 100.0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	UIManager.add_text_to_log("Inimigo Spawnado")
	timer_attack.timeout.connect(_on_timer_attack_timeout)
	timer_attack.start()
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	progress += speed * delta
	if health <= 0:
		end()


func receive_damage(damage: float, attack_element: Weak_System.ELEMENT):
	#retira vida do inimigo
	health -= damage * Weak_System.get_damage_mult(attack_element, element)
	UIManager.add_text_to_log(str("Vida do inimigo: ",health))

#função do timer
func _on_timer_attack_timeout() -> void:
	if is_instance_valid(tower):
		#só dispara quando estiver dentro da distância
		var distance = global_position.distance_to(tower.global_position)
		print("Distância",distance)
		if distance <= attack_range:
			shoot()

#função de disparar
func shoot():
	var new_shoot = bullet.instantiate()
	get_tree().root.add_child(new_shoot) 
	
	new_shoot.global_position = shoot_point.global_position	
	new_shoot.set_target(tower)

func end():
	UIManager.add_text_to_log("Inimigo morto")
	spawner.spawn_enemy() #spawna o próximo inimigo
	queue_free()
