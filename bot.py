import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from logic import *
from config import Token

user_answers = {}

def start(update: Update, context: CallbackContext) -> None:
    try:
        keyboard = [
            [InlineKeyboardButton("Пройти тест✔️", callback_data='take_test')],
            [InlineKeyboardButton("Выбрать сферу интересов👨‍🦱", callback_data='choose_interest')],
            [InlineKeyboardButton("Связаться с нами🤳", callback_data='contact_us')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "Привет!👋 Я бот, который поможет тебе найти подходящую профессию. Этот бот возможно, изменит твою жизнь раз и навсегда. "
            "Выбери один из вариантов ниже:", reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error in start function: {e}")
        update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

def handle_start_choice(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        query.answer()
        
        if query.data == 'take_test':
            start_test(update)
        elif query.data == 'choose_interest':
            show_interest_keyboard(update)
        elif query.data == 'contact_us':
            contact_us(update)
    except Exception as e:
        print(f"Error in handle_start_choice: {e}")
        query.reply_text("Произошла ошибка при обработке вашего выбора. Пожалуйста, попробуйте еще раз.")

def start_test(update: Update) -> None:
    try:
        query = update.callback_query
        query.answer()
        
        user_id = query.message.chat.id
        user_answers[user_id] = []  
        ask_question(update, 0)
    except Exception as e:
        print(f"Error in start_test: {e}")
        update.callback_query.reply_text("Не удалось начать тест. Пожалуйста, попробуйте снова.")

def ask_question(update: Update, question_index: int) -> None:
    try:
        user_id = update.callback_query.message.chat.id
        
        if question_index < len(questions):
            question = questions[question_index]
            keyboard = [[InlineKeyboardButton(option, callback_data=f'answer_{question_index}_{option}') for option in question["options"]]]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.callback_query.edit_message_text(
                text=question["question"], reply_markup=reply_markup
            )
        else:
            process_results(user_id)
    except Exception as e:
        print(f"Error in ask_question: {e}")
        update.callback_query.reply_text("Произошла ошибка при отображении вопроса. Пожалуйста, попробуйте снова.")

def handle_answer(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        query.answer()
        
        user_id = query.message.chat.id
        answer_data = query.data.split('_')
        
        if len(answer_data) == 3 and answer_data[0] == 'answer':
            question_index = int(answer_data[1])
            answer = answer_data[2]
            
            user_answers[user_id].append(answer)
            
            ask_question(update, question_index + 1)
    except Exception as e:
        print(f"Error in handle_answer: {e}")
        query.reply_text("Произошла ошибка при обработке вашего ответа. Пожалуйста, попробуйте снова.")

def process_results(user_id: int) -> None:
    try:
        answers = user_answers.get(user_id, [])
        
        if "Творческие" in answers:
            recommended_profession = "Художник"
        elif "Аналитические" in answers:
            recommended_profession = "Аналитик данных"
        elif "Технические" in answers:
            recommended_profession = "Инженер"
        else:
            recommended_profession = "Менеджер"

        # Отправка сообщения с рекомендованной профессией
        CallbackContext.bot.send_message(chat_id=user_id, text=f"На основе ваших ответов мы рекомендуем вам профессию: {recommended_profession}!")
    except Exception as e:
        print(f"Error in process_results: {e}")
        CallbackContext.bot.send_message(chat_id=user_id, text="Произошла ошибка при обработке результатов. Пожалуйста, попробуйте снова.")

def show_interest_keyboard(update: Update) -> None:
    try:
        keyboard = [
            [InlineKeyboardButton("Технологии", callback_data='tech')],
            [InlineKeyboardButton("Искусство", callback_data='art')],
            [InlineKeyboardButton("Наука", callback_data='science')],
            [InlineKeyboardButton("Бизнес", callback_data='business')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.callback_query.edit_message_text(
            text="Выбери одну из сфер интересов ниже:", reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error in show_interest_keyboard: {e}")
        update.callback_query.reply_text("Произошла ошибка при отображении сфер интересов. Пожалуйста, попробуйте снова.")

def contact_us(update: Update) -> None:
    try:
        query = update.callback_query
        query.answer()
        
        # Здесь вы можете указать контактные данные или ссылку на связь
        contact_info = "Вы можете связаться с нами по адресу: support@example.com"
        
        query.edit_message_text(text=contact_info)
    except Exception as e:
        print(f"Error in contact_us: {e}")
        update.callback_query.reply_text("Произошла ошибка при попытке связаться с нами. Пожалуйста, попробуйте еще раз.")

def main() -> None:
    create_db()  
    updater = Updater(Token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    
    dispatcher.add_handler(CallbackQueryHandler(handle_start_choice, pattern='^(take_test|choose_interest|contact_us)$'))
    
    dispatcher.add_handler(CallbackQueryHandler(handle_answer, pattern='^answer_'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

