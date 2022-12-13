import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
from datetime import datetime
import dash_daq as daq
# Importar hojas de trabajo de google drive     https://bit.ly/3uQfOvs
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
app.css.append_css({'external_url': '/static/reset.css'})
app.server.static_folder = 'static'
server = app.server

app.layout = dbc.Container([
    dcc.Store(id='store-data-dragado', storage_type='memory'),  # 'local' or 'session'
    dcc.Store(id='store-data-volqueta', storage_type='memory'),  # 'local' or 'session'
    dcc.Store(id='store-data-combustible', storage_type='memory'),  # 'local' or 'session'
    dcc.Store(id='store-data-bitacora', storage_type='memory'),  # 'local' or 'session'

    dcc.Interval(
        id='my_interval',
        disabled=False,
        interval=1 * 1000,
        n_intervals=0,
        max_intervals=1
    ),

    dbc.Row([
        dbc.Col(html.H1(
            "Summary of the Cauca River Material Extraction System by Dredging - PCH Calderas",
            style={'textAlign': 'center', 'color': '#082255', 'font-family': "Franklin Gothic"}), width=12, )
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.H5([
                        'The following interactive dashboard presents the results obtained by a company by extracting the sedimented material from the Cauca River at PCH calderas using the IMS5012 and DRAGMAR2 dredges. The solids are extracted from the site by dump trucks.'])

                ], title="Introduction"),
            ], start_collapsed=True, style={'textAlign': 'left', 'color': '#082255', 'font-family': "Franklin Gothic"}),

        ], style={'color': '#082255', 'font-family': "Franklin Gothic"}),
    ]),
    dbc.Row([
        dbc.Tabs(
            [
                dbc.Tab(dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Row(html.H2(['Daily Summary']),
                                                style={'textAlign': 'center', 'color': '#082255',
                                                       'font-family': "Franklin Gothic"})
                                    ])
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Enter Day:",
                                            id="selec-dia-dia-target",
                                            color="info",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the day entered by the user to know the operation summary for the selected day. Format DD/MM/YYYYYY.",
                                            target="selec-dia-dia-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        dcc.Dropdown(id='Dia',
                                                     options=[],
                                                     # value='4/2/2020',
                                                     style={'font-family': "Franklin Gothic"}
                                                     )
                                    ], xs=3, sm=3, md=3, lg=2, xl=2, ),

                                    # IMS5012
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button(
                                                "IMS5012 Horometer:",
                                                id="horo-ims-dia-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "Displays the time the IMS5012 dredge has been operated for the entered day.",
                                                target="horo-ims-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col([
                                            html.Div(id='horo-ims-dia', style={'font-family': "Franklin Gothic"})
                                        ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                        dbc.Col([
                                            dbc.Button(
                                                "IMS5012 Fuel:",
                                                id="combus-ims-dia-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "This is the amount of fuel used by the dredge IMS5012 for the entered day.",
                                                target="combus-ims-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col(
                                            dbc.Spinner(
                                                children=[html.Div(id='combus-ims-dia',
                                                                   style={'font-family': "Franklin Gothic"})],
                                                size="lg",
                                                color="primary", type="border", fullscreen=True, )
                                            , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                            align='center'),
                                        dbc.Col([
                                            dbc.Button(
                                                "Pumped Volume:",
                                                id="vol-bomb-ims-dia-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "It is the volume of water pumped from the Cauca River, with the dredge IMS5012, to the sediment settling container for a entered day. It is calculated as the pump flow rate multiplied by the operating time (dredge horometer).",
                                                target="vol-bomb-ims-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col(
                                            dbc.Spinner(children=[
                                                html.Div(id='vol-bomb-ims-dia', style={'font-family': "Franklin Gothic"})],
                                                size="lg",
                                                color="primary", type="border", fullscreen=True, )
                                            , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                            align='center'),

                                    ]),
                                    # DRAGMAR2
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button(
                                                "DRAGMAR2 Horometro:",
                                                id="horo-drag-dia-target",
                                                color="success",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "Displays the time the DRAGMAR2 dredge has been operated for the entered day.",
                                                target="horo-drag-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col([
                                            html.Div(id='horo-drag-dia', style={'font-family': "Franklin Gothic"})
                                        ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                        dbc.Col([
                                            dbc.Button(
                                                "DRAGMAR Fuel:",
                                                id="combus-drag-dia-target",
                                                color="success",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "This is the amount of fuel used by the dredge DRAGMAR2 for the entered day.",
                                                target="combus-drag-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col(
                                            dbc.Spinner(
                                                children=[html.Div(id='combus-drag-dia',
                                                                   style={'font-family': "Franklin Gothic"})],
                                                size="lg",
                                                color="primary", type="border", fullscreen=True, )
                                            , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                            align='center'),
                                        dbc.Col([
                                            dbc.Button(
                                                "Pumped Volume:",
                                                id="vol-bomb-drag-dia-target",
                                                color="success",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "It is the volume of water pumped from the Cauca River, with the dredge DRAGMAR2, to the sediment settling containers for a entered day. It is calculated as the pump flow rate multiplied by the operating time (dredge horometer).",
                                                target="vol-bomb-drag-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col(
                                            dbc.Spinner(children=[
                                                html.Div(id='vol-bomb-drag-dia',
                                                         style={'font-family': "Franklin Gothic"})],
                                                size="lg",
                                                color="primary", type="border", fullscreen=True, )
                                            , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                            align='center'),

                                    ]),
                                    # DOOSAN1
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button(
                                                "DOOSAN1 Operation:",
                                                id="horo-doosan1-dia-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "Shows whether the DOOSAN1 backhoe was operated for the entered day.",
                                                target="horo-doosan1-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col([
                                            html.Div(id='horo-doosan1-dia', style={'font-family': "Franklin Gothic"})
                                        ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                        dbc.Col([
                                            dbc.Button(
                                                "DOOSAN1 Fuel:",
                                                id="combus-doosan1-dia-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "This is the amount of fuel used by the DOOSAN1 backhoe for the entered day.",
                                                target="combus-doosan1-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col(
                                            dbc.Spinner(
                                                children=[html.Div(id='combus-doosan1-dia',
                                                                   style={'font-family': "Franklin Gothic"})],
                                                size="lg",
                                                color="primary", type="border", fullscreen=True, )
                                            , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                            align='center'),
                                    ]),
                                    # DOOSAN2
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button(
                                                "DOOSAN2 Operation:",
                                                id="horo-doosan2-dia-target",
                                                color="success",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "Shows whether the DOOSAN2 backhoe was operated for the entered day.",
                                                target="horo-doosan2-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col([
                                            html.Div(id='horo-doosan2-dia', style={'font-family': "Franklin Gothic"})
                                        ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                        dbc.Col([
                                            dbc.Button(
                                                "DOOSAN2 Fuel:",
                                                id="combus-doosan2-dia-target",
                                                color="success",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "This is the amount of fuel used by the DOOSAN2 backhoe for the entered day.",
                                                target="combus-doosan2-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col(
                                            dbc.Spinner(
                                                children=[html.Div(id='combus-doosan2-dia',
                                                                   style={'font-family': "Franklin Gothic"})],
                                                size="lg",
                                                color="primary", type="border", fullscreen=True, )
                                            , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                            align='center'),
                                    ]),
                                    # Zonas
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button(
                                                "Dredged areas:",
                                                id="zona-dia-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "Displays the areas that have been dredged for the entered day. Format: (Channel, Abscissa).",
                                                target="zona-dia-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col([
                                            html.Div(id='zona-dia', style={'font-family': "Franklin Gothic"})
                                        ], style={'textAlign': 'left'}, align='left'),
                                    ]),
                                    dbc.Row(dbc.Col(
                                        dbc.Spinner(children=[dcc.Graph(id="fig-pie-bitacora-dia")], size="lg",
                                                    color="primary", type="border", fullscreen=True, ),
                                        width={'size': 12, 'offset': 0}), ),

                                ])
                            ])
                        ])
                    ]),


                ]), label="Daily Summary", label_style={'color': '#082255', 'font-family': "Franklin Gothic"}),
                dbc.Tab(dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Row(html.H2(['Total Summary']),
                                                style={'textAlign': 'center', 'color': '#082255',
                                                       'font-family': "Franklin Gothic"})
                                    ]),
                                    dbc.Row([
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button(
                                                    "Start Date:",
                                                    id="dia-inicial-acum-target",
                                                    color="info",
                                                    className="me-1",
                                                    n_clicks=0,
                                                    style={'font-family': "Franklin Gothic"},
                                                ),
                                                dbc.Popover(
                                                    "This is the start date of operation.",
                                                    target="dia-inicial-acum-target",
                                                    body=True,
                                                    trigger="hover",
                                                    style={'font-family': "Franklin Gothic"}
                                                ),

                                            ], width=2, align='center', className="d-grid gap-2"),
                                            dbc.Col([
                                                html.Div(id='dia-inicial-acum',
                                                         style={'font-family': "Franklin Gothic"})
                                            ], xs=3, sm=3, md=3, lg=2, xl=2, align="center"),
                                            dbc.Col([
                                                dbc.Button(
                                                    "End Date:",
                                                    id="dia-final-acum-target",
                                                    color="info",
                                                    className="me-1",
                                                    n_clicks=0,
                                                    style={'font-family': "Franklin Gothic"},
                                                ),
                                                dbc.Popover(
                                                    "This is the last day of operation to date.",
                                                    target="dia-final-acum-target",
                                                    body=True,
                                                    trigger="hover",
                                                    style={'font-family': "Franklin Gothic"}
                                                ),

                                            ], width=2, align='center', className="d-grid gap-2"),
                                            dbc.Col([
                                                html.Div(id='dia-final-acum', style={'font-family': "Franklin Gothic"})
                                            ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                                align='center'),

                                        ]),


                                    ]),

                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Operated days:",
                                            id="dias-acum-target",
                                            color="info",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the number of days operated during the project.",
                                            target="dias-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='dias-acum', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),

                                    dbc.Col([
                                        dbc.Button(
                                            "Calendar Days:",
                                            id="dias-calendario-target",
                                            color="info",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "The number of calendar days elapsed during the project.",
                                            target="dias-calendario-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='dias-calendario-acum', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),

                                ]),
                                # IMS5012
                                dbc.Row([
                                        dbc.Col([
                                            dbc.Button(
                                                "IMS5012 Horometer:",
                                                id="horo-ims-acum-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "Shows the time that the IMS5012 dredge has been operated during the entire project.",
                                                target="horo-ims-acum-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col([
                                            html.Div(id='horo-ims-acum', style={'font-family': "Franklin Gothic"})
                                        ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                        dbc.Col([
                                            dbc.Button(
                                                "IMS5012 Fuel:",
                                                id="combus-ims-acum-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "This is the amount of fuel used by the IMS5012 dredge during the entire project.",
                                                target="combus-ims-acum-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col(
                                            dbc.Spinner(
                                                children=[html.Div(id='combus-ims-acum',
                                                                   style={'font-family': "Franklin Gothic"})],
                                                size="lg",
                                                color="primary", type="border", fullscreen=True, )
                                            , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                            align='center'),
                                        dbc.Col([
                                            dbc.Button(
                                                "Pumped Volume:",
                                                id="vol-bomb-ims-acum-target",
                                                color="primary",
                                                style={'font-family': "Franklin Gothic"},
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Popover(
                                                "This is the volume of water that is pumped from the Cauca River, with the dredge IMS5012, to the sediment settling containers during the entire project. It is calculated as the pump flow multiplied by the operating time (dredge horometer).",
                                                target="vol-bomb-ims-acum-target",
                                                body=True,
                                                trigger="hover",
                                                style={'font-family': "Franklin Gothic"}
                                            ),
                                        ], width=2, align='center', className="d-grid gap-2"),
                                        dbc.Col(
                                            dbc.Spinner(children=[
                                                html.Div(id='vol-bomb-ims-acum', style={'font-family': "Franklin Gothic"})],
                                                size="lg",
                                                color="primary", type="border", fullscreen=True, )
                                            , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                            align='center'),

                                    ]),
                                # DRAGMAR2
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "DRAGMAR2 Horometer:",
                                            id="horo-drag-acum-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "Displays the time the DRAGMAR2 dredge has been operated during the entire operation.",
                                            target="horo-drag-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='horo-drag-acum', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "DRAGMAR Fuel:",
                                            id="combus-drag-acum-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the dredge DRAGMAR2 during the entire operation.",
                                            target="combus-drag-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-drag-acum',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "Pumped Volume:",
                                            id="vol-bomb-drag-acum-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the volume of water pumped from the Cauca River, with the dredge DRAGMAR2, to the sediment settling containers during the entire operation. It is calculated as the pump flow rate multiplied by the operation time (dredge horometer).",
                                            target="vol-bomb-drag-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(children=[
                                            html.Div(id='vol-bomb-drag-acum',
                                                     style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),

                                ]),
                                # DOOSAN1 y DOOSAN2
                                dbc.Row([

                                    dbc.Col([
                                        dbc.Button(
                                            "DOOSAN1 Fuel:",
                                            id="combus-doosan1-acum-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the DOOSAN1 backhoe loader during the entire operation.",
                                            target="combus-doosan1-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-doosan1-acum',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "DOOSAN2 Fuel:",
                                            id="combus-doosan2-acum-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the DOOSAN2 backhoe loader during the entire operation.",
                                            target="combus-doosan2-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-doosan2-acum',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),

                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Total Pumped Volume:",
                                            id="vol-bomb-acum-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the volume of water that is pumped from the Cauca River, with the dredge IMS5012 and DRAGMAR2, to the sediment settling containers during the entire operation. It is calculated as the pump flow rate multiplied by the operation time (dredge hour meter).",
                                            target="vol-bomb-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(children=[
                                            html.Div(id='vol-bomb-acum',
                                                     style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "Total Fuel:",
                                            id="combus-acum-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the DOOSAN1 and DOOSAN2 backhoes and the IMS5012 and DRAGMAR2 dredges during the entire operation.",
                                            target="combus-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-acum',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Extracted Sludge:",
                                            id="lodo-extraído-target",
                                            color="dark",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the total volume of sludge removed during the entire operation. Up to 90000 m3 of sludge is planned to be removed.",
                                            target="lodo-extraído-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='lodos-extraídos', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "Operation Progress:",
                                            id="avance-target",
                                            color="dark",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the percentage of progress of the operation, equal to the volume of sludge extracted divided by 90000 m3.",
                                            target="avance-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='avance', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                    dbc.Col([
                                        dbc.Row([daq.GraduatedBar(
                                            id='barra-lodos-extraídos',
                                            # color='green',
                                            color={
                                                "ranges": {"red": [0, 3.3], "yellow": [3.3, 6.9], "green": [6.9, 10]}},
                                            showCurrentValue=False,
                                            step=0.25,
                                            value=0,
                                            size=220,
                                            style={'color': '#082255', 'font-family': "Franklin Gothic"}

                                        )]),
                                    ], width=2)
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Dredged Areas:",
                                            id="zona-acum-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "Shows the areas that have been dredged during the whole project. Format: (Channel, Abscissa).",
                                            target="zona-acum-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='zona-acum', style={'font-family': "Franklin Gothic"})
                                    ], style={'textAlign': 'left'}, align='left'),
                                ]),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-peso-vol-acum")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-horómetro")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-agua-LDS")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-pie-bitacora-acum")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),

                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-pimpinas")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),


                            ])
                        ])
                    ])
                ]), label="Total Summary", label_style={'color': '#082255', 'font-family': "Franklin Gothic"}),
                dbc.Tab(dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Row(html.H2(['Entered Summary']),
                                                style={'textAlign': 'center', 'color': '#082255',
                                                       'font-family': "Franklin Gothic"})
                                    ]),
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Enter Start Day:",
                                            id="selec-dia-ini-ingre-target",
                                            color="info",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the day entered by the user to know the operation summary for the selected day. Format DD/MM/YYYYYY.",
                                            target="selec-dia-ini-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        dcc.Dropdown(id='dia-ini-ingre',
                                                     options=[],
                                                     # value='4/2/2020',
                                                     style={'font-family': "Franklin Gothic"}
                                                     )
                                    ], xs=3, sm=3, md=3, lg=2, xl=2, ),
                                    dbc.Col([
                                        dbc.Button(
                                            "Enter End Day:",
                                            id="selec-dia-final-ingre-target",
                                            color="info",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the day entered by the user to know the operation summary for the selected day. Format DD/MM/YYYYYY.",
                                            target="selec-dia-final-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        dcc.Dropdown(id='dia-final-ingre',
                                                     options=[],
                                                     # value='4/2/2020',
                                                     style={'font-family': "Franklin Gothic"}
                                                     )
                                    ], xs=3, sm=3, md=3, lg=2, xl=2, ),

                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Operated Days:",
                                            id="dias-ingre-target",
                                            color="info",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "Number of days operated during the entered operation.",
                                            target="dias-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='dias-ingre', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),

                                    dbc.Col([
                                        dbc.Button(
                                            "Calendar Days:",
                                            id="dias-calendario-ingre-target",
                                            color="info",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "The number of calendar days elapsed during the entered operation.",
                                            target="dias-calendario-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='dias-calendario-ingre', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),

                                ]),
                                # IMS5012
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "IMS5012 Horometer:",
                                            id="horo-ims-ingre-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "Shows the time that the IMS5012 dredge has been operated during the entered operation.",
                                            target="horo-ims-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='horo-ims-ingre', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "IMS5012 Fuel:",
                                            id="combus-ims-ingre-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the IMS5012 dredge during the entered operation.",
                                            target="combus-ims-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-ims-ingre',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "Pumped Volume:",
                                            id="vol-bomb-ims-ingre-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the volume of water that is pumped from the Cauca River, with the dredge IMS5012, to the sediment settling containers during the entered operation. It is calculated as the pump flow multiplied by the operating time (dredge horometer).",
                                            target="vol-bomb-ims-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(children=[
                                            html.Div(id='vol-bomb-ims-ingre', style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),

                                ]),
                                # DRAGMAR2
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "DRAGMAR2 Horometer:",
                                            id="horo-drag-ingre-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "Shows the time the DRAGMAR2 dredge has been operated during the entered operation.",
                                            target="horo-drag-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='horo-drag-ingre', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "DRAGMAR Fuel:",
                                            id="combus-drag-ingre-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the dredge DRAGMAR2 during the entered operation.",
                                            target="combus-drag-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-drag-ingre',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "Pumped Volume:",
                                            id="vol-bomb-drag-ingre-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the volume of water pumped from the Cauca River, with the dredge DRAGMAR2, to the sediment settling containers during the entered operation. It is calculated as the pump flow rate multiplied by the operation time (dredge horometer).",
                                            target="vol-bomb-drag-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(children=[
                                            html.Div(id='vol-bomb-drag-ingre',
                                                     style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),

                                ]),
                                # DOOSAN1 y DOOSAN2
                                dbc.Row([

                                    dbc.Col([
                                        dbc.Button(
                                            "DOOSAN1 Fuel:",
                                            id="combus-doosan1-ingre-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the DOOSAN1 backhoe loader during the entered operation.",
                                            target="combus-doosan1-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-doosan1-ingre',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "DOOSAN2 Fuel:",
                                            id="combus-doosan2-ingre-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the DOOSAN2 backhoe loader during the entered operation.",
                                            target="combus-doosan2-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-doosan2-ingre',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),

                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Total Pumped Volume:",
                                            id="vol-bomb-ingre-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the volume of water that is pumped from the Cauca River, with the dredge IMS5012 and DRAGMAR2, to the sediment settling containers during the entered operation. It is calculated as the pump flow rate multiplied by the operation time (dredge horometer).",
                                            target="vol-bomb-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(children=[
                                            html.Div(id='vol-bomb-ingre',
                                                     style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "Total Fuel:",
                                            id="combus-ingre-target",
                                            color="success",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the amount of fuel used by the DOOSAN1 and DOOSAN2 backhoes and the IMS5012 and DRAGMAR2 dredges during the entered operation.",
                                            target="combus-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(
                                        dbc.Spinner(
                                            children=[html.Div(id='combus-ingre',
                                                               style={'font-family': "Franklin Gothic"})],
                                            size="lg",
                                            color="primary", type="border", fullscreen=True, )
                                        , xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'},
                                        align='center'),
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Extracted Sludge:",
                                            id="lodo-extraído-ingre-target",
                                            color="dark",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "This is the total volume of sludge removed during the entered operation. Up to 90000 m3 of sludge is planned to be removed.",
                                            target="lodo-extraído-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='lodos-extraídos-ingre', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                    dbc.Col([
                                        dbc.Button(
                                            "Operation Progress:",
                                            id="avance-ingre-target",
                                            color="dark",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the percentage of progress of the entered operation, equal to the volume of sludge extracted divided by 90000 m3.",
                                            target="avance-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='avance-ingre', style={'font-family': "Franklin Gothic"})
                                    ], xs=2, sm=2, md=2, lg=2, xl=2, style={'textAlign': 'center'}, align='center'),
                                    dbc.Col([
                                        dbc.Row([daq.GraduatedBar(
                                            id='barra-lodos-extraídos-ingre',
                                            # color='green',
                                            color={
                                                "ranges": {"red": [0, 3.3], "yellow": [3.3, 6.9], "green": [6.9, 10]}},
                                            showCurrentValue=False,
                                            step=0.25,
                                            value=0,
                                            size=220,
                                            style={'color': '#082255', 'font-family': "Franklin Gothic"}

                                        )]),
                                    ], width=2)
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Dredged Areas:",
                                            id="zona-ingre-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "Shows the areas that have been dredged during the entered operation. Format: (Channel, Abscissa).",
                                            target="zona-ingre-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        html.Div(id='zona-ingre', style={'font-family': "Franklin Gothic"})
                                    ], style={'textAlign': 'left'}, align='left'),
                                ]),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-peso-vol-ingre")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-horómetro-ingre")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-agua-LDS-ingre")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-pie-bitacora-ingre")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),

                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-pimpinas-ingre")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),

                            ]),
                        ]),
                    ]),
                ]), label="Entered Summary", label_style={'color': '#082255', 'font-family': "Franklin Gothic"}),
                dbc.Tab(dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Row(html.H2(['Extraction Summary']),
                                                style={'textAlign': 'center', 'color': '#082255',
                                                       'font-family': "Franklin Gothic"})
                                    ]),
                                ]),
                                dbc.Row([

                                    dbc.Col([
                                        dbc.Button(
                                            "Enter Day:",
                                            id="dia-GT-target",
                                            color="info",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the day entered by the user to know the extraction summary operation for the entered day. Format DD/MM/YYYYYY.",
                                            target="dia-GT-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col([
                                        dcc.Dropdown(id='fecha-extraccion',
                                                     options=[],
                                                     style={'font-family': "Franklin Gothic"}
                                                     )
                                    ], xs=3, sm=3, md=3, lg=2, xl=2, ),

                                ]),

                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Volume:",
                                            id="vol-GT-target",
                                            color="primary",
                                            style={'font-family': "Franklin Gothic"},
                                            className="me-1",
                                            n_clicks=0,
                                        ),
                                        dbc.Popover(
                                            "It is the volume of material extracted for a entered day.",
                                            target="vol-GT-target",
                                            body=True,
                                            trigger="hover",
                                            style={'font-family': "Franklin Gothic"}
                                        ),
                                    ], width=2, align='center', className="d-grid gap-2"),
                                    dbc.Col(html.Div(id='volumen-dia-extraccion'), xs=3, sm=3, md=3, lg=2, xl=2,
                                            style={'font-family': "Franklin Gothic"}),

                                ]),
                                dbc.Row(dbc.Col(
                                    dbc.Spinner(children=[dcc.Graph(id="fig-peso-dia")], size="lg",
                                                color="primary", type="border", fullscreen=True, ),
                                    width={'size': 12, 'offset': 0}),
                                ),



                            ])
                        ])
                    ])
                ]), label="Extraction Summary", label_style={'color': '#082255', 'font-family': "Franklin Gothic"}),
                dbc.Tab(dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                               dbc.Row([
                                   dbc.Col([
                                   dbc.Carousel(
                                    items=[
                                        {"key": "1", "src": "/assets/Isagen 1.jpeg", "header": "", },
                                        {"key": "2", "src": "/assets/Isagen 2.jpeg", "header": "", },
                                        {"key": "3", "src": "/assets/Isagen 3.jpeg", "header": "", },
                                        {"key": "4", "src": "/assets/Isagen 4.jpeg", "header": "", },
                                        {"key": "5", "src": "/assets/Isagen 5.jpeg", "header": "", },
                                        {"key": "6", "src": "/assets/Isagen 6.jpeg", "header": "", },
                                        {"key": "7", "src": "/assets/Isagen 7.jpeg", "header": "", },
                                        {"key": "8", "src": "/assets/Isagen 8.jpeg", "header": "", },
                                        {"key": "9", "src": "/assets/Isagen 9.jpeg", "header": "", },
                                        {"key": "10", "src": "/assets/Isagen 10.jpeg", "header": "", },
                                        {"key": "11", "src": "/assets/Isagen 11.jpeg", "header": "", },
                                        {"key": "12", "src": "/assets/Isagen 12.jpeg", "header": "", },
                                        {"key": "13", "src": "/assets/Isagen 13.jpeg", "header": "", },
                                        {"key": "14", "src": "/assets/Isagen 14.jpeg", "header": "", },
                                        {"key": "15", "src": "/assets/Isagen 15.jpeg", "header": "", },
                                        {"key": "16", "src": "/assets/Isagen 16.jpeg", "header": "", },
                                        {"key": "17", "src": "/assets/Isagen 17.jpeg", "header": "", },
                                        {"key": "18", "src": "/assets/Isagen 18.jpeg", "header": "", },
                                        {"key": "19", "src": "/assets/Isagen 19.jpeg", "header": "", },
                                        {"key": "20", "src": "/assets/Isagen 20.jpeg", "header": "", },
                                        {"key": "21", "src": "/assets/Isagen 21.jpeg", "header": "", },
                                        {"key": "22", "src": "/assets/Isagen 22.jpeg", "header": "", },
                                        {"key": "23", "src": "/assets/Isagen 23.jpeg", "header": "", },
                                        {"key": "24", "src": "/assets/Isagen 24.jpeg", "header": "", },


                                    ],
                                    controls=True,
                                    indicators=True,
                                    interval=5000,
                                    ride="carousel",
                                    variant="dark",
                                )
                                   ], width=8, align='center', style={'textAlign': 'center'}),

                               ])
                            ])
                        ])
                    ])
                ]), label="Pictures", label_style={'color': '#082255', 'font-family': "Franklin Gothic"}),

            ])
    ]),
])


@app.callback(
    Output(component_id='Dia', component_property='options'),
    Output(component_id='Dia', component_property='value'),
    Output(component_id='dia-inicial-acum', component_property='children'),
    Output(component_id='dia-final-acum', component_property='children'),
    Output(component_id='store-data-dragado', component_property='data'),
    Output(component_id='store-data-volqueta', component_property='data'),
    Output(component_id='store-data-combustible', component_property='data'),
    Output(component_id='store-data-bitacora', component_property='data'),
    Output(component_id='fecha-extraccion', component_property='options'),
    Output(component_id='fecha-extraccion', component_property='value'),

    Output(component_id='dia-ini-ingre', component_property='options'),
    Output(component_id='dia-ini-ingre', component_property='value'),

    Input('my_interval', 'n_intervals'),
)
def dropdownTiempoReal(value_intervals):
    SERVICE_ACCOUNT_FILE = 'keys_isagen.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # The ID spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1xXq-RceENIIlQRUVqG364oxHHxFlJ_e01T2JWITTQkc'

    SAMPLE_RANGE_COMBINADO = "Plantilla"

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_COMBINADO = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                          range=SAMPLE_RANGE_COMBINADO).execute()

    dfCOMBINADO = result_COMBINADO.get('values', [])
    names = ["Draga", "Fecha Dragado", "Horometro", "Caudal bomba m3/h", "Abscisa", "Canal",
             "", "", "", "Volqueta", "Fecha extracción", "Viajes", "Volumen m3", "", "", "",
             "Fecha combustible", "Volumen combustible gal", "Equipo", "", "", "",
             "Fecha bitacora", "Inicio", "Fin", "Total", "Evento", "Tipo",
             ]

    dfCOMBINADO = pd.DataFrame(dfCOMBINADO, columns=names)
    dfCOMBINADO.drop([0], inplace=True)
    dfCOMBINADO = dfCOMBINADO.rename(index=lambda x: x - 1)


    dfDragado = dfCOMBINADO.iloc[:, [0, 1, 2, 3, 4, 5]]
    dfVolqueta = dfCOMBINADO.iloc[:, [9, 10, 11, 12]]
    dfCombustible = dfCOMBINADO.iloc[:, [16, 17, 18]]
    dfBitacora = dfCOMBINADO.iloc[:, [22, 23, 24, 25, 26, 27]]

    dfDragado = dfDragado.replace(to_replace='None', value=np.nan).dropna(axis=0, how="all")
    dfVolqueta = dfVolqueta.replace(to_replace='None', value=np.nan).dropna(axis=0, how="all")
    dfCombustible = dfCombustible.replace(to_replace='None', value=np.nan).dropna(axis=0, how="all")
    dfBitacora = dfBitacora.replace(to_replace='None', value=np.nan).dropna(axis=0, how="all")

    dfDragado = dfDragado.replace(to_replace='', value=np.nan).dropna(axis=0, how="all")
    dfVolqueta = dfVolqueta.replace(to_replace='', value=np.nan).dropna(axis=0, how="all")
    dfCombustible = dfCombustible.replace(to_replace='', value=np.nan).dropna(axis=0, how="all")
    dfBitacora = dfBitacora.replace(to_replace='', value=np.nan).dropna(axis=0, how="all")

    dia = dfDragado["Fecha Dragado"]
    dia = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), dia))
    dia = list(dict.fromkeys(dia))
    dia.sort(reverse=True)
    dia = list(map(lambda fecha: str(fecha.day) + "/" + str(fecha.month) + "/" + str(fecha.year), dia))

    diaVolqueta = dfVolqueta["Fecha extracción"]
    diaVolqueta = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diaVolqueta))
    diaVolqueta = list(dict.fromkeys(diaVolqueta))
    diaVolqueta.sort(reverse=True)
    diaVolqueta = list(map(lambda fecha: str(fecha.day) + "/" + str(fecha.month) + "/" + str(fecha.year), diaVolqueta))

    # Calcula primer día operado
    diaPrimer = dia[-1]

    # Calcula último día operado
    diaHoy = dia[0]

    # Calcula último día operado Volqueta
    diaHoy2 = diaVolqueta[0]

    # Genera primer valor y lista de opciones del dia inicial ingresado por el usuario
    diaIni = dfDragado["Fecha Dragado"]
    diaIni = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diaIni))
    diaIni = list(dict.fromkeys(diaIni))
    diaIni.sort(reverse=False)
    diaIni = list(map(lambda fecha: str(fecha.day) + "/" + str(fecha.month) + "/" + str(fecha.year), diaIni))


    return dia, diaHoy, diaPrimer, diaHoy, \
           dfDragado.to_dict('records'), dfVolqueta.to_dict('records'), dfCombustible.to_dict('records'), \
           dfBitacora.to_dict('records'), diaVolqueta, diaHoy2, diaIni, diaPrimer


########
@app.callback(
    Output('dia-final-ingre', 'options'),
    Input(component_id='dia-ini-ingre', component_property='value'),

    Input(component_id='store-data-dragado', component_property='data'),
    Input(component_id='store-data-bitacora', component_property='data'),

)
def fecha_interactivo(value_dia, data1, data2,):
    data1 = pd.DataFrame(data1)
    data2 = pd.DataFrame(data2)
    value_dia = datetime.strptime(value_dia, "%d/%m/%Y")

    dfDragado = data1
    dfBitacora = data2

    diaFinalOpt = dfDragado["Fecha Dragado"]

    diaFinalOpt = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diaFinalOpt))
    diaFinalOpt.sort(reverse=False)



    dfDragado['Fecha TS'] = diaFinalOpt
    diaFinalOpt = dfDragado[dfDragado['Fecha TS'] > value_dia]
    diaFinalOpt = diaFinalOpt['Fecha TS']
    diaFinalOpt = list(dict.fromkeys(diaFinalOpt))


    diaFinalOpt = list(map(lambda x: str(x.day) + '/' + str(x.month) + '/' + str(x.year), diaFinalOpt))

    return [{'label': c, 'value': c} for c in diaFinalOpt]


@app.callback(
    Output('dia-final-ingre', 'value'),
    Input('dia-final-ingre', 'options'),
)
def set_Geotube_fecha_value(fecha_selec):
    x = fecha_selec[0]
    x = x["value"]
    return x

#######


@app.callback(

    Output(component_id='horo-ims-dia', component_property='children'),
    Output(component_id='horo-drag-dia', component_property='children'),
    Output(component_id='combus-ims-dia', component_property='children'),
    Output(component_id='combus-drag-dia', component_property='children'),
    Output(component_id='vol-bomb-ims-dia', component_property='children'),
    Output(component_id='vol-bomb-drag-dia', component_property='children'),
    Output(component_id='combus-doosan1-dia', component_property='children'),
    Output(component_id='horo-doosan1-dia', component_property='children'),
    Output(component_id='combus-doosan2-dia', component_property='children'),
    Output(component_id='horo-doosan2-dia', component_property='children'),
    Output(component_id='fig-pie-bitacora-dia', component_property='figure'),

    Output(component_id='fig-peso-dia', component_property='figure'),
    Output(component_id='volumen-dia-extraccion', component_property='children'),

    Output(component_id='horo-ims-acum', component_property='children'),
    Output(component_id='combus-ims-acum', component_property='children'),
    Output(component_id='vol-bomb-ims-acum', component_property='children'),
    Output(component_id='horo-drag-acum', component_property='children'),
    Output(component_id='combus-drag-acum', component_property='children'),
    Output(component_id='vol-bomb-drag-acum', component_property='children'),

    Output(component_id='combus-doosan1-acum', component_property='children'),
    Output(component_id='combus-doosan2-acum', component_property='children'),
    Output(component_id='vol-bomb-acum', component_property='children'),
    Output(component_id='combus-acum', component_property='children'),
    Output(component_id='lodos-extraídos', component_property='children'),
    Output(component_id='avance', component_property='children'),
    Output(component_id='barra-lodos-extraídos', component_property='value'),
    Output(component_id='fig-pie-bitacora-acum', component_property='figure'),
    Output(component_id='fig-agua-LDS', component_property='figure'),
    Output(component_id='fig-pimpinas', component_property='figure'),
    Output(component_id='fig-horómetro', component_property='figure'),
    Output(component_id='fig-peso-vol-acum', component_property='figure'),
    Output(component_id='dias-acum', component_property='children'),
    Output(component_id='zona-dia', component_property='children'),
    Output(component_id='zona-acum', component_property='children'),

    Output(component_id='dias-ingre', component_property='children'),
    Output(component_id='horo-ims-ingre', component_property='children'),
    Output(component_id='combus-ims-ingre', component_property='children'),
    Output(component_id='vol-bomb-ims-ingre', component_property='children'),
    Output(component_id='horo-drag-ingre', component_property='children'),
    Output(component_id='combus-drag-ingre', component_property='children'),
    Output(component_id='vol-bomb-drag-ingre', component_property='children'),
    Output(component_id='combus-doosan1-ingre', component_property='children'),
    Output(component_id='combus-doosan2-ingre', component_property='children'),
    Output(component_id='vol-bomb-ingre', component_property='children'),
    Output(component_id='combus-ingre', component_property='children'),
    Output(component_id='lodos-extraídos-ingre', component_property='children'),
    Output(component_id='avance-ingre', component_property='children'),
    Output(component_id='barra-lodos-extraídos-ingre', component_property='value'),
    Output(component_id='zona-ingre', component_property='children'),
    Output(component_id='fig-peso-vol-ingre', component_property='figure'),
    Output(component_id='fig-horómetro-ingre', component_property='figure'),
    Output(component_id='fig-agua-LDS-ingre', component_property='figure'),
    Output(component_id='fig-pie-bitacora-ingre', component_property='figure'),
    Output(component_id='fig-pimpinas-ingre', component_property='figure'),
    Output(component_id='dias-calendario-acum', component_property='children'),
    Output(component_id='dias-calendario-ingre', component_property='children'),

    Input('my_interval', 'n_intervals'),
    Input('Dia', 'value'),
    Input(component_id='store-data-dragado', component_property='data'),
    Input(component_id='store-data-volqueta', component_property='data'),
    Input(component_id='store-data-combustible', component_property='data'),
    Input(component_id='store-data-bitacora', component_property='data'),
    Input('fecha-extraccion', 'value'),
    Input('dia-ini-ingre', 'value'),
    Input('dia-final-ingre', 'value'),

)
def isagen(value_intervals, value_dia, data1, data2, data3, data4, value_dia_extraccion, value_dia_inicial, value_dia_final):
    data1 = pd.DataFrame(data1)
    data2 = pd.DataFrame(data2)
    data3 = pd.DataFrame(data3)
    data4 = pd.DataFrame(data4)

    dfDragado = data1
    dfVolqueta = data2
    dfCombustible = data3
    dfBitacora = data4

    ########################### Resumen Diario ################################

    # Calcula horómetro, combustible y volumen bombeado de la IMS5012

    # Horómetro y volumen bombeado IMS5012
    try:
        dfDragaIMS = dfDragado[dfDragado['Draga'] == 'IMS5012']
        dfDragaIMSDia = dfDragaIMS[dfDragaIMS['Fecha Dragado'] == value_dia]
        horoIMSdia = dfDragaIMSDia['Horometro']
        horoIMSdia = np.array(horoIMSdia)
        horoIMSdia = horoIMSdia[0]
        QIMS = dfDragaIMSDia['Caudal bomba m3/h']
        QIMS = np.array(QIMS)
        QIMS = QIMS[0]
        volBombIMSdia = float(horoIMSdia) * float(QIMS)
        horoIMSdia = str(horoIMSdia) + ' hr.'
        volBombIMSdia = str(volBombIMSdia) + ' m3'
        #print(horoIMSdia)
    except:
        horoIMSdia = str(0) + ' hr.'
        volBombIMSdia = str(0) + ' m3'
    # Horómetro y volumen bombeado DRAGMAR2
    try:
        dfDragaDRAG = dfDragado[dfDragado['Draga'] == 'DRAGMAR2']
        dfDragaDRAGDia = dfDragaDRAG[dfDragaDRAG['Fecha Dragado'] == value_dia]
        horoDRAGdia = dfDragaDRAGDia['Horometro']
        horoDRAGdia = np.array(horoDRAGdia)
        horoDRAGdia = horoDRAGdia[0]
        QDRAG = dfDragaDRAGDia['Caudal bomba m3/h']
        QDRAG = np.array(QDRAG)
        QDRAG = QDRAG[0]
        volBombDRAGdia = float(horoDRAGdia) * float(QDRAG)
        horoDRAGdia = str(horoDRAGdia) + ' hr.'
        volBombDRAGdia = str(volBombDRAGdia) + ' m3'
        # print(horoDRAGdia)
    except:
        horoDRAGdia = str(0) + ' hr.'
        volBombDRAGdia = str(0) + ' m3'

    # Combustible IMS5012
    try:
        dfDragaIMS = dfCombustible[dfCombustible['Equipo'] == 'IMS5012']
        dfDragaIMSDia = dfDragaIMS[dfDragaIMS['Fecha combustible'] == value_dia]
        combusIMSdia = dfDragaIMSDia['Volumen combustible gal']
        combusIMSdia = np.array(combusIMSdia)
        combusIMSdia = combusIMSdia[0]
        combusIMSdia = str(combusIMSdia) + ' gal'
    except:
        combusIMSdia = str(0) + ' gal'

    # Combustible DRAGMAR2
    try:
        dfDragaDRAG = dfCombustible[dfCombustible['Equipo'] == 'DRAGMAR2']
        dfDragaDRAGDia = dfDragaDRAG[dfDragaDRAG['Fecha combustible'] == value_dia]
        combusDRAGdia = dfDragaDRAGDia['Volumen combustible gal']
        combusDRAGdia = np.array(combusDRAGdia)
        combusDRAGdia = combusDRAGdia[0]
        combusDRAGdia = str(combusDRAGdia) + ' gal'
    except:
        combusDRAGdia = str(0) + ' gal'

    # Combustible y encendido/apagado DOOSAN1
    try:
        dfDragaDOOSAN1 = dfCombustible[dfCombustible['Equipo'] == 'DOOSAN1']
        dfDragaDOOSAN1Dia = dfDragaDOOSAN1[dfDragaDOOSAN1['Fecha combustible'] == value_dia]
        combusDOOSAN1dia = dfDragaDOOSAN1Dia['Volumen combustible gal']
        combusDOOSAN1dia = np.array(combusDOOSAN1dia)
        combusDOOSAN1dia = combusDOOSAN1dia[0]
        combusDOOSAN1dia = str(combusDOOSAN1dia) + ' gal'
        operDOOSAN1 = 'ON'
    except:
        combusDOOSAN1dia = str(0) + ' gal'
        operDOOSAN1 = 'OFF'

    # Combustible y encendido/apagado DOOSAN2
    try:
        dfDragaDOOSAN2 = dfCombustible[dfCombustible['Equipo'] == 'DOOSAN2']
        dfDragaDOOSAN2Dia = dfDragaDOOSAN2[dfDragaDOOSAN2['Fecha combustible'] == value_dia]
        combusDOOSAN2dia = dfDragaDOOSAN2Dia['Volumen combustible gal']
        combusDOOSAN2dia = np.array(combusDOOSAN2dia)
        combusDOOSAN2dia = combusDOOSAN2dia[0]
        combusDOOSAN2dia = str(combusDOOSAN2dia) + ' gal'
        operDOOSAN2 = 'ON'
    except:
        combusDOOSAN2dia = str(0) + ' gal'
        operDOOSAN2 = 'OFF'



    # Crea pie chart con bitácora del día
    dfBitacoraHora = dfBitacora['Total']
    dfBitacoraHora = list(map(lambda fecha: datetime.strptime(fecha, "%H:%M"), dfBitacoraHora))
    dfBitacoraHora1 = list(map(lambda fecha: round(fecha.hour, 2), dfBitacoraHora))
    dfBitacoraHora2 = list(map(lambda fecha: fecha.minute, dfBitacoraHora))
    dfBitacoraHora2 = list(map(lambda fecha: round(float(fecha) / 60, 2), dfBitacoraHora2))
    dfBitacoraHora = np.array(dfBitacoraHora1) + np.array(dfBitacoraHora2)
    dfBitacora['Horas'] = dfBitacoraHora

    dfBitacoraDia = dfBitacora[dfBitacora['Fecha bitacora'] == value_dia]

    pie_chart_bitacora_dia = px.pie(
        data_frame=dfBitacoraDia,
        values='Horas',
        names='Evento',
        color='Evento',  # differentiate markers (discrete) by color
        title='Daily Log',  # figure title
        hole=0.5,  # represents the hole in middle of pie
    )

    pie_chart_bitacora_dia.update_layout(
        font_family="Franklin Gothic",
        title_font_family="Franklin Gothic",
    )


    # Calcula las zonas dragadas en un día
    dfDragado['Zonas'] = '(' + dfDragado['Canal'] + ', ' + dfDragado['Abscisa'] + ')'
    zonasDia = dfDragado[dfDragado['Fecha Dragado'] == value_dia]
    zonasDia = zonasDia['Zonas']
    zonasDia = list(dict.fromkeys(zonasDia))
    zonasDragDia = ''

    for i in zonasDia:
        zonasDragDia = i + ', ' + zonasDragDia

    zonasDragDia = str(zonasDragDia)
    zonasDragDia = zonasDragDia[:-2]
    print('zonasDragDia')
    print(zonasDragDia)

    ########################### Resumen Acumulado ################################
    # Calcula los días mecánicos
    arrayDiasDragado = np.array(dfDragado['Fecha Dragado'])
    diasMec1 = arrayDiasDragado[0]
    diasMec1 = datetime.strptime(diasMec1, "%d/%m/%Y")
    diasMec2 = arrayDiasDragado[-1]
    diasMec2 = datetime.strptime(diasMec2, "%d/%m/%Y")
    diasMec = diasMec2 - diasMec1
    diasMec = diasMec.days + 1
    diasMecBarra = diasMec
    diasMec = str(diasMec) + ' days'


    # Calcula horómetro total de IMS5012 y DRAGMAR2 & Volumen bombeado
    dfDragaIMS = dfDragado[dfDragado['Draga'] == 'IMS5012']
    horoIMSacum = dfDragaIMS['Horometro']
    horoIMSacum = list(map(lambda x: float(x), horoIMSacum))
    horoIMSacum = np.array(horoIMSacum)

    volBombIMSacum = dfDragaIMS['Caudal bomba m3/h']
    volBombIMSacum = list(map(lambda x: float(x), volBombIMSacum))
    volBombIMSacum = np.array(volBombIMSacum)
    volBombIMSacum = volBombIMSacum * horoIMSacum
    volBombIMSacum2 = volBombIMSacum * horoIMSacum

    horoIMSacum = str(round(horoIMSacum.sum(), 2)) + ' hr.'
    volBombIMSacum = str(round(volBombIMSacum.sum(), 2)) + ' m3'

    dfDragaDRAG = dfDragado[dfDragado['Draga'] == 'DRAGMAR2']
    horoDRAGacum = dfDragaDRAG['Horometro']
    horoDRAGacum = list(map(lambda x: float(x), horoDRAGacum))
    horoDRAGacum = np.array(horoDRAGacum)

    volBombDRAGacum = dfDragaDRAG['Caudal bomba m3/h']
    volBombDRAGacum = list(map(lambda x: float(x), volBombDRAGacum))
    volBombDRAGacum = np.array(volBombDRAGacum)
    volBombDRAGacum = volBombDRAGacum * horoDRAGacum
    volBombDRAGacum2 = volBombDRAGacum * horoDRAGacum


    horoDRAGacum = str(round(horoDRAGacum.sum(), 2)) + ' hr.'
    volBombDRAGacum = str(round(volBombDRAGacum.sum(), 2)) + ' m3'

    # Calcula combustible total de IMS5012, DRAGMAR2, DOOSAN1 y DOOSAN2
    combusIMSacum = dfCombustible[dfCombustible['Equipo'] == 'IMS5012']
    combusIMSacum = combusIMSacum['Volumen combustible gal']
    combusIMSacum = list(map(lambda x: float(x), combusIMSacum))
    combusIMSacum = np.array(combusIMSacum)
    combusIMSacum2 = combusIMSacum.sum()
    combusIMSacum = str(round(combusIMSacum.sum(), 2)) + ' gal'

    combusDRAGacum = dfCombustible[dfCombustible['Equipo'] == 'DRAGMAR2']
    combusDRAGacum = combusDRAGacum['Volumen combustible gal']
    combusDRAGacum = list(map(lambda x: float(x), combusDRAGacum))
    combusDRAGacum = np.array(combusDRAGacum)
    combusDRAGacum2 = combusDRAGacum.sum()
    combusDRAGacum = str(round(combusDRAGacum.sum(), 2)) + ' gal'

    combusDOOSAN1acum = dfCombustible[dfCombustible['Equipo'] == 'DOOSAN1']
    combusDOOSAN1acum = combusDOOSAN1acum['Volumen combustible gal']
    combusDOOSAN1acum = list(map(lambda x: float(x), combusDOOSAN1acum))
    combusDOOSAN1acum = np.array(combusDOOSAN1acum)
    combusDOOSAN1acum2 = combusDOOSAN1acum.sum()
    combusDOOSAN1acum = str(round(combusDOOSAN1acum.sum(), 2)) + ' gal'

    combusDOOSAN2acum = dfCombustible[dfCombustible['Equipo'] == 'DOOSAN2']
    combusDOOSAN2acum = combusDOOSAN2acum['Volumen combustible gal']
    combusDOOSAN2acum = list(map(lambda x: float(x), combusDOOSAN2acum))
    combusDOOSAN2acum = np.array(combusDOOSAN2acum)
    combusDOOSAN2acum2 = combusDOOSAN2acum.sum()
    combusDOOSAN2acum = str(round(combusDOOSAN2acum.sum(), 2)) + ' gal'

    # Calcula volumen bombeado total y combustible total
    volBombAcum = volBombIMSacum2.sum() + volBombDRAGacum2.sum()
    volBombAcum = str(round(volBombAcum, 2)) + ' m3'
    combusAcum = combusDOOSAN2acum2 + combusDOOSAN1acum2 + combusIMSacum2 + combusDRAGacum2
    combusAcum = str(round(combusAcum, 2)) + ' gal'

    # Calcula volumen total de lodos extraídos y la barra
    numViajes = dfVolqueta['Viajes']
    numViajes = list(map(lambda x: float(x), numViajes))
    numViajes = np.array(numViajes)

    volVolqueta = dfVolqueta['Volumen m3']
    volVolqueta = list(map(lambda x: float(x), volVolqueta))
    volVolqueta = np.array(volVolqueta)

    volAcum = numViajes * volVolqueta
    volAcumBarra = round((volAcum.sum()/90000)*10, 2)

    volAcum = str(round(volAcum.sum(), 2)) + ' m3'

    # Calcula el avance de la operación
    avance = numViajes * volVolqueta
    avance = avance.sum() * 100 / 90000
    avance = str(round(avance, 2)) + '%'

    # Calcula los días operados en toda la operación
    diasVolqueta = dfVolqueta['Fecha extracción']
    diasVolqueta = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diasVolqueta))
    diasVolqueta = set(diasVolqueta)


    diasDragado = dfDragado['Fecha Dragado']
    diasDragado = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diasDragado))
    diasDragado = set(diasDragado)


    diasOper = diasVolqueta.union(diasDragado)
    diasOper = list(dict.fromkeys(diasOper))
    diasOper = str(len(diasOper)) + ' days'

    # Crea pie chart con bitácora acumulada
    pie_chart_bitacora_acum = px.pie(
         data_frame=dfBitacora,
         values='Horas',
         names='Evento',
         color='Evento',  # differentiate markers (discrete) by color
         #color_discrete_sequence=["green", "Black", "blue", "yellow", "red", "purple"],  # set marker colors
         #hover_name='negative',  # values appear in bold in the hover tooltip
         #hover_data=['positive'],            #values appear as extra data in the hover tooltip
         custom_data=['Total'],              #values are extra data to be used in Dash callbacks
         #labels={"state": "the State"},  # map the labels
         title='Project Log',  # figure title
         template='presentation',  #
         width=800,  # figure width in pixels
         height=600,  # figure height in pixels
         hole=0.5,  # represents the hole in middle of pie
     )

    pie_chart_bitacora_acum.update_layout(
         font_family="Franklin Gothic",
         title_font_family="Franklin Gothic",
    )



    ####################### Gráfico Volumen agua lodosa ingresado al Geotube ############################
    labelGraphGT = 'gal'

    dfQbombaIMS = dfDragado[dfDragado['Draga'] == 'IMS5012']
    QbombaIMS = dfQbombaIMS["Caudal bomba m3/h"]
    horoIMS = dfQbombaIMS["Horometro"]
    fechaHorasBombaIMS = dfQbombaIMS["Fecha Dragado"]
    fechaHorasBombaIMS = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaHorasBombaIMS))
    QbombaIMS = list(map(lambda x: float(x), QbombaIMS))
    horoIMS = list(map(lambda x: float(x), horoIMS))
    volLDSIMS = np.array(QbombaIMS) * np.array(horoIMS)

    # Crea la figura de agua lodosa
    volLDSIMS = list(map(lambda x: int(x), volLDSIMS))


    dfQbombaDRAG = dfDragado[dfDragado['Draga'] == 'DRAGMAR2']
    QbombaDRAG = dfQbombaDRAG["Caudal bomba m3/h"]
    horoDRAG = dfQbombaDRAG["Horometro"]
    fechaHorasBombaDRAG = dfQbombaDRAG["Fecha Dragado"]
    fechaHorasBombaDRAG = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaHorasBombaDRAG))
    QbombaDRAG = list(map(lambda x: float(x), QbombaDRAG))
    horoDRAG = list(map(lambda x: float(x), horoDRAG))
    volLDSDRAG = np.array(QbombaDRAG) * np.array(horoDRAG)
    volLDSDRAG = list(map(lambda x: int(x), volLDSDRAG))

    figAguaLDS = go.Figure()

    figAguaLDS.add_trace(go.Scatter(x=fechaHorasBombaIMS, y=volLDSIMS, name="IMS5012", text=volLDSIMS,
                                     mode='lines+markers+text', textposition='bottom right', ))
    figAguaLDS.add_trace(go.Scatter(x=fechaHorasBombaDRAG, y=volLDSDRAG, name="DRAGMAR2", text=volLDSDRAG,
                                     mode='lines+markers+text', textposition='bottom right', ))

    figAguaLDS.update_layout(title="Sludge Water Entered into Sediment Settling Containers", xaxis_title="Date",
                              yaxis_title="Volume [m3]")
    figAguaLDS.update_layout(legend=dict(
         orientation="h",
         yanchor="bottom",
         y=-0.7,
         xanchor="center",
         x=0.5
     ))

    figAguaLDS.update_layout(
         font_family="Franklin Gothic",
         # font_color="blue",
         title_font_family="Franklin Gothic",
         # title_font_color="red",
         # legend_title_font_color="green"
     )
    figAguaLDS.update_xaxes(title_font_family="Franklin Gothic")

    # Crea la figura de horómetro
    dfHoroIMS = dfDragado[dfDragado['Draga'] == 'IMS5012']
    horasIMS = dfHoroIMS['Horometro']
    horasIMS = list(map(lambda x: float(x), horasIMS))
    fechaHorasIMS = dfHoroIMS["Fecha Dragado"]
    fechaHorasIMS = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaHorasIMS))

    dfHoroDRAG = dfDragado[dfDragado['Draga'] == 'DRAGMAR2']
    horasDRAG = dfHoroDRAG['Horometro']
    horasDRAG = list(map(lambda x: float(x), horasDRAG))
    fechaHorasDRAG = dfHoroIMS["Fecha Dragado"]
    fechaHorasDRAG = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaHorasDRAG))



    figHorometro = go.Figure()

    figHorometro.add_trace(go.Scatter(x=fechaHorasIMS, y=horasIMS, name="IMS5012", text=horasIMS,
                                       mode='lines+markers+text', textposition='bottom right', ))

    figHorometro.add_trace(go.Scatter(x=fechaHorasDRAG, y=horasDRAG, name="DRAGMAR2", text=horasDRAG,
                                       mode='lines+markers+text', textposition='bottom right', ))


    figHorometro.update_layout(title="Horometer", xaxis_title="Date",
                                yaxis_title="Time [hr.]")
    figHorometro.update_layout(legend=dict(
         orientation="h",
         yanchor="bottom",
         y=-0.7,
         xanchor="center",
         x=0.5
    ))

    figHorometro.update_layout(
        font_family="Franklin Gothic",
        # font_color="blue",
        title_font_family="Franklin Gothic",
        # title_font_color="red",
        # legend_title_font_color="green"
    )
    figHorometro.update_xaxes(title_font_family="Franklin Gothic")

    # Crea la figura de las pimpinas
    dfCombustibleIMS = dfCombustible[dfCombustible['Equipo'] == 'IMS5012']
    ycombusIMS = dfCombustibleIMS['Volumen combustible gal']
    ycombusIMS = list(map(lambda x: float(x), ycombusIMS))
    fechaGasolinaIMS = dfCombustibleIMS['Fecha combustible']
    fechaGasolinaIMS = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaGasolinaIMS))

    dfCombustibleDRAG = dfCombustible[dfCombustible['Equipo'] == 'DRAGMAR2']
    ycombusDRAG = dfCombustibleDRAG['Volumen combustible gal']
    ycombusDRAG = list(map(lambda x: float(x), ycombusDRAG))
    fechaGasolinaDRAG = dfCombustibleDRAG['Fecha combustible']
    fechaGasolinaDRAG = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaGasolinaDRAG))

    dfCombustibleDOOSAN1 = dfCombustible[dfCombustible['Equipo'] == 'DOOSAN1']
    ycombusDOOSAN1 = dfCombustibleDOOSAN1['Volumen combustible gal']
    ycombusDOOSAN1 = list(map(lambda x: float(x), ycombusDOOSAN1))
    fechaGasolinaDOOSAN1 = dfCombustibleDOOSAN1['Fecha combustible']
    fechaGasolinaDOOSAN1 = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaGasolinaDOOSAN1))

    dfCombustibleDOOSAN2 = dfCombustible[dfCombustible['Equipo'] == 'DOOSAN2']
    ycombusDOOSAN2 = dfCombustibleDOOSAN1['Volumen combustible gal']
    ycombusDOOSAN2 = list(map(lambda x: float(x), ycombusDOOSAN2))
    fechaGasolinaDOOSAN2 = dfCombustibleDOOSAN2['Fecha combustible']
    fechaGasolinaDOOSAN2 = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaGasolinaDOOSAN2))


    suffixyPimpinas = 'Fuel Volume [gal]'


    figPimpinas = go.Figure()

    figPimpinas.add_trace(go.Scatter(x=fechaGasolinaIMS, y=ycombusIMS, text=ycombusIMS, name='IMS5012',
                                      mode='lines+markers+text', textposition='bottom right', ))
    figPimpinas.add_trace(go.Scatter(x=fechaGasolinaDRAG, y=ycombusDRAG, text=ycombusDRAG, name='DRAGMAR2',
                                      mode='lines+markers+text', textposition='bottom right', ))
    figPimpinas.add_trace(go.Scatter(x=fechaGasolinaDOOSAN1, y=ycombusDOOSAN1, text=ycombusDOOSAN1, name='DOOSAN1',
                                      mode='lines+markers+text', textposition='bottom right', ))
    figPimpinas.add_trace(go.Scatter(x=fechaGasolinaDOOSAN2, y=ycombusDOOSAN2, text=ycombusDOOSAN2, name='DOOSAN2',
                                      mode='lines+markers+text', textposition='bottom right', ))


    figPimpinas.update_layout(title="Volume of Fuel Consumption", xaxis_title="Date",
                               yaxis_title=suffixyPimpinas)
    figPimpinas.update_layout(legend=dict(
         orientation="h",
         yanchor="bottom",
         y=-0.5,
         xanchor="center",
         x=0.5,
     ), )

    figPimpinas.update_layout(
         font_family="Franklin Gothic",
         title_font_family="Franklin Gothic",
    )
    figPimpinas.update_xaxes(title_font_family="Franklin Gothic")


    # Crea figura de peso y volumen acumulados
    diasVolqueta = dfVolqueta['Fecha extracción']
    #diasVolqueta = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diasVolqueta))
    diasVolqueta = list(dict.fromkeys(diasVolqueta))

    volumenAcumY45 = [None]

    for i in diasVolqueta:
        #i2 = str(i.day) + "/" + str(i.month) + "/" + str(i.year)

        dfVolquetaDia = dfVolqueta[dfVolqueta["Fecha extracción"] == i]

        volumenAcumVec = dfVolquetaDia["Volumen m3"]
        volumenAcumVec = list(map(lambda x: float(x), volumenAcumVec))
        volumenAcumVec = np.array(volumenAcumVec)

        viajesAcumVec = dfVolquetaDia["Viajes"]
        viajesAcumVec = list(map(lambda x: float(x), viajesAcumVec))
        viajesAcumVec = np.array(viajesAcumVec)

        volumenAcumVec = volumenAcumVec * viajesAcumVec


        volumenAcumVec45 = round(sum(volumenAcumVec), 0)
        volumenAcumY45.append(volumenAcumVec45)

    volumenAcumY45.remove(None)

    fechaX45 = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diasVolqueta))



    figPesoVol = go.Figure()

    figPesoVol.add_trace(go.Scatter(x=fechaX45, y=volumenAcumY45, name="Volume [m3]", text=volumenAcumY45,
                                  mode='lines+markers+text', textposition='bottom right', ))
    figPesoVol.update_layout(title="Volumen of Extracted Material", xaxis_title="Date",
                        yaxis_title="Volume [m3]")
    figPesoVol.update_layout(legend=dict(
        yanchor="bottom",
        y=-0.5,
        xanchor="center",
        x=0.5
    ))

    figPesoVol.update_layout(
        font_family="Franklin Gothic",
        title_font_family="Franklin Gothic",
    )
    figPesoVol.update_xaxes(title_font_family="Franklin Gothic")

    # Calcula las zonas dragadas en un día
    #dfDragado['Zonas'] = '(' + dfDragado['Canal'] + ', ' + dfDragado['Abscisa'] + ')'
    #zonasAcum = dfDragado[dfDragado['Fecha Dragado'] == value_dia]
    zonasAcum = dfDragado['Zonas']
    zonasAcum = list(dict.fromkeys(zonasAcum))
    zonasDragAcum = ''

    for i in zonasAcum:
        zonasDragAcum = i + ', ' + zonasDragAcum

    zonasDragAcum = str(zonasDragAcum)
    zonasDragAcum = zonasDragAcum[:-2]
    print('zonasDragAcum')
    print(zonasDragAcum)



    ########################### Resumen Extracción ################################
    volDia = dfVolqueta[dfVolqueta['Fecha extracción'] == value_dia_extraccion]
    volDia = volDia['Volumen m3']
    volDia = list(map(lambda x: float(x), volDia))
    volDia = np.array(volDia)
    volDia = volDia.sum()
    volDia = str(volDia) + ' m3'

    # Gráfica volumen de volquetas

    numVolquetaDia = dfVolqueta[dfVolqueta['Fecha extracción'] == value_dia_extraccion]
    numVolquetaDia = numVolquetaDia['Volqueta']
    volumenVolquetaDia = dfVolqueta[dfVolqueta['Fecha extracción'] == value_dia_extraccion]
    volumenVolquetaDia = volumenVolquetaDia['Volumen m3']
    volumenVolquetaDia = list(map(lambda x: float(x), volumenVolquetaDia))
    volumenVolquetaDia = np.array(volumenVolquetaDia)

    viajesVolquetaDia = dfVolqueta[dfVolqueta['Fecha extracción'] == value_dia_extraccion]
    viajesVolquetaDia = viajesVolquetaDia['Viajes']
    viajesVolquetaDia = list(map(lambda x: float(x), viajesVolquetaDia))
    viajesVolquetaDia = np.array(viajesVolquetaDia)


    volumenVolquetaDia = volumenVolquetaDia * viajesVolquetaDia

    volDiaExtraccion = volumenVolquetaDia.sum()



    figPesoDia = go.Figure(data=[
        go.Bar(name='Volume [m3]', x=numVolquetaDia, y=volumenVolquetaDia, text=volumenVolquetaDia),

    ])

    figPesoDia.update_layout(title="Volume of Trucks with Extracted Material", xaxis_title="Truck",
                        yaxis_title="Volume [m3]")
    figPesoDia.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.5,
        xanchor="center",
        x=0.5,
    ))

    figPesoDia.update_layout(
        font_family="Franklin Gothic",
        title_font_family="Franklin Gothic",

    )
    figPesoDia.update_xaxes(title_font_family="Franklin Gothic")

    ############### Resumen Ingresado #######################

    print(dfDragado.dtypes)
    print(dfBitacora.dtypes)
    print(dfVolqueta.dtypes)
    print(dfCombustible.dtypes)

    value_dia_inicial = datetime.strptime(value_dia_inicial, "%d/%m/%Y")
    value_dia_final = datetime.strptime(value_dia_final, "%d/%m/%Y")


    dfDragadoIngre = dfDragado
    dfDragadoIngreFecha = dfDragado["Fecha Dragado"]
    dfDragadoIngreFecha = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), dfDragadoIngreFecha))

    dfDragadoIngre['Fecha TS'] = dfDragadoIngreFecha
    dfDragadoIngre = dfDragadoIngre[dfDragadoIngre['Fecha TS'] >= value_dia_inicial]
    dfDragadoIngre = dfDragadoIngre[dfDragadoIngre['Fecha TS'] <= value_dia_final]

    dfBitacoraIngre = dfBitacora
    dfBitacoraIngreFecha = dfBitacora["Fecha bitacora"]
    dfBitacoraIngreFecha = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), dfBitacoraIngreFecha))

    dfBitacoraIngre['Fecha TS'] = dfBitacoraIngreFecha
    dfBitacoraIngre = dfBitacoraIngre[dfBitacoraIngre['Fecha TS'] >= value_dia_inicial]
    dfBitacoraIngre = dfBitacoraIngre[dfBitacoraIngre['Fecha TS'] <= value_dia_final]

    dfCombustibleIngre = dfCombustible
    dfCombustibleIngreFecha = dfCombustible["Fecha combustible"]
    dfCombustibleIngreFecha = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), dfCombustibleIngreFecha))

    dfCombustibleIngre['Fecha TS'] = dfCombustibleIngreFecha
    dfCombustibleIngre = dfCombustibleIngre[dfCombustibleIngre['Fecha TS'] >= value_dia_inicial]
    dfCombustibleIngre = dfCombustibleIngre[dfCombustibleIngre['Fecha TS'] <= value_dia_final]

    dfVolquetaIngre = dfVolqueta
    dfVolquetaIngreFecha = dfVolqueta["Fecha extracción"]
    dfVolquetaIngreFecha = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), dfVolquetaIngreFecha))

    dfVolquetaIngre['Fecha TS'] = dfVolquetaIngreFecha
    dfVolquetaIngre = dfVolquetaIngre[dfVolquetaIngre['Fecha TS'] >= value_dia_inicial]
    dfVolquetaIngre = dfVolquetaIngre[dfVolquetaIngre['Fecha TS'] <= value_dia_final]


    # Calcula los días mecánicos
    arrayDiasDragadoIngre = np.array(dfDragadoIngre['Fecha Dragado'])
    diasMec1Ingre = arrayDiasDragadoIngre[0]
    diasMec1Ingre = datetime.strptime(diasMec1Ingre, "%d/%m/%Y")
    diasMec2Ingre = arrayDiasDragadoIngre[-1]
    diasMec2Ingre = datetime.strptime(diasMec2Ingre, "%d/%m/%Y")
    diasMecIngre = diasMec2Ingre - diasMec1Ingre
    diasMecIngre = diasMecIngre.days + 1
    diasMecBarraIngre = diasMecIngre
    diasMecIngre = str(diasMecIngre) + ' days'


    # Calcula horómetro total de IMS5012 y DRAGMAR2 & Volumen bombeado
    dfDragaIMSIngre = dfDragadoIngre[dfDragadoIngre['Draga'] == 'IMS5012']
    horoIMSIngre = dfDragaIMSIngre['Horometro']
    horoIMSIngre = list(map(lambda x: float(x), horoIMSIngre))
    horoIMSIngre = np.array(horoIMSIngre)

    volBombIMSIngre = dfDragaIMSIngre['Caudal bomba m3/h']
    volBombIMSIngre = list(map(lambda x: float(x), volBombIMSIngre))
    volBombIMSIngre = np.array(volBombIMSIngre)
    volBombIMSIngre = volBombIMSIngre * horoIMSIngre
    volBombIMSIngre2 = volBombIMSIngre * horoIMSIngre

    horoIMSIngre = str(round(horoIMSIngre.sum(), 2)) + ' hr.'
    volBombIMSIngre = str(round(volBombIMSIngre.sum(), 2)) + ' m3'

    dfDragaDRAGIngre = dfDragadoIngre[dfDragadoIngre['Draga'] == 'DRAGMAR2']
    horoDRAGIngre = dfDragaDRAGIngre['Horometro']
    horoDRAGIngre = list(map(lambda x: float(x), horoDRAGIngre))
    horoDRAGIngre = np.array(horoDRAGIngre)

    volBombDRAGIngre = dfDragaDRAGIngre['Caudal bomba m3/h']
    volBombDRAGIngre = list(map(lambda x: float(x), volBombDRAGIngre))
    volBombDRAGIngre = np.array(volBombDRAGIngre)
    volBombDRAGIngre = volBombDRAGIngre * horoDRAGIngre
    volBombDRAGIngre2 = volBombDRAGIngre * horoDRAGIngre


    horoDRAGIngre = str(round(horoDRAGIngre.sum(), 2)) + ' hr.'
    volBombDRAGIngre = str(round(volBombDRAGIngre.sum(), 2)) + ' m3'

    # Calcula combustible total de IMS5012, DRAGMAR2, DOOSAN1 y DOOSAN2
    combusIMSIngre = dfCombustibleIngre[dfCombustibleIngre['Equipo'] == 'IMS5012']
    combusIMSIngre = combusIMSIngre['Volumen combustible gal']
    combusIMSIngre = list(map(lambda x: float(x), combusIMSIngre))
    combusIMSIngre = np.array(combusIMSIngre)
    combusIMSIngre2 = combusIMSIngre.sum()
    combusIMSIngre = str(round(combusIMSIngre.sum(), 2)) + ' gal'

    combusDRAGIngre = dfCombustibleIngre[dfCombustibleIngre['Equipo'] == 'DRAGMAR2']
    combusDRAGIngre = combusDRAGIngre['Volumen combustible gal']
    combusDRAGIngre = list(map(lambda x: float(x), combusDRAGIngre))
    combusDRAGIngre = np.array(combusDRAGIngre)
    combusDRAGIngre2 = combusDRAGIngre.sum()
    combusDRAGIngre = str(round(combusDRAGIngre.sum(), 2)) + ' gal'

    combusDOOSAN1Ingre = dfCombustibleIngre[dfCombustibleIngre['Equipo'] == 'DOOSAN1']
    combusDOOSAN1Ingre = combusDOOSAN1Ingre['Volumen combustible gal']
    combusDOOSAN1Ingre = list(map(lambda x: float(x), combusDOOSAN1Ingre))
    combusDOOSAN1Ingre = np.array(combusDOOSAN1Ingre)
    combusDOOSAN1Ingre = combusDOOSAN1Ingre.sum()
    combusDOOSAN1Ingre2 = combusDOOSAN1Ingre.sum()
    combusDOOSAN1Ingre = str(round(combusDOOSAN1Ingre.sum(), 2)) + ' gal'

    combusDOOSAN2Ingre = dfCombustibleIngre[dfCombustibleIngre['Equipo'] == 'DOOSAN2']
    combusDOOSAN2Ingre = combusDOOSAN2Ingre['Volumen combustible gal']
    combusDOOSAN2Ingre = list(map(lambda x: float(x), combusDOOSAN2Ingre))
    combusDOOSAN2Ingre = np.array(combusDOOSAN2Ingre)
    combusDOOSAN2Ingre = combusDOOSAN2Ingre.sum()
    combusDOOSAN2Ingre2 = combusDOOSAN2Ingre.sum()
    combusDOOSAN2Ingre = str(round(combusDOOSAN2Ingre.sum(), 2)) + ' gal'

    # Calcula volumen bombeado total y combustible total
    volBombIngre = volBombIMSIngre2.sum() + volBombDRAGIngre2.sum()
    volBombIngre = str(round(volBombIngre, 2)) + ' m3'
    combusIngre = combusDOOSAN2Ingre2 + combusDOOSAN1Ingre2 + combusIMSIngre2 + combusDRAGIngre2
    combusIngre = str(round(combusIngre, 2)) + ' gal'

    # Calcula volumen total de lodos extraídos y la barra
    numViajesIngre = dfVolquetaIngre['Viajes']
    numViajesIngre = list(map(lambda x: float(x), numViajesIngre))
    numViajesIngre = np.array(numViajesIngre)

    volVolquetaIngre = dfVolquetaIngre['Volumen m3']
    volVolquetaIngre = list(map(lambda x: float(x), volVolquetaIngre))
    volVolquetaIngre = np.array(volVolquetaIngre)

    volIngre = numViajesIngre * volVolquetaIngre
    volIngreBarra = round((volIngre.sum()/90000)*10, 2)

    volIngre = str(round(volIngre.sum(), 2)) + ' m3'

    # Calcula el avance de la operación
    avanceIngre = numViajesIngre * volVolquetaIngre
    avanceIngre = avanceIngre.sum() * 100 / 90000
    avanceIngre = str(round(avanceIngre, 2)) + '%'

    # Calcula los días operados en toda la operación
    diasVolquetaIngre = dfVolquetaIngre['Fecha extracción']
    diasVolquetaIngre = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diasVolquetaIngre))
    diasVolquetaIngre = set(diasVolquetaIngre)

    diasDragadoIngre = dfDragadoIngre['Fecha Dragado']
    diasDragadoIngre = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diasDragadoIngre))
    diasDragadoIngre = set(diasDragadoIngre)

    diasOperIngre = diasVolquetaIngre.union(diasDragadoIngre)
    diasOperIngre = list(dict.fromkeys(diasOperIngre))
    diasOperIngre = str(len(diasOperIngre)) + ' days'

    # Crea pie chart con bitácora acumulada
    pie_chart_bitacora_Ingre = px.pie(
         data_frame=dfBitacoraIngre,
         values='Horas',
         names='Evento',
         color='Evento',  # differentiate markers (discrete) by color
         #color_discrete_sequence=["green", "Black", "blue", "yellow", "red", "purple"],  # set marker colors
         #hover_name='negative',  # values appear in bold in the hover tooltip
         #hover_data=['positive'],            #values appear as extra data in the hover tooltip
         custom_data=['Total'],              #values are extra data to be used in Dash callbacks
         #labels={"state": "the State"},  # map the labels
         title='Project Log',  # figure title
         template='presentation',  #
         width=800,  # figure width in pixels
         height=600,  # figure height in pixels
         hole=0.5,  # represents the hole in middle of pie
     )

    pie_chart_bitacora_Ingre.update_layout(
         font_family="Franklin Gothic",
         title_font_family="Franklin Gothic",
    )



    ####################### Gráfico Volumen agua lodosa ingresado al Geotube ############################
    labelGraphGT = 'gal'

    dfQbombaIMS = dfDragadoIngre[dfDragadoIngre['Draga'] == 'IMS5012']
    QbombaIMS = dfQbombaIMS["Caudal bomba m3/h"]
    horoIMS = dfQbombaIMS["Horometro"]
    fechaHorasBombaIMS = dfQbombaIMS["Fecha Dragado"]
    fechaHorasBombaIMS = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaHorasBombaIMS))
    QbombaIMS = list(map(lambda x: float(x), QbombaIMS))
    horoIMS = list(map(lambda x: float(x), horoIMS))
    volLDSIMS = np.array(QbombaIMS) * np.array(horoIMS)

    # Crea la figura de agua lodosa
    volLDSIMS = list(map(lambda x: int(x), volLDSIMS))


    dfQbombaDRAG = dfDragadoIngre[dfDragadoIngre['Draga'] == 'DRAGMAR2']
    QbombaDRAG = dfQbombaDRAG["Caudal bomba m3/h"]
    horoDRAG = dfQbombaDRAG["Horometro"]
    fechaHorasBombaDRAG = dfQbombaDRAG["Fecha Dragado"]
    fechaHorasBombaDRAG = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaHorasBombaDRAG))
    QbombaDRAG = list(map(lambda x: float(x), QbombaDRAG))
    horoDRAG = list(map(lambda x: float(x), horoDRAG))
    volLDSDRAG = np.array(QbombaDRAG) * np.array(horoDRAG)
    volLDSDRAG = list(map(lambda x: int(x), volLDSDRAG))

    figAguaLDSIngre = go.Figure()

    figAguaLDSIngre.add_trace(go.Scatter(x=fechaHorasBombaIMS, y=volLDSIMS, name="IMS5012", text=volLDSIMS,
                                     mode='lines+markers+text', textposition='bottom right', ))
    figAguaLDSIngre.add_trace(go.Scatter(x=fechaHorasBombaDRAG, y=volLDSDRAG, name="DRAGMAR2", text=volLDSDRAG,
                                     mode='lines+markers+text', textposition='bottom right', ))

    figAguaLDSIngre.update_layout(title="Sludge Water Entered into Sediment Settling Containers", xaxis_title="Date",
                              yaxis_title="Volume [m3]")
    figAguaLDSIngre.update_layout(legend=dict(
         orientation="h",
         yanchor="bottom",
         y=-0.7,
         xanchor="center",
         x=0.5
     ))

    figAguaLDSIngre.update_layout(
         font_family="Franklin Gothic",
         # font_color="blue",
         title_font_family="Franklin Gothic",
         # title_font_color="red",
         # legend_title_font_color="green"
     )
    figAguaLDSIngre.update_xaxes(title_font_family="Franklin Gothic")

    # Crea la figura de horómetro
    dfHoroIMS = dfDragadoIngre[dfDragadoIngre['Draga'] == 'IMS5012']
    horasIMS = dfHoroIMS['Horometro']
    horasIMS = list(map(lambda x: float(x), horasIMS))
    fechaHorasIMS = dfHoroIMS["Fecha Dragado"]
    fechaHorasIMS = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaHorasIMS))

    dfHoroDRAG = dfDragadoIngre[dfDragadoIngre['Draga'] == 'DRAGMAR2']
    horasDRAG = dfHoroDRAG['Horometro']
    horasDRAG = list(map(lambda x: float(x), horasDRAG))
    fechaHorasDRAG = dfHoroIMS["Fecha Dragado"]
    fechaHorasDRAG = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaHorasDRAG))



    figHorometroIngre = go.Figure()

    figHorometroIngre.add_trace(go.Scatter(x=fechaHorasIMS, y=horasIMS, name="IMS5012", text=horasIMS,
                                       mode='lines+markers+text', textposition='bottom right', ))

    figHorometroIngre.add_trace(go.Scatter(x=fechaHorasDRAG, y=horasDRAG, name="DRAGMAR2", text=horasDRAG,
                                       mode='lines+markers+text', textposition='bottom right', ))


    figHorometroIngre.update_layout(title="Horomter", xaxis_title="Date",
                                yaxis_title="Time [hr.]")
    figHorometroIngre.update_layout(legend=dict(
         orientation="h",
         yanchor="bottom",
         y=-0.7,
         xanchor="center",
         x=0.5
    ))

    figHorometroIngre.update_layout(
        font_family="Franklin Gothic",
        # font_color="blue",
        title_font_family="Franklin Gothic",
        # title_font_color="red",
        # legend_title_font_color="green"
    )
    figHorometroIngre.update_xaxes(title_font_family="Franklin Gothic")

    # Crea la figura de las pimpinas
    dfCombustibleIMS = dfCombustibleIngre[dfCombustibleIngre['Equipo'] == 'IMS5012']
    ycombusIMS = dfCombustibleIMS['Volumen combustible gal']
    ycombusIMS = list(map(lambda x: float(x), ycombusIMS))
    fechaGasolinaIMS = dfCombustibleIMS['Fecha combustible']
    fechaGasolinaIMS = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaGasolinaIMS))

    dfCombustibleDRAG = dfCombustibleIngre[dfCombustibleIngre['Equipo'] == 'DRAGMAR2']
    ycombusDRAG = dfCombustibleDRAG['Volumen combustible gal']
    ycombusDRAG = list(map(lambda x: float(x), ycombusDRAG))
    fechaGasolinaDRAG = dfCombustibleDRAG['Fecha combustible']
    fechaGasolinaDRAG = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaGasolinaDRAG))

    dfCombustibleDOOSAN1 = dfCombustibleIngre[dfCombustibleIngre['Equipo'] == 'DOOSAN1']
    ycombusDOOSAN1 = dfCombustibleDOOSAN1['Volumen combustible gal']
    ycombusDOOSAN1 = list(map(lambda x: float(x), ycombusDOOSAN1))
    fechaGasolinaDOOSAN1 = dfCombustibleDOOSAN1['Fecha combustible']
    fechaGasolinaDOOSAN1 = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaGasolinaDOOSAN1))

    dfCombustibleDOOSAN2 = dfCombustibleIngre[dfCombustibleIngre['Equipo'] == 'DOOSAN2']
    ycombusDOOSAN2 = dfCombustibleDOOSAN1['Volumen combustible gal']
    ycombusDOOSAN2 = list(map(lambda x: float(x), ycombusDOOSAN2))
    fechaGasolinaDOOSAN2 = dfCombustibleDOOSAN2['Fecha combustible']
    fechaGasolinaDOOSAN2 = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), fechaGasolinaDOOSAN2))


    suffixyPimpinas = 'Fuel Volume [gal]'


    figPimpinasIngre = go.Figure()

    figPimpinasIngre.add_trace(go.Scatter(x=fechaGasolinaIMS, y=ycombusIMS, text=ycombusIMS, name='IMS5012',
                                      mode='lines+markers+text', textposition='bottom right', ))
    figPimpinasIngre.add_trace(go.Scatter(x=fechaGasolinaDRAG, y=ycombusDRAG, text=ycombusDRAG, name='DRAGMAR2',
                                      mode='lines+markers+text', textposition='bottom right', ))
    figPimpinasIngre.add_trace(go.Scatter(x=fechaGasolinaDOOSAN1, y=ycombusDOOSAN1, text=ycombusDOOSAN1, name='DOOSAN1',
                                      mode='lines+markers+text', textposition='bottom right', ))
    figPimpinasIngre.add_trace(go.Scatter(x=fechaGasolinaDOOSAN2, y=ycombusDOOSAN2, text=ycombusDOOSAN2, name='DOOSAN2',
                                      mode='lines+markers+text', textposition='bottom right', ))


    figPimpinasIngre.update_layout(title="Volume of Fuel Consumption", xaxis_title="Date",
                               yaxis_title=suffixyPimpinas)
    figPimpinasIngre.update_layout(legend=dict(
         orientation="h",
         yanchor="bottom",
         y=-0.5,
         xanchor="center",
         x=0.5,
     ), )

    figPimpinasIngre.update_layout(
         font_family="Franklin Gothic",
         title_font_family="Franklin Gothic",
    )
    figPimpinasIngre.update_xaxes(title_font_family="Franklin Gothic")


    # Crea figura de peso y volumen acumulados
    diasVolqueta = dfVolquetaIngre['Fecha extracción']
    #diasVolqueta = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diasVolqueta))
    diasVolqueta = list(dict.fromkeys(diasVolqueta))

    volumenAcumY45 = [None]

    for i in diasVolqueta:
        #i2 = str(i.day) + "/" + str(i.month) + "/" + str(i.year)

        dfVolquetaDia = dfVolquetaIngre[dfVolquetaIngre["Fecha extracción"] == i]

        volumenAcumVec = dfVolquetaDia["Volumen m3"]
        volumenAcumVec = list(map(lambda x: float(x), volumenAcumVec))
        volumenAcumVec = np.array(volumenAcumVec)

        viajesAcumVec = dfVolquetaDia["Viajes"]
        viajesAcumVec = list(map(lambda x: float(x), viajesAcumVec))
        viajesAcumVec = np.array(viajesAcumVec)

        volumenAcumVec = volumenAcumVec * viajesAcumVec


        volumenAcumVec45 = round(sum(volumenAcumVec), 0)
        volumenAcumY45.append(volumenAcumVec45)

    volumenAcumY45.remove(None)

    fechaX45 = list(map(lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"), diasVolqueta))



    figPesoVolIngre = go.Figure()

    figPesoVolIngre.add_trace(go.Scatter(x=fechaX45, y=volumenAcumY45, name="Volumen [m3]", text=volumenAcumY45,
                                  mode='lines+markers+text', textposition='bottom right', ))
    figPesoVolIngre.update_layout(title="Volume of Extracted Material", xaxis_title="Date",
                        yaxis_title="Volume [m3]")
    figPesoVolIngre.update_layout(legend=dict(
        yanchor="bottom",
        y=-0.5,
        xanchor="center",
        x=0.5
    ))

    figPesoVolIngre.update_layout(
        font_family="Franklin Gothic",
        title_font_family="Franklin Gothic",
    )
    figPesoVolIngre.update_xaxes(title_font_family="Franklin Gothic")

    # Calcula las zonas dragadas en un día
    #dfDragado['Zonas'] = '(' + dfDragado['Canal'] + ', ' + dfDragado['Abscisa'] + ')'
    #zonasAcum = dfDragado[dfDragado['Fecha Dragado'] == value_dia]
    zonasIngre = dfDragadoIngre['Zonas']
    zonasIngre = list(dict.fromkeys(zonasIngre))
    zonasDragIngre = ''

    for i in zonasIngre:
        zonasDragIngre = i + ', ' + zonasDragIngre

    zonasDragIngre = str(zonasDragIngre)
    zonasDragIngre = zonasDragIngre[:-2]
    print('zonasDragIngre')
    print(zonasDragIngre)


    return horoIMSdia, horoDRAGdia, combusIMSdia, combusDRAGdia, volBombIMSdia, volBombDRAGdia, \
           combusDOOSAN1dia, operDOOSAN1, combusDOOSAN2dia, operDOOSAN2, pie_chart_bitacora_dia, \
           figPesoDia, volDiaExtraccion, horoIMSacum, combusIMSacum, volBombIMSacum, \
           horoDRAGacum,combusDRAGacum, volBombDRAGacum, combusDOOSAN1acum, combusDOOSAN2acum, \
           volBombAcum, combusAcum, volAcum, avance, volAcumBarra, pie_chart_bitacora_acum, \
           figAguaLDS, figPimpinas, figHorometro, figPesoVol, diasOper, zonasDragDia, zonasDragAcum, \
            diasOperIngre, horoIMSIngre, combusIMSIngre, volBombIMSIngre, horoDRAGIngre, combusDRAGIngre, \
            volBombDRAGIngre, combusDOOSAN1Ingre, combusDOOSAN2Ingre, volBombIngre, combusIngre, \
            volIngre, avanceIngre, volIngreBarra, zonasIngre, figPesoVolIngre, figHorometroIngre, \
            figAguaLDSIngre, pie_chart_bitacora_Ingre, figPimpinasIngre, diasMec, diasMecIngre



if __name__ == '__main__':
    app.run_server(debug=False)

