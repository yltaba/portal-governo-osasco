import pandas as pd

def gerar_tabela_admissoes_desligamentos(df_caged):
    admissoes = (
        df_caged.loc[df_caged["saldomovimentacao"] == 1]
        .groupby("mes", as_index=False)
        .agg({"saldomovimentacao": "sum"})
        .rename(columns={"saldomovimentacao": "admissoes"})
    )
    desligamentos = (
        df_caged.loc[df_caged["saldomovimentacao"] == -1]
        .groupby("mes", as_index=False)
        .agg({"saldomovimentacao": "sum"})
        .rename(columns={"saldomovimentacao": "desligamentos"})
    )
    admissoes_desligamentos = pd.merge(admissoes, desligamentos, on="mes")
    admissoes_desligamentos["desligamentos"] = admissoes_desligamentos[
        "desligamentos"
    ].abs()
    admissoes_desligamentos = admissoes_desligamentos.melt(
        id_vars="mes",
        value_vars=["admissoes", "desligamentos"],
        var_name="tipo",
        value_name="valor",
    )
    return admissoes_desligamentos