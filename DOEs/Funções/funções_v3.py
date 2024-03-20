import PyPDF2 #instalar com pip (FORA DE USO)
import pdfpumbler # instalar com pip

class Data: #Informações sobre data encontrada num DOE
  def __init__(self, dia, doc, pag, frase):
    self.dia = dia
    self.doc = doc
    self.pag = pag
    self.frase = frase

class Orgaos: #Órgãos no documento
  def __init__(self, nome, doc, page, y0, y1):
    self.nome = nome
    self.doc = doc
    self.page = page
    self.y0 = y0
    self.y1 = y1

class Contexto: #Texto entre órgãos de um documento
  def __init__(self, nome, doc, texto, y1, page1, y0, page2):
    self.nome = nome
    self.doc = doc
    self.texto = texto
    self.y1 = y1
    self.page1 = page1
    self.y0 = y0
    self.page2 = page2

#Busca por datas por extenso e resumida alocando em um vetor com todas as datas e identificação da data por documento
def extrair_data(pdf_files):
  datas = []
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

#Extrair os Órgãos de um DOE
def extrair_orgaos_PDF(pdf_files):
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
            if('(' not in temp or ')' not in temp):
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


#Extrai texto presente entre a lista de órgãos resultado da função:extrair_orgaos_PDF
def extrair_texto_entre_orgaos(lista):
  contexto = []
  with pdfplumber.open(lista[0].doc) as pdf:
    temp = ''
    l=0
    while(l<len(lista)):
      y1=0
      page1=0
      y0=0
      page2=0
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
                if(y1==0):
                  y1=pagina.chars[c]['y1']
                  page1=pagina.chars[c]['page_number']
                temp=temp+pagina.chars[c]['text']
                y0=pagina.chars[c]['y0']
                page2=pagina.chars[c]['page_number']
            elif(pagina.chars[c]['page_number']>lista[l].page):
              for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y0']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
              if(y1==0):
                y1=pagina.chars[c]['y1']
                page1=pagina.chars[c]['page_number']
              temp=temp+pagina.chars[c]['text']
              y0=pagina.chars[c]['y0']
              page2=pagina.chars[c]['page_number']
          elif(pagina.chars[c]['page_number']>=lista[l].page and pagina.chars[c]['page_number']<=lista[l+1].page):
            if(pagina.chars[c]['page_number']==lista[l].page and pagina.chars[c]['page_number']==lista[l+1].page):
              if(pagina.chars[c]['y1']<lista[l].y0 and pagina.chars[c]['y0']>lista[l+1].y1):
                for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y1']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
                if(y1==0):
                  y1=pagina.chars[c]['y1']
                  page1=pagina.chars[c]['page_number']
                temp = temp + pagina.chars[c]['text']
                y0=pagina.chars[c]['y0']
                page2=pagina.chars[c]['page_number']
            elif(pagina.chars[c]['page_number']==lista[l].page and pagina.chars[c]['page_number']<lista[l+1].page):
              if(pagina.chars[c]['y1']<lista[l].y0):
                for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y1']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
                if(y1==0):
                  y1=pagina.chars[c]['y1']
                  page1=pagina.chars[c]['page_number']
                temp = temp + pagina.chars[c]['text']
                y0=pagina.chars[c]['y0']
                page2=pagina.chars[c]['page_number']
            elif(pagina.chars[c]['page_number']>lista[l].page and pagina.chars[c]['page_number']<lista[l+1].page):
              for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y1']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
              if(y1==0):
                y1=pagina.chars[c]['y1']
                page1=pagina.chars[c]['page_number']
              temp=temp+pagina.chars[c]['text']
              y0=pagina.chars[c]['y0']
              page2=pagina.chars[c]['page_number']
            elif(pagina.chars[c]['page_number']>lista[l].page and pagina.chars[c]['page_number']==lista[l+1].page):
              if(pagina.chars[c]['y0']>lista[l+1].y1):
                for R in range(0,len(rects)):
                  if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y1']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
                    pagina.chars[c]['text'] = ''
                if(y1==0):
                  y1=pagina.chars[c]['y1']
                  page1=pagina.chars[c]['page_number']
                temp=temp+pagina.chars[c]['text']
                y0=pagina.chars[c]['y0']
                page2=pagina.chars[c]['page_number']
          elif(temp!=''):
            if('*** *** ***' in  temp):
              temp = temp.split('*** *** ***')
            contexto.append(temp)
            contexto[-1] = Contexto(lista[l].nome,lista[l].doc,temp,y1,page1,y0,page2)
            temp=''
      if(temp!=""):
        if('*** *** ***' in  temp):
              temp = temp.split('*** *** ***')
        contexto.append(temp)
        contexto[-1] = Contexto(lista[l].nome,lista[l].doc,temp,y1,page1,y0,page2)
        temp=''
      l+=1
    return contexto

#Busque todas as palavras em negrito dentro da lista resultado da função:extrair_texto_entre_orgaos
def palavras_negrito(contexto):
  palavrasnegrito = []
  tempnegrito = []
  temp = ''
  X = 0
  for Z in range(0,len(contexto)):
    if(X!=Z):
      X=Z
      palavrasnegrito.append(tempnegrito)
      tempnegrito = []
    with pdfplumber.open(contexto[Z].doc) as pdf:
      for P in range(contexto[Z].page1-1,contexto[Z].page2):
        texto = pdf.pages[P]
        for c in range(0,len(texto.chars)):
          if('Bold' in texto.chars[c]['fontname'] and texto.chars[c]['page_number']>=contexto[Z].page1 and texto.chars[c]['page_number']<=contexto[Z].page2):
            if(texto.chars[c]['page_number']==contexto[Z].page1 and texto.chars[c]['page_number']<contexto[Z].page2 and texto.chars[c]['y1']<=contexto[Z].y1):
              temp = temp + texto.chars[c]['text']
            elif(texto.chars[c]['page_number']>contexto[Z].page1 and texto.chars[c]['page_number']<contexto[Z].page2):
              temp = temp + texto.chars[c]['text']
            elif(texto.chars[c]['page_number']>contexto[Z].page1 and texto.chars[c]['page_number']==contexto[Z].page2 and texto.chars[c]['y0']>=contexto[Z].y0):
              temp = temp + texto.chars[c]['text']
            elif(contexto[Z].page1==contexto[Z].page2 and contexto[Z].page1==texto.chars[c]['page_number'] and texto.chars[c]['y1']<=contexto[Z].y1 and texto.chars[c]['y0']>=contexto[Z].y0):
              temp = temp + texto.chars[c]['text']
          elif(temp != ''):
            tempnegrito.append(temp)
            temp = ''
  if(X!=0):
      X=0
      palavrasnegrito.append(tempnegrito)
      tempnegrito = []
  return palavrasnegrito

#Retorna uma string sem acentos
def limpar_acentos(pagestring): #Tirar acentos de uma string
  Aacentuado = ['À','Á','Ã','Â']
  aacentuado = ['à','á','â','ã']
  Eacentuado = ['È','É','Ẽ','Ê']
  eacentuado = ['è','é','ê','ẽ']
  Iacentuado = ['Í','Ì','Î','Ĩ']
  iacentuado = ['ì','í','î','ĩ']
  Oacentuado = ['Ò','Ó','Ô','Õ']
  oacentuado = ['ò','ó','ô','õ']
  Uacentuado = ['Ù','Ú','Û','Ũ']
  uacentuado = ['ù','ú','û','ũ']
  for i in range(0,len(pagestring)):
    c=0
    while(c<len(pagestring)):
      if(pagestring[c] in Aacentuado):
        pagestring = pagestring.replace(pagestring[c],'A')
      elif(pagestring[c] in aacentuado):
        pagestring = pagestring.replace(pagestring[c],'a')
      elif(pagestring[c] in Eacentuado):
        pagestring = pagestring.replace(pagestring[c],'E')
      elif(pagestring[c] in eacentuado):
        pagestring = pagestring.replace(pagestring[c],'e')
      elif(pagestring[c] in Iacentuado):
        pagestring = pagestring.replace(pagestring[c],'I')
      elif(pagestring[c] in iacentuado):
        pagestring = pagestring.replace(pagestring[c],'i')
      elif(pagestring[c] in Oacentuado):
        pagestring = pagestring.replace(pagestring[c],'O')
      elif(pagestring[c] in oacentuado):
        pagestring = pagestring.replace(pagestring[c],'o')
      elif(pagestring[c] in Uacentuado):
        pagestring = pagestring.replace(pagestring[c],'U')
      elif(pagestring[c] in uacentuado):
        pagestring = pagestring.replace(pagestring[c],'u')
      c+=1
  return pagestring
