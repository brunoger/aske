from flask import Flask, request, render_template
import os
from Funções import *
from DownloadDOEs import *

app = Flask(__name__)

# Função para realizar a extração dos dados
def extrair_dados(orgao, periodo_inicio, periodo_fim):

    invalid = ['\uf0b7','\u25cf','\u02da','\u019f','\ufb01','\u0301','\u2010','\u03d0']

    # Converte as datas de string para objetos datetime
    periodo_inicio = datetime.strptime(periodo_inicio, '%Y-%m-%d')
    periodo_fim = datetime.strptime(periodo_fim, '%Y-%m-%d')

    # Calcula a diferença de dias entre o período de início e o período de fim
    diferenca_dias = (periodo_fim - periodo_inicio).days
    
    #Cria uma pasta com o nome especificado e baixa os Diários Oficiais do Estado até número especificado dias atrás
    # Baixa os Diários Oficiais do Estado conforme a diferença de dias calculada
    Baixar_DOEs('DOEs', diferenca_dias, periodo_fim)

    if os.path.exists('DOEsExtraidos') == False:
        os.makedirs('DOEsExtraidos')
    txt_extraido = 'txt extraido'
    if not os.path.exists(txt_extraido):
        os.makedirs(txt_extraido)

    print('Após baixado os DOEs, inicia a extração e o armazenamento:\n')

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
        print(f'\rProgresso: {progress_bar} {progress:.1%}', end='', flush=True)

    arquivos_criados = []  # Lista para armazenar os nomes dos arquivos criados

    for P in pdfpasta:
        if(os.path.exists(os.path.join('DOEsExtraidos',P))):
            print(P+' Documento já utilizado')
            os.remove(os.path.join('DOEs',P))
            continue
        elif(P.endswith('.pdf')):
            print('Documento '+P)
            z = 'DOEs/'+P
            listadocs.append(extrair_orgaos_PDF(z))
            listacontextos.append(extrair_texto_entre_orgaos(listadocs[-1]))
            listanegrito.append(palavras_negrito(listacontextos[-1]))
            bloco = listacontextos[-1][0].doc
            bloco = bloco.replace('DOEs/do','')
            bloco = bloco.replace('.pdf','')
            bloco = bloco.split('p')
            bloco = bloco[0]
            datachar = bloco[6:8]
            meschar = bloco[4:6]
            anochar = bloco[0:4]
            bloco = datachar+'-'+meschar+'-'+anochar
            temp = bloco
            for i in range(0,len(listacontextos[-1])):
                bloco = temp + ' ' + listacontextos[-1][i].nome + '.txt'
                if(type(listacontextos[-1][i].texto) == list):
                    for T in range(0,len(listacontextos[-1][i].texto)):
                        for UNICODE in invalid:
                            if(UNICODE in listacontextos[-1][i].texto[T]):
                                listacontextos[-1][i].texto[T] = listacontextos[-1][i].texto[T].replace(UNICODE,' ') 
                else:
                    for UNICODE in invalid:
                        if(UNICODE in listacontextos[-1][i].texto):
                            listacontextos[-1][i].texto = listacontextos[-1][i].texto.replace(UNICODE,' ')   
                if('(Continuação)' in bloco):
                    bloco = bloco.replace(' (Continuação)','')
                    bloco = bloco.replace(' .txt','.txt')
                    nome = os.path.join(txt_extraido,bloco)
                    file = open(nome,'a')
                    if(type(listacontextos[-1][i].texto) == list):
                        for T in range(0,len(listacontextos[-1][i].texto)):
                            file.write('\n'+listacontextos[-1][i].texto[T])
                    else:
                        file.write('\n'+listacontextos[-1][i].texto)
                else:
                    bloco = bloco.replace(' .txt','.txt')
                    nome = os.path.join(txt_extraido,bloco)
                    file = open(nome,'a')
                    if(type(listacontextos[-1][i].texto) == list):
                        for T in range(0,len(listacontextos[-1][i].texto)):
                            if(T==0):
                                file.write(listacontextos[-1][i].texto[T])
                            else:
                                file.write('\n'+listacontextos[-1][i].texto[T])
                    else:
                        file.write(listacontextos[-1][i].texto)
            file.close()
            os.rename(os.path.join('DOEs',P),os.path.join('DOEsExtraidos',P))

        #Organizar os DOEs em pastas de acordo com seu dia
        for i in os.listdir('txt extraido'):
            if(i.endswith('.txt')):
                temp = i[0:10]
                if os.path.exists(os.path.join('txt extraido',temp)) == False:
                    os.makedirs(os.path.join('txt extraido',temp))
                os.rename(os.path.join('txt extraido',i),os.path.join(os.path.join('txt extraido',temp),i))

    # Armazena os resultados em uma lista para retornar
    resultados = []
    for contexto_lista in listacontextos:
        for item in contexto_lista:
            # Verifica se o objeto item tem o atributo data
            if hasattr(item, 'data') and item.nome == orgao and periodo_inicio <= item.data <= periodo_fim:
                resultados.append({'titulo': item.titulo, 'data': item.data})
    
    return resultados, arquivos_criados

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
    resultados, arquivos_criados = extrair_dados(orgao, periodo_inicio, periodo_fim)

    # Retorna os resultados para o template HTML
    return render_template('resultados.html', orgao=orgao, resultados=resultados, arquivos_criados=arquivos_criados)

@app.route('/ler_arquivo/<path:nome_arquivo>')
def ler_arquivo(nome_arquivo):
    # Caminho para o arquivo
    caminho_arquivo = os.path.join('/home/bruno/Documentos/Doutorado/Busca Semântica/DOEs/App Web DOE', nome_arquivo)
    # Lê o conteúdo do arquivo
    with open(caminho_arquivo, 'r') as arquivo:
        conteudo = arquivo.read()
    # Retorna o conteúdo do arquivo
    return conteudo

if __name__ == '__main__':
    app.run(debug=True, port=8000)
