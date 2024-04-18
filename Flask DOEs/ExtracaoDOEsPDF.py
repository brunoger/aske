import os
from Funções import *
from DownloadDOEs import *

print('\nInício do código\n')

#Cria uma pasta com o nome especificado e baixa os Diários Oficiais do Estado até número especificado dias atrás
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

print('Terminada a extração, inicia o armazenamento em .pdf\n')

#Essa parte escreve todo conteúdo de um órgão encontrado nos DOEs especificados em um .pdf:
def extrair_conteudo(listacontextos):
    for contexto in listacontextos:
        bloco = contexto[0].doc
        bloco = bloco.replace('DOEs/do', '').replace('.pdf', '')
        bloco, datachar, meschar, anochar = bloco[:8], bloco[6:8], bloco[4:6], bloco[:4]
        bloco_nome = f"{datachar}-{meschar}-{anochar}"

        for i, item in enumerate(contexto):
            nome_arquivo = f"{bloco_nome} {item.nome}.txt"
            if '(Continuação)' in nome_arquivo:
                nome_arquivo = nome_arquivo.replace(' (Continuação)', '')
            with open(nome_arquivo, 'a' if '(Continuação)' in nome_arquivo else 'w') as file:
                if isinstance(item.texto, list):
                    file.write('\n'.join(item.texto))
                else:
                    file.write(item.texto)

# Exemplo de uso:
extrair_conteudo(listacontextos)
