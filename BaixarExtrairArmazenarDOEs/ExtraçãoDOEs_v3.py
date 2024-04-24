import os
from Funções import *
from DownloadDOEs import *

invalid = ['\uf0b7','\u25cf','\u02da','\u019f','\ufb01','\u0301','\u2010','\u03d0']

print('\nInício do código\n')

#Cria uma pasta com o nome especificado e baixa os Diários Oficiais do Estado até número especificado dias atrás

Baixar_DOEs('DOEs',7)

if os.path.exists('DOEsExtraidos') == False:
  os.makedirs('DOEsExtraidos')
txt_extraido = 'txt extraido'
if not os.path.exists(txt_extraido):
  os.makedirs(txt_extraido)

print('Após baixado os DOEs, inicia a extração e armazenamento\n')

#Essa parte faz toda a extração de órgãos e conteúdo dos documentos baixados
listadocs = []
listacontextos = []
listanegrito = []
pdfpasta = os.listdir('DOEs/')
pdfpasta.sort()

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
  if(i.endswith('.txt'):
    temp = i[0:10]
    if os.path.exists(os.path.join('txt extraido',temp)) == False:
      os.makedirs(os.path.join('txt extraido',temp))
    os.rename(os.path.join('txt extraido',i),os.path.join(os.path.join('txt extraido',temp),i))
