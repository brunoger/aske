import os
import json
from sklearn import metrics
from sklearn.cluster import KMeans, DBSCAN
from transformers import AutoTokenizer
from Funções import *
import matplotlib.pyplot as plt
import re
from unidecode import unidecode


tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-large-portuguese-cased')


arquivo = 'json extraidos/26-06-2024.json'
#26-06-2024.json, total de 736 publicações

arquivo = open(arquivo,'r')
teste = json.load(arquivo)

#print(len(teste))

amostranaoclusterizada = []
amostrasorgao = []
amostrasnegrito = []
amostrastexto = []
maxlenao = 0
maxlenan = 0
maxlente = 0


a=0



file = open('amostras[26-06-2024.json].txt','w')
for i in range(0,len(teste)):
    if('OUTROS' not in teste[i]['NOME']):
        file.write(format(i+1)+' '+format(teste[i]['NOME'])+' -> '+format(teste[i]['LISTANEGRITO'])+'\n')
        destaque = filtrar_termos(teste[i]['LISTANEGRITO'])
        
        if(destaque == None):
            amostranaoclusterizada.append(teste[i]['LISTANEGRITO'])
            for T in assunto:
                if(normalize(T).lower() in normalize(teste[i]['TEXTO']).lower()):
                    destaque = T
                    print(destaque)
                    break
                else:
                    destaque = ''
            

        amostrasnegrito.append(tokenizer.encode(destaque))
        
        amostrasorgao.append(tokenizer.encode(teste[i]['NOME']))
        if(maxlenao<len(amostrasorgao[-1])):
            maxlenao = len(amostrasorgao[-1])        
        if(maxlenan<len(amostrasnegrito[-1])):
            maxlenan=len(amostrasnegrito[-1])
        amostrastexto.append(tokenizer.encode(teste[i]['TEXTO']))
        if(maxlente<len(amostrastexto[-1])):
            maxlente = len(amostrastexto[-1])
    else:
        break   



file.close()

#print(len(amostrasorgao))



for i in range(0,len(amostrasorgao)):
    while(len(amostrasorgao[i])<maxlenao):
        amostrasorgao[i].append(0)
    while(len(amostrasnegrito[i])<maxlenan):
        amostrasnegrito[i].append(0)
    while(len(amostrastexto[i])<maxlente):
        amostrastexto[i].append(0)

inercia = []
coeficientes = []
valores = range(2,101)
X = amostrasnegrito

for p in valores:
    kk = KMeans(p,random_state=42).fit(X)
    inercia.append(kk.inertia_)
    coeficientes.append(metrics.silhouette_score(X,kk.labels_))
    txt = open(os.path.join('Resultados KMeans amostras','clusters='+format(p)+'[26-06-2024]'+'.txt'),'w')
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
#plt.savefig('Resultados KMeans amostras/26-06-2024.json 2-100 clusters.png')
plt.show()



print('\nExemplos que possuem um cluster próprio por não haver palavras reconhecidas na lista destaques: ',len(amostranaoclusterizada))
for Z in amostranaoclusterizada:
    print(Z)
