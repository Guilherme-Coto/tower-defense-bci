extends PathFollow3D

@export var speed = 4.0
@export var element : Weak_System.ELEMENT

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	print("Spawn")


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	progress += speed * delta
	if progress_ratio >= 1.0:
		end()
		
func end():
	print("end of the path")
	queue_free()
