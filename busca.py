# coding:utf-8
import requests
from bs4 import BeautifulSoup
from time import sleep, time
import json
import re
import socket
import socks
import sys
from TorCtl import TorCtl
from datetime import datetime,date,timedelta
from  manipular_arquivos import criar_pastas,pastas_ambiente

class Nucleo_Busca():
    data_atual_formatada = str(date.today()) 
    total_requisicoes_externas = 0
    def __init__(self, **kwargs):
        pastas_ambiente()
        self.espera_proxima_requisicao_seg = kwargs.get('espera_proxima_requisicao_seg',0)
        self.quantidade_requisicao_troca_IP = kwargs.get('quantidade_requisicao_troca_IP',10)
        print "Criando nova instância do Nucleo_Busca | Espera Requisiçao(em seg) = " + str(self.espera_proxima_requisicao_seg)
	
    def __conecta_Tor(self):
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1",9150, True)
        socket.socket = socks.socksocket

    def __solicita_renovar_ip(self):
        socks.setdefaultproxy()
        conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9151, passphrase="your_password")
        conn.send_signal("NEWNYM")
        #conn.close()
        self.__conecta_Tor()
	

    def __cronometro_proxima_requisicao(self,espera_proxima_requisicao_seg):
        for i in range(espera_proxima_requisicao_seg):
            print 'aguardando.... ' + str(i+1) + ' segundo(s)'
            sleep(1)
        
    def __realizar_requisicao(self,**kwargs):
        espera_proxima_requisicao_seg = kwargs.get('espera_proxima_requisicao_seg',self.espera_proxima_requisicao_seg)
        url = kwargs.get('url','')
        
        self.__cronometro_proxima_requisicao(espera_proxima_requisicao_seg)
        if Nucleo_Busca.total_requisicoes_externas % self.quantidade_requisicao_troca_IP == 0:
            self.__gerar_arquivo_log('log_scrapping_'+ self.data_atual_formatada +'.txt','\tTroca de IP Solicitada\n\n') 
            self.__solicita_renovar_ip()
        #resposta_requisicao_ip = requests.get('http://my-ip.heroku.com')
        #resposta_requisicao_ip = resposta_requisicao_ip.text
        #ip = resposta_requisicao_ip
        
        #resposta_requisicao_ip = requests.get('http://www.showmemyip.com/')
        #resposta_requisicao_ip_html = BeautifulSoup(resposta_requisicao_ip.text)
        #ip = resposta_requisicao_ip_html.find("span", id="IPAddress").string
        ip = self.__descobrir_ip()
        try:
            mensagem = str( '\t' + ip + '\t' + str(Nucleo_Busca.total_requisicoes_externas)  +' | '+ str(datetime.now()) + ' | ' + url + '\n')
            self.__gerar_arquivo_log('log_scrapping_'+ self.data_atual_formatada +'.txt',mensagem)  
            resposta_requisicao_completa = requests.get(url)
            self.__gerar_arquivo_log('log_scrapping_'+ self.data_atual_formatada +'.txt','\trecebido em '+ str(datetime.now()) + '\n\n') 
            Nucleo_Busca.total_requisicoes_externas += 1
            resposta_requisicao_html = resposta_requisicao_completa.text
            formatado_soup = BeautifulSoup(resposta_requisicao_html)
            return formatado_soup
        except requests.exceptions.ConnectionError as e:
            mensagem = str(ip + str(datetime.now()) + ' | ' + ' - ' + url + '\n\n')
            self.__gerar_arquivo_log('ERRO_log_'+ self.data_atual_formatada +'.txt',mensagem)
            #quit()

    def __descobrir_ip(self):
	    #resposta_requisicao_ip = requests.get('http://www.showmemyip.com/')
	    #resposta_requisicao_ip_html = BeautifulSoup(resposta_requisicao_ip.text)
	    #resposta_requisicao_ip_html = BeautifulSoup(resposta_requisicao_ip.text)
	    #ip = resposta_requisicao_ip_html.find("span", id="IPAddress").string
	    #print ip
	    #quit()
	    resposta_requisicao_ip = requests.get('http://my-ip.heroku.com')
	    #resposta_requisicao_ip = requests.get('http://www.podgorski.com.br/meu_ip.asp')
	    resposta_requisicao_ip = resposta_requisicao_ip.text
	    ip = resposta_requisicao_ip
	    return ip
           
    def __monta_novo_review_usuario_imdb_v2(self,filme_review, resposta_url_usuario_reviews, contador_filme,base_filme):
        # ur21404273 Teste no filme ur21404273 com 700 Reviews = 
        filme_id_imdb = filme_review.find("a").get('href').split('/')[2]
        filme_titulo = filme_review.find("a").string
        #self.__gerar_arquivo_log('log_scrapping_usuario_'+ self.data_atual_formatada +'.txt','\t' + str(contador_filme + 1) + ' ' + filme_titulo +'(' + filme_id_imdb + ')' + '\n')
        print '\t'+str(contador_filme + 1) + ' ' + filme_titulo +'(' + filme_id_imdb + ')'
        #base_filme = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')
        filme_ratting = base_filme[contador_filme].find_next("img").get('alt')
        filme_review_util = base_filme[contador_filme].find_next("small").string
        filme_opiniao_titulo = base_filme[contador_filme].find_next("b").string
        filme_data_review = base_filme[contador_filme].find_next("b").find_next("small").string
        filme_review_util_positivo = ''
        filme_review_util_total = ''
        if filme_review_util.find('people found the following review useful') != -1:
            if len(filme_review_util) > 0:
                filme_review_util_positivo = filme_review_util.split(' ')[0]
            if len(filme_review_util) > 3:
                filme_review_util_total = filme_review_util.split(' ')[3]
        filme_opiniao = base_filme[contador_filme].find_next("p").prettify()

        return self.__monta_dict_novo_review_usuario(filme_opiniao_titulo = filme_opiniao_titulo,
                                                filme_id = filme_id_imdb,
                                                filme_titulo = filme_titulo,
                                                filme_ratting = filme_ratting,
                                                filme_opiniao = filme_opiniao,
                                                filme_review_util_total = filme_review_util_total,
                                                filme_review_util_positivo = filme_review_util_positivo,
                                                filme_data_review = filme_data_review
        )


    
    def __monta_novo_review_usuario_imdb(self,filme_review, resposta_url_usuario_reviews, contador_filme):
        # ur21404273 Teste no filme ur21404273 com 700 Reviews = 
        filme_id_imdb = filme_review.find("a").get('href').split('/')[2]
        filme_titulo = filme_review.find("a").string
        print '\t'+str(contador_filme + 1) + ' ' + filme_titulo +'(' + filme_id_imdb + ')'
        filme_ratting = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')[contador_filme].find_next("img").get('alt')
        filme_review_util = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')[contador_filme].find_next("small").string
        filme_opiniao_titulo = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')[contador_filme].find_next("b").string
        filme_data_review = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')[contador_filme].find_next("b").find_next("small").string
        filme_review_util_positivo = ''
        filme_review_util_total = ''
        if filme_review_util.find('people found the following review useful') != -1:
            if len(filme_review_util) > 0:
                filme_review_util_positivo = filme_review_util.split(' ')[0]
            if len(filme_review_util) > 3:
                filme_review_util_total = filme_review_util.split(' ')[3]
        filme_opiniao = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')[contador_filme].find_next("p").prettify()
        
        return self.__monta_dict_novo_review_usuario(filme_opiniao_titulo = filme_opiniao_titulo,
                                                filme_id = filme_id_imdb,
                                                filme_titulo = filme_titulo,
                                                filme_ratting = filme_ratting,
                                                filme_opiniao = filme_opiniao,
                                                filme_review_util_total = filme_review_util_total,
                                                filme_review_util_positivo = filme_review_util_positivo,
                                                filme_data_review = filme_data_review
        )
        
    def __monta_novo_review_usuario_rotten(self,filme_review):

        filme_id_rotten = filme_review.find(target='_top').get('href').split('/')[2]
        filme_titulo = filme_review.find(target='_top').get('title')
        filme_ratting = filme_review.find('div','ratingStars').find_next('span')['class'][3]
        filme_opiniao = filme_review.find('p').prettify()

        return self.__monta_dict_novo_review_usuario(
                                                    filme_id = filme_id_rotten,
                                                    filme_titulo = filme_titulo,
                                                    filme_ratting = filme_ratting,
                                                    filme_opiniao = filme_opiniao,
                                                    
        )
    
    #Estrutura Review    
    def __monta_dict_novo_review_usuario(self, **kwargs):
        filme_opiniao_titulo = kwargs.get('filme_opiniao_titulo','')
        filme_id = kwargs.get('filme_id','')
        filme_data_review = kwargs.get('filme_data_review','')
        filme_titulo = kwargs.get('filme_titulo','')
        filme_ratting = kwargs.get('filme_ratting','')
        filme_opiniao = kwargs.get('filme_opiniao','')
        filme_review_util_total = kwargs.get('filme_review_util_total','')
        filme_review_util_positivo = kwargs.get('filme_review_util_positivo','')
        novo_review = {
            'filme_opiniao_titulo' : filme_opiniao_titulo,
            'filme_id': filme_id,
            'filme_data_review': filme_data_review,
            'filme_titulo': filme_titulo,
            'filme_ratting': filme_ratting,
            'filme_opiniao': filme_opiniao,
            'filme_review_util':
                {
                    'total': filme_review_util_total ,
                    'positivo': filme_review_util_positivo
                }
        }
        return novo_review
    
    def montar_modelo_reviews_usuario(self,usuario,recurso):
        
        reviews_modelo_usuario = ""
        if recurso == 'imdb':
            reviews_modelo_usuario = self.montar_modelo_reviews_usuario_imdb(usuario)
        elif recurso == 'imdb_coming_soon':
            reviews_modelo_usuario = self.montar_modelo_reviews_usuario_imdb(usuario)
        return reviews_modelo_usuario
    
    def montar_modelo_reviews_usuario_imdb(self,usuario):
        
        base_url = 'http://www.imdb.com/'
        reviews_modelo_usuario = []
        url_total_reviews_usuario = base_url + 'user/' + usuario + '/comments-index'      
        resposta_url_total_reviews_usuario = self.__realizar_requisicao(url = url_total_reviews_usuario)
        buscar_profundidade_usuario_reviews = resposta_url_total_reviews_usuario.find('small')
        if buscar_profundidade_usuario_reviews is not None:
            buscar_profundidade_usuario_reviews = buscar_profundidade_usuario_reviews.string.split(' ')[0]
            print 'Total de ' + str(buscar_profundidade_usuario_reviews) + ' Reviews'
            url_usuario_reviews = base_url + 'user/' + usuario + '/comments?start=0&count=' + str(buscar_profundidade_usuario_reviews) + '&summary=on&order=date'      
            resposta_url_usuario_reviews = self.__realizar_requisicao(url = url_usuario_reviews)
            filmes_review_usuario = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')
            #print filmes_review_usuario
        
            self.__gerar_arquivo_log('log_scrapping_usuario_'+ self.data_atual_formatada +'.txt', str(usuario) +' | '+ str(buscar_profundidade_usuario_reviews) +' reviews\n')
        
            inicio_composicao_review_usuario = time()
            contador_filme = 0
            for filme_review in filmes_review_usuario:
                if filmes_review_usuario.index(filme_review) == 0:
                    base_filme = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')
                # Removido o index da versao 01, por não trabalhar bem com a duplicidade
                #contador_filme = filmes_review_usuario.index(filme_review)
                print 'contador filme' + str(contador_filme)
                novo_review_modelo_usuario = self.__monta_novo_review_usuario_imdb_v2(filme_review, resposta_url_usuario_reviews, contador_filme, base_filme)
        
                reviews_modelo_usuario.append(novo_review_modelo_usuario)
                contador_filme += 1
            fim_composicao_review_usuario = time()
            tempo_decorrido_composicao_review_usuario  = str(timedelta(seconds=fim_composicao_review_usuario - inicio_composicao_review_usuario))
            self.__gerar_arquivo_log('log_scrapping_usuario_'+ self.data_atual_formatada +'.txt','\t' + 'Tempo de Processamento ' + tempo_decorrido_composicao_review_usuario + '\n')
            print 'Tempo de Processamento ' + tempo_decorrido_composicao_review_usuario
        else:
            self.__gerar_arquivo_log('log_scrapping_usuario_'+ self.data_atual_formatada +'.txt', str(usuario) +' | '+ str(buscar_profundidade_usuario_reviews) +' reviews\n\t' + 'Usuário Não Encontrado \n')
        return reviews_modelo_usuario

    def montar_reviews_usuario(dict_usuarios_reviews):
        
        for usuario in dict_usuarios_reviews['usuarios']:
            #usuario = 'ur2346881'
            print 'IMDB ' + usuario
            self.__gerar_arquivo_log('log_scrapping_'+ self.data_atual_formatada +'.txt','\t' + str(usuario) + '\n')
            if profundidade_busca_usuario_reviews == 0:
                url_total_reviews_usuario = base_url + 'user/' + usuario + '/comments-index'      
                resposta_url_total_reviews_usuario = self.__realizar_requisicao(url = url_total_reviews_usuario)
                buscar_profundidade_usuario_reviews = resposta_url_total_reviews_usuario.find('small').string.split(' ')[0]
            else:
                buscar_profundidade_usuario_reviews = profundidade_busca_usuario_reviews
            url_usuario_reviews = base_url + 'user/' + usuario + '/comments?start=0&count=' + str(buscar_profundidade_usuario_reviews) + '&summary=on&order=date'      
            resposta_url_usuario_reviews = self.__realizar_requisicao(url = url_usuario_reviews)
            filmes_review_usuario = resposta_url_usuario_reviews.find_all(style='background: #eeeeee; clear:both')
            
            contador_filme = 0
            reviews_usuario = []
            for filme_review in filmes_review_usuario:
                novo_review = self.__monta_novo_review_usuario_imdb(filme_review, resposta_url_usuario_reviews, contador_filme)
                contador_filme = contador_filme + 1
                print '---------    ' + str(contador_filme) + '   ----------'
                print novo_review
                reviews_usuario.append(novo_review)
            dict_usuarios_reviews['usuarios'][usuario]['reviews'] = reviews_usuario
            dict_usuarios_reviews['usuarios'][usuario]['total_reviews'] = buscar_profundidade_usuario_reviews
            
    def busca_estruturada(self,filme,recurso):
        
        if recurso == 'imdb':
            self.busca_estruturada_imdb(filme,1,)
        elif recurso == 'imdb_coming_soon':
            pass

        
    def busca_estruturada_imdb(self,filme_origem_busca,profundidade_busca_usuario_reviews):

        base_url = 'http://www.imdb.com/'
        url_filme = base_url + 'title/' + filme_origem_busca + '/'
        self.__gerar_arquivo_log('log_scrapping_'+ self.data_atual_formatada +'.txt', filme_origem_busca + ' Iniciado em ' + str(datetime.now()) + '\n\n')
        resposta_url_filme = self.__realizar_requisicao(url = url_filme)
        recomendacoes_filmes_relacionados_imdb = []
        total_usarios_reviews = ''
        dict_usuarios_reviews = {}
        erro_processamento = ''
        
        if resposta_url_filme is not None:
            busca_total_reviews_usuario = resposta_url_filme.find(itemprop='reviewCount')
            if busca_total_reviews_usuario is not None:
                    if len(busca_total_reviews_usuario) > 0:
                        total_usarios_reviews = busca_total_reviews_usuario.string.split(' ')[0].replace(',','')
            recomendacoes_filmes_relacionados_imdb = resposta_url_filme.find_all('div', class_="rec_overview")
        else:
            erro_processamento = 'sim'
        recomendacoes_imdb = []
        for recomendacao in recomendacoes_filmes_relacionados_imdb:
            filme_recomendado_imdb = {
                'filme_imdb_id': recomendacao.get('data-tconst'),
            }
            recomendacoes_imdb.append(filme_recomendado_imdb)
        
        url_filme_reviews = url_filme + 'reviews-index?start=0;count=' + total_usarios_reviews
        resposta_url_filme_reviews = self.__realizar_requisicao(url = url_filme_reviews)
        if resposta_url_filme_reviews is not None:
            filme_reviews = resposta_url_filme_reviews.find_all("td", class_="comment-summary")	
        
            dict_usuarios = {review.find("a").get('href').split('/')[2]: {} for review in filme_reviews}
            dict_usuarios_reviews['usuarios'] = dict_usuarios
        else:
            dict_usuarios_reviews['usuarios'] = {}
            erro_processamento = 'sim'
        
        # Chamar busca review por usuário
            
        dict_usuarios_reviews['filme_origem_busca'] = filme_origem_busca
        dict_usuarios_reviews['recomendacoes_imdb'] = recomendacoes_imdb
        dict_usuarios_reviews['erro_processamento'] = erro_processamento
        dict_usuarios_reviews['total_reviews'] = total_usarios_reviews
        
        self.__gerar_arquivo_json(dict_usuarios_reviews,'imdb',filme_origem_busca)
        self.__gerar_arquivo_log('log_scrapping_'+ self.data_atual_formatada +'.txt',filme_origem_busca + ' Finalizado em ' + str(datetime.now()) + '\n')
        self.__gerar_arquivo_log('log_scrapping_'+ self.data_atual_formatada +'.txt', '--------------------------------------------------\n\n')	
        return dict_usuarios_reviews

    def __verifica_quantidade_reviews_filme_imdb_coming_soon(self,id_imdb):
        base_url = 'http://www.imdb.com/'
        url_filme = base_url + 'title/' + id_imdb + '/'
        resposta_url_filme = self.__realizar_requisicao(url = url_filme)

        total_usarios_reviews = 0

        if resposta_url_filme is not None:
            busca_total_reviews_usuario = resposta_url_filme.find(itemprop='reviewCount')
            if busca_total_reviews_usuario is not None:
                    if len(busca_total_reviews_usuario) > 0:
                        if busca_total_reviews_usuario.string.split(' ')[1] == 'user':
                            total_usarios_reviews = busca_total_reviews_usuario.string.split(' ')[0].replace(',','')
                        else:
                            total_usarios_reviews = 0
        else:
            pass
        print 
        return total_usarios_reviews

    def range_busca_estruturada_filmes_imdb_coming_soon(self,range_busca_final):
        
        base_url = 'http://www.imdb.com/'
        url_coming_soon = base_url + 'movies-coming-soon/?ref_=hm_cs_sm/'
        resposta_url_coming_soon = self.__realizar_requisicao(url = url_coming_soon)
        
        range_busca = resposta_url_coming_soon.find('select','date_select').find_all('option')
        
        for range_busca_atual in range_busca:
            range_atual = range_busca_atual.get('value').split('/')[2]
            range_busca_final.append(range_atual)
        return range_busca_final

    def __monta_dict_novo_filme_coming_soon_imdb(self, **kwargs):
        
        filme_titulo = kwargs.get('filme_titulo','')
        filme_id_imdb = kwargs.get('filme_id_imdb','')
        filme_imagem = kwargs.get('filme_imagem','')
        filme_certificado = kwargs.get('filme_certificado','')
        filme_duracao = kwargs.get('filme_duracao','')
        filme_metascore = kwargs.get('filme_metascore','')
        filme_metascore_total_reviews = kwargs.get('filme_metascore_total_reviews','')
        filme_ano = kwargs.get('filme_ano','')
        filme_mes = kwargs.get('filme_mes','')
        filme_generos = kwargs.get('filme_generos','')
        filme_diretores = kwargs.get('filme_diretores','')
        filme_atores = kwargs.get('filme_atores','')
        filme_descricao = kwargs.get('filme_descricao','')
        filme_total_reviews = kwargs.get('filme_total_reviews','')
        
        filme_generos_tratado_json = []
        for genero_filme in filme_generos:
            filme_generos_tratado_json.append(str(genero_filme.string))

        filme_atores_tratado_json = []
        for ator_filme in filme_atores:
            
            ator = ator_filme.find(itemprop='name')
            ator_nome = ator.find('a').string.encode('utf-8')
            ator_id_imdb = ator.find('a').get('href').split('/')[2]
            ator_json = {
                'ator_id_imdb' : str(ator_id_imdb),
                'ator_nome' : str(ator_nome)
            }
            filme_atores_tratado_json.append(ator_json)
        
        
        filme_diretores_tratado_json = []
        for diretor_filme in filme_diretores:
            diretor = diretor_filme.find(itemprop='name')
            diretor_nome = diretor.find('a').string.encode('utf-8')
            diretor_id_imdb = diretor.find('a').get('href').split('/')[2]
            diretor_json = {
                'diretor_id_imdb' : str(diretor_id_imdb),
                'diretor_nome' : str(diretor_nome)
            }
            filme_diretores_tratado_json.append(diretor_json)
        
        novo_filme = {
            'filme_titulo' : str(filme_titulo.encode('utf-8')),
            'filme_id_imdb' : str(filme_id_imdb),
            'filme_imagem' : str(filme_imagem), 
            'filme_certificado' : str(filme_certificado), 
            'filme_duracao' : str(filme_duracao), 
            'filme_metascore' : str(filme_metascore), 
            'filme_metascore_total_reviews' : str(filme_metascore_total_reviews), 
            'filme_ano' : str(filme_ano),
            'filme_mes' : str(filme_mes),
            'filme_descricao' : str(filme_descricao),
            'filme_total_reviews' : str(filme_total_reviews),
            'filme_data_total_reviews' : str(datetime.now()),
            
            'filme_generos' : filme_generos_tratado_json,
            'filme_diretores' : filme_diretores_tratado_json,
            'filme_atores' :  filme_atores_tratado_json
            }
        
        print novo_filme
        return novo_filme

    def __monta_novo_filme_coming_soon_imdb(self,filme_mes,ano,mes):
        
        duracao_filme = ''
        metascore_filme = ''
        metacore_filme_reviews = ''
        certificado_filme = ''
        descricao_filme = ''
        ano_filme = ano
        mes_filme = mes
        generos_filme = []
        atores_filme = []
        diretores_filme = []
        total_reviews = 0
        imagem_filme = ''
            
        filme = filme_mes.find("h4")
        titulo = ' '.join(filme.find('a').get('title').split(' ')[:-1])
        id_imdb = filme.find('a').get('href').split('/')[2]
        
        # COLOCAR CONDICIONAL PARA VARRER FILMES DO MÊS ATUAL OU MAIS ANTIGOS
        total_reviews = self.__verifica_quantidade_reviews_filme_imdb_coming_soon(id_imdb)
        
        imagem_filme = filme_mes.find(itemprop='image').get('src')
        certificado = filme_mes.find('img','certimage')
        if certificado is not None:
            certificado_filme = certificado.get('title')
                
        duracao = filme_mes.find('time')                
        if duracao is not None:
            duracao_filme = duracao.string.split(" ")[0]
                
        metascore = filme_mes.find('div','metascore')
        if metascore is not None:
            metascore_filme = metascore.find_next('strong').string
            metacore_filme_reviews = metascore.find_next('a').string.split(' ')[0]
            
        descricao = filme_mes.find('div','outline').string                
        if descricao is not None:
            descricao_filme = descricao.encode('utf-8')
        
        generos_filme = filme_mes.find_all(itemprop='genre')
        atores_filme = filme_mes.find_all(itemprop='actors')
        diretores_filme = filme_mes.find_all(itemprop='director')
        
        #print '------------------'
        print '(' + str(total_reviews) + ') '+ titulo + ' ' + id_imdb + ' ' + duracao_filme + ' ' + metascore_filme + ' ' + metacore_filme_reviews + ' ' + certificado_filme + ' ' + ano_filme + ' ' + mes_filme
        #print imagem_filme
        #print '--------'
        #for genero_filme in generos_filme:
        #    print genero_filme.string
        #print '--------'
        #for ator_filme in atores_filme:
        #    ator = ator_filme.find(itemprop='name')
        #    ator_nome = ator.find('a').string.encode('utf-8')
        #    ator_id_imdb = ator.find('a').get('href').split('/')[2]
        #    print str(ator_nome) + ' ' + str(ator_id_imdb)
        #print '--------'
        #for diretor_filme in diretores_filme:
        #    diretor = diretor_filme.find(itemprop='name')
        #    diretor_nome = diretor.find('a').string.encode('utf-8')
        #    diretor_id_imdb = diretor.find('a').get('href').split('/')[2]
        #    print str(diretor_nome) + ' ' + str(diretor_id_imdb)
        #print '--------'
        #print descricao_filme
        #filmes_mes = resposta_url_coming_soon.find_all(itemprop='url')
        
        return self.__monta_dict_novo_filme_coming_soon_imdb(
            filme_titulo = titulo,
            filme_id_imdb = id_imdb,
            filme_imagem = imagem_filme,
            filme_certificado = certificado_filme,
            filme_duracao = duracao_filme,
            filme_metascore = metascore_filme,
            filme_metascore_total_reviews = metacore_filme_reviews,
            filme_ano = ano_filme,
            filme_mes = mes_filme,
            filme_generos = generos_filme,
            filme_diretores = diretores_filme,
            filme_atores = atores_filme,
            filme_descricao = descricao_filme,
            filme_total_reviews = total_reviews,
        )

    def busca_estruturada_identificadores_filmes_imdb_coming_soon(self,range_busca):
        
        filmes_coming_soon_mes = []    
        for range_busca_atual in range_busca:
        
            print range_busca_atual
            ano = range_busca_atual.split("-")[0]
            mes = range_busca_atual.split("-")[1]
            base_url = 'http://www.imdb.com/' 
                  
            url_coming_soon = base_url + 'movies-coming-soon/' + range_busca_atual + '/'
            resposta_url_coming_soon = self.__realizar_requisicao(url = url_coming_soon)

            filmes_mes = resposta_url_coming_soon.find_all('div', class_="list_item")
        
            for filme_mes in filmes_mes:
                filme = filme_mes.find("h4")
                id_imdb = filme.find('a').get('href').split('/')[2]
            
                filmes_coming_soon_mes.append(id_imdb)

        return filmes_coming_soon_mes

    def busca_estruturada_filmes_imdb_coming_soon(self,range_busca):
        
        print range_busca
        ano = range_busca.split("-")[0]
        mes = range_busca.split("-")[1]
        base_url = 'http://www.imdb.com/' 
        filmes_coming_soon_mes = []          

        dict_filmes_coming_soon_mes = {
            'ano': ano,
            'mes': mes
        }
        url_coming_soon = base_url + 'movies-coming-soon/' + range_busca + '/'
        resposta_url_coming_soon = self.__realizar_requisicao(url = url_coming_soon)
    
        filmes_mes = resposta_url_coming_soon.find_all('div', class_="list_item")
        
        for filme_mes in filmes_mes:
            filme = self.__monta_novo_filme_coming_soon_imdb(filme_mes,ano,mes)
            filmes_coming_soon_mes.append(filme)
        
        dict_filmes_coming_soon_mes['filmes'] = filmes_coming_soon_mes
            
        return dict_filmes_coming_soon_mes
        
    def _procura_usuario_busca_estruturada_rotten(self,trs,usuarios):
        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                link_td = td.find_all("a")
                usuario_id = ''
                if link_td:
                    usuario_id = link_td[0].get('href').split('/')[3]
                
                if (usuario_id not in usuarios) and usuario_id:
                    usuarios.append(usuario_id)
        return usuarios

    def busca_estruturada_rotten(self,filme_origem_busca,filme_referencia_imdb):
        base_url = 'http://www.rottentomatoes.com/'
        url_filme = base_url + 'm/' + filme_origem_busca + '/reviews/?page=1&type=user'
        print url_filme
        resposta_url_filme_reviews = self.__realizar_requisicao(url = url_filme)
        usuarios_filme = []
        dict_usuarios_reviews = {}
        erro_processamento = ''
        
        trs = resposta_url_filme_reviews.find_all("tr")
        paginas = resposta_url_filme_reviews.find("span",class_= "pageInfo").string
        pagina_atual = int(paginas.split(' ')[1])
        pagina_total = int(paginas.split(' ')[3])
        
        for i in range(1, pagina_total+1):
            if i == 1:
                self._procura_usuario_busca_estruturada_rotten(trs,usuarios_filme)
            else:
                url_filme = base_url + 'm/' + filme_origem_busca + '/reviews/?page=' + str(i) + '&type=user'
                print url_filme
                resposta_url_filme_reviews = self.__realizar_requisicao(url = url_filme)
                trs = resposta_url_filme_reviews.find_all("tr")
                self._procura_usuario_busca_estruturada_rotten(trs,usuarios_filme)
            print '------'
            print usuarios_filme
            print len(usuarios_filme)
        
        dict_usuarios = {usuario: {} for usuario in usuarios_filme}
        if dict_usuarios:
            dict_usuarios_reviews['usuarios'] = dict_usuarios
        else:
            dict_usuarios_reviews['usuarios'] = {}
        dict_usuarios_reviews['erro_processamento'] = erro_processamento
        dict_usuarios_reviews['total_reviews'] = len(usuarios_filme)
        
        dict_usuarios_reviews['filme_imdb_referencia'] = filme_referencia_imdb
        dict_usuarios_reviews['filme_origem_busca'] = filme_origem_busca       
        self.__gerar_arquivo_json(dict_usuarios_reviews,'rotten',filme_origem_busca)
        
        return dict_usuarios_reviews
    def busca_estruturada_rotten_old(self,filme_origem_busca,profundidade_busca_usuario_reviews_paginas):
        
        base_url = 'http://www.rottentomatoes.com/'
        url_filme = base_url + 'm/' + filme_origem_busca + '/reviews/?page=1&type=user&ajax=true'
        resposta_url_filme_reviews = self.__realizar_requisicao(url = url_filme)
        
        filme_reviews = resposta_url_filme_reviews.find_all("div", class_="media_block")
        
        dict_usuarios_reviews = {}
        dict_usuarios = {review.find("a").get('href').split('/')[3]: {} for review in filme_reviews}
        dict_usuarios_reviews['usuarios'] = dict_usuarios
        
        for usuario in dict_usuarios_reviews['usuarios']:
            #usuario = '789814099'
            print 'ROTTEN ' + usuario
            url_usuario_perfil = base_url + 'user/id/' + usuario + '/'      
            resposta_url_usuario_perfil = self.__realizar_requisicao(url = url_usuario_perfil)
            
            verifica_perfil_privado = resposta_url_usuario_perfil.find_all(text=re.compile("This user's profile has been set to private"))
            if not verifica_perfil_privado:
                total_reviews_usuario = resposta_url_usuario_perfil.find("a", id="profileRatings").string.split(' ')[0]
                total_paginas = int(total_reviews_usuario) / 10
                if total_paginas > profundidade_busca_usuario_reviews_paginas:
                    total_paginas = profundidade_busca_usuario_reviews_paginas
                else:
                    if int(total_reviews_usuario) % 10 > 0 :
                        total_paginas = total_paginas + 1
                reviews_usuario = [] 
                for pagina in range(1,total_paginas+1):
                    url_usuario_review =  base_url + 'user/id/' + usuario + '/ratings/?pageNum=' + str(pagina) + '&ajax=true'
                    print 'ROTTEN - PAGINA ' + str(pagina)
                    resposta_url_usuario_review = self.__realizar_requisicao(url = url_usuario_review)
                    
                    filmes_review_usuario = resposta_url_usuario_review.find_all("li", class_="media_block")
                    
                    for filme_review in filmes_review_usuario:
                        novo_review = self.__monta_novo_review_usuario_rotten(filme_review)
                        reviews_usuario.append(novo_review)
                dict_usuarios_reviews['usuarios'][usuario]['reviews'] = reviews_usuario
            else:
                print '----'
                print 'PERFIL PRIVADO ' + usuario
                print '----'
                        
        dict_usuarios_reviews['filme_origem_busca'] = filme_origem_busca       
        self.__gerar_arquivo_json(dict_usuarios_reviews,'rotten',filme_origem_busca)
        
        return dict_usuarios_reviews
    
    def busca_nao_estruturada_twitter(self,**kwargs):
        pass

    def __gerar_arquivo_json(self,dict_resposta,label_origem,filme):
        folder = 'itens_rastreados/item_semente/'
        filename = folder + label_origem +'_reviews_base_filme_' + filme + '.json'
        with open(filename, 'wb') as fp:
            json.dump(dict_resposta, fp)
        print('ARQUIVO SALVO EM ' + filename)

    def __gerar_arquivo_log(self,nome_arquivo,mensagem):
        folder = 'logs/'
        filename = folder + nome_arquivo
        with open(filename, 'a') as fp:
            fp.write(mensagem)