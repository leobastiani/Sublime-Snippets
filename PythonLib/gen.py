#!python3



libParaProcessar = [
    'os',
    'os.path',
    're',
    'math',
]




from pyquery import PyQuery as pq
import re
import os

def jQuery(url):
    return pq(url=url)



genStr = ''



for lib in libParaProcessar:

    url = 'https://docs.python.org/3/library/'+lib+'.html'


    if os.path.exists(lib+'.html'):
        with open(lib+'.html', 'r', encoding='utf-8') as file:
            j = pq(file.read())
    else:
        j = jQuery(url)



    # primeiros vamos processar as contantes e dps as funções
    for elem in j('dl.data'):
        # agora eu tenho q pegar
        # .descclassname e .descname
        descclassnames = pq(elem).find('.descclassname')
        for i, descclassname in enumerate(descclassnames):

            descname = pq(elem).find('.descname').eq(i)

            # exemplo = os.name
            name = pq(descclassname).text() + pq(descname).text()
            print("name:", name)
            # nomes coletados

        

    # agora coleto as funcoes
    fns = j('dl.function')
    for elem in fns:

        # exemplo name = name: os. ctermid ( ) ¶ Return the filename corresponding to the controlling terminal of the process. Availability: Unix.
        allFn = pq(elem).text().split(') ')
        allFn.pop()

        for fn in allFn:

            # se n começar com a lib, n processa
            if re.search(r'^'+lib+r'\.', fn) is None:
                continue

            # exemplo = os. getenv ( key , default=None )
            fn = fn+')'

            # exemplo =  os.getenv(key , default=None)
            fn = re.sub(r'(\w+)\.\s*(\w+)\s*\(\s*(.*?)\s*\)', r'\1.\2(\3)', fn)

            # exemplo = os.getenv(key, default=None)
            fn = re.sub(r'\s*,\s*', ', ', fn)
            print("fn:", fn)
            genStr += fn+'\n'





    with open(lib+'.html', 'w', encoding='utf-8') as file:
        file.write(pq(j).html())




# gera o Python.txt
with open('Python.txt', 'w', encoding='utf-8') as ptxt:
    with open('..\\Python.txt', 'r', encoding='utf-8') as ptxt2:
        ptxt.write(ptxt2.read()+'\n//GEN.py\n')


    ptxt.write(genStr)