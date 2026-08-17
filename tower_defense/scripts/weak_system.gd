extends Resource

#aqui vão estar definidas as fraquezas
class_name Weak_System

enum ELEMENT { Fire, Water, Wind, Electricity }

#lista das fraquezas
static var elements = {
	ELEMENT.Fire : {
		ELEMENT.Fire : "null",
		ELEMENT.Water : "weak",
		ELEMENT.Wind : "strong",
		ELEMENT.Electricity : "normal"
	},
	ELEMENT.Water: {
		ELEMENT.Fire : "strong",
		ELEMENT.Water : "null",
		ELEMENT.Wind : "normal",
		ELEMENT.Electricity  : "weak"
	},
	ELEMENT.Wind:{
		ELEMENT.Fire : "weak",
		ELEMENT.Water : "normal",
		ELEMENT.Wind : "null",
		ELEMENT.Electricity : "strong"	
	},
	ELEMENT.Electricity : {
		ELEMENT.Fire : "normal",
		ELEMENT.Water : "strong",
		ELEMENT.Wind : "weak",
		ELEMENT.Electricity : "null"	
	}
}

#função que retorna o dano a dar por multiplicação
static func get_damage_mult(attack_element, defense_element):
	#caso o elemento não esteja listado
	if not elements.has(defense_element):
		return 1
	
	var type = elements[defense_element][attack_element]
	
	if type == "weak":
		return 2
	elif type == "strong":
		return 0.5
	elif type == "null":
		return 0
	else:
		return 1
	
