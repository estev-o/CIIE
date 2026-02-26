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


def _aplicar_escudo(player):
    if getattr(player, "_mejora_escudo_aplicada", False):
        return

    player.escudo_activo = True
    if hasattr(player, "register_upgrade_cooldown"):
        player.register_upgrade_cooldown(
            "escudo",
            duration_seconds=300.0,
            asset_path="assets/mejoras/escudo.png",
        )
    player._mejora_escudo_aplicada = True

def _aplicar_blub_lava(player):
    if getattr(player, "_mejora_blub_lava_aplicada", False) or getattr(player, "_mejora_fuego_aplicada", False):
        return

    player.blub_lava_activo = True
    if hasattr(player, "register_upgrade_cooldown"):
        player.register_upgrade_cooldown(
            "blub_lava",
            duration_seconds=300.0,
            asset_path="assets/mejoras/blub_lava.png",
            key_hint="F",
        )

    player._walk_asset_file = "assets/Blub/PNG/Slime3/Walk/Slime3_Walk_full.png"
    player._idle_asset_file = "assets/Blub/PNG/Slime3/Idle/Slime3_Idle_full.png"
    # Mantener sincronizado con la comprobacion base de Character y recargar visual al instante.
    player._asset_file = player._walk_asset_file
    if hasattr(player, "load_sprites"):
        player.load_sprites()
    if hasattr(player, "animate"):
        player._curr_anim_list = None
        player._current_frame = 0
        player._anim_timer = 0.0
        player.animate(0.0, moving=False)

    player._mejora_blub_lava_aplicada = True
    player._mejora_fuego_aplicada = True


def _aplicar_super_azulejo(player):
    if getattr(player, "_mejora_super_azulejo_aplicada", False):
        return

    player.super_azulejo_habilitado = True
    if hasattr(player, "register_upgrade_cooldown"):
        player.register_upgrade_cooldown(
            "super_azulejo",
            duration_seconds=180.0,
            asset_path="assets/mejoras/super_azulejo.png",
            key_hint="R",
        )

    player._mejora_super_azulejo_aplicada = True


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
    "escudo": {
        "id": "escudo",
        "nombre": "Escudo",
        "descripcion": "Bloquea un golpe y se recarga cada 5 minutos.",
        "coste_adn": 45,
        "asset_path": "assets/mejoras/escudo.png",
        "apply": _aplicar_escudo,
    },
    "blub_lava": {
        "id": "blub_lava",
        "nombre": "Blub lava",
        "descripcion": "Convierte a Blub en su version de lava. Desbloquea la base para su ataque especial.",
        "coste_adn": 150,
        "asset_path": "assets/mejoras/blub_lava.png",
        "apply": _aplicar_blub_lava,
    },
    "super_azulejo": {
        "id": "super_azulejo",
        "nombre": "Super azulejo",
        "descripcion": "Activa 20s de disparo en 8 direcciones. Recarga en 3 minutos.",
        "coste_adn": 120,
        "asset_path": "assets/mejoras/super_azulejo.png",
        "apply": _aplicar_super_azulejo,
    },
}

_MEJORA_ALIASES = {
    "blub_fuego": "blub_lava",
    "fuego": "blub_lava",
}


def _resolver_mejora_id(mejora_id):
    return _MEJORA_ALIASES.get(mejora_id, mejora_id)


def obtener_mejora(mejora_id):
    return MEJORAS.get(_resolver_mejora_id(mejora_id))


def existe_mejora(mejora_id):
    return _resolver_mejora_id(mejora_id) in MEJORAS


def listar_mejoras():
    return list(MEJORAS.values())
