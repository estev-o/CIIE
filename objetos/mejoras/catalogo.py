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


def _aplicar_vida_extra(player, bonus, flag_attr):
    if getattr(player, flag_attr, False):
        return

    bonus = int(bonus)
    player.max_live = int(player.max_live) + bonus
    player._actual_life = min(int(player._actual_life) + bonus, int(player.max_live))
    setattr(player, flag_attr, True)


def _aplicar_vida_extra_s(player):
    _aplicar_vida_extra(player, 10, "_mejora_vida_extra_s_aplicada")


def _aplicar_vida_extra_m(player):
    _aplicar_vida_extra(player, 25, "_mejora_vida_extra_m_aplicada")


def _aplicar_vida_extra_l(player):
    _aplicar_vida_extra(player, 100, "_mejora_vida_extra_l_aplicada")


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
    "vida_extra_s": {
        "id": "vida_extra_s",
        "nombre": "Vida extra S",
        "descripcion": "Aumenta la vida maxima en 10.",
        "coste_adn": 12,
        "asset_path": "assets/mejoras/vida_extra_S.png",
        "apply": _aplicar_vida_extra_s,
    },
    "vida_extra_m": {
        "id": "vida_extra_m",
        "nombre": "Vida extra M",
        "descripcion": "Aumenta la vida maxima en 25.",
        "coste_adn": 30,
        "asset_path": "assets/mejoras/vida_extra_M.png",
        "apply": _aplicar_vida_extra_m,
    },
    "vida_extra_l": {
        "id": "vida_extra_l",
        "nombre": "Vida extra L",
        "descripcion": "Aumenta la vida maxima en 100.",
        "coste_adn": 120,
        "asset_path": "assets/mejoras/vida_extra_L.png",
        "apply": _aplicar_vida_extra_l,
    },
}


def obtener_mejora(mejora_id):
    return MEJORAS.get(mejora_id)


def existe_mejora(mejora_id):
    return mejora_id in MEJORAS


def listar_mejoras():
    return list(MEJORAS.values())
