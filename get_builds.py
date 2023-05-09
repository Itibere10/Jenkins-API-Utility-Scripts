# Declarando as bibliotecas
import requests
import pandas as pd
import pytz
import re
from datetime import datetime
import concurrent.futures

#Coletando os dados de Login para a autenticação
usuario = 'COLOCAR_ID_NATURA'
senha = 'COLOCAR_SENHA_NATURA'
auth = (usuario,senha)

# Define um timeout de 3 minutos
timeout = (180)

#Realizando a requisição dos jobs pela API do Jenkins
url = 'COLOCAR_URL_DO_JENKINS'
url = url+'api/json?pretty=true'
response = requests.get(url, auth=auth, timeout=timeout)
python_obj = response.json()
mapa = []

print('\n> Iniciando análise da branch',python_obj['name'],'...\n> URL:',python_obj['url'])
print('\n> Obtendo dados das últimas',len(python_obj['builds']),'builds...')

def process_build(build):
    check_url = build['url']+'consoleText'
    conteudo = requests.get(check_url,auth=auth).text
    conteudo = conteudo.split('\n')
    exec_jenkins = 0
    exec_bitbucket = 0
    status = 0
    for linha in conteudo:
        # Obtendo execuções do Jenkins...
        if re.search('Started by user', linha):
            exec_jenkins = linha
            exec_jenkins = exec_jenkins.replace("Started by user ","")
        # Obtendo execuções do Bitbucket...
        if re.search('"commit_author":', linha):
            exec_bitbucket = linha
            exec_bitbucket = exec_bitbucket[1:-1]
            exec_bitbucket = exec_bitbucket.replace('""','"')
            exec_bitbucket = exec_bitbucket.replace(",","\n")
            busca = re.search('"commit_author":"[^"]*"',exec_bitbucket)
            exec_bitbucket = busca.group()
            exec_bitbucket = exec_bitbucket.replace('"commit_author":"',"")
            exec_bitbucket = exec_bitbucket.replace('"','')
        # Obtendo o status final de execução...
        if re.search('Finished: SUCCESS|Finished: FAILURE', linha):
            status = linha
            status = status.replace("Finished: ","")
    return [build['number'], exec_jenkins, exec_bitbucket, status, build['url']]

if __name__ == '__main__':
    mapa = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        builds = python_obj['builds']
        results = executor.map(process_build, builds)
        for result in results:
            mapa.append(result)
            print('Mapeada a build:', result[0])


# Configurando DataFrame
df = pd.DataFrame(mapa)
df.columns = ['Numero','Exec. Jenkins','Exec. Bitbucket','Status','URL']
df['Exec. Jenkins'] = df['Exec. Jenkins'].str.replace("0", "Automacao/Bitbucket")
df['Exec. Jenkins'] = df['Exec. Jenkins'].fillna('Automacao/Bitbucket')
df['Status'] = df['Status'].str.replace("0","ABORTED")
df['Status'] = df['Status'].fillna('ABORTED')
df['Exec. Bitbucket'] = df['Exec. Bitbucket'].str.replace("0", "Sem commit detectado")
df['Exec. Bitbucket'] = df['Exec. Bitbucket'].fillna('Sem commit detectado')

# Definindo a expressão regular para ajustar os nomes na coluna Exec. Bitbucket
regex = re.compile('.*Sem commit detectado.*')

# Verifica quais linhas contêm a string desejada usando a expressão regular
mask = df['Exec. Bitbucket'].apply(lambda x: bool(regex.match(x)))

# Substitui os valores correspondentes com a nova string
df.loc[mask, 'Exec. Bitbucket'] = 'Sem commit detectado'

# Extrai a saida para um arquivo CSV
data = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d-%m-%Y_%H-%M')
df.to_csv('mapeamento-'+python_obj['name']+'-'+data+'.xlsx', index=False)

#print(df)
