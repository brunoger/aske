import os
import json
from Funções import *
from DownloadDOEs import *

print('\nInício do código\n')

#Cria uma pasta com o nome especificado e baixa os Diários Oficiais do Estado até número especificado dias atrás
Baixar_DOEs('DOEs',4)

#Pasta que guarda quais DOEs já estão extraídos em .json
if os.path.exists('DOEsExtraidos') == False:
  os.makedirs('DOEsExtraidos')

#Pasta que guarda os .json
if os.path.exists('json extraidos') == False:
  os.makedirs('json extraidos')

print('Após baixado os DOEs, inicia a extração:\n')

#Essa parte faz toda a extração de órgãos e conteúdo dos documentos baixados
listadocs = []
listacontextos = []
#listanegrito = []

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
for P in pdfpasta:
  if(os.path.exists(os.path.join('DOEsExtraidos',P))):
    print(P+' Documento já utilizado')
    os.remove(os.path.join('DOEs',P))
  elif(P.endswith('.pdf')):
    print('Documento '+P)
    z = 'DOEs/'+P
    listadocs.append(extrair_orgaos_PDF(z))
    listacontextos.append(extrair_texto_entre_orgaos(listadocs[-1]))
    #listanegrito.append(palavras_negrito(listacontextos[-1]))
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
          for L in range(0,len(listX)):
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
    for L in range(0,len(listX)):
      json.dump(listX, write_file, indent=4)


