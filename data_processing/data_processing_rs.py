#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plotly.graph_objects as go

from config.variables import VARIABLES_RS_PLOT, VARIABLES_RS
from config.models import MODELS_PLOT_RS, LEGENDE_HEURES_PROFILS


def build_rs_figures(data_rs, wich_heure, model_choisi):
    """
    Construit les figures de profils verticaux.
    """
    figures = {param: go.Figure() for param in VARIABLES_RS_PLOT}

    courbes_affichees = []

    for selection in wich_heure:

        afficher_legende = selection not in courbes_affichees
        if afficher_legende:
            courbes_affichees.append(selection)

        heure_cfg = LEGENDE_HEURES_PROFILS[selection]

        for param in VARIABLES_RS_PLOT:
            for model in model_choisi:

                model_cfg = MODELS_PLOT_RS.get(model)
                if model_cfg is None:
                    continue

                try:
                    param_data = data_rs[model][selection][param]
                except KeyError:
                    continue

                # Modèle AMDAR : points de mesure discrets, niveau propre par heure
                if model == 'Ab':
                    if not isinstance(param_data, list) or len(param_data) <= 1:
                        continue
                    try:
                        level = data_rs[model][selection]['level']
                    except KeyError:
                        continue

                    figures[param].add_trace(
                        go.Scatter(
                            x=param_data,
                            y=level,
                            mode="markers",
                            name=f"{model_cfg['name']} - {heure_cfg['value']}",
                            line=dict(
                                color=heure_cfg["color"],
                                width=8,
                                dash=model_cfg["line"],
                            ),
                            showlegend=afficher_legende,
                        )
                    )

                # Tous les autres modèles : profil continu, niveau commun
                else:
                    try:
                        level = data_rs[model]['level']
                    except KeyError:
                        continue

                    figures[param].add_trace(
                        go.Scatter(
                            x=param_data,
                            y=level,
                            mode="lines",
                            name=f"{model_cfg['name']} - {heure_cfg['value']}",
                            line=dict(
                                color=heure_cfg["color"],
                                width=4,
                                dash=model_cfg["line"],
                            ),
                            showlegend=afficher_legende,
                        )
                    )

    # Layout final
    for param in VARIABLES_RS_PLOT:
        figures[param].update_layout(
            height=1000,
            width=500,
            xaxis_title=f"{VARIABLES_RS[param]['label']} ({VARIABLES_RS[param]['unit']})",
            yaxis_title="Altitude (m agl)",
            title=param,
            template="plotly_white",
            hovermode="y unified",
        )

    return figures



