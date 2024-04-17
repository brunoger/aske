import requests
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import os
MAX_RETRIES = 1

def Baixar_DOEs(download_directory,dias_atras):

    if not os.path.exists(download_directory):
        os.mkdir(download_directory)
    else:
        print(f'Diretório {download_directory} já existe.')

    # Data atual
    data_atual = datetime.now()

    # Data de início (7 dias atrás)
    data_inicio = data_atual - timedelta(dias_atras)

    # Função para gerar URLs para cada parte do DOE de uma data específica para baixar
    def generate_urls(date):
        formatted_date = date.strftime("%Y%m%d")
        p01_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p01.pdf"
        p02_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p02.pdf"
        p03_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p03.pdf"
        p04_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p04.pdf"
        p05_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p05.pdf"
        p06_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p06.pdf"
        p07_url = f"http://imagens.seplag.ce.gov.br/PDF/{formatted_date}/do{formatted_date}p07.pdf"
        return p01_url, p02_url, p03_url, p04_url, p05_url, p06_url, p07_url

    # Função para verificar se uma URL existe
    def url_exists(url):
        response = requests.head(url, allow_redirects=False)
        return response.status_code == 200

    # Função para baixar um DOE em PDF
    def download_pdf(pdf_url):
        pdf_filename = os.path.basename(pdf_url)
        pdf_filepath = os.path.join(download_directory,pdf_filename)
        retries = 0

        if not os.path.exists(pdf_filepath):
            if url_exists(pdf_url):
                while retries < MAX_RETRIES:
                    try:
                        pdf_response = requests.get(pdf_url, timeout=30)
                        if pdf_response.status_code == 200:
                            with open(pdf_filepath, 'wb') as pdf_file:
                                pdf_file.write(pdf_response.content)
                            print(f'Diário Oficial baixado: {pdf_filename}')
                            break
                        else:
                            print(f'Erro ao baixar o Diário Oficial: {pdf_filename}')
                            break
                    except requests.exceptions.RequestException as e:
                        print(f'Erro na requisição: {e}')
                        retries += 1
                        time.sleep(5)
                else:
                    print(f'Falha após {MAX_RETRIES} tentativas. Desistindo: {pdf_filename}')
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
