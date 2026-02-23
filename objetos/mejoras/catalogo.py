def _aplicar_disparo_rapido(player):
    if getattr(player, "_mejora_disparo_rapido_aplicada", False):
        return

    launcher = getattr(player, "attack_launcher1", None)
    if launcher is None:
        return

    launcher.set_cooldown_multiplier(0.65)
    player._mejora_disparo_rapido_aplicada = True


def _aplicar_disparo_triple(player):
    if getattr(player, "_mejora_disparo_triple_aplicada", False):
        return

    player.disparo_triple_activo = True
    player._mejora_disparo_triple_aplicada = True


MEJORAS = {
    "disparo_rapido": {
        "id": "disparo_rapido",
        "nombre": "Disparo rapido",
        "descripcion": "Reduce el tiempo entre disparos del ataque basico.",
        "coste_adn": 10,
        "asset_path": "assets/mejoras/pocion_rapidez.png",
        "apply": _aplicar_disparo_rapido,
    },
    "disparo_triple": {
        "id": "disparo_triple",
        "nombre": "Disparo triple",
        "descripcion": "Dispara 3 proyectiles con una apertura pequena, estilo escopeta.",
        "coste_adn": 20,
        "asset_path": "assets/mejoras/disparo_triple.png",
        "apply": _aplicar_disparo_triple,
    },
}


def obtener_mejora(mejora_id):
    return MEJORAS.get(mejora_id)


def existe_mejora(mejora_id):
    return mejora_id in MEJORAS


def listar_mejoras():
    return list(MEJORAS.values())
