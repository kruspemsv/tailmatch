#!/usr/bin/env python
import sys
import time
import argparse
import threading
import re
from os import stat
from stat import ST_SIZE

def usage():
	parser = argparse.ArgumentParser(prog=__file__)
	parser.add_argument("-a", "--arquivos", nargs='*', required=True,
                        help="Arquivo(s) para monitorar.")
	parser.add_argument("-s", "--sleep", default=60, type=int,
						help="Intervalo do check. Default 60")
	parser.add_argument("-R", "--regex", required=True,
						help="Regex para ser buscada")
	parser.add_argument("-v", "--verbose",
						help="Lista verbose")
	return parser.parse_args()


class Arquivo(object):
	"""
	Classe Arquivo - Criada apenas uma vez em todo inicio de execucao.
	Cada objeto devera ser capaz de buscar seu final e saber se existe ou possui algum problema.
	"""
	def __init__(self, id, nome):
		self.id = id
		self.nome = nome
		self.ponteiro = self.seek_final()

	def seek_final(self):
		"""Ajusta o ponteiro para o final do arquivo"""
		if self.checa_existe():
			with open(self.nome) as f:
				f.seek(0, 2)
				return f.tell()
		else:
			return None

	def checa_truncate(self):
		"""Avalia se o arquivo foi truncado comparando o tamanho dele com o ultimo ponteiro disponivel"""
		if self.checa_existe():
			if stat(self.nome)[ST_SIZE] < self.ponteiro:
				self.ponteiro = self.seek_final()

	def checa_existe(self):
		"""Avalia se o arquivo existe. Utilizado para tratar remocao nao esperada, erro de leitura e afins"""
		try:
			with open(self.nome) as f:
				return True
			if self.ponteiro == None:
				self.seek_final()			
		except OSError as e:
			sys.stderr.write("WARNING: Arquivo %s. Erro: %s\n" % (self.nome, e.strerror))
			return False
		except IOError as e:
			sys.stderr.write("CRITICAL: Arquivo %s. Erro: %s\n" % (self.nome, e.strerror))
			return False


class Leitor(threading.Thread):
	""" 
	Classe Leitor
	Todo objeto sera uma Thread que roda a cada iteracao definida com sleep na chamada.
	Ele basicamente testa se o arquivo que referencia existe e caso:
		Sim: Abre o arquivo no ultimo ponteiro, busca pela regex desejada e contabiliza quantas ocorrencias encontrou
		Nao: Nao faz nada e aciona a opcao de checar se o arquivo foi truncado ou removido	
	"""
	def __init__(self, threadID, Arquivo, regex):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.Arquivo = Arquivo
		self.regex = regex
		self.regex_count = 0
		self.Arquivo.checa_truncate()

	def run(self):
		"""Metodo com override para chamar funcoes internas"""
		self.ler()
		self.Arquivo.checa_truncate()

	def ler(self):
		"""Funcao de validacao e tratativa para erros"""
		if self.Arquivo.checa_existe():
			with open(self.Arquivo.nome) as f:
				f.seek(self.Arquivo.ponteiro)
				for linha in f:
					self.busca(linha)
					self.Arquivo.ponteiro = f.tell()
				if self.regex_count > 0:
					sys.stdout.write("%d - %d resultados para '%s' no arquivo %s.\n" % (int(time.time()),
																						self.regex_count,
																						self.regex,
																						self.Arquivo.nome))

	def busca(self, linha):
		"""Funcao que efetivamente busca se o regex foi encontrado e atualiza o contador de ocorrencias"""
		match = re.findall(self.regex, linha)
		self.regex_count += len(match)
		

if __name__ == "__main__":
	options = usage()
	sys.stdout.write("%d - Iniciando processo com sleep de %d.\n" % (int(time.time()), options.sleep))
	l_verbose = []	
	catalogo = []

	for index, arquivo in enumerate(options.arquivos):
		a = Arquivo(index, arquivo)
		catalogo.append(a)

	while True:
		for arquivo in catalogo:
			threadID = arquivo.id
			t_arquivo = Leitor(threadID, arquivo, options.regex)
			t_arquivo.start()

		time.sleep(options.sleep)
