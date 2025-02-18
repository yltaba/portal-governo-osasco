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
    data_path / "caged.csv",
    encoding="latin1",
    sep=";",
    dtype={
        "ano": int,
        "mes": int,
        "sigla_uf": str,
        "id_municipio": int,
        "tipo_estabelecimento": int,
        "tipo_movimentacao_desagregado": int,
        "quantidade_horas_contratadas": int,
        "salario_mensal": float,
        "saldo_movimentacao": int,
        "indicador_aprendiz": int,
        "indicador_trabalho_intermitente": float,
        "indicador_trabalho_parcial": float,
        "tipo_deficiencia": float,
        "cbo_2002": str,
        "cbo_2002_descricao": str,
        "cnae_2": str,
        "grau_instrucao": int,
        "idade": int,
        "sexo": int,
        "raca_cor": int,
        "tamanho_estabelecimento": float,
        "cnae_2_descricao_secao": str,
        "sigla_uf_nome": str,
        "id_municipio_nome": str,
        "id_tabela": str,
        "raca_cor_descricao": str,
        "sexo_descricao": str,
        "grau_instrucao_descricao": str,
        "tipo_deficiencia_descricao": str,
    },
)

rais = pd.read_csv(
    data_path / "rais_estab.csv",
    sep=";",
    dtype={
        "ano": int,
        "sigla_uf": str,
        "id_municipio": int,
        "quantidade_vinculos_ativos": float,
        "quantidade_vinculos_clt": float,
        "quantidade_vinculos_estatutarios": float,
        "tamanho_estabelecimento": int,
        "cnae_1": str,
        "cnae_2": str,
        "cnae_2_subclasse": str,
        "descricao_secao_cnae_2": str,
        "descricao_secao_cnae_1": str,
        "descricao_secao_cnae": str,
    },
)
rais_anual = rais.groupby("ano", as_index=False).agg(
    {"quantidade_vinculos_ativos": "sum", "quantidade_vinculos_clt": "sum"}
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
