import os
import json
import numpy as np
from transformers import AutoTokenizer, AutoModelForMaskedLM, AutoModel
#import torch
#import dbscan
from sklearn.decomposition import PCA
from sklearn import metrics
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt


#print('Tokenizer\n')
tokenizer = AutoTokenizer.from_pretrained("neuralmind/bert-large-portuguese-cased")
#model = AutoModel.from_pretrained("neuralmind/bert-large-portuguese-cased")

pastajson = os.listdir('json teste')
pastajson.sort()

Mleninputorgao = 0
Mleninputdestaque = 0
#Mleninputtexto = 0


inputorgao = []
inputdestaque = []
#inputtexto = []


for I in pastajson:
    arquivo = os.path.join('json teste',I)

    arquivojson = open(arquivo,'r')

    jsonteste = json.load(arquivojson) 


    '''
    arquivojson = open('json extraidos/03-07-2023.json','r')
    jsonteste = json.load(arquivojson) 

    inputorgao = []
    inputdestaque = []
    inputtexto = []
    '''

    for F in range(0,len(jsonteste)):
        if('OUTROS' not in jsonteste[F]['NOME']):
        
            inputorgao.append(tokenizer.encode(jsonteste[F]['NOME']))
            if(Mleninputorgao==0 or Mleninputorgao<len(inputorgao[-1])):
                Mleninputorgao = len(inputorgao[-1])
        
            destaque = ''
            for i in jsonteste[F]['LISTANEGRITO']:
                destaque = destaque + i + ' '
            inputdestaque.append(tokenizer.encode(destaque))
            if(Mleninputdestaque==0 or Mleninputdestaque<len(inputdestaque[-1])):
                Mleninputdestaque = len(inputdestaque[-1])
        
            #inputtexto.append(tokenizer.encode(jsonteste[F]['TEXTO']))
            #if(Mleninputtexto==0 or Mleninputtexto<len(inputtexto[-1])):
            #    Mleninputtexto = len(inputtexto[-1])
    
        else:
            break


#Isso deixa todos os vetores terem o mesmo tamanho 
for Z in range(0,len(inputorgao)):
    while(len(inputorgao[Z])<Mleninputorgao):
        inputorgao[Z].append(0)
    
    while(len(inputdestaque[Z])<Mleninputdestaque):
        inputdestaque[Z].append(0)
    
    #while(len(inputtexto[Z])<Mleninputtexto):
    #    inputtexto[Z].append(0)

orgaodestaque = []



for Z in range(0,len(inputorgao)):
    orgaodestaque.append(inputorgao[Z]+inputdestaque[Z])
    #orgaotexto.append(inputorgao[Z]+inputtexto[Z])
    #destaquetexto.append(inputdestaque[Z]+inputtexto[Z])
    #orgaodestaquetexto.append(inputorgao[Z]+inputdestaque[Z]+inputtexto[Z])

#print(len(orgaodestaque))


X = orgaodestaque
Xnome = 'orgaodestaque'
epsilon = 0.25
amostras = 10

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

#for i, label in enumerate(labels):
#    print(f'Amostra {i} -> Cluster: {label}')

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

