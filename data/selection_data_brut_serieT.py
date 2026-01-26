from app import app
import datetime

from dash import dcc
import plotly.graph_objects as go

from . import read_aida
from . import read_arome

from config.variables import VARIABLES_PLOT, VARIABLES
from config.models import MODELS, RESEAUX

# -----------------------------------------------------------------------------
#   3. SERIES TEMPORELLES : Comparaison Obs/Modèles
# -----------------------------------------------------------------------------

def selection_data_brut_serieT(start_day, end_day):
    """
    Récupère les données disponibles sur AIDA :
    - Observations Météopole Flux
    - Modèles Arpège, Arome (ancienne et nouvelle version)
    """

    # Conversion des dates en jour de l'année
    start_doy = datetime.datetime(
        start_day.year, start_day.month, start_day.day
    ).strftime('%j')

    end_doy = datetime.datetime(
        end_day.year, end_day.month, end_day.day
    ).strftime('%j')

    data = {}
    charts = {}
    graphs = {}

    # -------------------------------------------------------------------------
    # Boucle principale sur les paramètres
    # -------------------------------------------------------------------------
    for param in VARIABLES_PLOT:

        data.setdefault(param, {})

        # ---------------------------------------------------------------------
        # Observations
        # ---------------------------------------------------------------------
        obs_model = 'Tf'
        data[param][obs_model] = {}

        obs_index = VARIABLES[param]["index_obs"]

        values_obs, time_obs, _ = read_aida.donnees(
            start_doy,
            end_doy,
            str(start_day.year),
            str(end_day.year),
            obs_index,
            obs_model
        )

        data[param][obs_model]['values'] = values_obs
        data[param][obs_model]['time'] = time_obs

        # ---------------------------------------------------------------------
        # Modèles numériques
        # ---------------------------------------------------------------------
        for model in MODELS:

            data[param].setdefault(model, {})

            for reseau in RESEAUX:

                data[param][model].setdefault(reseau, {})

                # -------------------------------------------------------------
                # AROME nouvelle version (enveloppes)
                # -------------------------------------------------------------
                if model == "Arome":

                    model_data = data[param][model][reseau]

                    model_data.update({
                        'values_mean': {},
                        'values_mean_plus_std': {},
                        'values_mean_moins_std': {},
                        'values_max': {},
                        'values_min': {},
                        'values_P1': {},
                        'values_P2': {},
                        'values_P3': {},
                        'values_P4': {},
                        'time': {}
                    })

                    param_arome = VARIABLES[param]['index_model_arome']

                    if param_arome is not None:

                        arome_data = read_arome.donnees(
                            start_day, end_day, reseau, param_arome
                        )

                        if not arome_data.empty:

                            time_index = arome_data.index

                            model_data['values_mean'] = (
                                arome_data.groupby(time_index).mean()[param_arome]
                            )

                            std = arome_data.groupby(time_index).std()[param_arome]

                            model_data['values_mean_plus_std'] = (
                                model_data['values_mean'] + std
                            )
                            model_data['values_mean_moins_std'] = (
                                model_data['values_mean'] - std
                            )

                            model_data['values_max'] = (
                                arome_data.groupby(time_index).max()[param_arome]
                            )
                            model_data['values_min'] = (
                                arome_data.groupby(time_index).min()[param_arome]
                            )

                            model_data['values_P1'] = arome_data.loc[
                                arome_data['Point'] == 11, param_arome
                            ]
                            model_data['values_P2'] = arome_data.loc[
                                arome_data['Point'] == 15, param_arome
                            ]
                            model_data['values_P3'] = arome_data.loc[
                                arome_data['Point'] == 6, param_arome
                            ]
                            model_data['values_P4'] = arome_data.loc[
                                arome_data['Point'] == 1, param_arome
                            ]

                            model_data['time'] = model_data['values_P4'].index

                # -------------------------------------------------------------
                # AROME / ARPEGE ancienne version (AIDA)
                # -------------------------------------------------------------
                else:

                    model_index = f"{VARIABLES[param]['index_model']}_{reseau}"

                    values_mod, time_mod, _ = read_aida.donnees(
                        start_doy,
                        end_doy,
                        str(start_day.year),
                        str(end_day.year),
                        model_index,
                        model
                    )

                    data[param][model][reseau]['values'] = values_mod
                    data[param][model][reseau]['time'] = time_mod

                    # Correction ARPEGE : H-1:59 → H:00
                    if time_mod is not None:
                        for i, ts in enumerate(time_mod):
                            if ts.minute == 59:
                                time_mod[i] = ts + datetime.timedelta(minutes=1)

                    # Décalage des flux à H:30
                    if param in [
                        'flx_mvt', 'flx_chaleur_sens', 'flx_chaleur_lat',
                        'SWD', 'SWU', 'LWD', 'LWU'
                    ]:
                        if time_mod is not None:
                            for i, ts in enumerate(time_mod):
                                time_mod[i] = ts - datetime.timedelta(minutes=30)

        # ---------------------------------------------------------------------
        # Création des figures
        # ---------------------------------------------------------------------
        charts[param] = go.Figure()
        graphs[param] = dcc.Graph(
            id=f'graph_{param}',
            figure=charts[param]
        )

    return data, charts, graphs
