import PyPDF2
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import os

# Diretório de destino para salvar os DOEs
download_directory = '/content/DOEs'

# Data atual
data_atual = datetime.now()

# Data de início (3 meses atrás)
data_inicio = data_atual - timedelta(days=90)

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

# Nome do arquivo PDF de saída combinado
combined_pdf_filename = 'combined_does.pdf'

# Lista para armazenar os caminhos completos dos arquivos PDF individuais
pdf_files = [os.path.join(pdf_directory, pdf_file) for pdf_file in os.listdir(pdf_directory) if pdf_file.endswith('.pdf')]

def combine_pdfs(input_pdfs, output_pdf):
    pdf_merger = PyPDF2.PdfMerger()

    # Adiciona cada PDF à lista de fusão
    for pdf_file in input_pdfs:
        pdf_merger.append(pdf_file)

    # Cria o arquivo PDF combinado
    with open(output_pdf, 'wb') as combined_pdf:
        pdf_merger.write(combined_pdf)

    print(f'PDFs combinados com sucesso em: {output_pdf}')

# Chama a função para combinar os PDFs
combine_pdfs(pdf_files, os.path.join(pdf_directory, combined_pdf_filename))

