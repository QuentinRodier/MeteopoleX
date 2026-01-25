#!/usr/bin/env python3
import dash

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# ou bien https://intra.cnrm.meteo.fr/MeteopoleX/css.css
#external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css']
external_stylesheets = ['assets/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, title='MeteopoleX')
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, title='MeteopoleX',
import callbacks
#                requests_pathname_prefix='/MeteopoleX/',
#                routes_pathname_prefix='/')
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
server = app.server

