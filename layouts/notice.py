#!/usr/bin/env python3

from dash import html
import base64


def _h(text):
    return html.H3(text, style={"margin": "1.5rem 0 0.5rem", "font-size": "15px", "font-weight": "bold"})

def _p(text):
    return html.P(text, style={"margin": "0 0 0.5rem", "font-size": "14px"})

def _code(text):
    return html.Code(text, style={
        "font-family": "monospace",
        "font-size": "13px",
        "background": "#f0f0f0",
        "padding": "1px 6px",
        "border-radius": "4px",
    })

def _note(text):
    return html.Div(text, style={
        "border-left": "3px solid #b5d4f4",
        "padding": "0.5rem 0.9rem",
        "font-size": "15px",
        "color": "#5f5e5a",
        "margin": "0.75rem 0",
    })

def _sep():
    return html.Hr(style={"border": "none", "border-top": "0.5px solid #d3d1c7", "margin": "1.5rem 0"})

def _cfg(key, desc):
    return html.Div([
        html.Span(_code(key), style={"min-width": "160px", "display": "inline-block"}),
        html.Span(desc, style={"color": "#737373", "font-size": "14px"}),
    ], style={"margin": "0.3rem 0"})

def _vtable(rows):
    return html.Table(
        [html.Tr([
            html.Td(_code(r[0]), style={"padding": "4px 8px", "color": "#737373", "white-space": "nowrap", "font-size": "14px", "border-top": "0.5px solid #e5e5e0", "vertical-align": "top", "width": "140px"}),
            html.Td(r[1], style={"padding": "4px 8px", "font-size": "14px", "border-top": "0.5px solid #e5e5e0"}),
            html.Td(r[2], style={"padding": "4px 8px", "font-size": "14px", "color": "#737373", "text-align": "right", "border-top": "0.5px solid #e5e5e0", "width": "60px"}),
        ]) for r in rows],
        style={"width": "100%", "border-collapse": "collapse"},
    )

def _vgroup(title, rows):
    return html.Div([
        html.Div(title, style={
            "font-size": "13px", "font-weight": "bold", "color": "#737373",
            "text-transform": "uppercase", "letter-spacing": "0.05em",
            "margin-bottom": "6px", "padding-bottom": "4px",
            "border-bottom": "0.5px solid #d3d1c7",
        }),
        _vtable(rows),
    ], style={"margin": "0.75rem 0"})

def _file_block(type_label, pattern, example):
    return html.Div([
        html.Div(type_label, style={"font-weight": "bold", "margin-bottom": "4px", "font-size": "13px"}),
        html.Div(_code(pattern)),
        html.Div(example, style={"font-size": "13px", "color": "#737373", "margin-top": "2px"}),
    ], style={
        "background": "#f0f0f0",
        "border-radius": "6px",
        "padding": "0.6rem 1rem",
        "margin": "0.5rem 0",
    })


# ── Pages disponibles ────────────────────────────────────────────────────────

pages_grid = html.Div([
    html.Div([
        html.Div(title, style={"font-size": "14px", "font-weight": "bold", "margin-bottom": "3px"}),
        html.Div(desc, style={"font-size": "14px", "color": "#737373"}),
    ], style={
        "background": "#f5f5f3",
        "border-radius": "6px",
        "padding": "0.6rem 0.8rem",
    }) for title, desc in [
        ("Séries temporelles",   "Évolution des paramètres sur la période sélectionnée"),
        ("Biais instantanés",    "Écart modèles / observations à chaque instant"),
        ("Biais moyens",         "Biais moyens horaires selon l'échéance"),
        ("Panneaux PV",          "Séries temporelles spécifiques au solaire"),
        ("Profils verticaux",    "Observations AMDAR et sorties opérationnelles en altitude"),
    ]
], style={
    "display": "grid",
    "grid-template-columns": "repeat(auto-fit, minmax(160px, 1fr))",
    "gap": "8px",
    "margin": "0.75rem 0 1rem",
})


# ── Tableau MODELS_CONFIG ────────────────────────────────────────────────────

models_config_table = _vtable([
    ("reader",           "Fichier de lecture de données", ""),
    ("param_key",        "Nom des variables dans les fichiers NetCDF", ""),
    ("is_climatology",   "True si le modèle est une modélisation en mode climat", ""),
    ("category",         "Type de modèle, pour la classification dans les dropdown de la sidebar", ""),
    ("file_prefix",      "Nom du modèle dans le nom de fichier", ""),
    ("default_selection","Modèles affichés par défaut au chargement", ""),
    ("mapping",          "Style graphique du modèle", ""),
    ("max_forecast_days","Echeance de prévision en jours", ""),
])


# ── Contenu principal ────────────────────────────────────────────────────────

notice_content = html.Div(
    [
        # Pages
        html.H2("Pages disponibles", style={"font-size": "17px", "font-weight": "bold", "margin": "1.5rem 0 0.75rem"}),
        pages_grid,
        _sep(),

        # Variables
        html.H2("Paramètres disponibles", style={"font-size": "17px", "font-weight": "bold", "margin": "1.5rem 0 0.5rem"}),

        _vgroup("Atmosphère", [
            ("tmp_2m",       "Température à 2 m",                                                        "°C"),
            ("tmp_10m",      "Température à 10 m",                                                       "°C"),
            ("hum_rel",      "Humidité relative",                                                        "%"),
            ("vent_ff10m",   "Vent moyen à 10 m",                                                        "m/s"),
            ("cumul_RR",     "Cumuls de pluie",                                                          "mm"),
        ]),
        _vgroup("Rayonnement", [
            ("SWD",  "Rayonnement global descendant (SW down)",  "W/m²"),
            ("SWU",  "Rayonnement global montant (SW up)",       "W/m²"),
            ("LWD",  "Rayonnement IR descendant (LW down)",      "W/m²"),
            ("LWU",  "Rayonnement IR montant (LW up)",           "W/m²"),
        ]),
        _vgroup("Flux de surface", [
            ("flx_chaleur_sens", "Flux de chaleur sensible",          "W/m²"),
            ("flx_chaleur_lat",  "Flux de chaleur latente",           "W/m²"),
            ("flx_chaleur_sol",  "Flux de conduction dans le sol",    "W/m²"),
            ("flx_mvt",          "Vitesse de friction",               "m/s"),
            ("tke",              "Énergie cinétique turbulente",      "m²/s²"),
        ]),
        _vgroup("Sol — températures", [
            ("t_surface",         "Température de surface",                                                "°C"),
            ("TG1cm … TG100cm",   "Température du sol à -1, -3, -10, -20, -30, -50, -70 cm et -1 m",     "°C"),
        ]),
        _vgroup("Sol — humidité", [
            ("WG1cm … WG100cm",   "Humidité du sol à -1, -5, -10, -20, -30, -50, -70 cm et -1 m",        "m³/m³"),
        ]),
        _vgroup("Panneaux photovoltaïques (page dédiée)", [
            ("PV",    "Puissance émise par les panneaux solaires",               "W/m²"),
            ("RGD",   "Rayonnement global descendant (capteurs CNR4 / BF5)",    "W/m²"),
            ("RD",    "Rayonnement diffus (capteur BF5)",                        "W/m²"),
            ("INSO",  "Durée d'insolation (capteur BF5)",                       "h"),
        ]),
        _vgroup("Profils verticaux (page dédiée)", [
            ("Température",      "Profil vertical — observations AMDAR + modèles",  "°C"),
            ("Humidité relative","Profil vertical",                                  "%"),
            ("Vent",             "Profil vertical",                                  "m/s"),
        ]),
        _sep(),

        # Légende
        html.H2("Légende des courbes", style={"font-size": "17px", "font-weight": "bold", "margin": "1.5rem 0 0.75rem"}),
        _note(
            "La légende des courbe est affichée dans le menu de gauche, et valable pour les séries temporelles et les biais instantanés et moyens. "
            "L'opacité des courbes diminue avec l'échéance. Le run du jour est affiché pleinement opaque ; "
            "les runs des jours précédents sont progressivement transparents, permettant la superposition des données."
        ),
        _sep(),

        # Fichiers
        html.H2("Format des fichiers d'entrée", style={"font-size": "17px", "font-weight": "bold", "margin": "1.5rem 0 0.75rem"}),
        _p(["Les données sont attendues au format ", html.Strong("NetCDF"), " (", _code(".nc"), ")."]),
        _file_block(
            "Modèle de prévision",
            "modele_date_reseau.nc",
            "ex : arpege_20260101_00.nc",
        ),
        _file_block(
            "Modèle en mode climat",
            "modele.nc",
            "ex : offlinexp1.nc",
        ),
        _note([
            "Le nom du fichier est analysé automatiquement pour identifier le modèle, la date et le réseau.",
            html.Br(),
            html.Strong("• Mode climat ("),
            _code("is_climatology=True"),
            html.Strong(") : "),
            "le fichier est toujours lu. Les courbes sont tracées en fonction de la correspondance des "
            "dates de validité du fichier avec les dates d'affichage sélectionnées. "
            "Aussi, les biais moyens ne sont pas calculés - le modèle étant indépendant de l'échéance, ils seraient identiques aux biais instantanés."
        ]),
        _sep(),

        # Config
        html.H2(["Configuration (fichier ", _code("config.py"), ")"],
                style={"font-size": "17px", "font-weight": "bold", "margin": "1.5rem 0 0.75rem"}),

        _h("Période par défaut"),
        _cfg("start", "Nombre de jours précédents affichés (défaut : 7)"),
        _cfg("end",   "Nombre de jours après aujourd'hui (défaut : 1)"),

        _h("Ajouter un modèle"),
        _cfg("MODELS",       "Ajouter le nom du modèle à la liste"),
        _cfg("MODELS_CONFIG","Créer une entrée avec les clés suivantes :"),
        models_config_table,
        _note([
            "Selon la provenance des données du modèle ajouté : ",
            html.Br(),
            html.Strong("• Via Emigram : "),
            "utiliser ", _code("reader='operationnel'"), " et ", _code("param_key='index_model'"), ".",
            html.Br(),
            html.Strong("• Source externe : "),
            "ajouter un fichier de lecture des données et ajouter le reader dans ", _code("selection_data.py"),
            ", puis déclarer les noms de variables dans ", _code("variables.py"),
            " en créant un nouvel index, pour les faire correspondre à la nomenclature MeteopoleX.",
        ]),

        _h("Ajouter un réseau"),
        _p(["Ajouter le réseau souhaité dans la liste ", _code("RESEAUX"),
            ", au format ", _code("J0:HH_%3600"), "."]),

        _h("Opacité des courbes"),
        _cfg("OPACITY_MIN", "Opacité minimale (défaut : 0.1)"),
        _cfg("OPACITY_MAX", "Opacité maximale (défaut : 1.0)"),

        _h(["Ajouter une variable (fichier ", _code("variables.py"), ")"]),
        _p(["Ajouter/Modifier la variable souhaitée dans le dictionnaire ", _code("VARIABLES"),
            ", et dans la liste ", _code("VARIABLES_PLOT"), "."]),

        html.Br(),
    ],
    style={"text-align": "left", "font-size": "14px", "line-height": "1.7"},
)


layout_notice = html.Div(
    [
        html.Br(),
        html.H1("MeteopoleX"),
        html.Br(),
        html.P(
            "Outil de visualisation et de comparaison de modèles météorologiques "
            "avec les observations sur le site de la Météopole.",
            style={"font-size": "15px", "color": "#5f5e5a"},
        ),
        notice_content,
    ],
    style={
        "margin-left": "50px",
        "text-align": "left", 
        "justifyContent": "center",
        "padding": "20px"}
)


