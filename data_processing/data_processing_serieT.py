import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from config.variables import VARIABLES_PLOT, VARIABLES
from config.models import RESEAUX
from config.config import arome_mapping, arpege_mapping, surfex_arp_mapping
#import lecture_mesoNH
#import lecture_surfex
from data.data_loader import data_loader


# Fonction principale appelée par le callback
def build_series_figures(
    start_day,
    end_day,
    reseau_obs,
    #reseau_arp,
    #reseau_aro,
    reseau_arome,
    reseau_arpege,
    show_surfex,
    #reseau_mnh,
    #reseau_surfex,
    #id_users,
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
    for selection in reseau_arpege or []:

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
                )

    # --- Arome Opérationnel ---
    for selection in reseau_arome or []:

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
                )

    # --- Surfex Arpège expérience ---
    if show_surfex:
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
                )

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

    # ------------------------------------------------------------------
    # Layout final
    # ------------------------------------------------------------------
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