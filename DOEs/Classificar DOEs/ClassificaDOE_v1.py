#Baixa o último DOE e extrai todas as palavras maiúsculas e sem número.

from io import BytesIO
import fitz  # PyMuPDF
import PyPDF2
import pdfrw
import re
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

def extrair_palavras_negrito_maiusculo(pdf_path):
  words = []
  with open(pdf_path, 'rb') as f:
    leitor = PyPDF2.PdfReader(f)
    for page in leitor.pages:
      texto = page.extract_text()
      # Expressão regular para encontrar palavras em negrito
      palavras_negrito = re.findall(r'\b(\d*[A-ZÀ-Ú]+\d*)\b', texto, re.UNICODE)
      for palavra in palavras_negrito:
        #Verifica se a palavra está maiúscula sem conter números.
        if palavra.isupper():
          palavra_sem_numeros = ''.join(filter(str.isalpha, palavra))
          words.append(palavra_sem_numeros)

  return words

# Exemplo de uso
pdf_path = '/content/DOEs/do20240214p01.pdf'

words = extrair_palavras_negrito_maiusculo(pdf_path)

# Escrever as palavras extraídos em um arquivo
output_file = "Palavras.txt"
with open(output_file, "w") as f:
    for palavra in words:
        f.write(palavra + "\n")

# def extract_uppercase_words(pdf_path):
#   """
#   Extrai palavras maiúsculas em caixas retangulares de um PDF.

#   Argumentos:
#     pdf_path: Caminho para o arquivo PDF.

#   Retorno:
#     Lista de palavras maiúsculas.
#   """

#   palavras_maiusculas_com_fundo_cinza = []

#   with open(pdf_path, "rb") as f:
#     pdf_reader = PyPDF2.PdfReader(f)
#     doc = fitz.Document(f)

#     for page_number in range(len(pdf_reader.pages)):
#       page = doc.load_page(page_number)
#       # Extrai caixas retangulares
#       rects = page.get_text("dict")

#       for rect in rects:
#         # Verifica se a chave "text" existe
#         if "text" in rect:
#           # Obtém o texto dentro da caixa
#           texto_caixa = rect["text"].strip()
#           # Obtém a cor de preenchimento da caixa
#           cor_preenchimento = rect["fill"]
#           # Verifica se a cor de preenchimento é cinza
#           if cor_preenchimento == (0.75, 0.75, 0.75):
#             # Verifica se todas as letras são maiúsculas
#             if texto_caixa.isupper():
#               palavras_maiusculas_com_fundo_cinza.append(texto_caixa)

#   return palavras_maiusculas_com_fundo_cinza

# # Exemplo de uso
# pdf_path = "/content/DOEs/do20240214p01.pdf"
# palavras_maiusculas_com_fundo_cinza = extract_uppercase_words(pdf_path)
# print(palavras_maiusculas_com_fundo_cinza)
