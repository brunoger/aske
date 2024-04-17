import os
from Funções import *
from DownloadDOEs import *

print('\nInício do código\n')

Baixar_DOEs('DOEs',7)

print('Após baixado os DOEs, inicia a extração:\n')

#Essa parte faz toda a extração de órgãos e conteúdo dos documentos baixados
listadocs = []
listacontextos = []
listanegrito = []
pdfpasta = os.listdir('DOEs/')
pdfpasta.sort()

for i in pdfpasta:
  if(i.endswith('.pdf')):
    print('Documento '+i)
    z = 'DOEs/'+i
    listadocs.append(extrair_orgaos_PDF(z))
    listacontextos.append(extrair_texto_entre_orgaos(listadocs[-1]))
    listanegrito.append(palavras_negrito(listacontextos[-1]))

print('Terminada a extração, inicia o armazenamento em .txt\n')

#Essa parte escreve todo conteúdo de um órgão em um .txt por DOE, incluindo quando é separado entre cadernos
for I in range(0,len(listacontextos)):
  bloco = listacontextos[I][0].doc
  bloco = bloco.replace('DOEs/do','')
  bloco = bloco.replace('.pdf','')
  bloco = bloco.split('p')
  bloco = bloco[0]
  datachar = bloco[6:8]
  meschar = bloco[4:6]
  anochar = bloco[0:4]
  bloco = datachar+'-'+meschar+'-'+anochar
  temp = bloco
  for i in range(0,len(listacontextos[I])):
    bloco = temp + ' ' + listacontextos[I][i].nome + '.txt'
    if('(Continuação)' in bloco):
      bloco = bloco.replace(' (Continuação)','')
      bloco = bloco.replace(' .txt','.txt')
      file = open(bloco,'a')
      if(type(listacontextos[I][i].texto) == list):
        for T in range(0,len(listacontextos[I][i].texto)):
          file.write('\n'+listacontextos[I][i].texto[T])
      else:
        file.write('\n'+listacontextos[I][i].texto)
    else:
      bloco = bloco.replace(' .txt','.txt')
      file = open(bloco,'w')
      if(type(listacontextos[I][i].texto) == list):
        for T in range(0,len(listacontextos[I][i].texto)):
          if(T==0):
            file.write(listacontextos[I][i].texto[T])
          else:
            file.write('\n'+listacontextos[I][i].texto[T])
      else:
        file.write(listacontextos[I][i].texto)
    file.close()
