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
        # define as snippets como strings
        self.setSnippetsStr()




        meioDaSaida = ''
        # obtem o conteudo dos arquivos finais
        # na forma de iterator
        snippetsFilesContent = self.getSnippetsFilesContent()
        # salva o arquivo final
        destFolder = self.parametros['dest'].parents[0]
        destFileBaseName = os.path.basename(filePath).partition('.')[0]+'.sublime-completions'
        destFile = destFolder / destFileBaseName
        reFuncName = re.compile(r'\s*\|\s*')
        for funcNames, CDATA, comentario in snippetsFilesContent:
            CDATA = CDATA.replace('\\$', '\\\\$')

            for funcName in reFuncName.split(funcNames):
                if comentario == '':
                    comentario = funcName


                print('Snippet   : '+funcName+'.sublime-snippet')
                print('CDATA     : '+CDATA)
                print('Comentario: '+comentario+'\n\n')
                meioDaSaida += '\t\t{ "trigger": "'+funcName+'\\t'+comentario+'", "contents": "'+CDATA+'" },\n'




        # após feito a string meioDaSaida
        with open(str(destFile), 'w', encoding='utf-8') as file:
            file.write('''{
\t"scope": "'''+self.parametros['scope']+'''",

\t"completions":
\t[
'''+meioDaSaida+'''\t]
}''')





    def setParametros(self):
        # todas as linhas que começam com @
        linhasComParametros = [linha for linha in self.fileLines if linha[0] == '@']


        # define os valores do parametro
        for linha in linhasComParametros:
            paramName, paramValue = re.search(r'@(\w+)\s*\:\s*(.*)', linha).groups()
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
            isNormal = True if re.match(r'^[^\s\(\)]+\s{4,}', snippetStr) else False
            if isNormal:
                yield from self.getSnippetsNormal(snippetStr)
            else:
                yield from self.getSnippetsLikeC(snippetStr)




    def getSnippetsLikeC(self, snippetStr):
        # os parametros são o último "(" e o primeiro ")"
        ultimoParantAberto = snippetStr.rindex("(")
        primeiroParentFechado = snippetStr.index(")")
        params = snippetStr[ultimoParantAberto+1:primeiroParentFechado]


        # obtendo o nome da função
        primeiroParentAberto = snippetStr.index("(")
        funcNames = snippetStr[0:primeiroParentAberto]



        

        # comentario
        comentarioIndex = snippetStr.find("//")
        if comentarioIndex == -1:
            comentario = funcNames
        else:
            comentario = snippetStr[comentarioIndex+2:].strip()
        


        # inicializa CDATA
        if params == '':
            CDATA = funcNames+'()'
        else:
            paramSplitted = re.split(r'\s*,\s*', params)
            # rearranja os parametros cortados
            i = 0
            CDATA = funcNames+'('
            hasIgual = False
            for param in paramSplitted:

                if param == '*':
                    # nao processa parametros com *
                    continue

                if param.find('=') != -1:
                    # se n coloquei o igual, coloco agr
                    if not hasIgual:
                        endCDATA = CDATA[-2:]

                        if endCDATA != ', ':
                            # termina com (
                            CDATA = CDATA+'${'+str(i+1)+':'
                        else:
                            CDATA = CDATA[:-2]+'${'+str(i+1)+':, '

                    hasIgual = True

                    # agr eu corto a parte que tem igual
                    key, val = re.findall(r'([\w\*]+)=(.*)', param)[0]
                    CDATA += '${%d:%s=${%d:%s}}, ' % (i+2, key, i+3, val)
                    i += 1

                else:
                    CDATA += '${%d:%s}, ' % (i+1, param)

                i += 1

            terminate = ')' if not hasIgual else '})'
            CDATA = CDATA[:-2]+terminate





        yield funcNames, CDATA, comentario




    def getSnippetsNormal(self, snippetStr):
        elems = re.split(r'\s{4,}', snippetStr)
        # o comentário é opicional
        comentario = elems[2] if len(elems) == 3 else elems[0]
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
