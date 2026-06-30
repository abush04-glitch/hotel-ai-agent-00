import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Setup API Keys (Render will inject these safely later)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Load Hotel Knowledge (Simplified RAG)
with open("knowledge.txt", "r") as file:
    hotel_info = file.read()

# 3. AI Processing Function
async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Prompt Engineering Strategy to reduce hallucinations
    prompt = f"""
    You are a professional, polite, multilingual hotel receptionist in Arba Minch, Ethiopia.
    Answer the user's question using ONLY the hotel information provided below. 
    If the answer is not in the information, say 'I do not have that information, please contact staff at the phone number provided.'
    Do not make up facts under any circumstance.
    
    Hotel Information:
    {hotel_info}
    
    User Question: {user_message}
    """
    
    try:
        response = model.generate_content(prompt)
        ai_reply = response.text
    except Exception as e:
        ai_reply = "Our system is temporarily responding slowly. Please try again in a moment or call our front desk directly."

    await update.message.reply_text(ai_reply)

# 4. Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Welcome to the Paradise Lodge AI Assistant! How can I help you with your stay or tour bookings in Arba Minch today?"
    await update.message.reply_text(welcome_text)

# 5. Server Startup
if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_ai))
    
    print("AI Agent is running...")
    app.run_polling()
