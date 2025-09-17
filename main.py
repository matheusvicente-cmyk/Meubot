import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔑 Tokens e chaves
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Token do bot do Telegram
INFINITEPAY_API_KEY = os.getenv("INFINITEPAY_API_KEY")  # Sua API Key InfinitePay
FILE_PATH = os.getenv("FILE_PATH", "arquivo.pdf")  # Arquivo que será entregue

# Inicializa Flask e Telegram
app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Dicionário simples para mapear usuários em espera de pagamento
usuarios_em_pagamento = {}

# 🚀 Comando inicial
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Digite /comprar para adquirir seu produto.")

# 🚀 Comando de compra
async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Criar cobrança na InfinitePay (exemplo simples)
    url = "https://api.infinitepay.io/checkout"
    payload = {
        "items": [
            {
                "name": "Arquivo Digital",
                "price": 1000,  # valor em centavos (R$10,00)
                "quantity": 1
            }
        ],
        "customer": {
            "name": "Cliente Telegram",
            "email": "cliente@example.com"
        },
        "payment_method": "pix"
    }
    headers = {
        "Authorization": f"Bearer {INFINITEPAY_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        payment_url = data.get("checkout_url")
        usuarios_em_pagamento[data.get("transaction_id")] = chat_id
        await update.message.reply_text(f"Para concluir o pagamento, acesse: {payment_url}")
    else:
        await update.message.reply_text("Erro ao gerar link de pagamento. Tente novamente.")

# 🚀 Webhook da InfinitePay
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    status = data.get("status")
    transaction_id = data.get("transaction_id")

    if status == "paid" and transaction_id in usuarios_em_pagamento:
        chat_id = usuarios_em_pagamento[transaction_id]
        application.bot.send_document(
            chat_id=chat_id,
            document=open(FILE_PATH, "rb"),
            caption="✅ Pagamento confirmado! Aqui está seu arquivo."
        )
        del usuarios_em_pagamento[transaction_id]

    return {"ok": True}

# 🚀 Configura comandos do bot
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("comprar", comprar))

# 🚀 Inicia o bot (modo webhook para Render)
@app.route("/")
def home():
    return "Bot rodando com sucesso!"

if __name__ == "__main__":
    import threading

    # Inicia bot em thread separada
    def run_bot():
        application.run_polling()

    t = threading.Thread(target=run_bot)
    t.start()

    # Inicia servidor Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
