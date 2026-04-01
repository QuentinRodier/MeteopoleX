import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import re
import matplotlib.colors as mcolors
from itertools import groupby

from config.variables import VARIABLES_PLOT, VARIABLES
from config.config import RESEAUX, MODELS_CONFIG, CONFIG_OBS, today, end, OPACITY_MAX, OPACITY_MIN
#import lecture_mesoNH
#import lecture_surfex
from data.data_loader import data_loader


def _apply_opacity(color: str, opacity: float) -> str:
    opacity = round(max(0.0, min(1.0, opacity)), 3)
    color = color.strip()

    # rgba() e
    m = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)", color)
    if m:
        return f"rgba({m.group(1)},{m.group(2)},{m.group(3)},{opacity})"

    # rgb()
    m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color)
    if m:
        return f"rgba({m.group(1)},{m.group(2)},{m.group(3)},{opacity})"

    try:
        r, g, b = mcolors.to_rgb(color)  
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return f"rgba({r},{g},{b},{opacity})"
    except ValueError:
        return color  # fallback : couleur inconnue, retournée telle quelle

def _filter_series_on_timerange(series, start_day, end_day):
    start_dt = datetime.datetime.combine(start_day, datetime.time.min)
    end_dt   = datetime.datetime.combine(end_day, datetime.time.max)
    return series[(series.index >= start_dt) & (series.index <= end_dt)]

def _get_line_style(base_style):
    CUSTOM_KEY = {'color', "mode", "marker_size"}
    return {k: v for k, v in base_style.items() if k not in CUSTOM_KEY}

def _add_trace(fig, x, y, name, base_style, opacity, legendgroup, showlegend):
    trace_mode = base_style.get("mode", "lines")
    marker_size = base_style.get("marker_size", 6)
    line_color = base_style.get("color", "blue")

    color_str = _apply_opacity(line_color, opacity)
    line_style = _get_line_style(base_style)

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            name=name,
            mode=trace_mode,
            line={"color": color_str, **line_style},
            marker=dict(color=color_str, size=marker_size),
            legendgroup=legendgroup,
            showlegend=showlegend,
            connectgaps=True,
        )
    )


# Fonction principale appelée par le callback
def build_series_figures(
    start_day,
    end_day,
    reseau_obs,
    **kwargs,
):

    #data_loader.clear()

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
                        line=CONFIG_OBS['Obs']['mapping'],
                    )
                )
    
    # --- CORRECTION BILAN D'ÉNERGIE (méthode ratio de Bowen) ---
    # Rn = SWD - SWU + LWD - LWU
    # Bo = H / LE  (ratio de Bowen obs)
    # H_corr  = (Rn - G) * Bo / (1 + Bo)
    # LE_corr = (Rn - G)      / (1 + Bo)

    def _get_obs_series(data, param):
        """Extrait la série obs d'un paramètre sous forme pd.Series, ou None."""
        try:
            vals  = data[param]["Tf"]["values"]
            times = data[param]["Tf"]["time"]
            if not isinstance(vals, (list, np.ndarray)) or len(vals) == 0:
                return None
            return pd.Series(
                vals.data if hasattr(vals, "data") else np.asarray(vals),
                index=pd.DatetimeIndex(times),
                name=param,
            )
        except (KeyError, TypeError):
            return None

    _required_bowen = {"SWD", "SWU", "LWD", "LWU", "flx_chaleur_sens", "flx_chaleur_lat"}
    _obs_series = {p: _get_obs_series(data, p) for p in _required_bowen | {"flx_chaleur_sol"}}

    if all(_obs_series[p] is not None for p in _required_bowen):

        # Index commun à toutes les séries obligatoires
        common_idx = _obs_series["SWD"].index

        for p in _required_bowen:
            common_idx = common_idx.intersection(_obs_series[p].index)

        def _align(s):
            return s.reindex(common_idx).astype(float)

        SWD = _align(_obs_series["SWD"])
        SWU = _align(_obs_series["SWU"])
        LWD = _align(_obs_series["LWD"])
        LWU = _align(_obs_series["LWU"])
        H   = _align(_obs_series["flx_chaleur_sens"])
        LE  = _align(_obs_series["flx_chaleur_lat"])
        # G optionnel — 0 si absent
        G   = _align(_obs_series["flx_chaleur_sol"]) if _obs_series["flx_chaleur_sol"] is not None \
            else pd.Series(0.0, index=common_idx)

        Rn = SWD - SWU + LWD - LWU

        Bo = H / LE

        denom = 1.0 + Bo

        # Masque : denom trop proche de 0 
        denom[np.abs(denom) < 0.3] = np.nan   # seuil ajustable

        H_corr  = (Rn - G) * Bo  / denom
        LE_corr = (Rn - G)       / denom

        #Tracé
        for fig_param, obs_series, corr_series, label_corr in [
            ("flx_chaleur_sens", H,   H_corr,  "Obs corrigées"),
            ("flx_chaleur_lat",  LE,  LE_corr, "Obs corrigées"),
        ]:
            if fig_param not in figures:
                continue

            color = CONFIG_OBS['Obs_corr']['mapping']['color']
            opacity_corr = CONFIG_OBS['Obs_corr']['opacity']

            # Masque : points valides dans les deux séries
            mask_valid = obs_series.notna() & corr_series.notna()

            # Découpage en segments continus
            segments = []
            in_seg = False
            start_i = None

            for i, valid in enumerate(mask_valid):
                if valid and not in_seg:
                    start_i = i
                    in_seg = True
                elif not valid and in_seg:
                    segments.append(slice(start_i, i))
                    in_seg = False
            if in_seg:
                segments.append(slice(start_i, len(mask_valid)))

            for seg_idx, seg in enumerate(segments):
                x_seg   = common_idx[seg]
                obs_seg  = obs_series.iloc[seg].values
                corr_seg = corr_series.iloc[seg].values

                x_fill = np.concatenate([x_seg, x_seg[::-1]])
                y_fill = np.concatenate([obs_seg, corr_seg[::-1]])

                figures[fig_param].add_trace(
                    go.Scatter(
                        x=x_fill,
                        y=y_fill,
                        fill="toself",
                        fillcolor=_apply_opacity(color, opacity_corr),
                        line=dict(color="rgba(0,0,0,0)"),
                        name=label_corr,
                        showlegend=(seg_idx==0),
                    )
                )
    
    # Sélections actives par modèle
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

                legend_shown = False

                for date_str, series in runs.items():
                    if not isinstance(series, pd.Series) or series.empty:
                        continue

                    # FILTRAGE TEMPOREL 
                    series = _filter_series_on_timerange(series, start_day, end_day)

                    if series.empty:
                        continue

                    # CAS CLIMATO
                    if cfg.get("is_climatology", False):

                        _add_trace(
                            figures[param],
                            x=series.index,
                            y=series.values,
                            name=selection,
                            base_style=base_style,
                            opacity=OPACITY_MAX,
                            legendgroup=f"{model}_{selection}",
                            showlegend=not legend_shown,
                        )

                        legend_shown = True
                        continue

                    # CAS OPÉRATIONNEL
                    try:
                        run_date = datetime.datetime.strptime(date_str, "%Y%m%d").date()
                    except ValueError:
                        continue  

                    MAX_FORECAST_DAYS = cfg.get('max_forecast_days', 4)

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

                        seg_x = [p[0] for p in segment]
                        seg_y = [p[1] for p in segment]
                        prev_last_point = segment[-1]

                        opacity = OPACITY_MAX - (
                            (OPACITY_MAX - OPACITY_MIN)
                            * min(age_days / MAX_FORECAST_DAYS, 1.0)
                        )

                        _add_trace(
                            figures[param],
                            x=seg_x,
                            y=seg_y,
                            name=selection,
                            base_style=base_style,
                            opacity=opacity,
                            legendgroup=f"{model}_{selection}",
                            showlegend=(not legend_shown and first_segment),
                        )

                        first_segment = False

                    legend_shown = True

    # Max commun pour flx_chaleur_sens et flx_chaleur_lat
    flux_params = ("flx_chaleur_sens", "flx_chaleur_lat")
    global_y_max = -np.inf

    for param in flux_params:
        if param in figures:
            for trace in figures[param].data:
                if trace.y is not None:
                    vals = [v for v in trace.y if v is not None and not np.isnan(float(v))]
                    if vals:
                        global_y_max = max(global_y_max, max(vals))

    global_y_max = global_y_max 
    # Layout final
    for param in VARIABLES_PLOT:

        if param in flux_params:
            yaxis_cfg = dict(range=[-50, global_y_max])
        else:
            yaxis_cfg = {}

        figures[param].update_layout(
            height=500, width=872,
            xaxis=dict(
                title="Date",
                tickformat='%a %d',
            ),
            yaxis=dict(
                title=VARIABLES[param]["unit"],
                **yaxis_cfg,
            ),
            title=VARIABLES[param]["title"],
            showlegend=False,
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

