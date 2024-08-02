import os
import json
import numpy as np
from sklearn import metrics
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from transformers import AutoTokenizer
from Funções import *
import matplotlib.pyplot as plt
import re
from unidecode import unidecode

tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-large-portuguese-cased')

arquivo = 'json extraidos/26-06-2024.json'

arquivo = open(arquivo,'r')
teste = json.load(arquivo)

#print(len(teste))

amostranaoclusterizada = []
amostrasorgao = []
amostrasdestaque = []
amostrastexto = []
maxlenao = 0
maxlenan = 0
maxlente = 0


a=0



#file = open('amostras[26-06-2024.json].txt','w')
for i in range(0,len(teste)):
    if('OUTROS' not in teste[i]['NOME']):
        #file.write(format(i+1)+' '+format(teste[i]['NOME'])+' -> '+format(teste[i]['LISTANEGRITO'])+'\n')
        destaque = filtrar_termos(teste[i]['LISTANEGRITO'])

        #print("\nTermos filtrados:")
        a=0
        #destaque = 0
        if(destaque == 0):
            for N in teste[i]['LISTANEGRITO']:
                for T in assunto:
                    if(normalize(T).upper() in normalize(N).upper()):
                        destaque = normalize(N)
                        a=1
                        break
                if(a==1):
                    break
        if(destaque == None):
            amostranaoclusterizada.append(teste[i]['LISTANEGRITO'])
            destaque=''
        #print(destaque)
        amostrasdestaque.append(tokenizer.encode(destaque))
        
        amostrasorgao.append(tokenizer.encode(teste[i]['NOME']))
        if(maxlenao<len(amostrasorgao[-1])):
            maxlenao = len(amostrasorgao[-1])        
        if(maxlenan<len(amostrasdestaque[-1])):
            maxlenan=len(amostrasdestaque[-1])
        amostrastexto.append(tokenizer.encode(teste[i]['TEXTO']))
        if(maxlente<len(amostrastexto[-1])):
            maxlente = len(amostrastexto[-1])
    else:
        break   



#file.close()

#print(len(amostrasorgao))



for i in range(0,len(amostrasorgao)):
    while(len(amostrasorgao[i])<maxlenao):
        amostrasorgao[i].append(0)
    while(len(amostrasdestaque[i])<maxlenan):
        amostrasdestaque[i].append(0)
    while(len(amostrastexto[i])<maxlente):
        amostrastexto[i].append(0)




X = amostrasdestaque
Xnome = 'amostrasdestaque'
epsilon = 0.1
amostras = 5

db = DBSCAN(eps=epsilon,min_samples=amostras,metric='cosine').fit(X)
labels = db.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

#print('\nHomogeneity: ',metrics.homogeneity_score(labels_true,labels))
#print('\nCompleteness: ',metrics.completeness_score(labels_true,labels))
#print('\nV-measure: ',metrics.v_measure_score(labels_true,labels))
#print('\nAdjusted Rand Index: ',metrics.adjusted_rand_score(labels_true,labels))
#print('\nAdjusted Mutual Information: ',metrics.adjusted_mutual_info_score(X,labels))
#print('leafsize: ',leafsize)

txt = open('clusters [26-06-2024.json](com DBSCAN) eps=0,1, min_samples=5.txt','w')
txt.write(f'Silhouette Coefficient: {metrics.silhouette_score(X, labels)}')
for i, label in enumerate(labels):
    txt.write(f'\nAmostra {i+1} -> Cluster: {label}')
txt.close()


print('\nepsilon = ',epsilon)
print('min_samples = ',amostras)
print('\nNúmero estimado de cluster: ',n_clusters_)
print('Número estimado de ruído: ',n_noise_)

print("Silhouette Coefficient: ", metrics.silhouette_score(X, labels))

pca = PCA(2)
Xreduzido = pca.fit_transform(X)

unique_labels = set(labels)
core_samples_mask = np.zeros_like(labels, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True

colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = labels == k

    xy = Xreduzido[class_member_mask & core_samples_mask]
    plt.plot(
        xy[:, 0],
        xy[:, 1],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=14,
    )

    xy = Xreduzido[class_member_mask & ~core_samples_mask]
    plt.plot(
        xy[:, 0],
        xy[:, 1],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=6,
    )

plt.title(f'{Xnome} com medidas: eps={epsilon} e min_samples={amostras}')
plt.show()

print('\nExemplos sem palavras encontradas: ',len(amostranaoclusterizada))
for Z in amostranaoclusterizada:
    print(Z)
