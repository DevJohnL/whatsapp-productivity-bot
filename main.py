import os
import re 
import requests
import traceback
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv() # Carrega as variáveis do arquivo.env

# ------- CONFIGURAÇÕES - PREENCHA COM SEUS DADOS -----
# Trello
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_IDEIAS_LIST_ID = os.getenv('TRELLO_IDEIAS_LIST_ID')

#Whatsapp (Meta)
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')

#Google Calendar (não precisa preencher nada aqui, ele usará o credentials.json)
# --------- FIM DAS CONFIGURAÇÕES ---------

# Inicializa o Flask, que criará nosso servidor web
app = Flask(__name__)

# ---- FUNÇÕES DE LÓGICA ----

def processar_mensagem(texto):
    """Analisa o texto da mensagem para identificar se é compromisso ou ideia."""
    # Procura pelo padrão "compromisso: [descrição] [dd/mm/aaaa] às [hh:mm]"
    match_compromisso = re.search(r'compromisso:\s*(.*?)\s*(\d{2}/\d{2}/\d{4})\s*às\s*(\d{2}:\d{2})', texto,re.IGNORECASE)

    if match_compromisso:
        descricao = match_compromisso.group(1).strip()
        data_str = match_compromisso.group(2)
        hora_str = match_compromisso.group(3)
        return {
            'tipo': 'compromisso',
            'descricao': descricao,
            'data': data_str,
            'hora': hora_str
        }                        
    #procura pelo padrão "ideia: [descrição]"
    elif texto.lower().startswith('ideia:'):
        return {
            'tipo': 'ideia',
            'descricao': texto [6:].strip()
        }
    return None # Se não for nenhum dos padrões

def criar_evento_google_agenda(descricao, data_str, hora_str):
    """Cria um evento no Google Calendar."""
    print("--- Iniciando criação de evento no Google Agenda ---")
    print(f"Recebido: Descrição='{descricao}', Data= '{data_str}', Hora='{hora_str}'")

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])

    if not creds or not creds.valid:
        print("Token inválido ou inexistente. Iniciando fluxo de nova autorização...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else: 
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/calendar'])
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("Novo token.json gerado com sucesso.")
    
    try:
        service = build('calendar', 'v3', credentials=creds)

        start_time_dt = datetime.strptime(f'{data_str} {hora_str}', '%d/%m/%Y %H:%M')
        end_time_dt = start_time_dt + timedelta(hours=1)

        print(f"ISO Start Time: {start_time_dt.isoformat()}")
        print(f"ISO End Time: {end_time_dt.isoformat()}")

        event = {
            'summary':descricao,
            'start': {'dateTime': start_time_dt.isoformat(), 'timeZone': 'America/Sao_Paulo'},
            'end': {'dateTime': end_time_dt.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        }

        print("Enviando evento para a API do Google...")
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"SUCESSO! Evento criado: {event.get('htmlLink')}")
        return True
    except Exception as e:
        print(f"!!! ERRO ao criar evento no Google Calendar: {e}")
        traceback.print_exc()
        return False

    # Converte data e hora para o formato RFC3339
    start_time_dt = datetime.strptime(f'{data_str} {hora_str}', '%d/%m/%Y %H:%M')
    end_time_dt = start_time_dt + timedelta(hours=1) #Evento com 1h de duração

    event = {
        'summary': descricao,
        'start': {
            'dateTime': start_time_dt.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': end_time_dt.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
    }

    try: 
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Evento criado: {event.get('htmllink')}")
        return True
    except Exception as e: 
        print(f"Erro ao criar evento no Google Calendar: {e}")
        return False
    
def criar_cartao_trello(descricao):
    """Cria um cartão na lista de Ideias do Trello."""
    url = "https://api.trello.com/1/cards"
    querystring = {
        "idList": TRELLO_IDEIAS_LIST_ID,
        "key": TRELLO_API_KEY,
        "token": TRELLO_API_TOKEN, 
        "name": descricao
    }
    try:
        response = requests.post(url, params=querystring)
        response.raise_for_status() # Lança erro se a requisição falhar
        print(f"Cartão criado no Trello: {response.json()['shortUrl']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar cartão no Trello: {e}")
        return False
    
# ------ ROTAS DO SERVIDOR WEB (WEBHOOK) ----

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == WHATSAPP_VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Erro de verificação.", 403
    if request.method == 'POST':
        data = request.get_json()
        try:
            if data and 'entry' in data:
                for entry in data['entry']:
                    for change in entry['changes']:
                        if 'messages' in change['value']:
                            for message in change['value']['messages']:
                                if message['type'] == 'text':
                                    texto_mensagem = message['text']['body']
                                    print(f"Mensagem recebida: {texto_mensagem}")

                                    info = processar_mensagem(texto_mensagem)


                                    if info:
                                        if info['tipo'] == 'compromisso':
                                            criar_evento_google_agenda(info['descricao'], info['data'], info['hora'])
                                            return "OK", 200 # Retorna OK após ação
                                        elif info['tipo'] == 'ideia':
                                            criar_cartao_trello(info['descricao'])
                                            return "OK", 200 # Retorna OK após a ação 
        except Exception as e:
            print(f"Ocorreu um erro ao processar a requisição: {e}")
            traceback.print_exc() # <------ A linha mágica que vai mostrar o erro
            return "Erro interno", 500
        
        return "Requisição recebida, mas nenhuma ação foi tomada.", 200
                            
    
# Rota principal para testar se o servidor está no ar
@app.route('/')
def index():
    return "<h1>Seuservidor de automação está no ar!</h1>"


if __name__ == '__main__':
    
    print("Servidor de automação pronto para receber mensagen.")

    

    app.run(port=5000, debug=True)

