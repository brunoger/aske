from flask import Flask, request, render_template, jsonify
import os
import json
from datetime import datetime, timedelta
from Funções import *
from DownloadDOEs import *

app = Flask(__name__)

# Função para verificar se os DOEs solicitados já foram extraídos
def verificar_diarios_solicitados(periodo_inicio, periodo_fim):
    data_atual = periodo_inicio
    while data_atual <= periodo_fim:
        # Converte a data atual para o formato YYYYMMDD
        data_atual_formatada = data_atual.strftime('%Y%m%d')
        # Verifica se o Diário Oficial do Estado correspondente à data atual está presente na pasta 'DOEsExtraidos'
        pdf_solicitado = f'do{data_atual_formatada}p01.pdf'
        if os.path.exists(os.path.join('DOEsExtraidos', pdf_solicitado)):
            # O DOE já foi extraído, prossiga para a próxima data
            data_atual += timedelta(days=1)
        else:
            # O DOE não foi encontrado, portanto, retorna False
            return False
    # Todos os DOEs foram encontrados, retorna True
    return True

# Função para verificar se uma palavra está presente no texto
def verificar_palavra(texto, palavra):
    return palavra.upper() in texto.upper()

# Função para calcular o progresso do processamento no terminal
def calcular_progresso(total_arquivos, contador_arquivos):
    if total_arquivos == 0:
        return 0
    progresso = contador_arquivos / total_arquivos
    progresso = min(progresso, 1)
    return progresso

# Função para atualizar a barra de progresso do terminal e retornar o progresso atual como uma resposta JSON
def update_progress(total_arquivos, contador_arquivos):
    progresso = calcular_progresso(total_arquivos, contador_arquivos)
    length = 50
    block = int(length * progresso)
    progress_bar = '[' + '#' * block + '-' * (length - block) + ']'
    print(f'\rProgresso: {progress_bar} {progresso:.1%}\n', end='', flush=True)
    return jsonify({'progresso': progresso})  # Retorna o progresso atual como uma resposta JSON

# Função para realizar a extração dos dados
def extrair_dados(orgao, palavra, periodo_inicio, periodo_fim):

    # Converte as datas de string para objetos datetime
    periodo_inicio = datetime.strptime(periodo_inicio, '%Y-%m-%d')
    periodo_fim = datetime.strptime(periodo_fim, '%Y-%m-%d')

    # Calcula a diferença de dias entre o período de início e o período de fim
    diferenca_dias = (periodo_fim - periodo_inicio).days

    # Verifica se a pasta 'DOEsExtraidos' existe ou não, caso não exista, cria a pasta
    if not os.path.exists('DOEsExtraidos'):
        os.makedirs('DOEsExtraidos')

    # Verifica se a pasta 'json extraidos' existe ou não, caso não exista, cria a pasta
    if not os.path.exists('json extraidos'):
        os.makedirs('json extraidos')

    # Verifica se os DOEs solicitados já foram extraídos, ou seja, se os arquivos já foram baixados e estão contidos na pasta
    if not verificar_diarios_solicitados(periodo_inicio, periodo_fim):
        # Baixa os DOEs solicitados se ainda não tiverem sido extraídos
        Baixar_DOEs('DOEs', diferenca_dias, periodo_fim)

    print('Após baixado os DOEs, inicia a extração e o armazenamento, caso ainda não tenha sido feito:\n')

    # Essa parte faz toda a extração de órgãos e conteúdo dos documentos baixados
    listadocs = []
    listaconteudos = []

    listX = []
    X = {
    'DATA',
    'CADERNO',
    'PAGINA',
    'NOME',
    'PUBLICACAO',
    'TEXTO'
    }

    pdfpasta = os.listdir('DOEs/')
    pdfpasta.sort()
    temp=''

    total_arquivos = len(pdfpasta)  # Conta o número total de arquivos a serem processados
    contador_arquivos = 0  # Inicializa o contador de arquivos processados

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
            caderno = bloco[1]
            bloco = bloco[0]
            caderno = caderno.replace('0','')
            caderno = caderno.replace('.','')
            caderno = int(caderno)
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
                    'CADERNO',
                    'PAGINA',
                    'NOME',
                    'PUBLICACAO',
                    'TEXTO'
                    }
            listadocs.append(extrair_orgaos_PDF(z))
            listaconteudos.append(extrair_texto_entre_orgaos(listadocs[-1]))
            for c in range(0, len(listaconteudos[-1])):
                if '(Continuação)' in listaconteudos[-1][c].nome:
                    listaconteudos[-1][c].nome = listaconteudos[-1][c].nome.replace('(Continuação)', '')
                nome_publicacao = listaconteudos[-1][c].nome.strip()  # Remove espaços em branco no início e no final
                if isinstance(listaconteudos[-1][c].publicacao, list):
                    for T in range(0, len(listaconteudos[-1][c].publicacao)):
                        listX.append({
                            'DATA': temp,
                            'CADERNO': caderno,
                            'PAGINA': listaconteudos[-1][c].publicacao[T].page,
                            'NOME': nome_publicacao,
                            'PUBLICACAO': 1 + T,
                            'TEXTO': listaconteudos[-1][c].publicacao[T].texto
                        })
                else:
                    listX.append({
                        'DATA': temp,
                        'CADERNO': caderno,
                        'PAGINA': listaconteudos[-1][c].publicacao.page,
                        'NOME': nome_publicacao,
                        'PUBLICACAO': 1,
                        'TEXTO': listaconteudos[-1][c].publicacao
                    })

            os.rename(os.path.join('DOEs', P), os.path.join('DOEsExtraidos', P))

        if(temp!=''):
            with open(os.path.join('json extraidos',temp+'.json'),'w') as write_file:
                json.dump(listX, write_file, indent=4)

        # Atualiza a barra de progresso com base no número total de arquivos
        contador_arquivos += 1
        update_progress(total_arquivos, contador_arquivos)

    # Organizar os DOEs em pastas de acordo com seu dia
    for i in os.listdir('json extraidos'):
        if(i.endswith('.json')):
            temp = i[0:10]
            if os.path.exists(os.path.join('json extraidos',temp)) == False:
                os.makedirs(os.path.join('json extraidos',temp))
            os.rename(os.path.join('json extraidos',i),os.path.join(os.path.join('json extraidos',temp),i))

    update_progress(total_arquivos, total_arquivos)  # Atualiza a barra de progresso para 100% no final do processamento

    # Armazena os arquivos JSON extraídos na lista arquivos_criados para retornar
    arquivos_criados = []
    arquivos_unicos = set()

    for root, _, files in os.walk('json extraidos'):
        for file in files:
            if file.endswith('.json'):
                data_arquivo = root.split('/')[1]
                data_arquivo_dt = datetime.strptime(data_arquivo, '%d-%m-%Y')
                if periodo_inicio <= data_arquivo_dt <= periodo_fim:
                    caminho_arquivo = os.path.join(root, file)
                    try:
                        with open(caminho_arquivo, 'r') as arquivo_json:
                            dados_json = json.load(arquivo_json)
                            for item in dados_json:
                                orgao_arquivo = item['NOME']
                                if orgao_arquivo.strip() in orgao.upper():
                                    arquivo = os.path.join(root, file)
                                    if arquivo not in arquivos_unicos:
                                        arquivos_criados.append({'titulo': file, 'data': data_arquivo})
                                        arquivos_unicos.add(arquivo)
                                        print("Arquivo adicionado à lista:", file)
                                elif 'TEXTO' in item and verificar_palavra(item['TEXTO'], palavra):
                                    arquivo = os.path.join(root, file)
                                    if arquivo not in arquivos_unicos:
                                        arquivos_criados.append({'titulo': file, 'data': data_arquivo})
                                        arquivos_unicos.add(arquivo)
                                        print("Arquivo adicionado à lista:", file)
                    except Exception as e:
                        print(f"Erro ao abrir o arquivo {caminho_arquivo}: {e}")

    print("Lista de arquivos criados:", arquivos_criados)

    return arquivos_criados

# Rota para renderizar a página inicial
@app.route('/')
def index():
    # Verifica se a pasta 'DOEs' já existe
    if not os.path.exists('DOEs'):
        os.makedirs('DOEs')  # Cria a pasta 'DOEs'

    # Verifica se a pasta 'DOEsExtraidos' já existe
    if not os.path.exists('DOEsExtraidos'):
        os.makedirs('DOEsExtraidos')  # Cria a pasta 'DOEsExtraidos'

    # Verifica se existe algum PDF na pasta 'DOEsExtraidos'
    pdfs_extraidos = [f for f in os.listdir('DOEsExtraidos') if f.endswith('.pdf')]

    # Se a pasta 'DOEsExtraidos' estiver vazia ou não existir
    if not pdfs_extraidos:
        # Obtém os períodos de início e fim da página index.html
        periodo_inicio = request.args.get('periodo_inicio')
        periodo_fim = request.args.get('periodo_fim')

        # Verifica se os períodos de início e fim foram fornecidos
        if periodo_inicio and periodo_fim:
            periodo_inicio_dt = datetime.strptime(periodo_inicio, '%Y-%m-%d')
            periodo_fim_dt = datetime.strptime(periodo_fim, '%Y-%m-%d')

            # Calcula a diferença de dias entre o período de início e o período de fim
            diferenca_dias = (periodo_fim_dt - periodo_inicio_dt).days

            # Baixa os DOEs solicitados
            Baixar_DOEs('DOEs', diferenca_dias, periodo_fim_dt)

    return render_template('index.html')

# Rota para processar os dados e retornar os resultados
@app.route('/process_data', methods=['POST'])
def process_data():
    # Recebe os dados enviados pelo formulário HTML
    orgao = request.form['orgao']
    palavra = request.form['palavra']
    periodo_inicio = request.form['periodo_inicio']
    periodo_fim = request.form['periodo_fim']

    # Chama a função para extrair os dados
    arquivos_criados = extrair_dados(orgao, palavra, periodo_inicio, periodo_fim)

    # Retorna os resultados para o template HTML
    return render_template('resultados.html', orgao=orgao, palavra=palavra, arquivos_criados=arquivos_criados)

@app.route('/ler_arquivo/<path:data_arquivo>/<path:nome_arquivo>')
def ler_arquivo(data_arquivo, nome_arquivo):

    texto_orgao = ""

    # Obtém o parâmetro 'orgao' da URL
    orgao = request.args.get('orgao')

    # Obtém o parâmetro 'palavra' da URL
    palavra = request.args.get('palavra')

    # Caminho para o arquivo
    caminho_arquivo = os.path.join('json extraidos', data_arquivo, nome_arquivo)
    
    # Lê o conteúdo do arquivo
    with open(caminho_arquivo, 'r') as arquivo:
        dados_json = json.load(arquivo)
    
    # Inicializa o contador de publicações
    i = 1
    
    # Procura pelo órgão ou palavra na lista de dados do arquivo
    for item in dados_json:
        if orgao is not None and 'NOME' in item and item['NOME'] in orgao.upper():
            # Verifica se o órgão está presente e se corresponde ao órgao especificado na URL
            if 'TEXTO' in item:
                # Se o texto contém a palavra buscada, adiciona à variável texto_orgao
                texto_orgao += f"Publicação {i}: {item['TEXTO']}<br><br>"
                i += 1

            if 'CADERNO' in item:
                texto_orgao += f"Carderno: {item['CADERNO']}" + "\n\n"  # Adiciona o número do caderno depois da publicação

            if 'PAGINA' in item:
                texto_orgao += f"Página: {item['PAGINA']}<br><br>"  # Adiciona o número da página depois do caderno
        
        elif palavra is not None and 'TEXTO' in item and verificar_palavra(item['TEXTO'], palavra):
            texto_orgao += f"Publicação {i}: {item['TEXTO']}<br><br>"
            i += 1

            if 'CADERNO' in item:
                texto_orgao += f"Carderno: {item['CADERNO']}" + "\n\n"  # Adiciona o número do caderno depois da publicação

            if 'PAGINA' in item:
                texto_orgao += f"Página: {item['PAGINA']}<br><br>"  # Adiciona o número da página depois do caderno

    
    # Verifica se o conteúdo do arquivo é relevante para o órgão ou palavra especificada
    # Se o 'orgao' ou 'palavra' não estiver presente na URL ou se não corresponder ao órgão ou palavra no arquivo,
    # retorna uma mensagem informando que o conteúdo não está disponível
    if texto_orgao == "":
        return "Conteúdo não disponível para o órgão ou palavra especificada."

    # Retorna o conteúdo do órgão
    return texto_orgao

# Rota para retornar o progresso atual do processamento
@app.route('/progresso')
def progresso():
    total_arquivos = len(os.listdir('DOEs/'))  # Obtém o número total de arquivos a serem processados
    contador_arquivos = len(os.listdir('DOEsExtraidos'))  # Obtém o número de arquivos já processados
    return jsonify({'progresso': contador_arquivos, 'totalArquivos': total_arquivos})

if __name__ == '__main__':
    app.run(debug=True)
