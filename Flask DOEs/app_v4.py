from flask import Flask, request, render_template
import os
import re
import json
from datetime import datetime, timedelta
from Funções import *
from DownloadDOEs import *

app = Flask(__name__)

def verificar_diarios_solicitados(periodo_inicio, periodo_fim):
    data_atual = periodo_inicio
    while data_atual <= periodo_fim:
        # Converte a data atual para o formato YYYYMMDD
        data_atual_formatada = data_atual.strftime('%Y%m%d')
        # Verifica se o Diário Oficial do Estado correspondente à data atual está presente na pasta 'DOEsExtraidos'
        pdf_solicitado = f'do{data_atual_formatada}p01.pdf'
        if os.path.exists(os.path.join('DOEsExtraidos', pdf_solicitado)):
            # Verifica se existe uma pasta com o nome da data do Diário Oficial baixado
            pasta_data_diario = data_atual.strftime('%d-%m-%Y')
            pasta_diario_existe = os.path.exists(os.path.join('txt extraido', pasta_data_diario))
            if not pasta_diario_existe:
                return False
        else:
            return False
        # Avança para o próximo dia
        data_atual += timedelta(days=1)
    return True

# Função para realizar a extração dos dados
def extrair_dados(orgao, periodo_inicio, periodo_fim):

    # Converte as datas de string para objetos datetime
    periodo_inicio = datetime.strptime(periodo_inicio, '%Y-%m-%d')
    periodo_fim = datetime.strptime(periodo_fim, '%Y-%m-%d')

    # Calcula a diferença de dias entre o período de início e o período de fim
    diferenca_dias = (periodo_fim - periodo_inicio).days

    # Verifica se a pasta 'DOEs Extraidos' existe ou não, caso não exista cria a pasta e baixa os DOEs conforme a diferença de dias calculada
    if os.path.exists('DOEsExtraidos') == False:
        Baixar_DOEs('DOEs', diferenca_dias, periodo_fim)
        os.makedirs('DOEsExtraidos')
    # Se a pasta existir, verifica se os DOEs buscados já foram extraídos, ou seja, se os arquivos já foram baixados e estão contidos na pasta
    else:
        if(verificar_diarios_solicitados(periodo_inicio, periodo_fim) == False):
            Baixar_DOEs('DOEs', diferenca_dias, periodo_fim)

    #Pasta que guarda os .json
    if os.path.exists('json extraidos') == False:
        os.makedirs('json extraidos')

    print('Após baixado os DOEs, inicia a extração e o armazenamento, caso ainda não tenha sido feito:\n')

    #Essa parte faz toda a extração de órgãos e conteúdo dos documentos baixados
    listadocs = []
    listacontextos = []

    listX = []
    X = {
    'DATA',
    'NOME',
    'PUBLICACAO',
    'TEXTO'
    }

    pdfpasta = os.listdir('DOEs/')
    pdfpasta.sort()
    temp=''

    # Esta função atualiza a barra de progresso
    def update_progress(progress):
        length = 50
        block = int(length * progress)
        progress_bar = '[' + '#' * block + '-' * (length - block) + ']'
        print(f'\rProgresso: {progress_bar} {progress:.1%}\n', end='', flush=True)

    update_progress(0.0)  # Atualiza a barra de progresso no início da iteração

    for P in pdfpasta:
        if(os.path.exists(os.path.join('DOEsExtraidos',P))):
            print(P+' Documento já utilizado')
            os.remove(os.path.join('DOEs',P))
        elif(P.endswith('.pdf')):
            print('Documento '+P)
            z = 'DOEs/'+P
            bloco = z
            bloco = bloco.replace('DOEs/do','')
            bloco = bloco.split('p')
            bloco = bloco[0]
            datachar = bloco[6:8]
            meschar = bloco[4:6]
            anochar = bloco[0:4]
            if(temp!=datachar+'-'+meschar+'-'+anochar):
                if(temp!=''):
                    with open(os.path.join('json extraidos',temp+'.json'),'w') as write_file:
                        json.dump(listX, write_file, indent=4)
                temp=datachar+'-'+meschar+'-'+anochar
                listX = []
                X = {
                    'DATA',
                    'NOME',
                    'PUBLICACAO',
                    'TEXTO'
                    }
            listadocs.append(extrair_orgaos_PDF(z))
            listacontextos.append(extrair_texto_entre_orgaos(listadocs[-1]))
            bloco = listacontextos[-1][0].doc
            bloco = bloco.replace('DOEs/do','')
            bloco = bloco.split('p')
            bloco = bloco[0]
            datachar = bloco[6:8]
            meschar = bloco[4:6]
            anochar = bloco[0:4]
            if(temp!=datachar+'-'+meschar+'-'+anochar):
                if(temp!=''):
                    with open(os.path.join('json extraidos',temp+'.json'),'w') as write_file:
                        json.dump(listX, write_file, indent=4)
                temp=datachar+'-'+meschar+'-'+anochar
                listX = []
                X = {
                    'DATA',
                    'NOME',
                    'PUBLICACAO',
                    'TEXTO'
                    }
            for c in range(0,len(listacontextos[-1])):
                if('(Continuação)' in listacontextos[-1][c].nome):
                    if(type(listacontextos[-1][c].texto) == list):
                        for T in range(0,len(listacontextos[-1][c].texto)):
                            listX.append({
                                'DATA': temp,
                                'NOME': listacontextos[-1][c].nome,
                                'PUBLICACAO': 1+T,
                                'TEXTO': listacontextos[-1][c].texto[T]
                            }) 
                    else:
                        listX.append({
                            'DATA': temp,
                            'NOME': listacontextos[-1][c].nome,
                            'PUBLICACAO': 1,
                            'TEXTO': listacontextos[-1][c].texto
                        })
                else:
                    if(type(listacontextos[-1][c].texto) == list):
                        for T in range(0,len(listacontextos[-1][c].texto)):
                            listX.append({
                            'DATA': temp,
                            'NOME': listacontextos[-1][c].nome,
                            'PUBLICACAO': 1+T,
                            'TEXTO': listacontextos[-1][c].texto[T]
                        }) 
                    else:
                        listX.append({
                            'DATA': temp,
                            'NOME': listacontextos[-1][c].nome,
                            'PUBLICACAO': 1,
                            'TEXTO': listacontextos[-1][c].texto
                        })
            os.rename(os.path.join('DOEs',P),os.path.join('DOEsExtraidos',P))

    if(temp!=''):
        with open(os.path.join('json extraidos',temp+'.json'),'w') as write_file:
            json.dump(listX, write_file, indent=4)

    # Organizar os DOEs em pastas de acordo com seu dia
    for i in os.listdir('json extraidos'):
        if(i.endswith('.json')):
            temp = i[0:10]
            if os.path.exists(os.path.join('json extraidos',temp)) == False:
                os.makedirs(os.path.join('json extraidos',temp))
            os.rename(os.path.join('json extraidos',i),os.path.join(os.path.join('json extraidos',temp),i))

    update_progress(1.0)  # Atualiza a barra de progresso para 100% no final do processamento

    # Armazena os arquivos JSON extraídos na lista arquivos_criados para retornar
    arquivos_criados = []
    arquivos_unicos = set()

    for root, _, files in os.walk('json extraidos'):
        for file in files:
            if file.endswith('.json'):
                data_arquivo = root.split('/')[1]
                data_arquivo_dt = datetime.strptime(data_arquivo, '%d-%m-%Y')
                if periodo_inicio <= data_arquivo_dt <= periodo_fim:
                    # Carregar o conteúdo do arquivo JSON
                    caminho_arquivo = os.path.join(root, file)
                    with open(caminho_arquivo, 'r') as arquivo_json:
                        dados_json = json.load(arquivo_json)
                    for item in dados_json:
                        orgao_arquivo = item['NOME']
                        if orgao_arquivo.strip() == orgao.upper():
                            arquivo = os.path.join(root, file)
                            # Verifica se o arquivo já foi adicionado
                            if arquivo not in arquivos_unicos:
                                arquivos_criados.append({'titulo': file, 'data': data_arquivo})
                                arquivos_unicos.add(arquivo)  # Adiciona o nome do arquivo ao conjunto de arquivos únicos
                                print("Arquivo adicionado à lista:", file)  # Verifica se o arquivo foi adicionado à lista

    print("Lista de arquivos criados:", arquivos_criados)  # Verifica a lista final de arquivos criados

    return arquivos_criados

# Rota para renderizar a página inicial
@app.route('/')
def index():

    # Verifica se existe algum PDF na pasta 'DOEsExtraidos' ou a pasta não existe
    pdfs_extraidos = []
    if not os.path.exists('DOEsExtraidos') or not os.listdir('DOEsExtraidos'):
        # Se a pasta 'DOEsExtraidos' não existir ou estiver vazia, cria a pasta 'DOEs' se já não existir
        if not os.path.exists('DOEs'):
            os.makedirs('DOEs')
        # Calcula a diferença de dias entre o período de início e o período de fim
        periodo_inicio = "2024-04-04"  # Define um período de início padrão
        #periodo_fim = datetime.now().strftime("%Y-%m-%d")  # Define o período de fim como a data atual
        periodo_fim = "2024-04-04"
        periodo_inicio_dt = datetime.strptime(periodo_inicio, '%Y-%m-%d')
        periodo_fim_dt = datetime.strptime(periodo_fim, '%Y-%m-%d')
        diferenca_dias = (periodo_fim_dt - periodo_inicio_dt).days
        # Baixa os DOEs solicitados
        Baixar_DOEs('DOEs', diferenca_dias, periodo_fim_dt)
    else:
        # Se a pasta 'DOEsExtraidos' existir e contiver arquivos, lista os arquivos PDF
        pdfs_extraidos = [f for f in os.listdir('DOEsExtraidos') if f.endswith('.pdf')]

    # Verifica se existe algum PDF na pasta 'DOEsExtraidos'
    if pdfs_extraidos:
        # Obtém a data do último PDF extraído
        data_ultimo_pdf = pdfs_extraidos[-1][2:10]
        # Verifica se existe uma pasta com o nome da data do último PDF na pasta 'json extraidos'
        if os.path.exists(os.path.join('json extraidos', data_ultimo_pdf)):
            # Redireciona para a rota que processa os dados
            return process_data()
    return render_template('index.html')

# Rota para processar os dados e retornar os resultados
@app.route('/process_data', methods=['POST'])
def process_data():
    # Recebe os dados enviados pelo formulário HTML
    orgao = request.form['orgao']
    periodo_inicio = request.form['periodo_inicio']
    periodo_fim = request.form['periodo_fim']

    # Chama a função para extrair os dados
    arquivos_criados = extrair_dados(orgao, periodo_inicio, periodo_fim)

    # Retorna os resultados para o template HTML
    return render_template('resultados.html', orgao=orgao, arquivos_criados=arquivos_criados)

@app.route('/ler_arquivo/<path:data_arquivo>/<path:nome_arquivo>')
def ler_arquivo(data_arquivo, nome_arquivo):

    texto_orgao = ""

    # Obtém o parâmetro 'orgao' da URL
    orgao = request.args.get('orgao')

    # Caminho para o arquivo
    caminho_arquivo = os.path.join('json extraidos', data_arquivo, nome_arquivo)
    
    # Lê o conteúdo do arquivo
    with open(caminho_arquivo, 'r') as arquivo:
        dados_json = json.load(arquivo)
    
    # Inicializa o contador de publicações
    i = 1
    
    # Procura pelo órgão na lista de dados do arquivo
    for item in dados_json:
        if 'NOME' in item and item['NOME'] == orgao.upper():
            if 'TEXTO' in item:
                texto_orgao += f"Publicação {i} {item['TEXTO']}\n\n" # Adiciona o número da publicação antes de cada texto
                i += 1  # Incrementa o contador de publicações
    
    # Verifica se o conteúdo do arquivo é relevante para o órgão especificado
    # Se o 'orgao' não estiver presente na URL ou se não corresponder ao órgão no arquivo,
    # retorna uma mensagem informando que o conteúdo não está disponível
    if texto_orgao is None:
        return "Conteúdo não disponível para o órgão especificado."

    # Retorna o conteúdo do órgão
    return texto_orgao

if __name__ == '__main__':
    app.run(debug=True, port=8000)
