#!/usr/bin/python
# coding:utf-8
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
import argparse
from  manipular_arquivos import *
from datetime import datetime
from collections import Counter
import time
from nltk.tokenize import word_tokenize
import re, htmlentitydefs
import string
import random
from nltk.corpus import stopwords
import pickle
import os
import json

from fuzzywuzzy import fuzz

from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer

class Nucleo_Pre_Processamento_Analise():
    
    def __init__(self, **kwargs):
        pastas_ambiente()
        self.palavras_comum_ao_dominio = kwargs.get('palavras_comum_dominio',[])
        self.quantidade_tokens_considerados = kwargs.get('quantidade_tokens_considerados',None)
        self.valor_base_positivo = kwargs.get('valor_base_positivo',7.0)
        self.valor_base_negativo = kwargs.get('valor_base_negativo',5.0)
        self.percentual = kwargs.get('percentual',75)
        print self.palavras_comum_ao_dominio
        
    
    
    def pre_processar_texto(self,opiniao):
        pre_proc_freq = ""
        #print self.palavras_comum_ao_dominio
        pre_processamento_opiniao = self.pre_processamento(opiniao)
        removed_stop_word_domain =  list(set(pre_processamento_opiniao) - set(self.palavras_comum_ao_dominio))
        if removed_stop_word_domain:
            counts = Counter(removed_stop_word_domain)
            pre_proc_freq = [x[0] for x in counts.most_common(self.quantidade_tokens_considerados)]
        
        return pre_proc_freq 
    
    def buscar_classificador(self,nome_classificador):
        if os.path.exists(nome_classificador):
            f = open(nome_classificador)
            classifier = pickle.load(f)
            f.close()
            return classifier
        return False
    
    def classificar(self,classificador,opiniao):
        saco_de_palavras = self.pre_processar_texto(opiniao)
        print saco_de_palavras
        #pos_nota = "{0:.1f}".format(float(classificador.prob_classify(self.word_feats(saco_de_palavras)).prob('pos')*10)/2.0)
        pos_nota = classificador.prob_classify(self.word_feats(saco_de_palavras)).prob('pos')
        neg_nota = classificador.prob_classify(self.word_feats(saco_de_palavras)).prob('neg')
        classificacao_opiniao =  classificador.classify(self.word_feats(saco_de_palavras))
        
        return classificacao_opiniao,pos_nota,neg_nota
    
    def heuristica_nota_imdb(self,classificacao_opiniao,pos_nota,neg_nota):
        pos_nota = "{0:.1f}".format(float(pos_nota*10)/2.0)
        neg_nota = "{0:.1f}".format(float(neg_nota*10)/2.0)

        if classificacao_opiniao == "pos":
            nota_positiva = round(float(pos_nota),1)
            valor = nota_positiva

        elif classificacao_opiniao == "neg":
            nota_negativa = 5.0 - round(float(neg_nota),1)
            valor = nota_negativa
    
        return valor
    # Gera arquivo dat de treino e teste para cada hipotese 
    def gerar_arquivo_dat(self,nome_arquivo,arquivo,pasta_destino):
        file = open(pasta_destino + nome_arquivo + ".dat", "w")
        file.write(arquivo)
        file.close()

    def verifica_rating_review(self,filme_rating,filme_data_review,data_limite_analise):
        if filme_rating is not None:
            if filme_rating != 'advertisement':
                filme_rating = "{0:.1f}".format(float(filme_rating.split('/')[0])/2)
            else:
                filme_rating = "{0:.1f}".format(float(7))
        else:
            filme_rating = "{0:.1f}".format(float(6))
        filme_data_review = datetime.strptime(filme_data_review, '%d %B %Y')

        if (filme_data_review <= data_limite_analise):
            if float(filme_rating) <= 5.0:
                return True
        return False

    def word_feats(self,words):
        return dict([(word, True) for word in words])

    def striphtml(self,data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    def unescape(self,text):
        def fixup(m):
            text = m.group(0)
            if text[:2] == "&#":
                # character reference
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text # leave as is
        return re.sub("&#?\w+;", fixup, text)




    def pre_processamento(self,test_string):
        #test_string = "<p> This movie begins with a shot of Josh (Jesse Eisenberg) brooding, and in the following hours (probably fewer than two, but feeling like many more) Josh keeps brooding and brooding and brooding some more. Not even the trace of a smile ever crosses his face. No matter whether he broods outdoors or in a car---he spends half the movie in a car, now as a passenger, now as the driver---his emotional repertoire is extremely limited. To use Dorothy Parker s famous words, he gives a striking performance that ran the gamut of emotions, from A to B. Come to think of it, maybe he got stuck at A, and never even got to B. <br> <br> Thematically this movie runs its gamut of ideas from the sophomoric to the inane. In brief then, avoid it if you can. If you choose to waste your money on this movie, don t say you were not warned </br> </br> </p>"

        clean_string = self.unescape(test_string.lower())

        porter = PorterStemmer()
        snowball = SnowballStemmer('english')
        wordnet = WordNetLemmatizer()

        regex = re.compile('[%s]' % re.escape(string.punctuation)) #see documentation here: http://docs.python.org/2/library/string.html

        raw_docs = self.striphtml(clean_string)

        #print raw_docs

        #raw_docs = "I first saw Münchhausen in my native Romania as a child during the war (I mean WWII) and the scene of the baron s landing on the moon and having a conversation with the head, lying on the ground, of a woman who left the rest of her body in her lunar home, made such a powerful impression on me that to this day I remember it in all its funny details. It was also the first movie in color I had ever seen; yes, those were the days when movies, as a rule, were in black and white.   Revisiting the movie now, as a euphemistically labeled senior citizen, I was surprised that it holds up quite well. It amuses, it surprises, it is well acted, the dialog is clever, written after all by the famous novelist Erich Kästner under a pseudonym to cover up the fact that the Nazis saw themselves forced to employ him after burning his books.   There is something quite disturbing in hindsight about this movie. Why was it made? It was released in the year between the Battle of Stalingrad and the Allied Normandy Invasion the two events that were to seal Germany s fate. Was it an attempt to sustain both at home and abroad the far-fetched illusion that the war was going so well that all the German people cared about was laughing at the Baron Münchhausen s lies? Or was it an attempt at showing that Babelsberg could produce a grand spectacle just as well as Hollywood? And if a spectacle was being offered, why, in a country in which mass murder and deception were the order of the day, was even the hero to be a liar?   I am asking these questions because much in this movie is disturbing for reasons related to them. Take the Baron himself, played in this movie by Hans Albers, the greatest star, the Clark Gable of German movies in those years, yet by the time of this movie a man in his fifties pretending to be irresistible to females. It is as if MGM had cast an aging Adolphe Menjou as Rhett Butler in Gone With the Wind. Now Albers is a fine actor, but to enjoy the movie you definitely have to suspend disbelief and pretend that the aging actor riding the cannonball is not bothered by arthritic pain.   The sets look more like cheap nouveau-riche furnishings and the costumes are cut from wartime stock. Ilse Werner, as Princess Isabella d Este, is as beautiful as ever, and as Count Cagliostro we get to see Ferdinand Marian, the actor who just a few years earlier had disgraced himself by playing the lead in Jud Süss, the most disgusting anti-Semitic propaganda film ever made, a fact that ultimately led Marian to alcoholism and a DUI death at war s end, considered a suicide by many.   Now, one can say, let s just watch the film for what it is, and not in its historic context. But then, Marian s acting of Cagliostro, a swindler, is crafted with the same mannerisms he used in creating the Jew Süss. In short, the undeniable artistic qualities of this movie are infected with the severe moral deficiencies of its makers, and this surprisingly renders the movie more interesting than it has any right of being. This is what disturbs me. ".decode('utf-8')

        tokenized_docs = [word_tokenize(raw_docs)]
        #print tokenized_docs


        tokenized_docs_no_punctuation = []

        for review in tokenized_docs:

            new_review = []
            for token in review: 
                new_token = regex.sub(u'', token)
                if not new_token == u'':
                    new_review.append(new_token)

            tokenized_docs_no_punctuation.append(new_review)

            #print tokenized_docs_no_punctuation

        tokenized_docs_no_stopwords = []
        for doc in tokenized_docs_no_punctuation:
            new_term_vector = []
            for word in doc:
                if not word in stopwords.words('english'):
                    new_term_vector.append(word)
            tokenized_docs_no_stopwords.append(new_term_vector)

            #print tokenized_docs_no_stopwords


        preprocessed_docs = []

        for doc in tokenized_docs_no_stopwords:
            final_doc = []
            for word in doc:
                #final_doc.append(word) # utilizando nenhuma tecnica
                final_doc.append(porter.stem(word))
                #final_doc.append(snowball.stem(word))
                #final_doc.append(wordnet.lemmatize(word)) #note that lemmatize() can also takes part of speech as an argument!
            preprocessed_docs.append(final_doc)

        #print preprocessed_docs
        #print len(preprocessed_docs[0])
        #print len(raw_docs.split(" "))

        return preprocessed_docs[0]


    def procura_filme_usuario(self,usuario,filme):
        caminho_arquivo = "usuarios_reviews/" + str(usuario) +".json"
        if os.path.exists(caminho_arquivo ):

            arquivo = open(caminho_arquivo, "r").read().decode('utf-8', 'ignore').encode('utf-8')
            dicionario = json.loads(arquivo)

            if usuario in dicionario:
                for item in dicionario[usuario]:
                    if item['filme'] == filme:
                        return item['review']
                        #return "encontrei"
                return None
            else:
                return None
    
    
    def analisar_classificador(self,classificador,amostra):
        
        pastas = [("itens_rastreados/modelos/modelo_usuario/", "finalizados")]
        extensao = ".json"
        arquivos_modelos = recuperar_arquivos_pastas(pastas,extensao)
        data_limite_analise = datetime.now()
        negfeats = []
        posfeats = []
        
        
        for arquivo_modelo in arquivos_modelos[:amostra]: 
            print arquivo_modelo
            dict_imdb = json.load(open(arquivo_modelo))

            for review in dict_imdb['reviews']:
                
                filme_data_review = review['filme_data_review']
                filme_rating = review["filme_ratting"]
                #filme_rating = "{0:.1f}".format(float(filme_rating.split('/')[0])/2)
                if self.verifica_rating_review(filme_rating,filme_data_review,data_limite_analise):
                    opiniao = review['filme_opiniao']
                    saco_de_palavras = self.pre_processar_texto(opiniao)
                    if saco_de_palavras:
                        pos_nota = classificador.prob_classify(self.word_feats(saco_de_palavras)).prob('pos')
                        neg_nota = classificador.prob_classify(self.word_feats(saco_de_palavras)).prob('neg')
                        classificacao_opiniao =  classificador.classify(self.word_feats(saco_de_palavras))
                        inferencia = self.heuristica_nota_imdb(classificacao_opiniao, pos_nota, neg_nota)
                        item_rating = "{0:.1f}".format(float(filme_rating.split('/')[0])/2)
                        print inferencia, item_rating

    
    def gerar_classificador(self,nome_classificador,amostra):

        nome_classificador =  'classificadores_nltk/classificador_' + nome_classificador +".pickle"

        pastas = [("itens_rastreados/modelos/modelo_usuario/", "finalizados")]
        extensao = ".json"
        arquivos_modelos = recuperar_arquivos_pastas(pastas,extensao)
        data_limite_analise = datetime.now()
        negfeats = []
        posfeats = []
        
        
        for arquivo_modelo in arquivos_modelos[:amostra]: 
            print arquivo_modelo
            dict_imdb = json.load(open(arquivo_modelo))

            for review in dict_imdb['reviews']:
                
                filme_data_review = review['filme_data_review']
                filme_rating = review["filme_ratting"]
                #filme_rating = "{0:.1f}".format(float(filme_rating.split('/')[0])/2)
                if self.verifica_rating_review(filme_rating,filme_data_review,data_limite_analise):
                    opiniao = review['filme_opiniao']
                    pre_processamento_opiniao = self.pre_processar_texto(opiniao)
                    
                    if pre_processamento_opiniao:
                        print pre_processamento_opiniao
                        #counts = Counter(removed_stop_word_domain)
                        #pre_proc_freq = [x[0] for x in counts.most_common(self.quantidade_tokens_considerados)]
                        if float(filme_rating.split('/')[0]) >= self.valor_base_positivo:
                            dic = (self.word_feats(pre_processamento_opiniao), 'pos')
                            posfeats.append(dic)
                        elif float(filme_rating.split('/')[0]) < self.valor_base_negativo:
                            dic = (self.word_feats(pre_processamento_opiniao), 'neg')
                            negfeats.append(dic)            

        negcutoff = len(negfeats)*3/4
        poscutoff = len(posfeats)*3/4


        random.shuffle(posfeats)
        random.shuffle(negfeats)

        trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
        testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
        print 'treino em %d instancias, teste em %d instancias' % (len(trainfeats), len(testfeats))
        
        classifier = NaiveBayesClassifier.train(trainfeats)
        print 'accuracia:', nltk.classify.util.accuracy(classifier, testfeats)

        # Salvar Classificador
        f = open(nome_classificador, 'wb')
        pickle.dump(classifier, f)
        f.close()
            
            
    #Descobrir Correlacao Item
    def carrega_itens(self,caminho):
        itens = []
        file = open(caminho, 'r')

        for line in file:
            item = line.replace("\n","").split(",")
            id_item = item[0]
            termos_item = item[1:]

            itens.append((id_item,termos_item))

        return itens
    
    def analisar_descoberta_item(self,filmes,amostra):
        
        identificadores_itens = []
        pastas = [("itens_rastreados/modelos/modelo_usuario/", "analisar")]
        extensao = ".json"
        arquivos_modelos = recuperar_arquivos_pastas(pastas,extensao)
        data_limite_analise = datetime.now()
        negfeats = []
        posfeats = []
        
        for termo in filmes:
            identificadores_itens.append(str(termo[0]))
        
        for arquivo_modelo in arquivos_modelos[:amostra]: 
            dict_imdb = json.load(open(arquivo_modelo))

            for review in dict_imdb['reviews']:
                filme_id = str(review['filme_id'].replace('tt',''))
                print filme_id
                if filme_id in identificadores_itens:
                    opiniao = review['filme_opiniao']
                    print self.descobre_item(filmes,opiniao),filme_id 
    
    #Carrega Item Identificadores e Codigo Legado
    def descobre_item(self,filmes,frase):
        filme_id = ""
        tipo_descoberta = ""
        tipo = ""
        maior_probabilidade = 0
        for termos in filmes:
            for termo in termos[1]:
                #print termo
                if termo[0] == '#':
                    hashtags = [word.lower() for word in frase.split() if word[0] == '#']
                    if hashtags:
                        #print hashtags
                        for hashtag in hashtags:
                            resultado_full = fuzz.ratio(termo, hashtag)
                            if resultado_full == 100:
                                filme_id =  termos[0]
                                tipo = "hash_full"
                                melhor_termo = hashtag
                                return filme_id,resultado_full,tipo

                            resultado_part = fuzz.partial_ratio(termo, hashtag)
                            resultado = resultado_part
                            #print str(termo) +' '+ str(hashtag) +' '+ str(resultado_part) 
                            tipo_descoberta = "hash"

                            if resultado > maior_probabilidade:
                                maior_probabilidade = resultado
                                filme_id =  termos[0]
                                tipo = tipo_descoberta
                                melhor_termo = hashtag

                else:
                    resultado_set = fuzz.token_set_ratio(termo, frase)

                    #resultado_part = fuzz.partial_ratio(termo, frase)
                    #print str(resultado_set) + ' ' +str(resultado_part)
                    #if resultado_set >= resultado_part: 
                    #    resultado = resultado_set
                    #else:
                    #    resultado = resultado_part
                    # Alternativa
                    resultado = resultado_set
                    tipo_descoberta = "contexto"

                    if resultado > maior_probabilidade:
                        maior_probabilidade = resultado
                        filme_id =  termos[0]
                        tipo = tipo_descoberta
                        melhor_termo = termo


        
            if maior_probabilidade > self.percentual: 
                return filme_id,maior_probabilidade,tipo,melhor_termo
            else:
                return filme_id,maior_probabilidade,tipo