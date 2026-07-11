extends Area3D

@export var speed: float = 15.0
var target: Node3D = null

func _ready() -> void:
	area_entered.connect(_on_area_entered)

func configurar_tiro(enemy: Node3D):
	target = enemy

func _process(delta: float) -> void:
	if not is_instance_valid(target):
		queue_free()
		return
		
	var direction = (target.global_position - global_position).normalized()
	global_position += direction * speed * delta

func _on_area_entered(body: Node3D) -> void:
	if body == target:
		print("Bateu no inimigo!")
		queue_free()
