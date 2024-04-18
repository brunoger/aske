from flask import Flask, request, render_template
import os
from Funções import *
from DownloadDOEs import *

app = Flask(__name__)

# Função para realizar a extração dos dados
def extrair_dados(orgao, periodo_inicio, periodo_fim):
    # Converte as datas de string para objetos datetime
    periodo_inicio = datetime.strptime(periodo_inicio, '%Y-%m-%d')
    periodo_fim = datetime.strptime(periodo_fim, '%Y-%m-%d')

    # Calcula a diferença de dias entre o período de início e o período de fim
    diferenca_dias = (periodo_fim - periodo_inicio).days
    
    # Baixa os Diários Oficiais do Estado conforme a diferença de dias calculada
    Baixar_DOEs('DOEs', diferenca_dias, periodo_fim)

    # Faz toda a extração de órgãos e conteúdo dos documentos baixados
    listadocs = []
    listacontextos = []
    listanegrito = []
    pdfpasta = os.listdir('DOEs/')
    pdfpasta.sort()

    for i in pdfpasta:
        if(i.endswith('.pdf')):
            z = 'DOEs/'+i
            listadocs.append(extrair_orgaos_PDF(z))
            listacontextos.append(extrair_texto_entre_orgaos(listadocs[-1]))
            listanegrito.append(palavras_negrito(listacontextos[-1]))

    # Armazena os resultados em uma lista para retornar
    resultados = []
    for contexto in listacontextos:
        for item in contexto:
            if item.nome == orgao and periodo_inicio <= item.data <= periodo_fim:
                resultados.append({'titulo': item.titulo, 'data': item.data})
    
    return resultados

# Rota para renderizar a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar os dados e retornar os resultados
@app.route('/process_data', methods=['POST'])
def process_data():
    # Recebe os dados enviados pelo formulário HTML
    orgao = request.form['orgao']
    periodo_inicio = request.form['periodo_inicio']
    periodo_fim = request.form['periodo_fim']
    
    # Chama a função para extrair os dados
    resultados = extrair_dados(orgao, periodo_inicio, periodo_fim)

    # Retorna os resultados para o template HTML
    return render_template('resultados.html', orgao=orgao, resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
