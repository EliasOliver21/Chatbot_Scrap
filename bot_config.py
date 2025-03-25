import telebot
import scrapping_vagas2
import threading

bot = telebot.TeleBot('7665199891:AAFfH_oEGDnCom1f1Grs4QmcUeImF9ORS6g')

@bot.message_handler(['start','help'])
def start(msg:telebot.types.Message):
    ola = "Olá, Mundo!"
    bot.reply_to(msg,ola)

@bot.message_handler(['vagas'])
def start(msg:telebot.types.Message):
    resposta = scrapping_vagas2.verify_vacancy()
    bot.reply_to(msg,resposta)

def verificacao(msg):

    try:
        resultado = scrapping_vagas2.verify_vacancy()  # Chama a função do outro script
        bot.send_message(msg.chat.id, f"🔍 Resultado da verificação: {resultado}")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Ocorreu um erro: {str(e)}")


@bot.message_handler(['vagas_temp'])
def start(msg:telebot.types.Message):
    
    bot.reply_to(msg, "⏳ Aguarde 50 segundos para a verificação...")

    temporizador = threading.Timer(20, verificacao,[msg])
    temporizador.start()


bot.infinity_polling()


