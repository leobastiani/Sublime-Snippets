#!python3

import sys
import os
import re
import glob
from pathlib import Path






class Snippets:
    '''classe com o arquivo de leitura'''

    filePath = None # arquivo que será lido, com todas as informações
    fileLines = [] # todo o conteúdo separado por linhas
    parametros = { # parametros do filePath lidos com @param: alguma coisa
        'dest': None,
        'scope': None,
    }
    snippetsStr = [] # lista com todas as listas com comandos





    def __init__(self, filePath):
        self.filePath = filePath
        with open(filePath, 'r', encoding='utf-8') as file:
            self.fileLines = [linha.strip() for linha in file.readlines() if linha != '\n' and linha != '']



        # já leu o arquivo, agora analisa suas linhas
        # e obtem os parametros
        self.setParametros()
        # define o destino como classe de path
        self.parametros['dest'] = Path(self.parametros['dest'])
        # já sou capaz de criar o diretório final
        try:
            os.makedirs(str(self.parametros['dest']))
        except:
            print('Diretório "%s" já existe.' % str(self.parametros['dest']))

        # define as snippets como strings
        self.setSnippetsStr()


        # esvazia o diretorio de saída
        for file in glob.glob(str(self.parametros['dest'] / '*.sublime-snippet')):
            os.remove(file)



        # obtem o conteudo dos arquivos finais
        # na forma de iterator
        snippetsFilesContent = self.getSnippetsFilesContent()
        reFuncName = re.compile(r'\s*\|\s*')
        for funcNames, CDATA, comentario in snippetsFilesContent:
            CDATA = CDATA.replace('\\n', '\n') # troca o \n em CDATA
            for funcName in reFuncName.split(funcNames):

                if comentario == '':
                    comentario = funcName


                fileDestContent = '''<!-- THIS WAS AUTOMATED GENERATED -->
    <snippet>
        <description>'''+comentario+'''</description>
        <content><![CDATA['''+CDATA+''']]></content>
        <tabTrigger>'''+funcName+'''</tabTrigger>
        <scope>'''+self.parametros['scope']+'''</scope>
    </snippet>'''



                # salva no arquivo final
                fileDest = self.parametros['dest'] / (funcName+'.sublime-snippet')
                with open(str(fileDest), 'w', encoding='utf-8') as file:
                    print('Snippet   : '+funcName+'.sublime-snippet')
                    print('CDATA     : '+CDATA)
                    print('Comentario: '+comentario+'\n\n')
                    file.write(fileDestContent)






    def setParametros(self):
        # todas as linhas que começam com @
        linhasComParametros = [linha for linha in self.fileLines if linha[0] == '@']


        # define os valores do parametro
        for linha in linhasComParametros:
            paramName, paramValue = re.search(r'\@(\w+)\s*\:\s*(.*)', linha).groups()
            self.parametros[paramName] = paramValue

        # se um dos parametros for None
        # nao pode permitir
        if None in self.parametros.values():
            raise SyntaxError("Nem todos os parametros foram definidos.")
        




    def setSnippetsStr(self):
        # simplesmente começa com uma palavra
        reIsSnippet = re.compile(r'\w+.*')
        linhasComSnippets = [linha for linha in self.fileLines if reIsSnippet.match(linha)]
        # define os snippets de string
        self.snippetsStr = linhasComSnippets




    def getSnippetsFilesContent(self):
        '''retorna um iterator da forma
        (funcNames, CDATA, comentario)'''
        # define isNormal para saber ql funcão deve chamar
        for snippetStr in self.snippetsStr:
            isNormal = True if re.match(r'^[^\(]+\s{4,}', snippetStr) else False
            if isNormal:
                yield from self.getSnippetsNormal(snippetStr)
            else:
                yield from self.getSnippetsLikeC(snippetStr)




    def getSnippetsLikeC(self, snippetStr):
        # os parametros são o último "(" e o primeiro ")"
        ultimoParentAberto = snippetStr.rindex("(")
        primeiroParentFechado = snippetStr.index(")")
        params = snippetStr[ultimoParentAberto+1:primeiroParentFechado]


        # obtendo o nome da função
        primeiroParentAberto = snippetStr.index("(")
        funcNames = snippetStr[0:primeiroParentAberto]
        

        # comentario
        comentarioIndex = snippetStr.find("//")
        if comentarioIndex == -1:
            comentario = '' # se não há comentario, devolve vazio
        else:
            comentario = snippetStr[comentarioIndex+2:].strip()
        


        # inicializa CDATA
        if params == '':
            CDATA = funcNames+'()'
        else:
            paramSplitted = re.split(r'\s*,\s*', params)
            # rearranja os parametros cortados
            for i, param in enumerate(paramSplitted):
                paramSplitted[i] = '${%d:%s}' % (i+1, param)
            CDATA = funcNames+'('+', '.join(paramSplitted)+')'



        yield funcNames, CDATA, comentario




    def getSnippetsNormal(self, snippetStr):
        elems = re.split(r'\s{4,}', snippetStr)
        # o comentário é opicional
        comentario = elems[2] if len(elems) == 3 else ''
        yield elems[0], elems[1], comentario







def obterArquivoPorParametro():
    # define o arquivo que será utilizado na classe Snippets
    if len(sys.argv) != 2:
        raise IOError("Insira um arquivo no parâmetro de entrada.")



    arquivo = sys.argv[1]
    if os.path.exists(arquivo):
        # já encontro o arquivo, só executar
         return arquivo

    # segunda tentativa do arquivo
    arquivo = glob.glob(arquivo+'.*')[0]
    if os.path.exists(arquivo):
        return arquivo


    raise IOError('Arquivo "'+sys.argv[1]+'" não encontrado.')








def main():

    Snippets(obterArquivoPorParametro())




if __name__ == '__main__':
    main()
