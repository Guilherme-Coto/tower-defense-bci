extends CanvasLayer

@onready var tower = get_tree().get_first_node_in_group("tower")

func on_button_power_clicket(element : Weak_System.ELEMENT):
	if element == Weak_System.ELEMENT.Fire:
		print("Selecionou Fogo")
	elif element == Weak_System.ELEMENT.Water:
		print("Selecionou Àgua")
	elif element == Weak_System.ELEMENT.Wind:
		print("Selecionou Vento")		
	elif element == Weak_System.ELEMENT.Earth:
		print("Selecionou Terra")
		
	tower.change_element(element)

func _on_btn_fire_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Fire)

func _on_btn_water_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Water)

func _on_btn_wind_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Wind)

func _on_btn_earth_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Earth)
