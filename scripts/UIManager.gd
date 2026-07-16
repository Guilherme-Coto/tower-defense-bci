extends MarginContainer

const label_prefab = preload("res://scenes/lbl_text_log.tscn") 

@onready var tower = get_tree().get_first_node_in_group("tower")
@onready var lbl_element = $VBox_element/lbl_element
@onready var log_container = $PanelContainer/LogScrollBar/VBCLogs
@onready var log_scrollbar = $PanelContainer/LogScrollBar

#botões
@onready var btn_fire = $VBoxContainer/HBoxContainer/btn_fire
@onready var btn_water = $VBoxContainer/HBoxContainer/btn_water
@onready var btn_wind = $VBoxContainer/HBoxContainer/btn_wind
@onready var btn_earth = $VBoxContainer/HBoxContainer/btn_earth

var blink_times = {
	"fire" : 5,
	"water" : 4,
	"earth" : 3,
	"wind" : 2.5
}

#diferentes timers
var timer_fire : Timer
var timer_water : Timer
var timer_earth : Timer
var timer_wind : Timer

func _ready() -> void:
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
	
	timer_fire.start()
	timer_water.start()
	timer_wind.start()
	timer_earth.start()

func _on_timer_fire_timeout():
	if btn_fire.disabled: #mostra o botão
		btn_fire.modulate.a = 1.0  
		btn_fire.disabled = false
	else: #esconde o botão
		btn_fire.modulate.a = 0.0 
		btn_fire.disabled = true

func _on_timer_water_timeout():
	if btn_water.disabled: #mostra o botão
		btn_water.modulate.a = 1.0  
		btn_water.disabled = false
	else: #esconde o botão
		btn_water.modulate.a = 0.0 
		btn_water.disabled = true
	
func _on_timer_wind_timeout():
	if btn_wind.disabled: #mostra o botão
		btn_wind.modulate.a = 1.0  
		btn_wind.disabled = false
	else: #esconde o botão
		btn_wind.modulate.a = 0.0 
		btn_wind.disabled = true

func _on_timer_earth_timeout():
	if btn_earth.disabled: #mostra o botão
		btn_earth.modulate.a = 1.0  
		btn_earth.disabled = false
	else: #esconde o botão
		btn_earth.modulate.a = 0.0 
		btn_earth.disabled = true
	
func _input(event: InputEvent) -> void:
	if event.is_action_pressed("log"):
		log_scrollbar.visible = not log_scrollbar.visible
		
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
	elif element == Weak_System.ELEMENT.Earth:
		lbl_element.text = "Terra"
		add_text_to_log("O jogador selecionouTerra")

	tower.change_element(element)

func _on_btn_fire_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Fire)

func _on_btn_water_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Water)

func _on_btn_wind_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Wind)

func _on_btn_earth_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Earth)

func add_text_to_log(text):
	#espera que seja carregado
	if log_container == null:
		await get_tree().process_frame
		
	var new_label = label_prefab.instantiate()
	new_label.text = format_text(text);
	log_container.add_child(new_label) 
	#vai seguindo o texto	
	log_scrollbar.scroll_vertical = log_container.size.y
	
func format_text(text):
	var hour = Time.get_time_string_from_system()
	return "[" + hour + "] " + text
