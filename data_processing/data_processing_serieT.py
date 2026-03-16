import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import re

from config.variables import VARIABLES_PLOT, VARIABLES
from config.config import RESEAUX, MODELS_CONFIG, today, end
#import lecture_mesoNH
#import lecture_surfex
from data.data_loader import data_loader


def _apply_opacity(color: str, opacity: float) -> str:
    """
    Convertit une couleur en rgba() avec l'opacité donnée.
    Formats supportés : #RRGGBB, #RGB, rgb(), rgba()
    (couvre tous les formats utilisés dans MODELS_CONFIG)
    """
    opacity = round(max(0.0, min(1.0, opacity)), 3)
    color = color.strip()


    # rgba() existant → remplace juste l'alpha
    m = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)", color)
    if m:
        return f"rgba({m.group(1)},{m.group(2)},{m.group(3)},{opacity})"


    # rgb()
    m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color)
    if m:
        return f"rgba({m.group(1)},{m.group(2)},{m.group(3)},{opacity})"


    # #RRGGBB  ← format utilisé dans ton mapping
    m = re.match(r"#([0-9a-fA-F]{6})", color)
    if m:
        h = m.group(1)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{opacity})"


    # #RGB
    m = re.match(r"#([0-9a-fA-F]{3})", color)
    if m:
        h = m.group(1)
        r, g, b = int(h[0]*2, 16), int(h[1]*2, 16), int(h[2]*2, 16)
        return f"rgba({r},{g},{b},{opacity})"


    # Fallback : couleur inconnue, retournée telle quelle
    return color


# Fonction principale appelée par le callback
def build_series_figures(
    start_day,
    end_day,
    reseau_obs,
    **kwargs,
):

    loaded = data_loader.load_series(start_day, end_day)
    data = loaded["base"]

    figures = {param: go.Figure() for param in VARIABLES_PLOT}

    # --- OBSERVATIONS ---
    if reseau_obs and "Obs" in reseau_obs:
        for param in VARIABLES_PLOT:
            if isinstance(data[param]["Tf"]["values"], (list, np.ndarray)):
                figures[param].add_trace(
                    go.Scatter(
                        x=data[param]["Tf"]["time"],
                        y=data[param]["Tf"]["values"].data,
                        mode="lines",
                        name="Obs",
                        line=dict(color="red"),
                    )
                )

    # --- ARPÈGE ---
    '''arp_mapping = {
        "Arp_J-1_00h": (RESEAUX[0], dict(color="navy", dash="dot"), True),
        "Arp_J-1_12h": (RESEAUX[1], dict(color="mediumslateblue", dash="dot"), "legendonly"),
        "Arp_J0_00h": (RESEAUX[2], dict(color="navy"), True),
        "Arp_J0_12h": (RESEAUX[3], dict(color="mediumslateblue"), True),
    }

    for selection in reseau_arp or []:
        if selection in arp_mapping:
            reseau, style, visible = arp_mapping[selection]
            for param in VARIABLES_PLOT:
                if isinstance(data[param]["Gt"][reseau]["values"], (list, np.ndarray)):
                    figures[param].add_trace(
                        go.Scatter(
                            x=data[param]["Gt"][reseau]["time"],
                            y=data[param]["Gt"][reseau]["values"].data,
                            name=selection,
                            line=style,
                            visible=visible,
                        )
                    )'''

    # --- AROME ANCIENNE VERSION ---
    '''aro_mapping = {
        "Aro_J-1_00h": (RESEAUX[0], dict(color="green", dash="dot")),
        "Aro_J-1_12h": (RESEAUX[1], dict(color="olive", dash="dot")),
        "Aro_J0_00h": (RESEAUX[2], dict(color="green")),
        "Aro_J0_12h": (RESEAUX[3], dict(color="olive")),
    }

    for selection in reseau_aro or []:
        if selection in aro_mapping:
            reseau, style = aro_mapping[selection]
            for param in VARIABLES_PLOT:
                if isinstance(data[param]["Rt"][reseau]["values"], (list, np.ndarray)):
                    figures[param].add_trace(
                        go.Scatter(
                            x=data[param]["Rt"][reseau]["time"],
                            y=data[param]["Rt"][reseau]["values"].data,
                            name=selection,
                            line=style,
                        )
                    )'''

    # --- AROME ENVELOPPE ---
    '''for selection in reseau_arome or []:

        if selection not in arome_mapping:
            continue

        reseau, style = arome_mapping[selection]

        for param in VARIABLES_PLOT:

            block = data[param]["Arome"][reseau]
            time = block["time"]

            # Moyenne
            if isinstance(block.get("values_mean"), pd.Series):
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_mean"],
                        name=f"{selection} moyenne",
                        line=style,
                    )
                )

            # Points spécifiques
            for key, color, label in [
                ("values_P1", "pink", "Point proche") ,
                #("values_P2", "grey", "100% urbain"),
                #("values_P3", "gold", "100% champs"),
                #("values_P4", "brown", "50/50"),
            ]:
            if isinstance(block.get("values_P"), pd.Series):
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_P"],
                        name=f"{selection} Point proche",
                        #line=dict(color=color),
                        line=style
                    )
                )

            # Enveloppe écart-type
            if isinstance(block.get("values_mean_plus_std"), pd.Series):
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_mean_plus_std"],
                        line=dict(color="rgba(0,0,0,0)"),
                        showlegend=False,
                    )
                )
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_mean_moins_std"],
                        fill="tonexty",
                        fillcolor="rgba(0,176,246,0.3)",
                        line=dict(color="rgba(0,0,0,0)"),
                        name=f"{selection} ± std",
                    )
                )

            # Enveloppe min/max
            if isinstance(block.get("values_max"), pd.Series):
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_max"],
                        line=dict(color="rgba(0,0,0,0)"),
                        showlegend=False,
                    )
                )
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_min"],
                        fill="tonexty",
                        fillcolor="rgba(0,15,226,0.2)",
                        line=dict(color="rgba(0,0,0,0)"),
                        name=f"{selection} min/max",
                    )
                )'''

    # --- Arpège Opérationnel ---
    '''for selection in reseau_arpege or []:

        if selection not in arpege_mapping:
            continue

        reseau, style = arpege_mapping[selection]

        for param in VARIABLES_PLOT:

            block = data[param]["Arpege"][reseau]
            time = block["time"]

            if isinstance(block.get("values_P"), pd.Series):
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_P"],
                        name=f"{selection}",
                        line=style,
                        connectgaps=True
                    )
                )'''

    # --- Arome Opérationnel ---
    '''for selection in reseau_arome or []:

        if selection not in arome_mapping:
            continue

        reseau, style = arome_mapping[selection]

        for param in VARIABLES_PLOT:

            block = data[param]["Arome"][reseau]
            time = block["time"]

            if isinstance(block.get("values_P"), pd.Series):
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_P"],
                        name=f"{selection}",
                        line=style,
                        connectgaps=True
                    )
                )'''

    # --- Surfex Arpège expérience ---
    '''if show_surfex:
        for param in VARIABLES_PLOT:

            # Prendre le premier réseau disponible (données identiques pour tous)
            block = data[param].get("Surfex_arpege", {}).get(RESEAUX[0], {})
            time  = block.get("time")

            if isinstance(block.get("values_P"), pd.Series):
                figures[param].add_trace(
                    go.Scatter(
                        x=time,
                        y=block["values_P"],
                        name="SURFEX Arpège",
                        line=surfex_arp_mapping,
                    )
                )'''

    '''# MÉSO-NH UTILISATEURS
    line_styles = ["solid", "dot", "dash", "longdash", "dashdot"]

    for idx, user_id in enumerate(id_users or []):
        if not user_id:
            continue

        data_user = lecture_mesoNH.mesoNH_user(
            start_day, end_day, user_id, VARIABLES_PLOT
        )

        nb_days = (end_day - start_day).days

        for i in range(nb_days + 1):
            day_str = (start_day + datetime.timedelta(days=i)).strftime("%Y%m%d")

            for param in VARIABLES_PLOT:
                try:
                    if isinstance(data_user[day_str][param], (list, np.ndarray)):
                        figures[param].add_trace(
                            go.Scatter(
                                x=data_user[day_str]["time"],
                                y=data_user[day_str][param],
                                name=f"MésoNH id {user_id}",
                                line=dict(
                                    color="black",
                                    dash=line_styles[idx % len(line_styles)],
                                ),
                            )
                        )
                except KeyError:
                    pass

    # SURFEX UTILISATEURS
    for idx, user_id in enumerate(id_users or []):
        if not user_id:
            continue

        data_user = lecture_surfex.surfex_user(
            start_day, end_day, user_id, VARIABLES_PLOT
        )

        nb_days = (end_day - start_day).days

        for i in range(nb_days + 1):
            day_str = (start_day + datetime.timedelta(days=i)).strftime("%Y%m%d")

            for param in VARIABLES_PLOT:
                try:
                    if isinstance(data_user[day_str][param], (list, np.ndarray)):

                        if param in [
                            "flx_mvt",
                            "flx_chaleur_sens",
                            "flx_chaleur_lat",
                            "SWD",
                            "SWU",
                            "LWD",
                            "LWU",
                        ]:
                            x_time = data_user[day_str]["timeFlux"]
                        else:
                            x_time = data_user[day_str]["time"]

                        figures[param].add_trace(
                            go.Scatter(
                                x=x_time,
                                y=data_user[day_str][param],
                                name=f"SURFEX id {user_id}",
                                line=dict(
                                    color="black",
                                    dash=line_styles[idx % len(line_styles)],
                                ),
                            )
                        )
                except KeyError:
                    pass'''
    
    # Modèles opérationnels : boucle générique sur MODELS_CONFIG
    # Chaque modèle expose ses sélections UI via MODEL_UI_MAPPING.
    # Pour chaque sélection active, on trace une courbe par run disponible.

    # Sélections actives par modèle, transmises par le callback
    active_selections = {
        model: kwargs.get(cfg['callback_param'], []) or []
        for model, cfg in MODELS_CONFIG.items()
    }

    for model, cfg in MODELS_CONFIG.items():

        ui_mapping  = MODELS_CONFIG[model]['mapping']
        selections  = active_selections.get(model, [])

        for selection in selections:

            if selection not in ui_mapping:
                continue

            reseau, base_style = ui_mapping[selection]

            for param in VARIABLES_PLOT:

                block = data[param].get(model, {}).get(reseau, {})
                runs  = block.get("runs", {})

                if not runs:
                    continue

                sorted_dates = sorted(runs.keys())
                legend_shown = False

                for date_str in sorted_dates:
                    series = runs[date_str]
                    if not isinstance(series, pd.Series) or series.empty:
                        continue

                    run_date = datetime.datetime.strptime(date_str, "%Y%m%d").date()
                    MAX_FORECAST_DAYS = end
                    OPACITY_MIN = 0.15
                    OPACITY_MAX = 1.0
                    line_color = base_style.get("color", "blue")

                    from itertools import groupby

                    def get_age(t):
                        forecast_date = t.date() if hasattr(t, 'date') else t
                        return max(0, (forecast_date - run_date).days)

                    points = list(zip(series.index, series.values))
                    grouped = groupby(points, key=lambda p: get_age(p[0]))

                    prev_last_point = None
                    first_segment = True

                    for age_days, group in grouped:
                        segment = list(group)
                        if prev_last_point:
                            segment = [prev_last_point] + segment

                        opacity = OPACITY_MAX - (OPACITY_MAX - OPACITY_MIN) * min(age_days / MAX_FORECAST_DAYS, 1.0)
                        color_str = _apply_opacity(line_color, opacity) 

                        seg_x = [p[0] for p in segment]
                        seg_y = [p[1] for p in segment]
                        prev_last_point = segment[-1]

                        figures[param].add_trace(
                            go.Scatter(
                                x=seg_x,
                                y=seg_y,
                                name=f"{selection}",
                                mode="lines",
                                line={**{k: v for k, v in base_style.items() if k != "color"}, "color": color_str},
                                legendgroup=f"{model}_{selection}",
                                showlegend=(not legend_shown and first_segment),
                                connectgaps=True,
                            )
                        )
                        first_segment = False

                    legend_shown = True

    # Layout final
    for param in VARIABLES_PLOT:
        figures[param].update_layout(
            height=450, width=800,
            xaxis_title="Date et heure",
            yaxis_title=VARIABLES[param]["unit"],
            title=VARIABLES[param]["title"],
            showlegend=True,
            hovermode="x unified",
            template="plotly_white",
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )

    return figures

