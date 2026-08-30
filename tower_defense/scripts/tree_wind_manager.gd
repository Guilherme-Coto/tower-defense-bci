extends Node3D

const tree_wind_shader = preload("res://shaders/tree_wind.gdshader")

func _ready() -> void:
	for child in get_children():
		_apply_wind_to_node(child)

func _apply_wind_to_node(node: Node) -> void:
	if node is MeshInstance3D:
		_setup_mesh_wind(node)
	for child in node.get_children():
		_apply_wind_to_node(child)

func _setup_mesh_wind(mesh_inst: MeshInstance3D) -> void:
	var node_name = mesh_inst.name.to_lower()
	var mesh_name = ""
	if mesh_inst.mesh:
		mesh_name = mesh_inst.mesh.resource_name.to_lower()
		
	var is_leaf = "leaf" in node_name or "object_6" in node_name or "leaf" in mesh_name
	
	# Only apply shader to leaves/foliage. The trunk remains completely still/solid!
	if not is_leaf:
		return
		
	var active_mat = mesh_inst.get_active_material(0)
	var orig_tex: Texture2D = null
	var orig_tint: Color = Color.WHITE
	
	if active_mat is StandardMaterial3D:
		orig_tex = active_mat.albedo_texture
		orig_tint = active_mat.albedo_color
	elif active_mat is BaseMaterial3D:
		orig_tex = active_mat.albedo_texture
		orig_tint = active_mat.albedo_color
		
	var shader_mat = ShaderMaterial.new()
	shader_mat.shader = tree_wind_shader
	if orig_tex:
		shader_mat.set_shader_parameter("texture_albedo", orig_tex)
	shader_mat.set_shader_parameter("color_tint", orig_tint)
	shader_mat.set_shader_parameter("wind_speed", 1.4)
	shader_mat.set_shader_parameter("wind_strength", 0.008)
	shader_mat.set_shader_parameter("leaf_flutter_strength", 0.004)
	shader_mat.set_shader_parameter("leaf_flutter_speed", 3.0)
	shader_mat.set_shader_parameter("wind_direction", Vector2(1.0, 0.4))
	shader_mat.set_shader_parameter("alpha_scissor_threshold", 0.5)
	
	mesh_inst.material_override = shader_mat
