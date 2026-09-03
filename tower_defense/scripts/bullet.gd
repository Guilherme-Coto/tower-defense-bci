extends Area3D

@export var speed: float = 16.0
@export var element : Weak_System.ELEMENT = Weak_System.ELEMENT.Fire

var target: Node3D = null
var is_active: bool = true

@onready var core_mesh: MeshInstance3D = $CoreMesh
@onready var glow_mesh: MeshInstance3D = $OuterGlowMesh
@onready var trail_particles: GPUParticles3D = $TrailParticles
@onready var impact_particles: GPUParticles3D = $ImpactParticles
@onready var bullet_light: OmniLight3D = $BulletLight

const bullet_shader = preload("res://shaders/bullet_orb.gdshader")

var ELEMENT_THEMES = {
	Weak_System.ELEMENT.Fire: {
		"core": Color(1.0, 0.25, 0.02, 1.0),
		"rim": Color(1.0, 0.85, 0.15, 1.0),
		"light": Color(1.0, 0.5, 0.1, 1.0),
		"particle": Color(1.0, 0.55, 0.1, 0.9),
		"energy": 4.5
	},
	Weak_System.ELEMENT.Water: {
		"core": Color(0.05, 0.5, 1.0, 1.0),
		"rim": Color(0.4, 0.9, 1.0, 1.0),
		"light": Color(0.2, 0.7, 1.0, 1.0),
		"particle": Color(0.4, 0.85, 1.0, 0.9),
		"energy": 3.8
	},
	Weak_System.ELEMENT.Wind: {
		"core": Color(0.2, 0.85, 0.5, 1.0),
		"rim": Color(0.7, 1.0, 0.8, 1.0),
		"light": Color(0.3, 1.0, 0.6, 1.0),
		"particle": Color(0.5, 1.0, 0.7, 0.9),
		"energy": 4.0
	},
	Weak_System.ELEMENT.Electricity: {
		"core": Color(1.0, 0.88, 0.05, 1.0),
		"rim": Color(1.0, 1.0, 0.75, 1.0),
		"light": Color(1.0, 0.95, 0.4, 1.0),
		"particle": Color(1.0, 1.0, 0.5, 1.0),
		"energy": 5.0
	}
}

func _ready() -> void:
	area_entered.connect(_on_area_entered)
	apply_element_theme()

func change_element(new_element: Weak_System.ELEMENT) -> void:
	element = new_element
	if is_inside_tree():
		apply_element_theme()

func apply_element_theme() -> void:
	var theme = ELEMENT_THEMES.get(element, ELEMENT_THEMES[Weak_System.ELEMENT.Fire])
	
	var mat = ShaderMaterial.new()
	mat.shader = bullet_shader
	mat.set_shader_parameter("core_color", theme["core"])
	mat.set_shader_parameter("rim_color", theme["rim"])
	mat.set_shader_parameter("emission_energy", theme["energy"])
	
	if core_mesh:
		core_mesh.material_override = mat
	
	if glow_mesh:
		var glow_mat = mat.duplicate()
		glow_mat.set_shader_parameter("fresnel_power", 1.5)
		glow_mesh.material_override = glow_mat
		
	if bullet_light:
		bullet_light.light_color = theme["light"]
		
	if trail_particles and trail_particles.draw_pass_1:
		var p_mat = trail_particles.draw_pass_1.material
		if p_mat is StandardMaterial3D:
			p_mat = p_mat.duplicate()
			p_mat.albedo_color = theme["particle"]
			trail_particles.draw_pass_1.material = p_mat

	if impact_particles and impact_particles.draw_pass_1:
		var imp_mat = impact_particles.draw_pass_1.material
		if imp_mat is StandardMaterial3D:
			imp_mat = imp_mat.duplicate()
			imp_mat.albedo_color = theme["particle"]
			impact_particles.draw_pass_1.material = imp_mat

func set_target(enemy: Node3D) -> void:
	target = enemy

func _process(delta: float) -> void:
	if not is_active:
		return
		
	if not is_instance_valid(target):
		_destroy_bullet()
		return
		
	var target_pos = target.global_position
	# Aim slightly towards center of target
	if target.has_node("Body"):
		target_pos = target.get_node("Body").global_position
		
	var direction = (target_pos - global_position).normalized()
	global_position += direction * speed * delta
	
	# Slight spin
	if core_mesh:
		core_mesh.rotate_y(8.0 * delta)
		core_mesh.rotate_z(6.0 * delta)

func _on_area_entered(area: Area3D) -> void:
	if not is_active or not is_instance_valid(target):
		_destroy_bullet()
		return
		
	var parent = area.get_parent_node_3d()
	
	if parent == target or area == target:
		if parent and parent.has_method("receive_damage"):
			parent.receive_damage(40, element)
		elif area.has_method("receive_damage"):
			area.receive_damage(40, element)
		_trigger_impact()

func _trigger_impact() -> void:
	is_active = false
	if core_mesh:
		core_mesh.visible = false
	if glow_mesh:
		glow_mesh.visible = false
	if trail_particles:
		trail_particles.emitting = false
		
	if impact_particles:
		impact_particles.restart()
		impact_particles.emitting = true
		
	if bullet_light:
		var tween = create_tween()
		tween.tween_property(bullet_light, "light_energy", 0.0, 0.25)
		
	get_tree().create_timer(0.3).timeout.connect(func(): queue_free())

func _destroy_bullet() -> void:
	is_active = false
	queue_free()
