extends Node3D
#este script é unicamente para o modo automático

@onready var tower: Node3D = get_tree().get_first_node_in_group("tower")
@onready var UIManager: CanvasLayer = get_tree().get_first_node_in_group("UIManager")

func _ready() -> void:
	pass

func _process(_delta: float) -> void:
	_auto_play()

func _auto_play() -> void:
	if not is_instance_valid(tower):
		tower = get_tree().get_first_node_in_group("tower")
		if not is_instance_valid(tower):
			return
			
	if not is_instance_valid(UIManager):
		UIManager = get_tree().get_first_node_in_group("UIManager")

	var target_enemy = _get_target_enemy()
	if not target_enemy:
		return

	var enemy_element
	if "element" in target_enemy:
		enemy_element = target_enemy.element
	elif target_enemy.get_parent() and "element" in target_enemy.get_parent():
		enemy_element = target_enemy.get_parent().element
	else:
		return 

	var best_attack_element = _get_counter_element(enemy_element)


	if tower.current_element != best_attack_element:
		if is_instance_valid(UIManager):
			UIManager.active_a_button(best_attack_element)
		else:
			tower.change_element(best_attack_element)

func _get_target_enemy() -> Node3D:
	if is_instance_valid(tower) and tower.actual_enemy and is_instance_valid(tower.actual_enemy):
		return tower.actual_enemy

	var enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in enemies:
		if is_instance_valid(enemy):
			return enemy

	return null

func _get_counter_element(defense_element: Weak_System.ELEMENT) -> Weak_System.ELEMENT:
	var best_element: Weak_System.ELEMENT = Weak_System.ELEMENT.Fire
	var max_multiplier: float = -1.0

	var all_elements = [
		Weak_System.ELEMENT.Fire,
		Weak_System.ELEMENT.Water,
		Weak_System.ELEMENT.Wind,
		Weak_System.ELEMENT.Electricity
	]

	for attack_elem in all_elements:
		var mult = Weak_System.get_damage_mult(attack_elem, defense_element)
		if mult > max_multiplier:
			max_multiplier = mult
			best_element = attack_elem

	return best_element
