#!/usr/bin/python
# coding:utf-8
import json
from os import listdir
from os.path import isfile, join
import datetime
from  manipular_arquivos import *
from busca import Nucleo_Busca
from random import choice
from time import sleep, time
from os import path
import threading

class Pool_Requisicao():
    
    def __init__(self, **kwargs):
        self.theads_requisicoes = kwargs.get('theads_requisicoes',1)
        self.espera_proxima_requisicao_seg = kwargs.get('espera_proxima_requisicao_seg',0)
        self.quantidade_requisicao_troca_IP = kwargs.get('quantidade_requisicao_troca_IP',10)

    def daemon(self):
        self.requisicao_modelo_usuario()

    def non_daemon(self):
        for x in range(0, self.theads_requisicoes):
            d = threading.Thread(name='daemon', target=self.daemon)
            d.setDaemon(True)
            d.start()
        d.join()


    def solicitar_requisicao_modelo_usuario(self):
        t = threading.Thread(name='non-daemon', target=self.non_daemon)
        t.setDaemon(True)
        t.start()
        t.join()


    def requisicao_modelo_usuario(self):
        inicio_script = time()
        conta_usuario = 0

        pasta_agendados = [("itens_rastreados/modelos/modelo_usuario/", "agendados"),]
        pasta_processados = [("itens_rastreados/modelos/modelo_usuario/", "processados"),
                             ("itens_rastreados/modelos/modelo_usuario/", "finalizados")]
        extensao = '.json'
        caminho_arquivos_processados = 'itens_rastreados/modelos/modelo_usuario/processados/'
        caminho_arquivos_finalizados = 'itens_rastreados/modelos/modelo_usuario/finalizados/'

        arquivos_agendados = recuperar_arquivos_pastas(pasta_agendados,extensao)
        arquivos_processados = recuperar_arquivos_pastas(pasta_processados,extensao)
        esqueleto_modelo_usuario = {
                                        'status_arquivo': '',
                                        'data_criacao' : '',
                                        'data_finalizacao': '',
                                        'usuario' : '',

                                   }

        nucleo = Nucleo_Busca(espera_proxima_requisicao_seg = self.espera_proxima_requisicao_seg,
                              quantidade_requisicao_troca_IP = self.quantidade_requisicao_troca_IP,)

        for arquivo_agendado in arquivos_agendados:
            usuarios_modelo = json.load(open(arquivo_agendado))  
            manipula_usuarios_modelo = usuarios_modelo[:]      
            for usuario in usuarios_modelo:
                conta_usuario += 1
                usuario = choice(manipula_usuarios_modelo)
                print str(conta_usuario) + ' ' + usuario
                manipula_usuarios_modelo.remove(usuario)
                arquivo_usuario = usuario + extensao
                caminho_e_arquivo_processado = caminho_arquivos_processados + arquivo_usuario
                caminho_e_arquivo_finalizado = caminho_arquivos_finalizados + arquivo_usuario
                if path.isfile(caminho_e_arquivo_processado) == False and path.isfile(caminho_e_arquivo_finalizado) == False: 
                    esqueleto_modelo_usuario['status_arquivo'] = 'novo'
                    esqueleto_modelo_usuario['usuario'] = usuario
                    esqueleto_modelo_usuario['data_criacao'] = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")
                    gerar_arquivo(usuario,esqueleto_modelo_usuario,caminho_arquivos_processados)

                    dicionario_usuario = json.load(open(caminho_e_arquivo_processado))
                    dicionario_usuario['reviews'] = nucleo.montar_modelo_reviews_usuario(usuario,'imdb')
                    dicionario_usuario['status_arquivo'] = 'finalizado'
                    dicionario_usuario['data_finalizacao'] = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S")
                    gerar_arquivo(usuario,dicionario_usuario,caminho_arquivos_processados)

                    mover_arquivo(arquivo_usuario, caminho_arquivos_processados, caminho_arquivos_finalizados)
                else:
                    print 'arquivo existente'


        fim_script = time()
        tempo_decorrido  = str(datetime.timedelta(seconds=fim_script - inicio_script))

        print 'Processo Realizado em ' + tempo_decorrido