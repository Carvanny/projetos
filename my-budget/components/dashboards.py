from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
from globals import *
import urllib.request
import json
import locale
import time
from app import app

import pdb
from dash_bootstrap_templates import template_from_url, ThemeChangerAIO

card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

graph_margin = dict(l=25, r=25, t=25, b=0)

hoje = datetime.today()


# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
            # Saldo
            dbc.Col([
                    dbc.CardGroup([
                        dbc.Card([
                            html.Legend("Saldo"),
                            html.H5("R$ -", id="p-saldo-dashboards", style={}),
                        ], style={"padding-left": "20px", "padding-top": "10px"}),
                        dbc.Card(
                            html.Div(className="fa fa-university", style=card_icon),
                            color="warning",
                            style={"maxWidth": 75, "height": 100,
                                   "margin-left": "-10px"},
                        )])
                    ], width=4),

            # Receita
            dbc.Col([
                    dbc.CardGroup([
                        dbc.Card([
                            html.Legend("Receita"),
                            html.H5("R$ -", id="p-receita-dashboards"),
                        ], style={"padding-left": "20px", "padding-top": "10px"}),
                        dbc.Card(
                            html.Div(className="fa fa-smile-o",
                                     style=card_icon),
                            color="success",
                            style={"maxWidth": 75, "height": 100,
                                   "margin-left": "-10px"},
                        )])
                    ], width=4),

            # Despesa
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Legend("Despesas"),
                        html.H5("R$ -", id="p-despesa-dashboards"),
                    ], style={"padding-left": "20px", "padding-top": "10px"}),
                    dbc.Card(
                        html.Div(className="fa fa-meh-o", style=card_icon),
                        color="danger",
                        style={"maxWidth": 75, "height": 100,
                               "margin-left": "-10px"},
                    )])
            ], width=4),

            # Investimentos
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Legend("Investimentos"),
                        html.H5("R$ -", id="p-investimentos-dashboards"),
                    ], style={"padding-left": "20px", "padding-top": "10px"}),
                    dbc.Card(
                        html.Div(className="fa fa-money", style=card_icon),
                        color="brown",
                        style={"maxWidth": 75, "height": 100,
                               "margin-left": "-10px"},
                    )])
            ], width=4),

            # Bitcoin
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Legend("Bitcoin"),
                        html.H5("$ -", id="p-bitcoin-dashboards"),
                    ], style={"padding-left": "20px", "padding-top": "10px"}),
                    dbc.Card(
                        html.Div(className="fa fa-btc", style=card_icon),
                        color="blue",
                        style={"maxWidth": 75, "height": 100,
                               "margin-left": "-10px"},
                    )])
            ], width=4),

            ], style={"margin": "10px"}),

    dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.Legend("Filtrar lançamentos", className="card-title"),
                    html.Label("Categorias das receitas"),
                    html.Div(
                        dcc.Dropdown(
                            id="dropdown-receita",
                            clearable=False,
                            style={"width": "100%"},
                            persistence=True,
                            persistence_type="session",
                            multi=True)
                    ),

                    html.Label("Categorias das despesas",
                               style={"margin-top": "10px"}),
                    dcc.Dropdown(
                        id="dropdown-despesa",
                        clearable=False,
                        style={"width": "100%"},
                        persistence=True,
                        persistence_type="session",
                        multi=True
                    ),

                    html.Label("Categorias dos investimentos", style={"margin-top": "10px"}),
                    dcc.Dropdown(
                        id="dropdown-investimentos",
                        clearable=False,
                        style={"width": "100%"},
                        persistence=True,
                        persistence_type="session",
                        multi=True
                    ),

                    html.Legend("Período de Análise", style={"margin-top": "10px"}),
                    dcc.DatePickerRange(
                        month_format='MMMM Y',
                        end_date_placeholder_text='Data...',
                        start_date = datetime(hoje.year, hoje.month, 1),
                        end_date=datetime(hoje.year, hoje.month, 30),
                        with_portal=True,
                        updatemode='singledate',
                        id='date-picker-config',
                        style={'z-index': '100'})],

                    style={"height": "100%", "padding": "20px"}),

            ], width=4),

            dbc.Col(
                dbc.Card(
                    dcc.Graph(  id="graph1"), 
                                style={"height": "100%", "padding": "10px"}), 
                                width=8),], 
                                style={"margin": "10px"}
                            ),

    dbc.Row([
            dbc.Col(
                dbc.Card(
                    dcc.Graph(  id="graph2"),
                                style={"padding": "10px"}), 
                                width=6),
            dbc.Col(
                dbc.Card(
                    dcc.Graph(  id="graph3"),
                                style={"padding": "10px"}),
                                width=3),
            dbc.Col(
                dbc.Card(
                    dcc.Graph(  id="graph4"),
                                style={"padding": "10px"}),
                                width=3),
            ], 
            style={"margin": "10px"})
])


# =========  Callbacks  =========== #
# Dropdown Receita
@app.callback([Output("dropdown-receita", "options"),
               Output("dropdown-receita", "value"),
               Output("p-receita-dashboards", "children")],
               [Input("store-receitas", "data"),
               Input('date-picker-config', 'start_date'),
               Input('date-picker-config', 'end_date')]               
)          
def populate_dropdownvalues(data, start_date, end_date):
    df = pd.DataFrame(data)

    mask = (df['Data'] > start_date) & (df['Data'] <= end_date)
    df_final = df.loc[mask]
    print(df_final)
    valor = df_final['Valor'].sum()
    val = df_final.Categoria.unique().tolist()
    locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')
    valor_real = locale.currency(valor)

    return [([{"label": x, "value": x} for x in df.Categoria.unique()]), val, f"{valor_real}"]

# Dropdown Despesa
@app.callback([Output("dropdown-despesa", "options"),
               Output("dropdown-despesa", "value"),
               Output("p-despesa-dashboards", "children")],
               [Input("store-despesas", "data"),
               Input('date-picker-config', 'start_date'),
               Input('date-picker-config', 'end_date')]   
)
def populate_dropdownvalues(data, start_date, end_date):
    df = pd.DataFrame(data)
    mask = (df['Data'] > start_date) & (df['Data'] <= end_date)
    df_final = df.loc[mask]    
    valor = df_final['Valor'].sum()
    val = df_final.Categoria.unique().tolist()
    locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')
    valor_real = locale.currency(valor)
    return [([{"label": x, "value": x} for x in df.Categoria.unique()]), val, f"{valor_real}"]

# VALOR - saldo
@app.callback(
    Output("p-saldo-dashboards", "children"),
    [Input("store-despesas", "data"),
     Input("store-receitas", "data"),
     Input('date-picker-config', 'start_date'),
     Input('date-picker-config', 'end_date')  
    ])
def saldo_total(despesas, receitas, start_date, end_date):
    df_despesas = pd.DataFrame(despesas)
    df_receitas = pd.DataFrame(receitas)

    mask_despesas = (df_despesas['Data'] > start_date) & (df_despesas['Data'] <= end_date)
    df_despesas_final = df_despesas.loc[mask_despesas]  

    mask_receita = (df_receitas['Data'] > start_date) & (df_receitas['Data'] <= end_date)
    df_receitas_final = df_receitas.loc[mask_receita]      

    valor = df_receitas_final['Valor'].sum() - df_despesas_final['Valor'].sum()
    locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')
    valor_real = locale.currency(valor)
    return f"{valor_real}"

# Dropdown Investimentos
@app.callback([Output("dropdown-investimentos", "options"),
               Output("dropdown-investimentos", "value"),
               Output("p-investimentos-dashboards", "children")],
              Input("store-investimentos", "data"))
def populate_dropdownvalues(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()
    locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')
    valor_real = locale.currency(valor)
    
    return [([{"label": x, "value": x} for x in df.Categoria.unique()]), val, f"{valor_real}"]

# VALOR - Bitcoin
@app.callback([Output("p-bitcoin-dashboards", "children")],
              Input("store-investimentos", "data"))
def populate_dropdownvalues(data):
    locale.setlocale(locale.LC_MONETARY, 'en_US.UTF-8')
    valor_real = locale.currency(obter_valor_bitcoin())

    return [f"{valor_real}"]


# Gráfico 1
@app.callback(
    Output('graph1', 'figure'),
    [Input('store-despesas', 'data'),
     Input('store-receitas', 'data'),
     Input("dropdown-despesa", "value"),
     Input("dropdown-receita", "value"),
     Input(ThemeChangerAIO.ids.radio("theme"), "value")])
def update_output(data_despesa, data_receita, despesa, receita, theme):
    df_ds = pd.DataFrame(data_despesa).sort_values(by='Data', ascending=True)
    df_rc = pd.DataFrame(data_receita).sort_values(by='Data', ascending=True)

    dfs = [df_ds, df_rc]
    for df in dfs:
        df['Acumulo'] = df['Valor'].cumsum()
        df["Data"] = pd.to_datetime(df["Data"])
        df["Mes"] = df["Data"].apply(lambda x: x.month)

    df_receitas_mes = df_rc.groupby("Mes")["Valor"].sum()
    df_despesas_mes = df_ds.groupby("Mes")["Valor"].sum()
    df_saldo_mes = df_receitas_mes - df_despesas_mes
    df_saldo_mes.to_frame()
    df_saldo_mes = df_saldo_mes.reset_index()
    df_saldo_mes['Acumulado'] = df_saldo_mes['Valor'].cumsum()
    df_saldo_mes['Mes'] = df['Mes'].apply(lambda x: calendar.month_abbr[x])

    df_ds = df_ds[df_ds['Categoria'].isin(despesa)]
    df_rc = df_rc[df_rc['Categoria'].isin(receita)]

    fig = go.Figure()

    # fig.add_trace(go.Scatter(name='Despesas', x=df_ds['Data'], y=df_ds['Acumulo'], fill='tonexty', mode='lines'))
    fig.add_trace(go.Scatter(
        name='Receitas', x=df_rc['Data'], y=df_rc['Acumulo'], fill='tonextx', mode='lines'))
    # fig.add_trace(go.Scatter(name='Saldo Mensal', x=df_saldo_mes['Mes'], y=df_saldo_mes['Acumulado'], mode='lines'))

    fig.update_layout(margin=graph_margin, template=template_from_url(theme))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    return fig

# Gráfico 2
@app.callback(
    Output('graph2', 'figure'),
    [Input('store-receitas', 'data'),
     Input('store-despesas', 'data'),
     Input('dropdown-receita', 'value'),
     Input('dropdown-despesa', 'value'),
     Input('date-picker-config', 'start_date'),
     Input('date-picker-config', 'end_date'),
     Input(ThemeChangerAIO.ids.radio("theme"), "value")]
)
def graph2_show(data_receita, data_despesa, receita, despesa, start_date, end_date, theme):
    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)

    dfs = [df_ds, df_rc]

    df_rc['Output'] = 'Receitas'
    df_ds['Output'] = 'Despesas'
    df_final = pd.concat(dfs)

    mask = (df_final['Data'] > start_date) & (df_final['Data'] <= end_date)
    df_final = df_final.loc[mask]

    df_final = df_final[df_final['Categoria'].isin(
        receita) | df_final['Categoria'].isin(despesa)]

    fig = px.bar(df_final, x="Data", y="Valor",
                 color='Output', barmode="group")
    fig.update_layout(margin=graph_margin, template=template_from_url(theme))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    return fig


# Gráfico 3
@app.callback(
    Output('graph3', "figure"),
    [Input('store-receitas', 'data'),
     Input('dropdown-receita', 'value'),
     Input(ThemeChangerAIO.ids.radio("theme"), "value")]
)
def pie_receita(data_receita, receita, theme):
    df = pd.DataFrame(data_receita)
    df = df[df['Categoria'].isin(receita)]

    fig = px.pie(df, values=df.Valor, names=df.Categoria, hole=.2)
    fig.update_layout(title={'text': "Receitas"})
    fig.update_layout(margin=graph_margin, template=template_from_url(theme))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    return fig

# Gráfico 4
@app.callback(
    Output('graph4', "figure"),
    [Input('store-despesas', 'data'),
     Input('dropdown-despesa', 'value'),
     Input(ThemeChangerAIO.ids.radio("theme"), "value")]
)
def pie_despesa(data_despesa, despesa, theme):
    df = pd.DataFrame(data_despesa)
    df = df[df['Categoria'].isin(despesa)]

    fig = px.pie(df, values=df.Valor, names=df.Categoria, hole=.2)
    fig.update_layout(title={'text': "Despesas"})

    fig.update_layout(margin=graph_margin, template=template_from_url(theme))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    return fig



def obter_valor_bitcoin():
    try:
        url = "http://api.coindesk.com/v1/bpi/currentprice.json"
        with urllib.request.urlopen(url) as url:
            response = url.read()
            data = json.loads(response.decode('utf-8'))
            valor = float(data['bpi']['USD']['rate'].replace(",", ""))

            print("Valor do bitcoin agora: ", valor)
            return valor
    except urllib.error.HTTPError:
        print('URL inexistente!')


