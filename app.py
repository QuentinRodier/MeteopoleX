#!/usr/bin/env python3
import dash

external_stylesheets = ['assets/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, title='MeteopoleX')
                requests_pathname_prefix='/MeteopoleX/',
                routes_pathname_prefix='/')
# Do not move this import must stick to right after the definition of app
import callbacks

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
server = app.server
