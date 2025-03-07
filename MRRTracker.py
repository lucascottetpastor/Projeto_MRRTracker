import streamlit as st
import pandas as pd
import plotly.express as px


def organizar_df(df):
    df['data início'] = pd.to_datetime(df['data início'])
    df['data status'] = pd.to_datetime(df['data status'])
    df['data cancelamento'] = pd.to_datetime(df['data cancelamento'], errors='coerce')
    df['próximo ciclo'] = pd.to_datetime(df['próximo ciclo'], errors='coerce')
    return df

def mrr(df):
    df['mes_ano'] = pd.to_datetime(df['data início'], errors='coerce').dt.to_period('M')
    df_mrr = df[df['status'] == 'Ativa'].groupby('mes_ano')['valor'].sum().reset_index()
    df_mrr['valor'] = pd.to_numeric(df_mrr['valor'], errors='coerce')
    df_mrr = df_mrr.dropna(subset=['valor'])
    df_mrr['ano'] = df_mrr['mes_ano'].dt.strftime('%Y')
    df_mrr['mes'] = df_mrr['mes_ano'].dt.strftime('%b')
    df_mrr['mes_ano'] = df_mrr['mes_ano'].dt.strftime('%m/%Y')
    return df_mrr

def churn_rate(df):
    df['mes inicio'] = pd.to_datetime(df['data início'], errors='coerce').dt.to_period('M')
    df['mes cancelamento'] = pd.to_datetime(df['data cancelamento'], errors='coerce').dt.to_period('M')
    assinaturas_canceladas = df[df['status'] == 'Cancelada']
    cancelamentos_por_mes = assinaturas_canceladas['mes cancelamento'].value_counts().sort_index()
    total_assinaturas_iniciais_por_mes = df.groupby('mes inicio')['ID assinante'].nunique()
    churn_rate_por_mes = cancelamentos_por_mes / total_assinaturas_iniciais_por_mes
    df_churn = pd.DataFrame()
    df_churn['ano_mes'] = churn_rate_por_mes.index.astype(str)
    df_churn['valor'] = churn_rate_por_mes.values
    df_churn['ano_mes'] = pd.to_datetime(df_churn['ano_mes'])
    df_churn['ano'] = df_churn['ano_mes'].dt.year.astype('object')
    df_churn['mes'] = df_churn['ano_mes'].dt.strftime('%b')

    return df_churn

def receita_ano(df):
    df_ativas = df[df['status'] == 'Ativa']
    receita_total_por_ano = df_ativas.groupby(df_ativas['data início'].dt.year)['valor'].sum().reset_index()
    receita_total_por_ano.columns = ['ano', 'receita_total']
    return receita_total_por_ano

def ativo_cancelado(df):
    df['ativo'] = df['status'].apply(lambda x: 1 if x == 'Ativa' else 0)

    df['ano'] = df['data início'].dt.year
    assinaturas_por_mes = df.groupby(['ano', 'status']).size().reset_index(name='contagem')
    return assinaturas_por_mes

st.set_page_config(layout="wide")
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df = organizar_df(df)
    df_mrr = mrr(df)
    df_churn_rate = churn_rate(df)
    df_receitaano = receita_ano(df)
    df_ativo_cancel = ativo_cancelado(df)

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    fig_mrr = px.bar(df_mrr, x='mes', y='valor', title='MRR', color='ano')
    col1.plotly_chart(fig_mrr)
    fig_churn = px.bar(df_churn_rate, x='mes', y='valor', title='CHURN RATE', color='ano')
    col2.plotly_chart(fig_churn)
    fig_receitaano = px.bar(df_receitaano, x='ano', y='receita_total', title='RECEITA TOTAL POR ANO')
    col3.plotly_chart(fig_receitaano)
    fig_ativo_cancel = px.bar(df_ativo_cancel, x='ano', y='contagem',color='status',title='ATIVO E CANCELADO')
    col4.plotly_chart(fig_ativo_cancel)
else:
    st.warning("Por favor, faça o upload de um arquivo Excel.")
