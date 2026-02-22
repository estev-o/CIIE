hello_blob = {
    "init": {
        "author": "Blob",
        "text": "Hola, soy Blob",
        "options": [
            {"text": "¿Que es este sitio?", "next": "sitio"},
            {"text": "¿Como he llegado aquí?", "next": "blub"},
            {"text": "¿Que mejoras vendes aqui?", "next": "tienda"},
            {"text": "Marcho que teño que marchar", "next": None}
        ],
        "f": None
    },
    "sitio": {
        "author": "Blob",
        "text": "Este sitio es el laboratorio de Gilbertov. Una dungeon mala mala con bichos pila chungos que te quieren hacer daño.",
        "next": "init",
        "f": None
    },
    "blub": {
        "author": "Blub",
        "text": "Por una serie de malas decisiones que has tomado, te presentaste voluntario para formar parte de un experimento. El objetivo de ese experimento era formar a alguien para que fuese el mejor estudiante. Y saliste tu :V",
        "next": "init",
        "f": None
    },
    "tienda": {
        "author": "Blob",
        "text": "A ver que tengo por aqui...",
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
        "options_hint": "Flechas para cambiar | ENTER para elegir",
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
