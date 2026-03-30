from dash import html

layout_serie_temporelle = html.Div(
    [
        html.H1("Séries temporelles"),

        html.Div(
            id="series-graphs-container",
            #className="row"
        )

    ],
    style={
        "textAlign": "center",
        "justifyContent": "center"
    }
)