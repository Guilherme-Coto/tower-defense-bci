extends Area3D

@export var speed: float = 15.0
@export var element : Weak_System.ELEMENT

var target: Node3D = null

func _ready() -> void:
	area_entered.connect(_on_area_entered)

func change_element(new_element: Weak_System.ELEMENT):
	element = new_element

func set_target(enemy: Node3D):
	target = enemy

func _process(delta: float) -> void:
	if not is_instance_valid(target):
		queue_free()
		return
		
	var direction = (target.global_position - global_position).normalized()
	global_position += direction * speed * delta

func _on_area_entered(area: Area3D) -> void:
	if not is_instance_valid(target):
		queue_free()
		return
		
	var parent = area.get_parent_node_3d()
	
	if parent == target: #inimigo ataca a torre
		if parent.has_method("receive_damage"):
			parent.receive_damage(40, element)
		queue_free()
	elif area == target: #a torre ataca inimigo
		if parent and parent.has_method("receive_damage"):
			parent.receive_damage(40, element)
		queue_free()
