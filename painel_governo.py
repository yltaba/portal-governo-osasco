import pandas as pd
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from pathlib import Path
import plotly.express as px

TEMPLATE = "plotly_white"

# Caminho dos dados
data_path = Path().resolve().parent / "etl" / "data" / "processed"

# Carregar os dados
caged = pd.read_csv(
    "data/caged_saldo_movimentacao_anual.csv",
    encoding="latin1",
    sep=";"
)

rais = pd.read_csv(
    "data/rais_anual.csv",
    sep=";"
)


# Criar lista de opções únicas para o dropdown
opcoes_cnae = [
    {"label": x, "value": x}
    for x in sorted(caged["cnae_2_descricao_secao"].dropna().unique())
]
opcoes_cnae_rais = [
    {"label": x, "value": x}
    for x in sorted(rais["descricao_secao_cnae"].dropna().unique())
]


# Layout da aplicação Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        html.Div(
            [
                html.Img(
                    src="https://osasco.sp.gov.br/wp-content/uploads/2024/12/logo-pmo-2025-2028-horizontal.png",
                    style={
                        "width": "50%",
                        "height": "50%",
                        "display": "block",
                        "margin": "auto",
                        "margin-top": "30px",
                    },
                )
            ],
            style={"text-align": "center"},
        ),
        html.Div(
            [
                html.H2("Dados CAGED", className="text-center mt-4"),
                # Dropdown filtro fig-saldo-anual
                dcc.Dropdown(
                    id="filtro-cnae-caged-saldo",
                    options=[{"label": "Todos", "value": "Todos"}] + opcoes_cnae,
                    value="Todos",
                    clearable=False,
                    className="mb-3",
                ),
                # Gráfico
                dcc.Graph(id="fig-saldo-anual"),
            ]
        ),
        html.Div(
            [
                html.H2("Dados RAIS", className="text-center mt-4"),
                # Dropdown filtro fig-saldo-anual
                dcc.Dropdown(
                    id="filtro-cnae-rais-saldo",
                    options=[{"label": "Todos", "value": "Todos"}] + opcoes_cnae,
                    value="Todos",
                    clearable=False,
                    className="mb-3",
                ),
                # Gráfico
                dcc.Graph(id="fig-rais-anual"),
            ]
        ),
    ]
)


@app.callback(
    Output("fig-saldo-anual", "figure"), Input("filtro-cnae-caged-saldo", "value")
)
def atualizar_grafico_caged(filtro_cnae):
    if filtro_cnae == "Todos":
        df_filtrado = caged
    else:
        df_filtrado = caged[caged["cnae_2_descricao_secao"] == filtro_cnae]

    caged_ano = df_filtrado.groupby("ano", as_index=False).agg(
        {"saldo_movimentacao": "sum"}
    )

    fig = px.bar(
        caged_ano,
        x="ano",
        y="saldo_movimentacao",
        title=f"Saldo de Movimentações por Ano",
        template=TEMPLATE,
    )

    return fig


@app.callback(
    Output("fig-rais-anual", "figure"), Input("filtro-cnae-rais-saldo", "value")
)
def atualizar_grafico_rais_anual(filtro_cnae):
    if filtro_cnae == "Todos":
        df_filtrado = rais
    else:
        df_filtrado = rais[rais["descricao_secao_cnae"] == filtro_cnae]

    rais_anual = df_filtrado.groupby("ano", as_index=False).agg(
        {"quantidade_vinculos_ativos": "sum"}
    )

    fig = px.line(
        rais_anual,
        x="ano",
        y="quantidade_vinculos_ativos",
        markers="o",
        title="Estoque de postos de trabalho por ano",
        template=TEMPLATE,
    )

    return fig


# Executar o app
if __name__ == "__main__":
    app.run_server(debug=True)
