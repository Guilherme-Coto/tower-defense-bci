extends MarginContainer

@onready var tower = get_tree().get_first_node_in_group("tower")
@onready var lbl_element = $VBox_element/lbl_element


func on_button_power_clicket(element : Weak_System.ELEMENT):
	if element == Weak_System.ELEMENT.Fire:
		lbl_element.text = "Fogo"
	elif element == Weak_System.ELEMENT.Water:
		lbl_element.text = "Água"
	elif element == Weak_System.ELEMENT.Wind:
		lbl_element.text = "Vento"
	elif element == Weak_System.ELEMENT.Earth:
		lbl_element.text = "Terra"

	tower.change_element(element)

func _on_btn_fire_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Fire)

func _on_btn_water_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Water)

func _on_btn_wind_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Wind)

func _on_btn_earth_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Earth)
