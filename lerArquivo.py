#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import os
import sys
import glob
import shutil
import datetime

# Caminho completo do diretório do script
path = os.path.dirname(os.path.realpath(__file__))

# Abrir arquivo de saída para gravação das queries
file_sql = "/sistema/satelital/csv2db.sql" 
#file_sql = "%s/arquivo/csv2db.sql" %path
fileout = open(file_sql,'w')

# Listar arquivos
#mydir = "%s/arquivo/*.csv" %path
mydir = "/sistema/satelital/*.csv"
listing = sorted(glob.glob(mydir))
print ('Lendo arquivos .csv')




conn = psycopg2.connect(host = "localhost", database = "estatisticas", user="user_estatistica", password="3st4t1st1c4")
curs = conn.cursor()

for filename in listing:
	temp = filename.split(os.sep) [-1]
	nome_arquivo = temp.replace("","").replace(".csv","")
	print (nome_arquivo)
	nome = nome_arquivo.split('_')
	print (nome[1])
	filename = datetime.datetime.strptime(nome[1], '%Y%m%d')
	print (filename)
	ano =filename.strftime('%Y')
	print ano
	mes =filename.strftime('%m')
	print mes
	dia =filename.strftime('%d')
	print dia
	nome_da_tabela = 'public.skywave%s_%s_%s' %(dia, mes, ano)
	print nome_da_tabela	
	
 
	#with open('%s/arquivo/%s.csv' %(path, nome_arquivo)) as arq:
	with open('/sistema/satelital/%s.csv' %(nome_arquivo)) as arq:
		temp = arq.readline()
		cabecalho = temp.strip().split(",")
		for linha in arq:
			linha_array = linha.strip().split(",")
			query = "INSERT INTO %s(skymobileid,skytransaction,skyvolume,skydt_insert) VALUES ('%s','%s',%s,'%s');\n" %(nome_da_tabela, linha_array[4], linha_array[7], linha_array[10], linha_array[6])
					# Imprimir query em arquivo SQL
			print query
			curs.execute(query)
			conn.commit()
			fileout.write(query)
fileout.close()
curs.close()
conn.close()
print ('Gravando dados no DB...')
	
# Abrir conexão, executar SQL e fechar conexão
#conn = psycopg2.connect(host = "localhost", database = "estatisticas", user="user_estatistica", password="3st4t1st1c4")
#curs = conn.cursor()
#curs.execute(open(file_sql, "r").read())
#conn.commit()
# Fechar ponteiro
#curs.close()
# Fechar conexão se fizer inserção em banco
#conn.close()

# Apagar arquivos da pasta arquivo se tiver sub-diretorios e quiser apagar apenas os arquivos descomente o ELIF
print ('Apagando dados da pasta arquivo')
folder = '/home/willian.bezerra.ext/python/arquivo/'
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
       # Elif os.path.isdir(file_path): shutil.rmtree(file_path) 
    except Exception as e:
        print(e)
