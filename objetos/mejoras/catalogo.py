def _aplicar_disparo_rapido(player):
    """
    Placeholder del paso 1.
    En el paso 2 se aplicara el cooldown real en attack_launcher1.
    """
    return None


MEJORAS = {
    "disparo_rapido": {
        "id": "disparo_rapido",
        "nombre": "Disparo rapido",
        "descripcion": "Reduce el tiempo entre disparos del ataque basico.",
        "coste_adn": 10,
        "apply": _aplicar_disparo_rapido,
    },
}


def obtener_mejora(mejora_id):
    return MEJORAS.get(mejora_id)


def existe_mejora(mejora_id):
    return mejora_id in MEJORAS


def listar_mejoras():
    return list(MEJORAS.values())
