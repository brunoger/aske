#Vinícius
import PyPDF2 #instalar com pip
import pdfplumber #instalar com pip
import requests
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import os
import nltk
nltk.download('all')
from nltk import *
MAX_RETRIES = 3

class Data: #classificação de datas encontradas no documento
  def __init__(self, dia, doc, pag, frase):
    self.dia = dia
    self.doc = doc
    self.pag = pag
    self.frase = frase

# Diretório de destino para salvar os DOEs
download_directory = '/content/DOEs'

if not os.path.exists(download_directory):
    os.mkdir(download_directory)
else:
    print(f'Diretório {download_directory} já existe.')

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


#Busca por datas por extenso e resumida alocando em um vetor com todas as datas e identificação da data por documento
def find_date(pdf_files, datas):
  leitor = PyPDF2.PdfReader(pdf_files)
  for i in range(0,len(leitor.pages)):
    sentences = sent_tokenize(leitor.pages[i].extract_text())
    for S in range(0,len(sentences)):
      TOKEN = word_tokenize(sentences[S])
      for j in range(0,len(TOKEN)):
        TOKEN[j].lower()
        if(TOKEN[j].isdigit() and j+4<len(TOKEN)): #Caso data por extenso exemplo: 25 de dezembro de 2023
          j=j+1
          if(TOKEN[j] == 'de'):
            j=j+1
            if(TOKEN[j] == 'janeiro' or TOKEN[j] == 'fevereiro' or TOKEN[j] == 'março' or TOKEN[j] == 'abril' or TOKEN[j] == 'maio' or TOKEN[j] == 'junho' or TOKEN[j] == 'julho' or TOKEN[j] == 'agosto' or TOKEN[j] == 'setembro' or TOKEN[j] == 'outubro' or TOKEN[j] == 'novembro' or TOKEN[j] == 'dezembro'):
              j=j+1
              if(TOKEN[j] == 'de'):
                j=j+1
                if(TOKEN[j].isdigit()):
                  #print(TOKEN[j-4],TOKEN[j-3],TOKEN[j-2],TOKEN[j-1],TOKEN[j])
                  datas.append(TOKEN[j-4]+' '+TOKEN[j-3]+' '+TOKEN[j-2]+' '+TOKEN[j-1]+' '+TOKEN[j])
                  pdf_files = pdf_files.replace('/content/DOEs/','')
                  datas[-1] = Data(datas[-1],pdf_files,i+1,S+1)

        elif(TOKEN[j].count('/')>=2): #Caso data resumida exemplo: DD/MM/YYYY
          x=0 #posição na string
          n=0 #quantidade de números
          b=0 #quantidade de /
          while(x<len(TOKEN[j])):
            if(TOKEN[j][x].isnumeric()):
              #print(TOKEN[z][x])
              n+=1
            elif(TOKEN[j][x] == '/' and ((n==2 and b==0) or (n==4 and b==1))):
              b+=1
            elif(TOKEN[j][x].isnumeric()==False and TOKEN[j][x] != '/'):
              TOKEN[j] = TOKEN[j].replace(TOKEN[j][x],'')
              continue
            elif(TOKEN[j][x] == '/' and b==2):
              temp1 = TOKEN[j].split('/')
              temp2  = temp1[0]
              for f in range(1,len(temp1)-1):
                temp2 = temp2 + '/' + temp1[f]
              TOKEN[j] = temp2
            x=x+1
          if(n==8 and b==2):
            #print(i,j,z,TOKEN[j])
            datas.append(TOKEN[j])
            pdf_files = pdf_files.replace('/content/DOEs/','')
            datas[-1] = Data(datas[-1],pdf_files,i+1,S+1)

        elif(TOKEN[j].count('.')==2 and TOKEN[j].count('/')==0 and TOKEN[j].count('-')==0): #Caso data formato DD.MM.YYYY
          C=0
          N=0
          while(C<len(TOKEN[j])):
            if(TOKEN[j][C].isnumeric()):
              C+=1
              N+=1
            elif(TOKEN[j][C]=='.' and N%3!=0):
              C+=1
              N+=1
            else:
              TOKEN[j] = TOKEN[j].replace(TOKEN[j][C],'')
          if(N==10):
            datas.append(TOKEN[j])
            pdf_files = pdf_files.replace('/content/DOEs/','')
            datas[-1] = Data(datas[-1],pdf_files,i+1,S+1)
            
  return datas

#Lista com todas as palavras em negrito de um PDF
def palavras_negrito(pdf_files): 
  palavrasnegrito = []
  temp=''
  with pdfplumber.open(pdf_files) as pdf:
    for i in range(0,len(pdf.pages)):
      texto = pdf.pages[i]
      for c in range(0,len(texto.chars)):
        if('Bold' in texto.chars[c]['fontname']):
          temp = temp + texto.chars[c]['text']
        elif(temp != ''):
          palavrasnegrito.append(temp)
          temp = ''
  return palavrasnegrito
