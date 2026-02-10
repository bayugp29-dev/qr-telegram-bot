import os
import logging
import qrcode
from io import BytesIO
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes, 
    filters
)

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token dari environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_message = f"""
👋 Halo {user.first_name}!

🤖 Generator QR Code kamera Bot!

📱 **Fitur yang tersedia:**
• Generate QR Kode kamera
• QR Code dengan warna custom
• QR Code dengan logo (coming soon)
• Download QR Code dalam format PNG

⚡ **Cara menggunakan:**
1. Kirim kode kamera
2. Pilih warna QR Code
3. Download QR Code Anda

📌 **Perintah yang tersedia:**
/start - Memulai bot
/help - Menampilkan bantuan
/about - Tentang bot ini

✨ Coba kirim Kode Kamera sekarang!
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Generate QR", callback_data="generate")],
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 **Bantuan QR Code Bot**

🔹 **Cara Menggunakan:**
1. Kirim teks, URL, atau nomor telepon
2. Pilih warna QR Code yang diinginkan
3. QR Code akan dibuat secara otomatis
4. Download gambar QR Code

🔹 **Contoh penggunaan:**
- Kirim: `https://google.com`
- Kirim: `Hello World!`
- Kirim: `+6281234567890`
- Kirim: `WIFI:S:MyNetwork;T:WPA;P:MyPassword;;`

🔹 **Fitur:**
• QR Code dari teks/URL
• Pilihan warna custom
• Format PNG berkualitas tinggi
• Gratis tanpa batas

🔹 **Perintah:**
/start - Memulai bot
/help - Menampilkan bantuan ini
/about - Info tentang bot
"""
    await update.message.reply_text(help_text)

# Command: /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """
🤖 **QR Code Generator Bot**

📱 **Versi:** 1.0
🔧 **Status:** Online 24/7
👨‍💻 **Developer:** @YourUsername
📅 **Update:** November 2024

✨ **Fitur:**
• Generate QR Code online
• Tanpa perlu install aplikasi
• Bekerja di semua perangkat
• Gratis selamanya

🔐 **Privasi:**
• Tidak menyimpan data Anda
• QR Code dihapus setelah dikirim
• Aman dan terenkripsi

💡 **Tips:** QR Code dapat menyimpan:
- URL website
- Teks biasa
- Kontak telepon
- Koneksi WiFi
- Informasi produk
"""
    await update.message.reply_text(about_text)

# Handle text messages
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if len(text) > 500:
        await update.message.reply_text("❌ Teks terlalu panjang! Maksimal 500 karakter.")
        return
    
    # Save text to context for later use
    context.user_data['qr_text'] = text
    
    # Show color selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("⚫ Hitam", callback_data="color_black"),
            InlineKeyboardButton("🔵 Biru", callback_data="color_blue"),
        ],
        [
            InlineKeyboardButton("🔴 Merah", callback_data="color_red"),
            InlineKeyboardButton("🟢 Hijau", callback_data="color_green"),
        ],
        [
            InlineKeyboardButton("🟣 Ungu", callback_data="color_purple"),
            InlineKeyboardButton("🟠 Oranye", callback_data="color_orange"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📝 **Teks yang akan diubah:**\n`{text[:50]}{'...' if len(text) > 50 else ''}`\n\n"
        "🎨 **Pilih warna QR Code:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Generate QR Code function
def generate_qr_code(text, color='black'):
    """Generate QR code image"""
    # Map color names to RGB values
    color_map = {
        'black': (0, 0, 0),
        'blue': (0, 0, 255),
        'red': (255, 0, 0),
        'green': (0, 128, 0),
        'purple': (128, 0, 128),
        'orange': (255, 165, 0)
    }
    
    # Get RGB color
    fill_color = color_map.get(color, (0, 0, 0))
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color=fill_color, back_color="white")
    
    # Convert to bytes
    bio = BytesIO()
    bio.name = f'qr_code_{color}.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    
    return bio

# Handle callback queries (button presses)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "generate":
        await query.edit_message_text(
            "📝 **Kirim teks atau URL yang ingin diubah menjadi QR Code!**\n\n"
            "Contoh: `https://google.com` atau `Hello World!`",
            parse_mode='Markdown'
        )
    
    elif query.data == "help":
        await help_command(update, context)
    
    elif query.data.startswith("color_"):
        color = query.data.replace("color_", "")
        
        if 'qr_text' not in context.user_data:
            await query.edit_message_text("❌ Tidak ada teks yang ditemukan. Kirim teks terlebih dahulu!")
            return
        
        text = context.user_data['qr_text']
        
        # Generate QR code
        await query.edit_message_text("⏳ Sedang membuat QR Code...")
        
        try:
            qr_image = generate_qr_code(text, color)
            
            # Send QR code image
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=qr_image,
                caption=f"✅ **QR Code Berhasil Dibuat!**\n\n"
                       f"📝 **Kode Kamera:** `{text[:100]}{'...' if len(text) > 100 else ''}`\n"
                       f"🎨 **Warna:** {color.capitalize()}\n\n"
                       f"📥 Klik gambar untuk mendownload",
                parse_mode='Markdown'
            )
            
            # Ask if user wants another QR
            keyboard = [
                [InlineKeyboardButton("🔄 Buat Lagi", callback_data="generate")],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "✨ QR Code telah dikirim!\n\n"
                "Apakah Anda ingin membuat QR Code lagi?",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            await query.edit_message_text("❌ Terjadi kesalahan saat membuat QR Code. Silakan coba lagi.")
    
    elif query.data == "menu":
        await start(update, context)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Maaf, terjadi kesalahan. Silakan coba lagi nanti."
        )
    except:
        pass

# Main function
def main():
    """Start the bot"""
    if not TOKEN:
        print("❌ ERROR: Token bot tidak ditemukan!")
        print("Pastikan Anda telah mengatur TELEGRAM_BOT_TOKEN di file .env")
        return
    
    print("🚀 Starting QR Code Bot...")
    
    # Create Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("✅ Bot berjalan! Tekan Ctrl+C untuk berhenti.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
