from dash import Input, Output, callback, html
from config.config import MODELS_CONFIG, CONFIG_OBS


@callback(
    Output("common-legend", "children"),
    Input("multi_select_line_chart_obs", "value"),
    *[Input(cfg["dropdown_id"], "value") for cfg in MODELS_CONFIG.values()]
)
def update_legend(obs_selection, *model_selections):
    items = []

    # Observations
    if obs_selection and "Obs" in obs_selection:
        color = CONFIG_OBS["Obs"]["mapping"]["color"]
        items.append(_legend_item("Observations", color, "solid"))

    # Obs corrigées
    if obs_selection and "Obs" in obs_selection:
        color = CONFIG_OBS["Obs_corr"]["mapping"]["color"]
        items.append(_legend_item("Observations corrigées", color, "solid"))

    # Modèles
    for (model, cfg), selection in zip(MODELS_CONFIG.items(), model_selections):
        for label in (selection or []):
            if label in cfg["mapping"]:
                _, style = cfg["mapping"][label]
                color = style.get("color", "gray")
                dash = style.get("dash", "solid")
                items.append(_legend_item(label, color, dash))


    return items


def _legend_item(label, color, dash_style):
    """Crée une ligne de légende avec un trait coloré."""
    dash_map = {
        "solid": "none",
        "dot": "4px 2px",
        "dash": "8px 4px",
        "longdash": "16px 4px",
        "dashdot": "8px 4px 2px 4px",
    }
    border_style = dash_map.get(dash_style, "none")

    return html.Div([
        html.Div(style={
            "display": "inline-block",
            "width": "30px",
            "height": "3px",
            "backgroundColor": color,
            "borderTop": f"3px dashed {color}" if dash_style != "solid" else f"3px solid {color}",
            "marginRight": "8px",
            "verticalAlign": "middle",
        }),
        html.Span(label, style={"fontSize": "0.85rem", "verticalAlign": "middle"}),
    ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"})

