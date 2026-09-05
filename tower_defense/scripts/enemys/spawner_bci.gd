extends Node3D

## spawner_bci.gd
## Spawner limpo para o Modo BCI jogável.
## A torre é controlada pela mente (UDP 4242) ou pelas teclas 1, 2, 3, 4.

const enemy_fire = preload("res://scenes/enemies/enemy_fire.tscn")
const enemy_water = preload("res://scenes/enemies/enemy_water.tscn")
const enemy_wind = preload("res://scenes/enemies/enemy_wind.tscn")
const enemy_electricity = preload("res://scenes/enemies/enemy_electricity.tscn")

const ENEMIES = [enemy_fire, enemy_water, enemy_wind, enemy_electricity]
const ELEMENT_NAMES = ["Fogo", "Água", "Vento", "Eletricidade"]

@onready var UIManager = get_tree().get_first_node_in_group("UIManager")
@onready var spawner: Path3D = $"../EnemyPath"
@onready var bci = get_tree().get_first_node_in_group("BCI")

@export var waves: int = 5
@export var rest_duration: float = 2.0
@export var spawn_sequence: Array[int] = [0, 1, 2, 3] # Fogo, Água, Vento, Eletricidade

var total_waves: int = 5
var current_wave: int = 1
var sequence_idx: int = 0
var active_enemy: Node3D = null

func _ready() -> void:
	if Engine.has_singleton("GameSettings") or get_node_or_null("/root/GameSettings"):
		var gs = get_node_or_null("/root/GameSettings")
		if gs:
			waves = gs.get_waves()
			
	total_waves = max(1, waves)
	current_wave = 1
	sequence_idx = 0
	
	if UIManager and UIManager.has_method("update_wave_info"):
		UIManager.update_wave_info(current_wave, total_waves)
		
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("BCI_Gameplay_Started", 0.0)
		
	await get_tree().create_timer(1.5).timeout
	_spawn_next_enemy()

func _spawn_next_enemy() -> void:
	# Se a onda atual acabou, avança para a próxima
	if sequence_idx >= spawn_sequence.size():
		current_wave += 1
		sequence_idx = 0
		
		if current_wave > total_waves:
			print("[SpawnerBCI] Todas as ondas concluídas com sucesso!")
			if bci and bci.has_method("send_bci_marker"):
				bci.send_bci_marker("Game_Won", 0.0)
			await get_tree().create_timer(2.0).timeout
			get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
			return
		else:
			await get_tree().create_timer(2.0).timeout

	if UIManager and UIManager.has_method("update_wave_info"):
		UIManager.update_wave_info(current_wave, total_waves)

	var enemy_elem: int = spawn_sequence[sequence_idx]
	var enemy_name: String = ELEMENT_NAMES[enemy_elem]

	# Atualiza o texto discreto no canto superior esquerdo
	if UIManager and UIManager.has_method("change_next_element"):
		UIManager.change_next_element("Inimigo: " + enemy_name)

	# Marcador BCI de fundo para o Python (sem ruído visual no ecrã)
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("Trial_Start_Enemy_" + enemy_name, 0.0)

	# Instancia o inimigo
	var enemy_scene = ENEMIES[enemy_elem]
	var new_enemy = enemy_scene.instantiate()
	spawner.add_child(new_enemy)
	active_enemy = new_enemy

	sequence_idx += 1

## Chamado por enemy.gd quando um inimigo morre
func spawn_enemy(_force: bool = false, _specific_elem: int = -1) -> void:
	active_enemy = null
	
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("Enemy_Defeated", 0.0)
		bci.send_bci_marker("Rest_Start", 0.0)
		
	await get_tree().create_timer(rest_duration).timeout
	
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("Rest_End", 0.0)
		
	_spawn_next_enemy()

func kill_active_enemy() -> void:
	if active_enemy and is_instance_valid(active_enemy):
		if active_enemy.has_method("end"):
			active_enemy.end()
