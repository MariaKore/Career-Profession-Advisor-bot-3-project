import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import telebot
from config import *
bot = telebot.TeleBot(Token)

questions = [
    {
        "question": "Какой тип задач вам больше нравится?",
        "options": ["Творческие", "Аналитические", "Технические", "Социальные"]
    },
    {
        "question": "Какую среду вы предпочитаете?",
        "options": ["Офис", "На улице", "Дома", "В команде"]
    },
    {
        "question": "Что вам больше интересно?",
        "options": ["Наука", "Искусство", "Технологии", "Бизнес"]
    }
]

user_answers = {}

def create_db():
    conn = sqlite3.connect('career_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professions (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            skills TEXT,
            resources TEXT,
            prospects TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            interests TEXT,
            skills TEXT
        )
    ''')
    conn.commit()
    conn.close()

@bot.message_handler(func=lambda message: True)
def handle_interests(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()  

    user_interest = query.data  
    chat_id = query.message.chat.id
    
    conn = sqlite3.connect('career_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (chat_id, interests) VALUES (?, ?)', (chat_id, user_interest))
    conn.commit()
    conn.close()

    query.edit_message_text(text="Отлично! Теперь я могу подобрать тебе профессию на основе твоих интересов. Сейчас пришлем результат!✔️")
    recommend_professions(chat_id)

def recommend_professions(chat_id: int) -> None:
    conn = sqlite3.connect('career_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT interests FROM users WHERE chat_id = ?', (chat_id,))
    interests = cursor.fetchone()
    
    if interests:
        interests = interests[0]
        cursor.execute('SELECT * FROM professions WHERE name = ?', (interests,))
        professions = cursor.fetchall()
        
        if professions:
            response = "Вот несколько профессий/сфер, которые могут тебя заинтересовать и изменят твою жизнь раз и навсегда:\n"
            for prof in professions:
                response += f"{prof[1]}: {prof[2]}\n"  
            CallbackContext.bot.send_message(chat_id=chat_id, text=response)
        else:
            CallbackContext.bot.send_message(chat_id=chat_id, text="Извини, я не нашел подходящих профессий.😱 Приносим свои извинения😭")
    
    conn.close()

