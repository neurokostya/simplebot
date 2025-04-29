import os
import logging
from dotenv import load_dotenv
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from poems_storage import PoemsStorage

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Инициализируем хранилище стихов
poems_storage = PoemsStorage()

# Стили стихов
POEM_STYLES = {
    'classic': 'классическое стихотворение с рифмой',
    'haiku': 'хайку (три строки: 5-7-5 слогов)',
    'free': 'верлибр (свободный стих)',
    'funny': 'весёлое стихотворение с юмором',
    'romantic': 'романтическое стихотворение'
}

async def generate_poem(theme: str, style: str = 'classic') -> str:
    """Генерирует стихотворение на заданную тему в выбранном стиле"""
    style_description = POEM_STYLES.get(style, POEM_STYLES['classic'])
    prompt = f"""Напиши {style_description} на тему "{theme}".
    Стихотворение должно быть на русском языке.
    Добавь эмодзи, подходящие к теме стихотворения."""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    return f"Ошибка при генерации стихотворения: {response.status}"
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

def get_style_keyboard():
    """Создаёт клавиатуру для выбора стиля стихотворения"""
    keyboard = []
    for style, description in POEM_STYLES.items():
        keyboard.append([InlineKeyboardButton(description, callback_data=f"style_{style}")])
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [KeyboardButton("🎨 Выбрать стиль")],
        [KeyboardButton("❓ Помощь")],
        [KeyboardButton("📝 Мои сохранённые стихи")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        'Привет! Я бот-поэт! ✨\n'
        'Я могу писать стихи в разных стилях!\n'
        'Используй кнопки меню или просто напиши мне тему для стихотворения! (＾▽＾)',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "Я умею писать стихи в разных стилях! ╰(▔∀▔)╯\n\n"
        "🎨 Доступные стили:\n"
    )
    for style, description in POEM_STYLES.items():
        help_text += f"• {description}\n"
    
    help_text += "\nКоманды:\n"
    help_text += "/start - Начать общение\n"
    help_text += "/style - Выбрать стиль стихотворения\n"
    help_text += "/help - Показать это сообщение\n\n"
    help_text += "Просто напиши мне тему, и я сочиню стихотворение! ✨"
    
    await update.message.reply_text(help_text)

async def style_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /style"""
    await update.message.reply_text(
        "Выбери стиль стихотворения:",
        reply_markup=get_style_keyboard()
    )

async def handle_style_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора стиля"""
    query = update.callback_query
    await query.answer()
    
    style = query.data.replace("style_", "")
    context.user_data['current_style'] = style
    
    await query.message.reply_text(
        f"Отлично! Теперь я буду писать в стиле: {POEM_STYLES[style]}\n"
        "Напиши мне тему для стихотворения! ✨"
    )

async def show_saved_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает сохранённые стихи пользователя"""
    user_id = update.effective_user.id
    poems = poems_storage.get_user_poems(user_id)
    
    if not poems:
        await update.message.reply_text("У тебя пока нет сохранённых стихов! (＞﹏＜)")
        return
    
    response = "Твои сохранённые стихи:\n\n"
    for i, poem_data in enumerate(poems, 1):
        response += f"{i}. Тема: {poem_data['theme']}\n"
        response += f"Стиль: {POEM_STYLES[poem_data['style']]}\n"
        response += f"Дата: {poem_data['timestamp']}\n"
        response += f"\n{poem_data['poem']}\n\n"
        
        if i < len(poems):
            response += "---\n\n"
    
    await update.message.reply_text(response)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback запросов"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("style_"):
        await handle_style_callback(update, context)
    elif query.data.startswith("regenerate_"):
        theme = query.data.replace("regenerate_", "")
        style = context.user_data.get('current_style', 'classic')
        poem = await generate_poem(theme, style)
        
        keyboard = [
            [
                InlineKeyboardButton("♻️ Перегенерировать", callback_data=f"regenerate_{theme}"),
                InlineKeyboardButton("💾 Сохранить", callback_data="save_poem")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"Вот новое стихотворение про {theme}:\n\n{poem}",
            reply_markup=reply_markup
        )
    elif query.data == "save_poem":
        # Получаем последнее сообщение с стихотворением
        message_text = query.message.text
        theme = message_text.split("про ")[1].split(":")[0]
        poem = message_text.split("\n\n", 1)[1]
        style = context.user_data.get('current_style', 'classic')
        
        # Сохраняем стихотворение
        poems_storage.add_poem(
            user_id=query.from_user.id,
            poem=poem,
            theme=theme,
            style=style
        )
        
        await query.message.reply_text("Стихотворение сохранено! ✨")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    if text == "🎨 Выбрать стиль":
        await style_command(update, context)
        return
    elif text == "❓ Помощь":
        await help_command(update, context)
        return
    elif text == "📝 Мои сохранённые стихи":
        await show_saved_poems(update, context)
        return
    
    style = context.user_data.get('current_style', 'classic')
    await update.message.reply_text("Сочиняю стихотворение... (◕‿◕✿)")
    poem = await generate_poem(text, style)
    
    # Добавляем кнопки действий под стихотворением
    keyboard = [
        [
            InlineKeyboardButton("♻️ Перегенерировать", callback_data=f"regenerate_{text}"),
            InlineKeyboardButton("💾 Сохранить", callback_data="save_poem")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Вот что я сочинил(а) про {text}:\n\n{poem}",
        reply_markup=reply_markup
    )

def main():
    # Получаем токен бота из переменных окружения
    token = os.getenv('BOT_TOKEN')
    
    if not DEEPSEEK_API_KEY:
        print("Ошибка: Не найден DEEPSEEK_API_KEY в файле .env")
        return
    
    # Создаём приложение
    app = Application.builder().token(token).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('style', style_command))
    
    # Добавляем обработчик callback'ов
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Добавляем обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print('Бот-поэт запущен! (◕‿◕✿)')
    app.run_polling(poll_interval=1)

if __name__ == '__main__':
    main() 