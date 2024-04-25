from flask import Flask, request, render_template
import os
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

    invalid = ['\uf0b7','\u25cf','\u02da','\u019f','\ufb01','\u0301','\u2010','\u03d0']

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

    # Verifica se a pasta 'txt extraido' existe, senão cria
    txt_extraido = 'txt extraido'
    if not os.path.exists(txt_extraido):
        os.makedirs(txt_extraido)

    print('Após baixado os DOEs, inicia a extração e o armazenamento, caso ainda não tenha sido feito:\n')

    # Faz toda a extração de órgãos e conteúdo dos documentos baixados
    listadocs = []
    listacontextos = []
    listanegrito = []
    pdfpasta = os.listdir('DOEs/')
    pdfpasta.sort()

    # Esta função atualiza a barra de progresso
    def update_progress(progress):
        length = 50
        block = int(length * progress)
        progress_bar = '[' + '#' * block + '-' * (length - block) + ']'
        print(f'\rProgresso: {progress_bar} {progress:.1%}\n', end='', flush=True)

    update_progress(0.0)  # Atualiza a barra de progresso no início da iteração

    for P in pdfpasta:
        if os.path.exists(os.path.join('DOEsExtraidos', P)):
            print(P + ' Documento já processado')
            os.remove(os.path.join('DOEs', P))
            continue
        elif P.endswith('.pdf'):
            if os.path.exists(os.path.join(txt_extraido, P.replace('.pdf', '.txt'))):
                print(P + ' PDF já existe')
                os.remove(os.path.join('DOEs', P))
                continue
            
            print('Documento ' + P)
            z = 'DOEs/' + P
            listadocs.append(extrair_orgaos_PDF(z))
            listacontextos.append(extrair_texto_entre_orgaos(listadocs[-1]))
            listanegrito.append(palavras_negrito(listacontextos[-1]))
            bloco = listacontextos[-1][0].doc
            bloco = bloco.replace('DOEs/do', '')
            bloco = bloco.replace('.pdf', '')
            bloco = bloco.split('p')
            bloco = bloco[0]
            datachar = bloco[6:8]
            meschar = bloco[4:6]
            anochar = bloco[0:4]
            bloco = datachar + '-' + meschar + '-' + anochar
            temp = bloco
            for i in range(0, len(listacontextos[-1])):
                bloco = temp + ' ' + listacontextos[-1][i].nome + '.txt'
                if os.path.exists(os.path.join(txt_extraido, bloco)):
                    continue
                if type(listacontextos[-1][i].texto) == list:
                    for T in range(0, len(listacontextos[-1][i].texto)):
                        for UNICODE in invalid:
                            if UNICODE in listacontextos[-1][i].texto[T]:
                                listacontextos[-1][i].texto[T] = listacontextos[-1][i].texto[T].replace(UNICODE, ' ')
                else:
                    for UNICODE in invalid:
                        if UNICODE in listacontextos[-1][i].texto:
                            listacontextos[-1][i].texto = listacontextos[-1][i].texto.replace(UNICODE, ' ')
                if '(Continuação)' in bloco:
                    bloco = bloco.replace(' (Continuação)', '')
                    bloco = bloco.replace(' .txt', '.txt')
                    nome = os.path.join(txt_extraido, bloco)
                    file = open(nome, 'a')
                    if type(listacontextos[-1][i].texto) == list:
                        for T in range(0, len(listacontextos[-1][i].texto)):
                            file.write('\n' + listacontextos[-1][i].texto[T])
                    else:
                        file.write('\n' + listacontextos[-1][i].texto)
                else:
                    bloco = bloco.replace(' .txt', '.txt')
                    nome = os.path.join(txt_extraido, bloco)
                    file = open(nome, 'a')
                    if type(listacontextos[-1][i].texto) == list:
                        for T in range(0, len(listacontextos[-1][i].texto)):
                            if T == 0:
                                file.write(listacontextos[-1][i].texto[T])
                            else:
                                file.write('\n' + listacontextos[-1][i].texto[T])
                    else:
                        file.write(listacontextos[-1][i].texto)
            file.close()
            os.rename(os.path.join('DOEs', P), os.path.join('DOEsExtraidos', P))

        # Organizar os DOEs em pastas de acordo com seu dia
        for i in os.listdir('txt extraido'):
            if(i.endswith('.txt')):
                temp = i[0:10]
                if os.path.exists(os.path.join('txt extraido',temp)) == False:
                    os.makedirs(os.path.join('txt extraido',temp))
                os.rename(os.path.join('txt extraido',i),os.path.join(os.path.join('txt extraido',temp),i))

    update_progress(1.0)  # Atualiza a barra de progresso para 100% no final do processamento

    # Armazena os arquivos txt extraídos na lista arquivos_criados para retornar
    arquivos_criados = []

    for root, _, files in os.walk('txt extraido'):
        for file in files:
            if file.endswith('.txt'):
                data_arquivo = root.split('/')[1]  # Obtém a parte da data do caminho do arquivo
                data_arquivo_dt = datetime.strptime(data_arquivo, '%d-%m-%Y')
                if periodo_inicio <= data_arquivo_dt <= periodo_fim:
                    orgao_arquivo = file[11:-4]  # Obtém o nome do órgão do nome do arquivo
                    if orgao_arquivo == orgao:
                        arquivo = os.path.join(root, file)
                        arquivos_criados.append({'titulo': file, 'data': data_arquivo})

    return arquivos_criados

# Rota para renderizar a página inicial
@app.route('/')
def index():
    # Verifica se existe algum PDF na pasta 'DOEsExtraidos'
    pdfs_extraidos = [f for f in os.listdir('DOEsExtraidos') if f.endswith('.pdf')]
    if pdfs_extraidos:
        # Obtém a data do último PDF extraído
        data_ultimo_pdf = pdfs_extraidos[-1][2:10]
        # Verifica se existe uma pasta com o nome da data do último PDF na pasta 'txt extraido'
        if os.path.exists(os.path.join('txt extraido', data_ultimo_pdf)):
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
    # Caminho para o arquivo
    caminho_arquivo = os.path.join('txt extraido', data_arquivo, nome_arquivo)
    # Lê o conteúdo do arquivo
    with open(caminho_arquivo, 'r') as arquivo:
        conteudo = arquivo.read()   
    # Retorna o conteúdo do arquivo
    return conteudo

if __name__ == '__main__':
    app.run(debug=True)
