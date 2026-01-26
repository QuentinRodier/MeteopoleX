#!/usr/bin/env python3

from dash import html
import base64

# -----------------------------------------------------------------------------
#   2. NOTICE
# -----------------------------------------------------------------------------

# Chargement de l'image explicative
notice_image_path = 'assets/fig1.png'
notice_image_base64 = base64.b64encode(
    open(notice_image_path, 'rb').read()
).decode('ascii')


notice_content = html.Div(
    [

        html.H3('Abréviations pour les tracés'),
        html.Br(),

        html.Span(
            'Les différentes courbes de la page "Séries temporelles" sont nommées de la manière suivante :'
        ),

        html.Div(
            [
                html.Span(
                    '"Nom-du-modèle_date-de-run"',
                    style={"font-weight": "bold"}
                )
            ],
            className="twelve columns",
            style={"text-align": "center", "justifyContent": "center"},
        ),

        html.Br(),

        html.Span(
            'Par exemple, on se place le 15 avril : la courbe affichée ce jour-là '
            'nommée "Aro_J-1_12h" est le run d’Arome qui a tourné le 14 avril '
            '(J-1) à 12h.'
        ),

        html.Span(
            [
                html.Span(
                    ' Quant aux 2 dernières cases de sélection, leur nomenclature est pensée sous la forme '
                ),
                html.Span(
                    '"Modèle_Forçages"',
                    style={"font-weight": "bold"}
                ),
                html.Span(
                    '. Ainsi, "MésoNH_Arp" désigne le tracé de MésoNH forcé par Arpège '
                    '(voir les rubriques "Visualisation des runs automatiques de MesoNH" '
                    'et "Visualisation des runs automatiques de SURFEX" pour plus de précisions).'
                ),
            ]
        ),

        html.Br(),
        html.Br(),
        html.Br(),

        html.H3(
            'Pourquoi y a-t-il des tracés en pointillés et pas en trait plein '
            'à la date d’aujourd’hui ?'
        ),

        html.Br(),

        html.Span(
            'Chaque run considéré donne des valeurs à au moins 48h d’échéance. '
            'Ainsi, à une date donnée, les tracés à J0 sont les 24 premières heures '
            'des runs du jour, et ceux à J-1 vont de la 25ème à la 48ème heure des '
            'runs du jour d’avant.'
        ),

        html.Br(),
        html.Br(),

        html.Span(
            'Pour la date actuelle (aujourd’hui), c’est légèrement différent : '
            'le rapatriement des données vers AIDA ne se fait qu’à 6h du matin. '
            'Les données les plus récentes disponibles sont donc celles des runs '
            'de la veille, tracées en pointillés.'
        ),

        html.Br(),

        html.Div(
            [
                html.Img(
                    src=f'data:image/png;base64,{notice_image_base64}',
                    style={'height': '50%', 'width': '50%'}
                )
            ],
            className="twelve columns",
            style={"text-align": "center"},
        ),

        html.Br(),
        html.Br(),
        html.Br(),

        html.H3('Visualisation des données d’AROME'),

        html.Span(
            'Le modèle AROME tourne deux fois par jour, à midi et minuit, '
            'pour un ensemble de 16 points autour de la Météopole.'
        ),

        html.Br(),

        html.Span(
            'Exemple : ',
            style={"font-weight": "bold"}
        ),

        html.Span(
            'Arome_J0_00H Point 50% urbain 50% champs',
            style={"font-weight": "bold"}
        ),

        html.Br(),
        html.Br(),

        html.Span(
            'Sont également représentés : la moyenne des 16 points, '
            'les étendues min-max et l’écart-type.'
        ),

        html.Br(),
        html.Br(),

        html.H3('Visualisation des runs automatiques de MésoNH'),

        html.Span(
            'Chaque jour vers 10h, 3 runs de MésoNH sont lancés :'
        ),

        html.Div(
            [
                html.Span('MesoNH-Aro', style={"font-weight": "bold"}),
                html.Span(' : forcé par Arome 0h du jour.')
            ],
            className="twelve columns",
            style={"text-align": "center"},
        ),

        html.Div(
            [
                html.Span('MesoNH-Arp', style={"font-weight": "bold"}),
                html.Span(' : forcé par Arpège 0h du jour.')
            ],
            className="twelve columns",
            style={"text-align": "center"},
        ),

        html.Div(
            [
                html.Span('MesoNH-Obs', style={"font-weight": "bold"}),
                html.Span(
                    ' : forcé par Arome 0h de l’avant-veille en altitude '
                    '+ observations au sol.'
                )
            ],
            className="twelve columns",
            style={"text-align": "center"},
        ),

        html.Br(),
        html.Br(),

        html.H3('Visualisation des runs automatiques de SURFEX'),

        html.Span(
            'Les runs SURFEX s’exécutent quotidiennement à 10h :'
        ),

        html.Div(
            [
                html.Span('SURFEX_Aro', style={"font-weight": "bold"}),
                html.Span(' : forcé par Arome 00h du jour.')
            ],
            className="twelve columns",
            style={"text-align": "center"},
        ),

        html.Div(
            [
                html.Span('SURFEX_Arp', style={"font-weight": "bold"}),
                html.Span(' : forcé par Arpège 00h du jour.')
            ],
            className="twelve columns",
            style={"text-align": "center"},
        ),

        html.Div(
            [
                html.Span('SURFEX_Obs', style={"font-weight": "bold"}),
                html.Span(' : forcé par les observations de Météopole Flux.')
            ],
            className="twelve columns",
            style={"text-align": "center"},
        ),

        html.Br(),
        html.Br(),

        html.H3('Rejeu de MésoNH'),

        html.Span(
            'Un utilisateur peut lancer un run de MésoNH personnalisé, '
            'forcé par AROME.'
        ),

        html.Br(),
        html.Br(),

        html.Span(
            'Un identifiant unique est fourni pour chaque simulation. '
            'Il permet ensuite de visualiser le run sur la plateforme.'
        ),
    ],
    className="twelve columns",
    style={"text-align": "left", "justifyContent": "center"},
)


layout_notice = html.Div(
    [
        html.Br(),
        html.H1('Précisions relatives aux abréviations et aux modèles utilisés'),
        html.Br(),
        notice_content,
    ],
    className="twelve columns",
    style={"text-align": "center", "justifyContent": "center"},
)
