extends CanvasLayer

const label_prefab = preload("res://scenes/lbl_text_log.tscn") 

@onready var tower = get_tree().get_first_node_in_group("tower")
@onready var LSLManager = get_tree().get_first_node_in_group("LSLManager")

@onready var lbl_element = $UI/VBox_element/lbl_element
@onready var log_container = $UI/PanelContainer/LogScrollBar/VBCLogs
@onready var log_scrollbar = $UI/PanelContainer/LogScrollBar
@onready var box_blink = $UI/VBoxBlinkContainer/BoxBlink

#botões
@onready var btn_fire = $UI/VBoxContainer/HBoxContainer/btn_fire
@onready var btn_water = $UI/VBoxContainer/HBoxContainer/btn_water
@onready var btn_wind = $UI/VBoxContainer/HBoxContainer/btn_wind
@onready var btn_electricity = $UI/VBoxContainer/HBoxContainer/btn_electricity

@onready var pause_menu = $PauseMenu

var blink_times = {
	"fire" : 0.2,
	"water" : 0.250,
	"earth" : 0.333,
	"wind" : 0.500
}

var box_blink_time = 0.250

#diferentes timers
var timer_fire : Timer
var timer_water : Timer
var timer_earth : Timer
var timer_wind : Timer

var timer_box_blink : Timer

var buttons_blink = false
var box_isblinking = false


var timers_list : Array[Timer] = []
var actual_index : int = 0
var timer_alter : Timer


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS # Permite que este nó continue ativo para despausar
	
	add_text_to_log("Sistema de Log/UI iniciado")
	
	#dá set aos timers
	#timer botão de fogo
	timer_fire = Timer.new()
	timer_fire.wait_time = blink_times["fire"]
	timer_fire.timeout.connect(_on_timer_fire_timeout)
	#timer botão de água
	timer_water = Timer.new()
	timer_water.wait_time = blink_times["water"]
	timer_water.timeout.connect(_on_timer_water_timeout)
	#timer botão de vento
	timer_wind = Timer.new()
	timer_wind.wait_time = blink_times["wind"]
	timer_wind.timeout.connect(_on_timer_wind_timeout)
	#timer botão de terra
	timer_earth = Timer.new()
	timer_earth.wait_time = blink_times["earth"]
	timer_earth.timeout.connect(_on_timer_earth_timeout)
	
	#adiciona os timers à cena
	add_child(timer_fire)
	add_child(timer_water)
	add_child(timer_wind)
	add_child(timer_earth)
	
	#coloca os timers na lista
	timers_list = [timer_fire, timer_water, timer_wind, timer_earth]
	
	#inicializa o timer que altera de 3 em 3 segundos
	timer_alter = Timer.new()
	timer_alter.wait_time = 3.0
	timer_alter.timeout.connect(_on_timer_alter_timeout)
	add_child(timer_alter)

	#configura o timer do quadrado
	timer_box_blink = Timer.new()
	timer_box_blink.wait_time = box_blink_time
	timer_box_blink.timeout.connect(_on_timer_box_blink_timeout)
	add_child(timer_box_blink)

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("log"):
		log_scrollbar.visible = not log_scrollbar.visible
	
	if event.is_action_pressed("blink_buttons"):
		if buttons_blink:
			timer_alter.stop()
			timers_list[actual_index].stop()
			
			#ativa os botões
			btn_fire_enable()
			btn_water_enable()
			btn_wind_enable()
			btn_electricity_enable()
			
			buttons_blink = false
		else:
			#renicia o ciclo
			actual_index = 0
			timer_alter.start()
			timers_list[actual_index].start()

			buttons_blink = true
	elif event.is_action_pressed("box_blink"):
		if box_isblinking:
			timer_box_blink.stop()
			box_isblinking = false
		else:
			timer_box_blink.start()
			box_isblinking = true
	
	if event.is_action_pressed("pause"):		
		toggle_pause()
	
func _on_timer_alter_timeout() -> void:
	timers_list[actual_index].stop()
	_check_btn_active(actual_index)

	actual_index = (actual_index + 1) % timers_list.size()
	
	timers_list[actual_index].start()

func _check_btn_active(indice: int) -> void:
	match indice:
		0: btn_fire_enable()
		1: btn_water_enable()
		2: btn_wind_enable()
		3: btn_electricity_enable()

func _on_timer_fire_timeout():
	if btn_fire.disabled: #mostra o botão
		btn_fire_enable()
	else: #esconde o botão
		btn_fire_disable()

func _on_timer_water_timeout():
	if btn_water.disabled: #mostra o botão
		btn_water_enable()
	else: #esconde o botão
		btn_water_disable()
	
func _on_timer_wind_timeout():
	if btn_wind.disabled: #mostra o botão
		btn_wind_enable()
	else: #esconde o botão
		btn_wind_disable()

func _on_timer_earth_timeout():
	if btn_electricity.disabled: #mostra o botão
		btn_electricity_enable()
	else: #esconde o botão
		btn_electricity_disable() 

#função para o timer piscar
func _on_timer_box_blink_timeout():
	box_blink.visible = not box_blink.visible

#funções de ativação e desativação dos botões
func btn_fire_enable():
	btn_fire.modulate.a = 1.0  
	btn_fire.disabled = false	
	if LSLManager: LSLManager.send_marker("FIRE_MARKER")
func btn_fire_disable():
	btn_fire.modulate.a = 0.0 
	btn_fire.disabled = true
	
func btn_water_enable():
	btn_water.modulate.a = 1.0  
	btn_water.disabled = false
	if LSLManager: LSLManager.send_marker("WATER_MARKER")
func btn_water_disable():
	btn_water.modulate.a = 0.0 
	btn_water.disabled = true
	
func btn_wind_enable():
	btn_wind.modulate.a = 1.0  
	btn_wind.disabled = false
	if LSLManager: LSLManager.send_marker("WIND_MARKER")
func btn_wind_disable():
	btn_wind.modulate.a = 0.0 
	btn_wind.disabled = true

func btn_electricity_enable():
	btn_electricity.modulate.a = 1.0  
	btn_electricity.disabled = false
	if LSLManager: LSLManager.send_marker("ELECTRICITT_MARKER")
func btn_electricity_disable():
	btn_electricity.modulate.a = 0.0 
	btn_electricity.disabled = true

#função de clique em um botão de elemento
func on_button_power_clicket(element : Weak_System.ELEMENT):
	if element == Weak_System.ELEMENT.Fire:
		lbl_element.text = "Fogo"
		add_text_to_log("O jogador selecionou Fogo")
	elif element == Weak_System.ELEMENT.Water:
		lbl_element.text = "Água"
		add_text_to_log("O jogador selecionou Água")
	elif element == Weak_System.ELEMENT.Wind:
		lbl_element.text = "Vento"
		add_text_to_log("O jogador selecionou Vento")
	elif element == Weak_System.ELEMENT.Electricity:
		lbl_element.text = "Eletricidade"
		add_text_to_log("O jogador selecionou Eletricidade")

	if tower: tower.change_element(element)

func _on_btn_fire_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Fire)

func _on_btn_water_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Water)

func _on_btn_wind_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Wind)

func _on_btn_electricity_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Electricity)

func add_text_to_log(text):
	#espera que seja carregado
	if log_container == null:
		await get_tree().process_frame
		
	var new_label = label_prefab.instantiate()
	new_label.text = format_text(text);
	log_container.add_child(new_label) 
	#vai seguindo o texto	
	await get_tree().process_frame
	log_scrollbar.scroll_vertical = int(log_container.size.y)
	
func format_text(text):
	var hour = Time.get_time_string_from_system()
	return "[" + hour + "] " + text


func _on_btn_quit_pressed() -> void:
	get_tree().paused = false 
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_btn_resume_pressed() -> void:
	toggle_pause()

func toggle_pause() -> void:
	#inverte o estado
	get_tree().paused = !get_tree().paused
	pause_menu.visible = get_tree().paused
