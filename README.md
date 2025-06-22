Assistente de Produtividade para WhatsApp
Um bot pessoal para WhatsApp que automatiza a criação de eventos no Google Agenda e cartões no Trello a partir de simples mensagens de texto.

🤖 Sobre o Projeto
Nascido da necessidade de organizar ideias e compromissos que surgem a qualquer momento, este bot funciona como um assistente pessoal. 
Basta enviar uma mensagem para um número no WhatsApp, e o bot inteligentemente identifica se é uma nova ideia para um projeto ou um compromisso 
com data e hora, adicionando-o automaticamente à ferramenta correta (Trello para ideias, Google Agenda para compromissos).

✨ Principais Funcionalidades
Recebimento em Tempo Real: Utiliza webhooks da API do WhatsApp para receber mensagens instantaneamente.
Processamento Inteligente: Analisa o conteúdo da mensagem para diferenciar comandos como ideia: e compromisso:.
Integração com Trello: Cria um novo cartão em um quadro e lista específicos para cada nova ideia recebida.
Integração com Google Calendar: Agenda um novo evento com título, data e hora corretos diretamente na agenda principal do usuário.
🛠 Tecnologias Utilizadas
Backend: Python, Flask
APIs: Google Calendar API, Trello API, WhatsApp Business Platform API
Ferramentas de Desenvolvimento: Ngrok (para testes locais), PythonAnywhere (para implantação futura)
Segurança: Variáveis de ambiente com python-dotenv para gerenciamento de chaves de API.
🚀 Começando
Para executar uma cópia deste projeto localmente, siga estes passos.

Pré-requisitos
Você precisará ter o Python 3, o Git e (opcionalmente) uma ferramenta de túnel como o ngrok ou localtunnel instalados.

Instalação
Clone o repositório:


git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
Crie um Ambiente Virtual (Recomendado):


python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
Instale as dependências:



pip install -r requirements.txt
Configure suas credenciais:

Crie suas chaves de API para o Google Calendar, Trello e WhatsApp Business.
Baixe o arquivo credentials.json do Google e coloque-o na pasta do projeto.
Na raiz do projeto, crie um arquivo chamado .env e adicione suas chaves, seguindo o modelo do arquivo .env.example:
TRELLO_API_KEY="SUA_CHAVE_DE_API_DO_TRELLO"
TRELLO_API_TOKEN="SEU_TOKEN_DO_TRELLO"
TRELLO_IDEIAS_LIST_ID="ID_DA_SUA_LISTA_DE_IDEIAS_NO_TRELLO"
WHATSAPP_VERIFY_TOKEN="CRIE_UMA_SENHA_FORTE_PARA_O_WEBHOOK"
Execute o servidor Flask:



python main.py
Crie um túnel para a porta 5000 com o Ngrok ou Localtunnel e configure a URL gerada como o Webhook no seu painel da Meta for Developers.

✍ Como Usar
Envie mensagens para o seu número de teste do WhatsApp usando os seguintes formatos:

Para criar uma ideia no Trello:
ideia: Criar um novo projeto
Para criar um compromisso na Google Agenda:
compromisso: Reunião com time de produto 24/06/2025 às 14:30
📜 Licença
Distribuído sob a licença MIT. Veja LICENSE para mais informações.

