# Bot Telegram + InfinitePay

Bot de vendas que recebe pagamentos via InfinitePay e envia arquivo automático no Telegram.

## Como rodar no Render
1. Crie um novo Web Service no Render.
2. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
3. Adicione variáveis de ambiente:
   - TELEGRAM_TOKEN
   - INFINITEPAY_API_KEY
   - FILE_PATH (ex: arquivo.pdf)
