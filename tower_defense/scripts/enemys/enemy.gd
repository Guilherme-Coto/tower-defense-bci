extends PathFollow3D

const bullet = preload("res://scenes/bullet.tscn")

@onready var shoot_point = $ShootPoint
@onready var tower = get_tree().get_first_node_in_group("tower")
@onready var UIManager = get_tree().get_first_node_in_group("UIManager")
@onready var spawner = get_tree().get_first_node_in_group("spawner")
@onready var timer_attack = $TimerAttack

@export var speed = 0.5
@export var element : Weak_System.ELEMENT = Weak_System.ELEMENT.Fire
@export var attack_range: float = 3.0

var max_health = 250.0
var health = 250.0

@onready var slime_mesh: MeshInstance3D = get_node_or_null("Body/SlimeMesh")
@onready var health_bar_fill: MeshInstance3D = get_node_or_null("HealthBar/BarFill")
var hit_tween: Tween
var original_mat: ShaderMaterial

func _ready() -> void:
	UIManager.add_text_to_log("Inimigo Spawnado")
	timer_attack.timeout.connect(_on_timer_attack_timeout)
	timer_attack.start()
	
	if slime_mesh and slime_mesh.material_override is ShaderMaterial:
		original_mat = slime_mesh.material_override.duplicate()
		slime_mesh.material_override = original_mat
		
	_update_health_bar()

func _process(delta: float) -> void:
	progress += speed * delta
	
	# Slight cute slime bounce along path
	if has_node("Body"):
		var hop = abs(sin(progress * 4.0)) * 0.08
		$Body.position.y = hop
		
	if health <= 0:
		end()

func receive_damage(damage: float, attack_element: Weak_System.ELEMENT) -> void:
	var mult = Weak_System.get_damage_mult(attack_element, element)
	var final_damage = damage * mult
	health -= final_damage
	_update_health_bar()
	_trigger_hit_flash()
	UIManager.add_text_to_log(str("Vida do inimigo: ", snapped(health, 0.1)))

func _trigger_hit_flash() -> void:
	if not original_mat:
		return
	if hit_tween and hit_tween.is_valid():
		hit_tween.kill()
		
	original_mat.set_shader_parameter("is_hit", true)
	hit_tween = create_tween()
	hit_tween.tween_interval(0.09)
	hit_tween.tween_callback(func(): original_mat.set_shader_parameter("is_hit", false))

func _update_health_bar() -> void:
	if not health_bar_fill:
		return
	var pct = clamp(health / max_health, 0.0, 1.0)
	health_bar_fill.scale.x = pct
	# Center alignment adjustment
	health_bar_fill.position.x = -0.5 * (1.0 - pct)

func _on_timer_attack_timeout() -> void:
	if is_instance_valid(tower):
		var distance = global_position.distance_to(tower.global_position)
		if distance <= attack_range:
			shoot()

func shoot() -> void:
	var new_shoot = bullet.instantiate()
	get_tree().root.add_child(new_shoot)
	new_shoot.change_element(element)
	new_shoot.global_position = shoot_point.global_position
	new_shoot.set_target(tower)

func end() -> void:
	UIManager.add_text_to_log("Inimigo morto")
	if "reverse_mode" in spawner and spawner.reverse_mode:
		spawner.play_reverse_music_then_spawn()
	else:
		spawner.spawn_enemy()
	queue_free()
