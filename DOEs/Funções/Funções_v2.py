import PyPDF2 #instalar com pip
import pdfpumbler # instalar com pip

class Data: Informações sobre data encontrada num DOE
  def __init__(self, dia, doc, pag, frase):
    self.dia = dia
    self.doc = doc
    self.pag = pag
    self.frase = frase

#Busca por datas por extenso e resumida alocando em um vetor com todas as datas e identificação da data por documento
def find_date(pdf_files, datas):
  with pdfplumber.open(pdf_files) as leitor:
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
                    datas.append(TOKEN[j-4]+' '+TOKEN[j-3]+' '+TOKEN[j-2]+' '+TOKEN[j-1]+' '+TOKEN[j])
                    pdf_files = pdf_files.replace('/content/DOEs/','')
                    datas[-1] = Data(datas[-1],pdf_files,i,S)
          elif(TOKEN[j].count('/')>=2): #Caso data resumida exemplo: DD/MM/YYYY
            x=0 #posição na string
            n=0 #quantidade de números
            b=0 #quantidade de /
            while(x<len(TOKEN[j])):
              if(TOKEN[j][x].isnumeric()):
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
              datas.append(TOKEN[j])
              pdf_files = pdf_files.replace('/content/DOEs/','')
              datas[-1] = Data(datas[-1],pdf_files,i,S)
          elif(TOKEN[j].count('.')==2 and TOKEN[j].count('/')==0 and TOKEN[j].count('-')==0): #Caso data formato DD.MM.YYYY
            C=0
            N=0
            while(C<len(TOKEN[j])):
              if(TOKEN[j][C].isnumeric()):
                C+=1
                N+=1
              elif(TOKEN[j][C]=='.' and N==2):
                C+=1
              elif(TOKEN[j][C]=='.' and N==4):
                C+=1
              else:
                TOKEN[j] = TOKEN[j].replace(TOKEN[j][C],'')
            if(N==8 and C==10):
              datas.append(TOKEN[j])
              pdf_files = pdf_files.replace('/content/DOEs/','')
              datas[-1] = Data(datas[-1], pdf_files, i, S)  
  return datas

#Extrai palavras em negrito de um PDF e separa órgãos caso estejam concatenados a qualquer outra palavras
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
  palavrasnegrito = organizar_palavras_negrito(palavrasnegrito)
  return palavrasnegrito

def organizar_palavras_negrito(palavrasnegrito):
  orgaos = ['PODER EXECUTIVO','GOVERNADORIA','CASA CIVIL','EMPRESA DE TECNOLOGIA DA INFORMAÇÃO DO CEARÁ','PROCURADORIA GERAL DO ESTADO', 'CONTROLADORIA E OUVIDORIA-GERAL DO ESTADO','CONSELHO ESTADUAL DE EDUCAÇÃO','SECRETARIAS E VINCULADAS','SECRETARIA DE ADMNISTRAÇÃO PENITENCIÁRIA E RESSOCIALIZAÇÃO','SECRETARIA DAS CIDADES','SUPERINTENDÊNCIA DE OBRAS PÚBLICAS','COMPANHIA DE ÁGUA E ESGOTO DO CEARÁ','SECRETARIA DE CIÊNCIA, TECNOLOGIA E EDUCAÇÃO SUPERIOR','FUNDAÇÃO CEARENSE DE APOIO AO DESENVOLVIMENTO CIENTÍFICO E TECNOLÓGICO','FUNDAÇÃO UNIVERSIDADE ESTADUAL VALE DO ACARAÚ','FUNDAÇÃO UNIVERSIDADE REGIONAL DO CARIRI','FUNDAÇÃO UNIVERSIDADE ESTADUAL DO CEARÁ','NÚCLEO DE TECNOLOGIA E QUALIDADE INDUSTRIAL DO CEARÁ','SECRETARIA DA CULTURA','SECRETARIA DO DESENVOLVIMENTO AGRÁRIO','EMPRESA DE ASSISTÊNCIA TÉCNICA E EXTENSÃO RURAL DO CEARÁ','SECRETARIA DO DESENVOLVIMENTO ECONÔMICO','COMPANHIA DE DESENVOLVIMENTO DO COMPLEXO INDUSTRIAL E PORTUÁRIO DO PECÉM S.A.','SECRETARIA DA EDUCAÇÃO','SECRETARIA DA FAZENDA','SECRETARIA DA INFRAESTRUTURA','DEPARTAMENTO ESTADUAL DE TRÂNSITO','DEPARTAMENTO ESTADUAL DE TRÂNSITO','SECRETARIA DA JUVENTUDE','SECRETARIA DO MEIO AMBIENTE E MUDANÇA DO CLIMA','SUPERINTENDÊNCIA ESTADUAL DO MEIO AMBIENTE','SECRETARIA DAS MULHERES','SECRETARIA DO PLANEJAMENTO E GESTÃO','INSTITUTO DE SAÚDE DOS SERVIDORES DO ESTADO DO CEARÁ','COMPANHIA DE HABITAÇÃO DO ESTADO DO CEARÁ','SECRETARIA DA PROTEÇÃO SOCIAL','SUPERINTENDÊNCIA DO SISTEMA ESTADUAL DE ATENDIMENTO SOCIOEDUCATIVO','SECRETARIA DOS RECURSOS HÍDRICOS','FUNDAÇÃO CEARENSE DE METEOROLOGIA E RECURSOS HÍDRICOS','SECRETARIA DA SAÚDE','SECRETARIA DA SEGURANÇA PÚBLICA E DEFESA SOCIAL','SUPERINTENDÊNCIA DA POLÍCIA CIVIL','POLÍCIA MILITAR DO CEARÁ','CORPO DE BOMBEIROS MILITAR DO ESTADO DO CEARÁ','PERÍCIA FORENSE DO CEARÁ','ACADEMIA ESTADUAL DE SEGURANÇA PÚBLICA','CONTROLADORIA GERAL DE DISCIPLINA DOS ÓRGÃOS DE SEGURANÇA PÚBLICA E SISTEMA PENITENCIÁRIO','OUTROS']
  for p in range(0,len(palavrasnegrito)):
    for o in range(0,len(orgaos)):
      if(orgaos[o] in palavrasnegrito[p]):
        temp=''
        w=0
        while(temp!=orgaos[o]):
          if(temp==''):
            temp=temp+palavrasnegrito[p][w]
            C=w
            w+=1
          if(temp!='' and temp[len(temp)-1]==orgaos[o][len(temp)-1]):
            temp=temp+palavrasnegrito[p][w]
            w+=1
          if(temp[len(temp)-1]!=orgaos[o][len(temp)-1]):
            temp=''
        if(C==0):
          palavrasnegrito[p] = palavrasnegrito[p].replace(temp,'')
          palavrasnegrito.insert(p,temp)
        else:
          while(w<len(palavrasnegrito[p])):
            temp=temp+palavrasnegrito[p][w]
            w+=1
          palavrasnegrito[p] = palavrasnegrito[p].replace(temp,'')
          palavrasnegrito.insert(p+1,temp)
  return palavrasnegrito

def extrair_orgaos_PDF(pdf_files): #Extrai Orgaos presentes em um documento
  lista = []
  listaadic = []
  with pdfplumber.open(pdf_files) as pdf:
    for P in range(0,len(pdf.pages)):
      pagina = pdf.pages[P]
      for i in range(0,len(pagina.rects)):
        temp=''
        for w in range(0,len(pagina.chars)):
          if(pagina.chars[w]['x0']>=pagina.rects[i]['x0'] and pagina.chars[w]['x1']<=pagina.rects[i]['x1'] and pagina.chars[w]['y1']>=pagina.rects[i]['y0'] and pagina.chars[w]['y1']<=pagina.rects[i]['y1']):
            temp=temp+pagina.chars[w]['text']
            page = pagina.chars[w]['page_number']
            y0 = pagina.chars[w]['y0']
            y1 = pagina.chars[w]['y1']
        if(temp!=''):
          if(temp not in listaadic):
            for z in range(0,len(temp)):
              if(temp[z].isnumeric() or temp[z].islower()):
                temp=''
                break
            if(temp!=''):
              lista.append(temp)
              listaadic.append(temp)
              lista[-1] = Orgaos(temp,pdf_files,page,y0,y1)
            temp=''
  return lista

def extrair_texto_entre_orgaos(lista): #Extrai texto entre orgaos
  contexto = []
  with pdfplumber.open(lista[0].doc) as pdf:
    temp = ''
    l=0
    while(l<len(lista)):
      for p in range(0,len(pdf.pages)):
        pagina = pdf.pages[p]
        rects = pagina.rects
        for c in range(0,len(pagina.chars)):
          if(l+1==len(lista)):
            if(pagina.chars[c]['page_number']==lista[l].page):
              if(pagina.chars[c]['y1']<lista[l].y0):
                for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y0']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
                temp=temp+pagina.chars[c]['text']
            elif(pagina.chars[c]['page_number']>lista[l].page):
              for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y0']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
              temp=temp+pagina.chars[c]['text']
          elif(pagina.chars[c]['page_number']>=lista[l].page and pagina.chars[c]['page_number']<=lista[l+1].page):
            if(pagina.chars[c]['page_number']==lista[l].page and pagina.chars[c]['page_number']==lista[l+1].page):
              if(pagina.chars[c]['y1']<lista[l].y0 and pagina.chars[c]['y0']>lista[l+1].y1):
                for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y0']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
                temp = temp + pagina.chars[c]['text']
            elif(pagina.chars[c]['page_number']==lista[l].page and pagina.chars[c]['page_number']<lista[l+1].page):
              if(pagina.chars[c]['y1']<lista[l].y0):
                for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y0']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
                temp = temp + pagina.chars[c]['text']
            elif(pagina.chars[c]['page_number']>lista[l].page and pagina.chars[c]['page_number']<lista[l+1].page):
              for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y0']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
              temp=temp+pagina.chars[c]['text']
            elif(pagina.chars[c]['page_number']>lista[l].page and pagina.chars[c]['page_number']==lista[l+1].page):
              if(pagina.chars[c]['y0']>lista[l+1].y1):
                for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y0']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
                temp=temp+pagina.chars[c]['text']
          elif(temp!=''):
            if('*** *** ***' in  temp):
              temp = temp.split('*** *** ***')
            contexto.append(temp)
            contexto[-1] = Contexto(lista[l].doc,l,temp)
            temp=''
      if(temp!=""):
        if('*** *** ***' in  temp):
              temp = temp.split('*** *** ***')
        contexto.append(temp)
        contexto[-1] = Contexto(lista[l].doc,l,temp)
        temp=''
      l+=1
    return contexto
