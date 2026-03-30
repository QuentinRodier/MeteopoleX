from dash import Input, Output, html, dcc
from app import app
from datetime import date
from config.variables import VARIABLES_PLOT
from config.config import MODELS_CONFIG
from data_processing.data_processing_biais import build_biais_figures


# Calcul automatique des catégories depuis la config
CATEGORIES = list(dict.fromkeys(cfg['category'] for cfg in MODELS_CONFIG.values()))

def category_dropdown_id(cat_name):
    return f"dropdown_cat_{cat_name.lower().replace('é','e').replace(' ','_')}"


category_inputs = [
    Input(category_dropdown_id(cat), "value")
    for cat in CATEGORIES
]


@app.callback(
    Output("biais-graphs-container", "children"),
    [
        Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date"),
    ] + category_inputs,
)
def update_biais(start_day, end_day, *category_values):

    start_day = date.fromisoformat(start_day)
    end_day = date.fromisoformat(end_day)

    cat_selected = {
        cat: (vals or [])
        for cat, vals in zip(CATEGORIES, category_values)
    }

    def filter_model(model_name):
        keys = list(MODELS_CONFIG[model_name]['mapping'].keys())
        cat = MODELS_CONFIG[model_name]['category']
        return [v for v in cat_selected.get(cat, []) if v in keys]

    kwargs = {
        cfg['callback_param']: filter_model(model_name)
        for model_name, cfg in MODELS_CONFIG.items()
    }

    chartB, graphB = build_biais_figures(start_day, end_day, **kwargs)

    graphs = []

    for param in VARIABLES_PLOT:
        graphs.append(
            html.Div(
                dcc.Graph(
                    id=f"graphB_{param}",
                    figure=chartB[param],
                    config={'responsive': True}
                ),
                className="six columns",
                style={'display': 'inline-block'}
            )
        )

    return graphs

