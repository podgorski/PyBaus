#!/usr/bin/python
# coding:utf-8
import json
from os import listdir
from os.path import isfile, join
import datetime
from  manipular_arquivos import *
from random import choice
from time import sleep, time
from os import path


class Nucleo_Estruturacao():
    
    def __init__(self, **kwargs):
        pastas_ambiente()
        self.itens_por_modelo = kwargs.get('itens_por_modelo',100)
        self.complemento_nome_arquivo = kwargs.get('complemento_nome_arquivo','')
        
    
    def alterar_identidade_real_do_usuario(self,prefixo,quantidade_caracteres,numeracao_inicial,pasta,pasta_destino):
        
        numeracao = numeracao_inicial
        extensao = ".json"
        arquivos_modelo = recuperar_arquivos_pastas(pasta,extensao)
        
        for arquivo in arquivos_modelo:
            identificador = str(prefixo) + str(numeracao).zfill(quantidade_caracteres) 
            identificador_arquivo = identificador + extensao 
            copiar_arquivo(arquivo,pasta_destino,identificador_arquivo)
            print identificador
            numeracao += 1
            
            pasta_destino_e_arquivo = pasta_destino + identificador_arquivo
            
            
            with open(pasta_destino_e_arquivo, "r+") as jsonFile:
                data = json.load(jsonFile)

                tmp = data['usuario']
                data['usuario'] = identificador

                jsonFile.seek(0)  # rewind
                jsonFile.write(json.dumps(data))
                jsonFile.truncate()

    
    def organizar_modelos_agendados(self):
        pastas = [("itens_rastreados/", "item_semente")]
        extensao = ".json"
        usuarios = []
        total_modelos_criados_execucao = 0
        arquivos_modelo = []
        usuarios_modelo = []
        usuarios_em_modelos_criados = []

        pasta = [("itens_rastreados/modelos/modelo_usuario/", "agendados"),]
        arquivos_modelo = recuperar_arquivos_pastas(pasta,extensao)

        for arquivo_modelo in arquivos_modelo:
            dicionario_arquivo_modelo = json.load(open(arquivo_modelo))

            for usuario in dicionario_arquivo_modelo:
                if usuario not in usuarios_em_modelos_criados:
                    usuarios_em_modelos_criados.append(str(usuario))
                    print 'usuarios adicionados previamente aos modelos ' + str(len(usuarios_em_modelos_criados)) 

        for arquivo in recuperar_arquivos_pastas(pastas,extensao):
            dicionario_arquivo = json.load(open(arquivo))
            usuarios = recuperar_usuarios_arquivo(dicionario_arquivo,usuarios,usuarios_em_modelos_criados)

        conta_item = 0
        for usuario in usuarios:
            conta_item +=1
            usuarios_modelo.append(usuario)
            if conta_item == self.itens_por_modelo:
                print 'total ' + str(len(usuarios_modelo))
                total_modelos_criados_execucao +=1
                aux_nome_modelo = datetime.datetime.now().strftime("%d%m%Y%I%M%S") +'_'+str(total_modelos_criados_execucao)
                gerar_arquivo('modelo' + self.complemento_nome_arquivo + '_' + str(aux_nome_modelo),usuarios_modelo,'itens_rastreados/modelos/modelo_usuario/agendados')
                usuarios_modelo = []
                conta_item = 0

        print 'total ' + str(len(usuarios_modelo))
        if len(usuarios_modelo) > 0:
            total_modelos_criados_execucao +=1
            aux_nome_modelo = datetime.datetime.now().strftime("%d%m%Y%I%M%S") +'_'+str(total_modelos_criados_execucao)
            gerar_arquivo('modelo' + self.complemento_nome_arquivo + '_' + str(aux_nome_modelo),usuarios_modelo,'itens_rastreados/modelos/modelo_usuario/agendados')