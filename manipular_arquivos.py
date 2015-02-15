#!/usr/bin/python
# coding:utf-8
import json
from os import listdir, rename, makedirs
from os.path import isfile, join, exists
import datetime
import shutil


def copiar_arquivo(pasta_e_arquivo_local,pasta_destino,nome_arquivo):
    
    if nome_arquivo:
        destino = pasta_destino + nome_arquivo
    else:
        destino = pasta_destino
    
    shutil.copy2(pasta_e_arquivo_local, destino)
    

def criar_pastas(pastas):
    
    for nome_pasta in pastas:
        if not exists(nome_pasta):
            makedirs(nome_pasta)


def pastas_ambiente():
    pastas = [  "logs",
                "itens_rastreados",
                "classificadores_nltk",
                "itens_rastreados/modelos",
                "itens_rastreados/item_semente",
                "itens_rastreados/modelos/modelo_usuario",
                "itens_rastreados/modelos/modelo_usuario/agendados",
                "itens_rastreados/modelos/modelo_usuario/finalizados",
                "itens_rastreados/modelos/modelo_usuario/processados",
                "itens_rastreados/modelos/modelo_usuario/analisar",
                "itens_rastreados/modelos/modelo_usuario/modelos_sem_identificador_original"]
    criar_pastas(pastas)

def mover_arquivo(arquivo,pasta_origem, pasta_destino):
    origem = pasta_origem + arquivo
    destino = pasta_destino + arquivo
    rename(origem, destino)

def recuperar_arquivos_pastas(pastas,extensao):
    arquivos = []
    for pasta in pastas:
        path_pasta = pasta[0] + pasta[1]
        arquivos_pasta = [ f for f in listdir(path_pasta) if isfile(join(path_pasta,f)) ]

        for arquivo_pasta in arquivos_pasta: 
            if arquivo_pasta not in arquivos:
                if arquivo_pasta.endswith(extensao):
                    arquivos.append(path_pasta +'/'+ arquivo_pasta)
                    print 'adicionado aos arquivos ' + str(len(arquivos))
    return arquivos
    
def recuperar_identificador_arquivos(arquivos):
    arquivo_versao = []
    for arquivo in arquivos:
        arquivo_versao.append(int(arquivo.split("/")[1].split("_")[0]))
    arquivo_versao.sort()
    
    return arquivo_versao
    
def recuperar_identificador_arquivo_mais_recente(arquivos):
    return max(arquivos)

def recuperar_arquivo_mais_recente(arquivos):
    arquivos.sort()
    return arquivos[-1]
    
def recuperar_arquivo_anterior_ao_mais_recente(arquivos):
    arquivos.remove(max(arquivos))
    arquivos.sort()
    return arquivos[-1]
    
def recuperar_usuarios_arquivo(arquivo,usuarios,usuarios_em_modelos_criados):

    for usuario in arquivo['usuarios']:
        if usuario not in usuarios:
            if usuario not in usuarios_em_modelos_criados:
                usuarios.append(usuario)
                print 'usuarios adicionados - ' + str(len(usuarios))
            else:
                print 'usuario previamente no modelo ' + usuario
        else:
            print 'usuario adicionado anteriormente ' + usuario
    return usuarios

def gerar_arquivo(nome_arquivo,conteudo,pasta):
    folder = pasta + '/'
    filename = folder + nome_arquivo + '.json'
    with open(filename, 'wb') as fp:
        json.dump(conteudo, fp)