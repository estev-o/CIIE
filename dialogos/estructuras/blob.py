hello_blob = {
    "init": {
        "author": "Blob",
        "text": "Hola, soy Blob",
        "options": [
            {"text": "¿Qué es este sitio?", "next": "sitio"},
            {"text": "¿Cómo he llegado aquí?", "next": "blub"},
            {"text": "¿Qué mejoras vendes aquí?", "next": "tienda"},
            {"text": "Marcho que teño que marchar", "next": None}
        ],
        "options_hint": "W/S para cambiar | ENTER para elegir | ESC para salir",
        "options_hint_controller": "D-Pad para cambiar | A para elegir | B para salir",
        "f": None
    },
    "sitio": {
        "author": "Blob",
        "text": "Este sitio es el laboratorio de Gilbertov. Una dungeon mala mala con bichos muy chungos que te quieren hacer daño.",
        "next": "init",
        "f": None
    },
    "blub": {
        "author": "Blub",
        "text": "Por una serie de malas decisiones que has tomado, te presentaste voluntario para formar parte de un experimento. El objetivo de ese experimento era formar a alguien para que fuese el mejor estudiante. Y saliste tú :V",
        "next": "init",
        "f": None
    },
    "tienda": {
        "author": "Blob",
        "text": "A ver qué tengo por aquí...",
        "next": "tienda_lista",
        "f": None
    },
    "tienda_lista": {
        "author": "Blob",
        "text": "",
        "options": [
            {"text": "Ahora mismo no tengo stock", "next": "init"}
        ],
        "f": None,
        "options_hint": "A/D para cambiar | ENTER para elegir",
        "options_hint_controller": "D-Pad para cambiar | A para elegir",
        "selected_option_name_in_text": True,
        "show_selected_option_info": True,
        "carousel_options": True
    },
    "tienda_compra_pendiente": {
        "author": "Blob",
        "text": "",
        "next": None,
        "f": None
    }
}