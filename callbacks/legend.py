from dash import Input, Output, callback, html
from config.config import MODELS_CONFIG, CONFIG_OBS


def get_categories():
    return list(dict.fromkeys(cfg['category'] for cfg in MODELS_CONFIG.values()))

def category_dropdown_id(cat_name):
    return f"dropdown_cat_{cat_name.lower().replace('é','e').replace(' ','_')}"

def build_cat_selected(category_values):
    return {cat: (vals or []) for cat, vals in zip(get_categories(), category_values)}

def filter_model(model_name, cat_selected):
    keys = list(MODELS_CONFIG[model_name]['mapping'].keys())
    cat = MODELS_CONFIG[model_name]['category']
    return [v for v in cat_selected.get(cat, []) if v in keys]


CATEGORIES = get_categories()


@callback(
    Output("common-legend", "children"),
    Input("dropdown_cat_observations", "value"),
    *[Input(category_dropdown_id(cat), "value") for cat in CATEGORIES]
)
def update_legend(obs_selection, *category_values):
    items = []
    cat_selected = build_cat_selected(category_values)

    # Observations
    if obs_selection and "Obs" in obs_selection:
        color = CONFIG_OBS["Obs"]["mapping"]["color"]
        items.append(_legend_item("Observations", color, "solid"))

    # Obs corrigées (automatiques)
    if obs_selection and "Obs" in obs_selection:
        color = CONFIG_OBS["Obs_corr"]["mapping"]["color"]
        items.append(_legend_item("Observations corrigées", color, "solid"))

    # Modèles
    for model_name, cfg in MODELS_CONFIG.items():
        selection = filter_model(model_name, cat_selected)
        for label in selection:
            if label in cfg["mapping"]:
                _, style = cfg["mapping"][label]
                color = style.get("color", "gray")
                dash = style.get("dash", "solid")
                items.append(_legend_item(label, color, dash))

    return items


def _legend_item(label, color, dash_style):
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

