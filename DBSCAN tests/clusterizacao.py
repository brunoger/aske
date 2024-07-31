import os
import json
from sklearn import metrics
from sklearn.cluster import KMeans, DBSCAN
from transformers import AutoTokenizer
from Funções import *
import matplotlib.pyplot as plt
import re


ASSUNTO = [
'AVISO','CONCORRÊNCIA','INSTRUÇÃO NORMATIVA','INSTRUÇÃO','CITAÇÃO POR EDITAL',
'EDITAL DE INTIMAÇÃO','EDITAL DE CONVOCAÇÃO','EDITAL DE NOTIFICAÇÃO','EDITAL','Convocação',
' ATA','ATO DECLARATÓRIO','LICENCIAMENTO','CORRIGENDA','DECRETO',
'LEI ','LEIN','PORTARIA ADMINISTRATIVA','INDENIZAÇÃO','PENSÃO',
'RECONHECIMENTO DE DÍVIDA','RECONHECIMENTO DE DESPESA',
'RECONHECIMENTO','DESPESA','DÍVIDA','divida','EXONERAR',
'NOMEAR','AUTORIZAR','DESIGNAR','DESIGNA','Constituir','COMPOR',
'ADITIVOS AOS CONTRATOS','ADITIVO AO CONTRATO','ADITIVO DE CONVÊNIO',
'ADITIVO','FOMENTO','CONTRATO','DECLARAÇÃO','COOPERAÇÃO TÉCNICA','COOPERAÇÃO',
'INEXIGIBILIDADE','PERMISSÃO DE USO','PERMISSÃO',
'EXTRATO','Extrato','EXECUÇÃO','MECENATO',
'ORDEM DE SERVIÇO','ORDEM','RESCISÃO','RATIFICAÇÃO','REQUISIÇÃO',
'CONVOCAÇÃO','RESOLUÇÃO','HOMOLOGAÇÃO','AFASTAMENTO','APOSENTAR','CESSAR','TORNAR SEM EFEITO','TORNAR',
'diária','Diária','DIÁRIA','multa','MULTA','Multa','sanção','SANÇÃO',
'ESTÁGIO','bolsa',
'concessão','ABONO',
'DESISTÊNCIA','HOMOLOGAR','compor','PROGRESSÃO','VALE-TRANS',
'dispensa','DESLIGAR','Desligar','desligar','promover','extinguir','extinta','premiação','apura','afere','oficia',
'NEGAR','homologar','declarar','excluir','gratificação','falecimento','estabelecer','apostilamento',

'REVOGAÇÃO','TERMO DE AUTORIZAÇÃO DE USO','TERMO','Termo','LICITACAO','LICITAÇÃO','DISPENSA','DISPENSA',
'viajar','PUNIR','acatar','RESULTADO','FINAL','RESULTADO FINAL'
]

tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-large-portuguese-cased')

filtro_regex = re.compile(r'\b'+r'\b|\b'.join([re.escape(keyword) for keyword in ASSUNTO])+r'\b',re.IGNORECASE)

arquivo = 'json extraidos/02-01-2024.json'

arquivo = open(arquivo,'r')
teste = json.load(arquivo)

#print(len(teste))

amostrasorgao = []
amostrasnegrito = []
amostrastexto = []
maxlenao = 0
maxlenan = 0
maxlente = 0


a=0

#file = open('Resultados KMeans amostras/amostras[02-01-2024.json].txt','w')
for i in range(0,len(teste)):
    if('OUTROS' not in teste[i]['NOME']):
        #file.write(format(i+1)+' '+format(teste[i]['NOME'])+' -> '+format(teste[i]['LISTANEGRITO'])+'\n')
        destaque = ''
        
        for N in teste[i]['LISTANEGRITO']:
            
            a=0
            for T in ASSUNTO:
                if(T.upper() in N.upper()):
                    a=N
                    break
            if(a==N or a==T):
                destaque=a
                break
            else:
                destaque=a
                continue
            
        if(destaque == 0):
            print(i,teste[i]['LISTANEGRITO'])
            destaque = ''
        amostrasorgao.append(tokenizer.encode(teste[i]['NOME']))
        if(maxlenao<len(amostrasorgao[-1])):
            maxlenao = len(amostrasorgao[-1])
        #print(destaque)
        destaque = tirar_acentos_stopwords(destaque)
        #print(destaque)
        amostrasnegrito.append(tokenizer.encode(destaque))
        if(maxlenan<len(amostrasnegrito[-1])):
            maxlenan=len(amostrasnegrito[-1])
        amostrastexto.append(tokenizer.encode(teste[i]['TEXTO']))
        if(maxlente<len(amostrastexto[-1])):
            maxlente = len(amostrastexto[-1])
    else:
        break   
#file.close()

#print(len(amostrasorgao))
'''


for i in range(0,len(amostrasorgao)):
    while(len(amostrasorgao[i])<maxlenao):
        amostrasorgao[i].append(0)
    while(len(amostrasnegrito[i])<maxlenan):
        amostrasnegrito[i].append(0)
    while(len(amostrastexto[i])<maxlente):
        amostrastexto[i].append(0)

inercia = []
coeficientes = []
valores = range(2,90)
X = amostrasnegrito

for p in valores:
    kk = KMeans(p,random_state=42).fit(X)
    inercia.append(kk.inertia_)
    coeficientes.append(metrics.silhouette_score(X,kk.labels_))
    txt = open(os.path.join('Resultados KMeans amostras','clusters='+format(p)+'[destaque = N]'+'.txt'),'w')
    txt.write(f'Coeficiente de silhueta: {coeficientes[-1]}\n')
    for i,label in enumerate(kk.labels_):
        txt.write(f'amostra:{i+1} -> cluster:{label+1}\n')
    txt.close()


maiorsilhueta = 0
indice = 0

for i in range(0,len(coeficientes)):
    if(coeficientes[i]>maiorsilhueta):
        maiorsilhueta=coeficientes[i]
        clusters = i+2

print(f'Maior silhueta = {maiorsilhueta}')
print(f'número de clusters = {clusters}')


plt.figure(figsize=(8,6))
plt.plot(valores,inercia,'bo-')
plt.xlabel('Número de Clusters (k)')
plt.ylabel('Inércia')
plt.title('Método do Cotovelo para Encontrar o Número Ideal de Clusters')
plt.savefig('Resultados KMeans amostras/02-01-2024.json [destaque = T] 2-89 clusters.png')
plt.show()

'''
