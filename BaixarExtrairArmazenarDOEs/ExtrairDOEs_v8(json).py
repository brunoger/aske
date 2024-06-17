import os
import json
from Funções import *
from DownloadDOEs import *

print('\nInício do código\n')

#Cria uma pasta com o nome especificado e baixa os Diários Oficiais do Estado até número especificado dias atrás
Baixar_DOEs('DOEs', 2)

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

listX = []
X = {
  'DATA',
  'CADERNO',
  'PAGINA',
  'NOME',
  'PUBLICACAO',
  'TEXTO',
  'LISTANEGRITO'
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
    bloco = z
    bloco = bloco.replace('DOEs/do','')
    bloco = bloco.split('p')
    caderno = bloco[1]
    bloco = bloco[0]
    caderno = caderno.replace('0','')
    caderno = caderno.replace('.','')
    caderno = int(caderno)
    print(bloco,caderno)
    datachar = bloco[6:8]
    meschar = bloco[4:6]
    anochar = bloco[0:4]

    if(temp!=datachar+'-'+meschar+'-'+anochar):
      if(temp!=''):
        with open('json extraidos/'+temp+'.json','w') as write_file:
          json.dump(listX, write_file, indent=4)
      temp=datachar+'-'+meschar+'-'+anochar
      listX = []
      X = {
          'DATA',
          'CADERNO',
          'PAGINA',
          'NOME',
          'PUBLICACAO',
          'TEXTO',
          'LISTANEGRITO'
          }

    listadocs.append(extrair_orgaos_PDF(z))
    listacontextos.append(extrair_texto_entre_orgaos(listadocs[-1]))

    for c in range(0,len(listacontextos[-1])):
      if('(Continuação)' in listacontextos[-1][c].nome or ' (Continuação)' in listacontextos[-1][c].nome):
        listacontextos[-1][c].nome = listacontextos[-1][c].nome.replace(' (Continuação)','')
        if(type(listacontextos[-1][c].publicacao) == list):
          for T in range(0,len(listacontextos[-1][c].publicacao)):
            listX.append({
              'DATA': temp,
              'CADERNO': caderno,
              'PAGINA': listacontextos[-1][c].publicacao[T].page1,
              'NOME': listacontextos[-1][c].nome,
              'PUBLICACAO': 1+T,
              'TEXTO': listacontextos[-1][c].publicacao[T].texto,
              'LISTANEGRITO': listacontextos[-1][c].publicacao[T].negrito
            })
        else:
          listX.append({
              'DATA': temp,
              'CADERNO': caderno,
              'PAGINA': listacontextos[-1][c].publicacao.page1,
              'NOME': listacontextos[-1][c].nome,
              'PUBLICACAO': 1+T,
              'TEXTO': listacontextos[-1][c].publicacao.texto,
              'LISTANEGRITO': listacontextos[-1][c].publicacao.negrito
            })
      else:
        if(type(listacontextos[-1][c].publicacao) == list):
          for T in range(0,len(listacontextos[-1][c].publicacao)):
            listX.append({
              'DATA': temp,
              'CADERNO': caderno,
              'PAGINA': listacontextos[-1][c].publicacao[T].page1,
              'NOME': listacontextos[-1][c].nome,
              'PUBLICACAO': 1+T,
              'TEXTO': listacontextos[-1][c].publicacao[T].texto,
              'LISTANEGRITO': listacontextos[-1][c].publicacao[T].negrito
            })
        else:
          listX.append({
              'DATA': temp,
              'CADERNO': caderno,
              'PAGINA': listacontextos[-1][c].publicacao.page1,
              'NOME': listacontextos[-1][c].nome,
              'PUBLICACAO': 1+T,
              'TEXTO': listacontextos[-1][c].publicacao.texto,
              'LISTANEGRITO': listacontextos[-1][c].publicacao.negrito
            })
    os.rename(os.path.join('DOEs',P),os.path.join('DOEsExtraidos',P))

if(temp!=''):
  with open('json extraidos/'+temp+'.json','w') as write_file:
    json.dump(listX, write_file, indent=4)
