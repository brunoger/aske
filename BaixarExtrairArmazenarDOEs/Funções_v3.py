import pdfplumber

class Orgaos:
  def __init__(self, nome, doc, page, y0, y1):
    self.nome = nome
    self.doc = doc
    self.page = page
    self.y0 = y0
    self.y1 = y1

class Conteudo:
  def __init__(self, nome, doc, publicacao, y1, page1, y0, page2):
    self.nome = nome
    self.doc = doc
    self.publicacao = publicacao
    self.y1 = y1
    self.page1 = page1
    self.y0 = y0
    self.page2 = page2

class Publicacao:
  def __init__(self, texto, page):
    self.texto = texto
    self.page = page

#Extrai os órgãos presentes de um DOE
def extrair_orgaos_PDF(pdf_files):
  lista = []
  listaadic = []
  with pdfplumber.open(pdf_files) as pdf:
    for P in range(0,len(pdf.pages)):
      pagina = pdf.pages[P]
      i=0
      while(i<len(pagina.rects)):
        temp=''
        for w in range(0,len(pagina.chars)):
          if(pagina.chars[w]['x0']>=pagina.rects[i]['x0'] and pagina.chars[w]['x1']<=pagina.rects[i]['x1'] and pagina.chars[w]['y1']>=pagina.rects[i]['y0'] and pagina.chars[w]['y1']<=pagina.rects[i]['y1']):
            temp=temp+pagina.chars[w]['text']
            page = pagina.chars[w]['page_number']
            y0 = pagina.chars[w]['y0']
            y1 = pagina.chars[w]['y1']
          if('Bold' not in pagina.chars[w]['fontname'] and pagina.chars[w]['x0']>=pagina.rects[i]['x0'] and pagina.chars[w]['x1']<=pagina.rects[i]['x1'] and pagina.chars[w]['y1']>=pagina.rects[i]['y0'] and pagina.chars[w]['y1']<=pagina.rects[i]['y1']):
            temp=''
            break
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
        i+=1
  return lista

  #Extrai texto presente entre os órgãos de um documento
def extrair_texto_entre_orgaos(lista):
  contexto = []
  publicacoes = []
  with pdfplumber.open(lista[0].doc) as pdf:
    temp = ''
    l=0
    while(l<len(lista)):
      publicpage = 0
      y1=0
      page1=0
      y0=0
      page2=0
      for p in range(lista[l].page-1,len(pdf.pages)):
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
                if('*** *** ***' in temp):
                  temp = temp.split('*** *** ***')
                  publicacoes.append(temp[0])
                  temp=''
                  publicacoes[-1] = Publicacao(publicacoes[-1],pagina.chars[c]['page_number'])
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
              if(publicpage==0):
                  publicpage = pagina.chars[c]['page_number']
              if('*** *** ***' in temp):
                temp = temp.split('*** *** ***')
                publicacoes.append(temp[0])
              temp=''
              publicacoes[-1] = Publicacao(publicacoes[-1],publicpage)
              publicpage=0
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
                if(publicpage==0):
                  publicpage = pagina.chars[c]['page_number']
                if('*** *** ***' in temp):
                  temp = temp.split('*** *** ***')
                  publicacoes.append(temp[0])
                  temp=''
                  publicacoes[-1] = Publicacao(publicacoes[-1],publicpage)
                  publicpage=0
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
                if(publicpage==0):
                  publicpage = pagina.chars[c]['page_number']
                if('*** *** ***' in temp):
                  temp = temp.split('*** *** ***')
                  publicacoes.append(temp[0])
                  temp=''
                  publicacoes[-1] = Publicacao(publicacoes[-1],publicpage)
                  publicpage=0
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
              if(publicpage==0):
                  publicpage = pagina.chars[c]['page_number']
              if('*** *** ***' in temp):
                temp = temp.split('*** *** ***')
                publicacoes.append(temp[0])
                temp=''
                publicacoes[-1] = Publicacao(publicacoes[-1],publicpage)
                publicpage=0
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
                if(publicpage==0):
                  publicpage = pagina.chars[c]['page_number']
                if('*** *** ***' in temp):
                  temp = temp.split('*** *** ***')
                  publicacoes.append(temp[0])
                  temp=''
                  publicacoes[-1] = Publicacao(publicacoes[-1],publicpage)
                  publicpage=0
                y0=pagina.chars[c]['y0']
                page2=pagina.chars[c]['page_number']
          elif(temp!=''):
            publicacoes.append(temp)
            publicacoes[-1] = Publicacao(publicacoes[-1],publicpage)
            temp=''
            contexto.append('')
            contexto[-1] = Conteudo(lista[l].nome,lista[l].doc,publicacoes,y1,page1,y0,page2)
            publicacoes = []
      if(temp!=''):
        publicacoes.append(temp)
        publicacoes[-1] = Publicacao(publicacoes[-1],publicpage)
        temp=''
        contexto.append('')
        contexto[-1] = Conteudo(lista[l].nome,lista[l].doc,publicacoes,y1,page1,y0,page2)
        publicacoes = []
      l+=1
    return contexto

#Busca todas as palavras em negrito dentro da lista do extrair_texto_entre_orgaos
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
