import fitz  # PyMuPDF
import re
import nltk
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import os

#Criar pasta de Diários Oficiais do Estado
if '/content/DOEs' not in '/content':
  os.makedirs('/content/DOEs', exist_ok=True)

# Diretório de destino para salvar os DOEs
download_directory = '/content/DOEs'

# Data atual
data_atual = datetime.now()

# Data de início (1 dia atrás)
data_inicio = data_atual - timedelta(days=1)

# Função para gerar URLs para cada parte do DOE de uma data específica para baixar
def generate_urls(date):
    formatted_date = date.strftime("%Y%m%d")
    p01_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p01.pdf"
    p02_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p02.pdf"
    p03_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p03.pdf"
    p04_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p04.pdf"
    p05_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p05.pdf"
    return p01_url, p02_url, p03_url, p04_url, p05_url

# Função para verificar se uma URL existe
def url_exists(url):
    response = requests.head(url, allow_redirects=False)
    return response.status_code == 200

# Função para baixar um DOE em PDF
def download_pdf(pdf_url):
    pdf_filename = os.path.basename(pdf_url)
    pdf_filepath = os.path.join(download_directory, pdf_filename)

    if not os.path.exists(pdf_filepath):
        if url_exists(pdf_url):
            pdf_response = requests.get(pdf_url)

            if pdf_response.status_code == 200:
                with open(pdf_filepath, 'wb') as pdf_file:
                    pdf_file.write(pdf_response.content)
                print(f'Diário Oficial baixado: {pdf_filename}')
            else:
                print(f'Erro ao baixar o Diário Oficial: {pdf_filename}')
        else:
            print(f'Url nao encontrada: {pdf_url}')
    else:
        print(f'PDF ja existe: {pdf_filename}')

# Baixar os novos arquivos
for pdf_url in generate_urls(data_atual):
    download_pdf(pdf_url)

# Verificar se os arquivos existentes são iguais aos novos antes de excluir
existing_files = [f for f in os.listdir(download_directory) if os.path.isfile(os.path.join(download_directory, f))]
new_files = [os.path.basename(url) for url in generate_urls(data_atual)]

# Os arquivos existentes são diferentes dos novos, então exclua os arquivos baixados
for pdf_url in generate_urls(data_atual):
    pdf_filename = os.path.basename(pdf_url)
    pdf_filepath = os.path.join(download_directory, pdf_filename)
    if pdf_filename in existing_files:
        os.remove(pdf_filepath)
        print(f'Arquivo baixado excluído: {pdf_filepath}')

print("Processo concluído.")

# Função para verificar a existência de arquivos em paralelo
def check_file_existence(urls):
    with ThreadPoolExecutor(max_workers=5) as executor:  # Ajuste o número de threads conforme necessário
        results = list(executor.map(url_exists, urls))
    return results

# Função para baixar vários DOEs em paralelo
def download_multiple_pdfs(pdf_urls):
    with ThreadPoolExecutor(max_workers=5) as executor:  # Ajuste o número de threads conforme necessário
        executor.map(download_pdf, pdf_urls)

while data_atual >= data_inicio:
    urls_to_check = list(generate_urls(data_atual))
    existing_urls = [url for url, exists in zip(urls_to_check, check_file_existence(urls_to_check)) if exists]
    download_multiple_pdfs(existing_urls)
    data_atual -= timedelta(days=1)

# Diretório onde os PDFs individuais estão localizados
pdf_directory = '/content/DOEs'

# Verifica se o diretório existe
if not os.path.exists(pdf_directory):
    print(f"O diretório {pdf_directory} não existe.")
    exit()

# Nome do arquivo PDF de saída combinado
combined_pdf_filename = 'combined_does.pdf'

# Lista para armazenar os caminhos completos dos arquivos PDF individuais
pdf_files = [os.path.join(pdf_directory, pdf_file) for pdf_file in os.listdir(pdf_directory) if pdf_file.endswith('.pdf')]

if not pdf_files:
    print("Nenhum arquivo PDF encontrado no diretório.")
    exit()

def combine_pdfs(input_pdfs, output_pdf):
    pdf_merger = PyPDF2.PdfMerger()

    # Adiciona cada PDF à lista de fusão
    for pdf_file in input_pdfs:
        pdf_merger.append(pdf_file)

    # Cria o arquivo PDF combinado
    with open(output_pdf, 'wb') as combined_pdf:
        pdf_merger.write(combined_pdf)

    print(f'PDFs combinados com sucesso em: {output_pdf}')

# Caminho para o arquivo PDF combinado
combined_pdf_path = os.path.join(pdf_directory, combined_pdf_filename)

# Verifica se o arquivo PDF combinado já existe
if not os.path.exists(combined_pdf_path):
    # Chama a função para combinar os PDFs
    combine_pdfs(pdf_files, combined_pdf_path)
    print("PDFs combinados com sucesso.")
else:
    print("O arquivo PDF combinado já existe. A combinação não foi realizada.")

def extract_text_from_pdf(pdf_path):
    try:
        text = ''
        with fitz.open(pdf_path) as pdf_file:
            for page_num in range(len(pdf_file)):
                page = pdf_file.load_page(page_num)
                text += page.get_text()

        return text.strip()  # Remova espaços em branco extras no início e no final do texto
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
        return None

# Função para extrair nomes próprios de um texto
def extract_proper_names(text):
    sentences = nltk.sent_tokenize(text)
    proper_names = []

    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        tagged_words = nltk.pos_tag(words)

        # Loop sobre as palavras marcadas
        for i in range(len(tagged_words)):
            word, tag = tagged_words[i]

            # Verifica se a palavra está toda em maiúsculas e não é um verbo
            if word.isupper() and 'VB' not in tag:
              proper_names.append(word)
            # Verifica se a primeira letra é maiúscula e as demais são minúsculas, e não é um verbo
            elif word[0].isupper() and word[1:].islower() and 'VB' not in tag:
              proper_names.append(word)

    return proper_names

pdf_path = '/content/DOEs/combined_does.pdf'
pdf_text = extract_text_from_pdf(pdf_path)
names = extract_proper_names(pdf_text)

if pdf_text:
    print("Texto extraído do PDF e salvo em DOE.txt")
    with open(f"DOE.txt", "w") as f:
      f.write(pdf_text)
else:
    print("Não foi possível extrair texto do PDF.")

# Escrever os nomes extraídos em um arquivo
output_file = "Nomes.txt"
with open(output_file, "w") as f:
    for name in names:
        f.write(name + "\n")

if names:
    print(f"Nomes encontrados no PDF foram salvos em '{output_file}'.")
else:
    print("Nenhum nome encontrado no PDF.")
