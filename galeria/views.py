import plotly.express as px
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from django.shortcuts import render
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Configurar o locale para Brasil

def format_number(value):
    return locale.format_string("%.2f", value, grouping=True).replace(",", "X").replace(".", ",").replace("X", ".")


def index(request):
    # Carregar o arquivo Excel
    df_prod = pd.read_excel('dados/data.xlsx')

    # Criar a nova coluna 'Produção'
    def classify_material(material):
        if material in [
            "ITM 04 SINTER BLEND ALIMENTACAO",
            "ITM 04 SINTER ESPECIAL ALIMENTACAO",
            "Sinter ITM 04",
            "ITM 04[SUBPRODUTO]-ITM 09 HEMATITINHA COMUM"
        ]:
            return "ITM 04"
     
            return "ITM 09"
        elif material in [
            "Sinter Especial",
            "Sinter Premium",
            "Hematitinha Premium ITM 09",
            "Hematitinha Especial ITM 09 A"
        ]:
            return "ITM 09"
        elif material in [
            "scalper 1 especial",
            "scalper 2 especial",
            "Sinter blendagem"
        ]:
            return "Scalper"
        elif material in [
            "ITM 02 PRINCIPAL-PATIO DE PRODUTOS SINTER FEED ESPECIAL",
            "ITM 02 PRINCIPAL-USINA DE BLENDAGEM SINTER FEED ESPECIAL",
            "ITM 02 PRINCIPAL-USINA DE BLENDAGEM SILICOSO",
            "ITM 02 PRINCIPAL-PATIO MANGABA[PILHA SILICOSO] SILICOSO",
            "Rejeito Fino Principal",
            "ITM 02 PRINCIPAL-PATIO MANGABA[PILHA OVER] OVER",
            "ITM 02 PRINCIPAL-PDE SAMPAIO OVER"
        ]:
            return "ITM 02"
        elif material in [
            "ITM 02 NOVA[A]-USINA DE BLENDAGEM SINTER FEED ESPECIAL",
            "ITM 02 NOVA[A]-PATIO DE PRODUTOS SINTER FEED ESPECIAL",
            "ITM 02 NOVA[A]-PATIO MANGABA[PILHA SILICOSO] SILICOSO",
            "ITM 02 NOVA[A]-USINA DE BLENDAGEM SILICOSO",
            "Rejeito Fino A",
            "ITM 02 NOVA-PATIO MANGABA[PILHA OVER] OVER",
            "ITM 02 NOVA-PDE SAMPAIO OVER"
        ]:
            return "ITM 02 A"
        elif material in [
            "ITM 02 NOVA[B]-USINA DE BLENDAGEM SINTER FEED ESPECIAL",
            "ITM 02 NOVA[B]-PATIO DE PRODUTOS SINTER FEED ESPECIAL",
            "ITM 02 NOVA[B]-PATIO MANGABA[PILHA SILICOSO] SILICOSO",
            "ITM 02 NOVA[B]-USINA DE BLENDAGEM SILICOSO",
            "Rejeito Fino B",
            "ITM 02 NOVA-PDE SAMPAIO OVER",
            "ITM 02 NOVA-PATIO MANGABA[PILHA OVER] OVER"
        ]:
            return "ITM 02 B"
        elif material in [
            "DESAGUAMENTO DE PRODUTO ITM 8-PATIO DE PRODUTOS PELLET FEED",
            "DESAGUAMENTO DE PRODUTO ITM 8-USINA DE BLENDAGEM PELLET FEED",
            "Rejeito Desaguado",
            "ITM 08-PATIO MANGABA[PILHA OVER] OVER",
            "ITM 08-PDE SAMPAIO OVER",
            "Rejeito Filtrado",
            "Feijãozinho ITM 02 Principal"
        ]:
            return "ITM 08"
        elif material == "CBMM":
            return "CBMM"
        elif material == "PFF ITM 04":
            return "ITM 04"
        elif material == "Rejeito Filtrado":
            return "Filtro"
        else:
            return None
        
    df_prod['Produção'] = df_prod['Material'].apply(classify_material)

      # Criar a nova coluna 'tipo_produção'
    def classify_tipo_producao(material):
        if material == "Sinter Especial":
            return "Sinter Feed Especial"
        elif material in [
            "Sinter Premium"
        ]:
            return "Sinter Feed Premium"
        elif material in [
            "Hematitinha Premium ITM 09"
        ]:
            return "Hematitinha Premium"
        elif material in [
            "ITM 04[SUBPRODUTO]-ITM 09 HEMATITINHA COMUM"
        ]:
            return "Hematitinha Comum"
        elif material in [
            "scalper 1 especial",
            "scalper 2 especial",
            "Sinter blendagem"
        ]:
            return "Sinter Feed Especial Scalper"
        elif material in [
            "Hematitinha Especial ITM 09 A"
        ]:
            return "Hematitinha Especial"
        elif material in [
            "DESAGUAMENTO DE PRODUTO ITM 8-PATIO DE PRODUTOS PELLET FEED",
            "DESAGUAMENTO DE PRODUTO ITM 8-USINA DE BLENDAGEM PELLET FEED"
        ]:
            return "Pellet Feed"
        elif material in [
            "ITM 02 PRINCIPAL-PATIO DE PRODUTOS SINTER FEED ESPECIAL",
            "ITM 02 PRINCIPAL-USINA DE BLENDAGEM SINTER FEED ESPECIAL",
            "ITM 02 NOVA[A]-USINA DE BLENDAGEM SINTER FEED ESPECIAL",
            "ITM 02 NOVA[A]-PATIO DE PRODUTOS SINTER FEED ESPECIAL",
            "ITM 02 NOVA[B]-USINA DE BLENDAGEM SINTER FEED ESPECIAL",
            "ITM 02 NOVA[B]-PATIO DE PRODUTOS SINTER FEED ESPECIAL"
        ]:
            return "Sinter Feed"
        else:
            return None

    df_prod['tipo_produção'] = df_prod['Material'].apply(classify_tipo_producao)


    # Capturar filtros enviados pelo formulário
    producao_filtro = request.GET.getlist('producao')  
    tipo_producao_filtro = request.GET.getlist('tipo_producao')  
    data_inicial = request.GET.get('data_inicial')  
    data_final = request.GET.get('data_final')  

    # Definir automaticamente o primeiro dia do mês e a data atual caso os filtros não sejam fornecidos
    hoje = datetime.today()
    primeiro_dia_mes = hoje.replace(day=1)

    if not data_inicial:
        data_inicial = primeiro_dia_mes.strftime('%Y-%m-%d')
    if not data_final:
        data_final = hoje.strftime('%Y-%m-%d')

    # Converter para datetime para aplicar a filtragem
    df_prod['data'] = pd.to_datetime(df_prod['data'])

    # Filtrar por Período de Datas
    df_prod = df_prod[(df_prod['data'] >= pd.to_datetime(data_inicial)) & (df_prod['data'] <= pd.to_datetime(data_final))]



    # Filtrar por Produção
    if producao_filtro:
        df_prod = df_prod[df_prod['Produção'].isin(producao_filtro)]

    # Filtrar por Tipo de Produção
    if tipo_producao_filtro:
        df_prod = df_prod[df_prod['tipo_produção'].isin(tipo_producao_filtro)]

    # Filtrar por Período de Datas
    if data_inicial:
        df_prod = df_prod[df_prod['data'] >= pd.to_datetime(data_inicial)]
    if data_final:
        df_prod = df_prod[df_prod['data'] <= pd.to_datetime(data_final)]

  
     # Filtrar e preparar os dados
    df_prod = df_prod[['data', 'Peso (t/dia)', 'Produção', 'tipo_produção', 'Fe','SiO2','Al','P']].dropna(subset=['data', 'Peso (t/dia)', 'Produção', 'tipo_produção',])

   # Calcular o total diário de produção
    df_soma_total = df_prod.groupby('data', as_index=False)['Peso (t/dia)'].sum()

    # Arredondar valores para duas casas decimais
    df_soma_total['Peso (t/dia)'] = df_soma_total['Peso (t/dia)'].round(2)

    # Calcular o total acumulado de todo o período
    peso_total_acumulado = df_prod['Peso (t/dia)'].sum()

    # Ritmo
    numero_de_dias_atual = (pd.to_datetime(data_final) - pd.to_datetime(data_inicial)).days + 1
    numero_de_dias_total_do_mes = (pd.to_datetime(data_final).replace(day=1) + pd.DateOffset(months=1) - timedelta(days=1)).day

    ritmo = peso_total_acumulado * numero_de_dias_total_do_mes/ numero_de_dias_atual

    # Carregar dados das metas de produção
    df_prod_metas = pd.read_excel('dados/metas_produção.xlsx')

    # Garantir que a coluna 'data' está no formato datetime
    df_prod_metas['data'] = pd.to_datetime(df_prod_metas['data'])

    # Aplicar os filtros de período
    df_prod_metas_filtrado = df_prod_metas[
        (df_prod_metas['data'] >= pd.to_datetime(data_inicial)) & 
        (df_prod_metas['data'] <= pd.to_datetime(data_final))
    ]

    # Se a coluna 'Produção' existir nas metas, aplicar os filtros correspondentes
    if 'Produção' in df_prod_metas.columns and producao_filtro:
        df_prod_metas_filtrado = df_prod_metas_filtrado[df_prod_metas_filtrado['Produção'].isin(producao_filtro)]

    # Se a coluna 'tipo_produção' existir nas metas, aplicar os filtros correspondentes
    if 'tipo_produção' in df_prod_metas.columns and tipo_producao_filtro:
        df_prod_metas_filtrado = df_prod_metas_filtrado[df_prod_metas_filtrado['tipo_produção'].isin(tipo_producao_filtro)]

    # Agrupar os valores somados das metas após aplicar os filtros
    df_prod_metas_soma = df_prod_metas_filtrado.groupby('data', as_index=False)[['massa', 'orçado','Produção','tipo_produção']].sum()

    # Calcular a meta acumulada após aplicar os filtros
    massa_total_meta = df_prod_metas_soma['massa'].sum()
    massa_total_orçado = df_prod_metas_soma['orçado'].sum()


    #####Projetado#####
    data_final_dt = pd.to_datetime(data_final)
    primeiro_dia_mes_filtrado = data_final_dt.replace(day=1)
    ultimo_dia_mes_filtrado = data_final_dt.replace(day=1) + pd.DateOffset(months=1) - timedelta(days=1)

    # Calcular os dias restantes dentro do mês filtrado
    dias_faltando = (ultimo_dia_mes_filtrado - data_final_dt).days

    # Filtrar os valores da meta para os dias restantes dentro do mês filtrado
    df_prod_metas_faltantes = df_prod_metas[
        (df_prod_metas['data'] > data_final_dt) & 
        (df_prod_metas['data'] <= ultimo_dia_mes_filtrado)
    ]

    # Aplicar os filtros de Produção e Tipo de Produção na tabela de metas faltantes
    if producao_filtro:
        df_prod_metas_faltantes = df_prod_metas_faltantes[df_prod_metas_faltantes['Produção'].isin(producao_filtro)]

    if tipo_producao_filtro:
        df_prod_metas_faltantes = df_prod_metas_faltantes[df_prod_metas_faltantes['tipo_produção'].isin(tipo_producao_filtro)]

    # Somar as metas dos dias restantes dentro do mês filtrado
    meta_faltante = df_prod_metas_faltantes['massa'].sum()

    # Projeção final dentro do mês filtrado
    projetado = peso_total_acumulado + meta_faltante
        
   ##### Total Planejado #####

    # Definir o primeiro e o último dia do mês sendo filtrado
    data_final_dt = pd.to_datetime(data_final)
    primeiro_dia_mes_filtrado = data_final_dt.replace(day=1)
    ultimo_dia_mes_filtrado = data_final_dt.replace(day=1) + pd.DateOffset(months=1) - timedelta(days=1)

    # Filtrar os valores da meta para o mês inteiro (sem filtrar pelos dias já passados)
    df_prod_metas_mes = df_prod_metas[
        (df_prod_metas['data'] >= primeiro_dia_mes_filtrado) & 
        (df_prod_metas['data'] <= ultimo_dia_mes_filtrado)
    ]

    # Aplicar os filtros de Produção e Tipo de Produção
    if producao_filtro:
        df_prod_metas_mes = df_prod_metas_mes[df_prod_metas_mes['Produção'].isin(producao_filtro)]

    if tipo_producao_filtro:
        df_prod_metas_mes = df_prod_metas_mes[df_prod_metas_mes['tipo_produção'].isin(tipo_producao_filtro)]

    # Somar todas as metas do mês filtrado após aplicar os filtros
    total_planejado = df_prod_metas_mes['massa'].sum()

    df_pizza = df_prod.groupby('tipo_produção', as_index=False)['Peso (t/dia)'].sum()
    # Função para calcular a média ponderada de Fe excluindo valores 0
   # Função para calcular a média ponderada excluindo valores 0
    
    def media_ponderada(x, coluna):
        df_filtrado = df_prod.loc[x.index, :]  # Garantir que estamos acessando os índices corretamente
        valores_filtrados = x[x > 0]  # Excluir valores zero
        pesos_filtrados = df_filtrado.loc[valores_filtrados.index, 'Peso (t/dia)']  # Ajustar os pesos para os valores válidos

        if pesos_filtrados.sum() == 0:  # Evitar divisão por zero
            return np.nan
        return (valores_filtrados * pesos_filtrados).sum() / pesos_filtrados.sum()

    # Aplicar a função dentro do .agg()
    df_tabela = df_prod.groupby('tipo_produção', as_index=False).agg({
        'Peso (t/dia)': 'sum', 
        'Fe': lambda x: media_ponderada(x, 'Fe'),
        'SiO2': lambda x: media_ponderada(x, 'SiO2'),
        'Al': lambda x: media_ponderada(x, 'Al'),
        'P': lambda x: media_ponderada(x, 'P')
    })

    # Calcular o total da coluna "Peso Total (t/dia)"
    total_peso = df_tabela['Peso (t/dia)'].sum()

    # Calcular a média ponderada total de Fe e SiO2 excluindo valores 0
    df_filtrado_fe = df_prod[df_prod['Fe'] > 0]  # Apenas valores de Fe maiores que 0
    df_filtrado_sio2 = df_prod[df_prod['SiO2'] > 0]
    df_filtrado_al = df_prod[df_prod['Al'] > 0]  
    df_filtrado_p = df_prod[df_prod['P'] > 0]  

    total_fe = (df_filtrado_fe['Fe'] * df_filtrado_fe['Peso (t/dia)']).sum() / df_filtrado_fe['Peso (t/dia)'].sum()
    total_sio2 = (df_filtrado_sio2['SiO2'] * df_filtrado_sio2['Peso (t/dia)']).sum() / df_filtrado_sio2['Peso (t/dia)'].sum()
    total_al = (df_filtrado_al['Al'] * df_filtrado_al['Peso (t/dia)']).sum() / df_filtrado_al['Peso (t/dia)'].sum()
    total_p = (df_filtrado_p['P'] * df_filtrado_p['Peso (t/dia)']).sum() / df_filtrado_p['Peso (t/dia)'].sum()

    # Adicionar a linha de total
    df_tabela.loc[len(df_tabela)] = ["<b>Total</b>", total_peso, total_fe, total_sio2, total_al, total_p]  

    # Formatar os números no estilo 17,520.00
    df_tabela["Peso (t/dia)"] = df_tabela["Peso (t/dia)"].apply(lambda x: f"{x:,.2f}")
    df_tabela["Fe"] = df_tabela["Fe"].apply(lambda x: f"{x:,.2f}" if not np.isnan(x) else "-")
    df_tabela["SiO2"] = df_tabela["SiO2"].apply(lambda x: f"{x:,.2f}" if not np.isnan(x) else "-")
    df_tabela["Al"] = df_tabela["Al"].apply(lambda x: f"{x:,.2f}" if not np.isnan(x) else "-")
    df_tabela["P"] = df_tabela["P"].apply(lambda x: f"{x:,.2f}" if not np.isnan(x) else "-")

    # Garantir que "Peso (t/dia)" está no formato correto antes do cálculo
    df_tabela['Peso (t/dia)'] = df_tabela['Peso (t/dia)'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

    # Criar um dicionário para armazenar os valores projetados por tipo de produção
    projetado_dict = {}

    for tipo in df_tabela['tipo_produção']:
        # Total produzido até agora para esse tipo de produção
        peso_acumulado_tipo = df_prod[df_prod['tipo_produção'] == tipo]['Peso (t/dia)'].sum()

        # Filtrar metas futuras para esse tipo de produção
        df_metas_faltantes_tipo = df_prod_metas_faltantes[df_prod_metas_faltantes['tipo_produção'] == tipo]

        # Somar as metas futuras desse tipo de produção (considerando os dias que faltam)
        meta_faltante_tipo = df_metas_faltantes_tipo['massa'].sum()

        # Calcular o projetado final para esse tipo de produção
        projetado_tipo = peso_acumulado_tipo + meta_faltante_tipo

        # Armazenar no dicionário
        projetado_dict[tipo] = projetado_tipo

    # Adicionar os valores à coluna "Projetado"
    df_tabela['Projetado'] = df_tabela['tipo_produção'].map(projetado_dict)

    # Formatar os valores para exibição correta
    df_tabela["Projetado"] = df_tabela["Projetado"].apply(lambda x: format_number(x))


    # Definir a cor da primeira barra com base na comparação
    cor_peso_total = "#2ECC71" if peso_total_acumulado > massa_total_meta else "#E74C3C"


  
    # Mantém os valores como números para os gráficos
    peso_total_acumulado_num = peso_total_acumulado
    massa_total_meta_num = massa_total_meta
    massa_total_orçado_num = massa_total_orçado
    ritmo_num = ritmo
    projetado_num = projetado
    total_planejado_num = total_planejado
 

    # Formatar apenas para exibição de texto
    peso_total_acumulado = format_number(peso_total_acumulado_num)
    massa_total_meta = format_number(massa_total_meta_num)
    massa_total_orçado= format_number(massa_total_orçado_num)
    ritmo = format_number(ritmo_num)
    projetado = format_number(projetado_num)
    total_planejado = format_number(total_planejado_num)

    
    ### Projetado tabela Total######
    df_tabela.loc[len(df_tabela) - 1, "Projetado"] = format_number(projetado_num)


    # Criar subplots com dois gráficos lado a lado
    fig = make_subplots(
    rows=1, 
    cols=2, 
    column_widths=[0.85, 0.15],  # O primeiro gráfico ocupará 70% e o segundo 30% do espaço
    horizontal_spacing= 0  # Reduz a separação entre os gráficos
    )

    # Criar o gráfico de barras com os valores totais diários
    fig.add_trace(
    go.Bar(
        x=df_soma_total['data'],
        y=df_soma_total['Peso (t/dia)'],  # Deve ser numérico
        text=df_soma_total['Peso (t/dia)'].apply(format_number),  # Formata para exibição
        textposition='inside',
        insidetextanchor='middle',
        textangle=270,
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color= "#215F9A"),
        name="Peso Total",
        showlegend=False
    ),
    row=1, col=1
    )

    fig.add_trace(
    go.Scatter(
        x=df_prod_metas_soma['data'],  
        y=df_prod_metas_soma['massa'],  # Mantém como número para o gráfico
        mode='lines+markers+text',  # Adiciona texto formatado sobre os pontos
        textposition="top center",
        line=dict(color="gray", width=2, dash="dot"),  
        marker=dict(size=7, color="gray"),  
        name="Tendência",
        showlegend=False
    ),
    row=1, col=1
    )
    # Criar anotações para cada ponto
    annotations = [
    dict(
        x=row['data'],  
        y=row['massa'] + 10,  
        text=format_number(row['massa']),  # Formata os números corretamente
        showarrow=False,  
        font=dict(size=18, family="Segoe UI Semibold", color='gray'),
        textangle=270,  
        xanchor='center',
        yanchor='bottom'
    ) for _, row in df_prod_metas_soma.iterrows()
    ]

    # Adicionar anotações ao layout do gráfico
    fig.update_layout(annotations=annotations)

    # Criar o gráfico de barras com duas colunas: produção acumulada e meta de produção acumulada
    fig.add_trace(
    go.Bar(
        x=["Total Real"],  
        y=[peso_total_acumulado_num],  # Agora passa o número, não a string
        text=peso_total_acumulado,  # Texto formatado para exibição
        textposition='inside',
        textangle=270,
        insidetextanchor='middle',
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color="#163E64"),
        name="Peso Total Acumulado",
        showlegend=False
    ),
    row=1, col=2
    )

    fig.add_trace(
    go.Bar(
        x=["Plan. Acum."],  
        y=[massa_total_meta_num],  # Passa o número, não a string
        text=massa_total_meta,  # Texto formatado
        textposition='inside',
        textangle=270,
        insidetextanchor='middle',
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color="#AEAEAE"),
        name="Meta de Produção",
        showlegend=False
    ),
    row=1, col=2
    )

    fig.add_trace(
    go.Bar(
        x=["Ritmo"],  
        y=[ritmo_num],  # Passa o número
        text=ritmo,  # Texto formatado
        textposition='inside',
        textangle=270,
        insidetextanchor='middle',
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color="#104862"),
        name="Ritmo",
        showlegend=False
    ),
    row=1, col=2
    )

    fig.add_trace(
    go.Bar(
        x=["Projetado"],  
        y=[projetado],  # Passa o número
        text=projetado,  # Texto formatado  # Texto formatado
        textposition='inside',
        textangle=270,
        insidetextanchor='middle',
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color="#7F7F7F"),
        name="Ritmo",
        showlegend=False
    ),
    row=1, col=2
    )

    fig.add_trace(
    go.Bar(
        x=["Total Planejado"],  
        y=[total_planejado],  # Passa o número
        text=total_planejado,  # Texto formatado  # Texto formatado
        textposition='inside',
        textangle=270,
        insidetextanchor='middle',
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color="#262626"),
        name="Ritmo",
        showlegend=False
    ),
    row=1, col=2
    )

    
    fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',  
    paper_bgcolor='rgba(0,0,0,0)',  
    font=dict(
        family="Segoe UI Semibold",
        size=16
    ),
    yaxis_title='Produção dia (ton)',
    xaxis=dict(
        tickangle=45,
        tickmode='array',
        tickvals=df_soma_total['data'],
        tickformat="%b %d"
    ),
    yaxis=dict(
        tickformat=",.2f",
        separatethousands=True
    ),
    yaxis2=dict(  
        showticklabels=False,  # Esconde os valores do eixo Y do segundo gráfico
        showgrid=False,        # Remove a grade do eixo Y
        zeroline=False         # Esconde a linha zero
    ),
    margin=dict(l=0.1, r=0.1, t=0.1, b=0.1)
    )

    fig_pizza = px.pie(
    df_pizza,  
    names='tipo_produção',  
    values='Peso (t/dia)',
    title="Distribuição da Produção por Tipo",
    hole=0.4 
    )
    # Aumentar fonte do título e legenda
    fig_pizza.update_layout(
    title={'text': "Produção realizada", 'font':{'family': "Segoe UI Semibold", 'size': 28, 'color': "#4A4A4A"}},  # Tamanho do título
    legend=dict(font=dict(size=14))  # Tamanho da fonte da legenda
    )
    
    # Remover a legenda externa
    fig_pizza.update_layout(
    showlegend=False  # Oculta a legenda externa
    )

    fig_pizza.update_traces(
    textinfo="label+percent",  # Mostra o nome e a porcentagem em cada fatia
    textfont=dict(family="Segoe UI Semibold", size=18, color="#4A4A4A"),  # Aumentar o tamanho da fonte dos valores
    insidetextorientation="radial"  # Melhor alinhamento do texto dentro da pizza
    )
    fig_pizza.update_layout(
        margin=dict(l=80, r=80, t=80, b=80)
    )
    

    # Criar tabela no Plotly
    fig_tabela = go.Figure(data=[go.Table(
        columnwidth=[500,250,120,150,120,120,230],
        header=dict(
            values=["<b>Produto</b>", "<b>Massa(t_bu)</b>","<b>%Fe</b>","<b>%SiO2</b>","<b>%Al</b>","<b>%P</b>","<b>Projetado</b>"],
            fill_color='#163E64',  # Cor de fundo do cabeçalho
            font=dict(color='white', size=20),
            align='center',
            height=40  # Aumentar altura do cabeçalho
        ),
        cells=dict(
            values=[df_tabela['tipo_produção'], df_tabela['Peso (t/dia)'],df_tabela['Fe'],df_tabela['SiO2'],df_tabela['Al'],df_tabela['P'],df_tabela['Projetado']],
            fill=dict(color=['#E5ECF6'] * (len(df_tabela) - 1) + ['#D1D5DB']),
            fill_color=['#E5ECF6', '#F8FAFC'],  # Alternância de cores nas linhas
            font=dict(size=18),
            align='center',
             height=45  # Aumentar altura das células
        )
    )])
    fig_tabela.update_layout(
    width=950,  # Aumentar largura
    height=500,  # Aumentar altura
    margin=dict(l=10, r=10, t=10, b=10)
)
    
    # Criar subplots com dois gráficos lado a lado
    fig_02 = make_subplots(
    rows=1, 
    cols=1, 
    horizontal_spacing= 0  # Reduz a separação entre os gráficos
    )

    #############graficos de indicadores################
    fig_02.add_trace(
    go.Bar(
        x=[peso_total_acumulado_num],  
        y=['Total'],  # Valores numéricos no eixo Y
        text=peso_total_acumulado,  # Texto formatado para exibição
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color= cor_peso_total),
        name="Peso Total Acumulado",
        showlegend=False,
        orientation='h'
    ),
    row=1, col=1
    )

    fig_02.add_trace(
    go.Bar(
        x=[massa_total_meta_num],  
        y=['Total'],  # Valores numéricos no eixo Y
        text=massa_total_meta,  # Texto formatado para exibição
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color="#215F9A"),
        name="Meta de Produção",
        showlegend=False,
        orientation='h'
    ),
    row=1, col=1
    )

    fig_02.add_trace(
    go.Bar(
        x=[massa_total_orçado_num],  
        y=['Total'],  # Valores numéricos no eixo Y
        text=massa_total_orçado,  # Texto formatado para exibição
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(size=18, family="Segoe UI Semibold", color="white"),
        marker=dict(color="#0E2841"),
        name="Meta de Produção",
        showlegend=False,
        orientation='h'
    ),
    row=1, col=1
    )


    # Converter o gráfico para HTML
    grafico_html = fig.to_html(full_html=False)
    grafico_pizza_html = fig_pizza.to_html(full_html=False)
    tabela_html = fig_tabela.to_html(full_html=False)
    grafico_html_orçado = fig_02.to_html(full_html=False)

    # Renderizar o template com o gráfico e os filtros aplicados
    return render(request, 'galeria/index.html', {
        'grafico': grafico_html,
        'grafico_pizza': grafico_pizza_html,
        'tabela': tabela_html,
        'producao_filtro': producao_filtro,
        'data_inicial_filtro': data_inicial,
        'data_final_filtro': data_final,
        'grafico_orçado': grafico_html_orçado
    })


                            

