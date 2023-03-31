# Declarando as bibliotecas
import json
import requests
import pandas as pd
import numpy as np
import pytz
import getpass
from datetime import datetime

# Dados de entrada:
usuario = 'USERNAME'
senha = 'PASSWORD'
url = 'http://jenkins.com.br/job/Repo/job/Pasta/'

#Autenticando a comunicação e acesso ao servidor
auth = (usuario,senha)

#Realizando a requisição dos jobs pela API do Jenkins
url = url + 'api/json?tree=jobs[name,jobs[name,url]]&pretty=true'
response = requests.get(url, auth=auth)
python_obj = response.json()

#Declarando o mapeamento
mapa = []

# Realizando o loop de mapeamento
for x in range(len(python_obj['jobs'])):
    for y in range(len(python_obj['jobs'][x]['jobs'])):
        mapa.append([[python_obj['jobs'][x]['name']],python_obj['jobs'][x]['jobs'][y]['name'],python_obj['jobs'][x]['jobs'][y]['url']])

# Configurando e ajustando o DataFrame
df = pd.DataFrame(mapa)
df.columns = ['Repositorio','Branch','URL']
df['Repositorio'] = df['Repositorio'].astype(str).str.replace("[","").str.replace("]","")
df['Repositorio'] = df['Repositorio'].str.replace("'", "")

data = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d-%m-%Y_%H-%M')
df.to_csv('jobs-'+data+'.xlsx', index=False)

print(df)
