extends Node3D

const bullet = preload("res://scenes/bullet.tscn") 

@onready var shoot_point = $ShootPoint
@onready var timer_attack = $TimerAttack
@onready var UIManager = get_tree().get_first_node_in_group("UIManager")

var health = 1000.0

var enemies_in_range : Array[Node3D]
var actual_enemy: Node3D = null #inimigo a focar
var current_element = Weak_System.ELEMENT.Fire 

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	#conecta as funções
	$Range.area_entered.connect(_on_enemy_entered)
	$Range.area_exited.connect(_on_enemy_exited)

	timer_attack.timeout.connect(_on_timer_attack_timeout)
	timer_attack.start()
	
func _process(delta: float) -> void:
	update_target() #vai atualizando o alvo
	
func update_target() -> void:
	#filtra os inimigos pelos que existem
	enemies_in_range = enemies_in_range.filter(func(e): return is_instance_valid(e))
	
	if enemies_in_range.size() > 0:
		actual_enemy = enemies_in_range[0]
	else:
		actual_enemy = null
	
#função que lida com o contacto de um inimigo com a área
func _on_enemy_entered(body: Node3D) -> void:
	if body.is_in_group("enemies"):
		UIManager.add_text_to_log("Torre detetou um inimigo")
		enemies_in_range.append(body)

#função que lida com a saída de um inimigo da área
func _on_enemy_exited(body: Node3D) -> void:
	enemies_in_range.erase(body)

#função do timer
func _on_timer_attack_timeout() -> void:
	if actual_enemy and is_instance_valid(actual_enemy):
		shoot()

#função de disparar
func shoot():
	var new_shoot = bullet.instantiate()
	get_tree().root.add_child(new_shoot) 
	new_shoot.change_element(current_element)
	new_shoot.global_position = shoot_point.global_position	
	new_shoot.set_target(actual_enemy)
	
func receive_damage(damage: float):
	#retira vida do inimigo
	health -= damage 
	print("Vida deste inimigo: ", health)
	
func change_element(new_element: Weak_System.ELEMENT):
	current_element = new_element
