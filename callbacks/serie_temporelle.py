from dash import Input, Output, html, dcc
from app import app
from datetime import date
from config.variables import VARIABLES_PLOT
from data_processing.data_processing_serieT import build_series_figures


@app.callback(
    Output("series-graphs-container", "children"),
    [
        Input("multi_select_line_chart_obs", "value"),
        #Input("multi_select_line_chart_ARP", "value"),
        #Input("multi_select_line_chart_ARO", "value"),
        Input("multi_select_line_chart_AROME", "value"),
        #Input("multi_select_line_chart_MNH", "value"),
        #Input("multi_select_line_chart_SURFEX", "value"),
        Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date"),
        #Input("id_user1", "value"),
        #Input("id_user2", "value"),
        #Input("id_user3", "value"),
        #Input("id_user4", "value"),
        #Input("id_user5", "value"),
    ],
)
def update_line(
    reseau_obs,
    #reseau_arp,
    #reseau_aro,
    reseau_arome,
    #reseau_mnh,
    #reseau_surfex,
    start_day,
    end_day,
    #id_user1,
    #id_user2,
    #id_user3,
    #id_user4,
    #id_user5,
):

    if start_day:
        start_day = date.fromisoformat(start_day)
    if end_day:
        end_day = date.fromisoformat(end_day)

    figures = build_series_figures(
        start_day,
        end_day,
        reseau_obs,
        #reseau_arp,
        #reseau_aro,
        reseau_arome,
        #reseau_mnh,
        #reseau_surfex,
        #[id_user1, id_user2, id_user3, id_user4, id_user5],
    )

    # Génération dynamique des Graph
    graphs = []

    for param in VARIABLES_PLOT:
        graphs.append(
            html.Div(
                dcc.Graph(
                    id=f"graph_{param}",
                    figure=figures[param],
                    config={'responsive':True}
                ),
                className="six columns",
                style={'display': 'inline-block'}       #Intéraction zoom / nbr de colonnes
            )
        )

    return graphs