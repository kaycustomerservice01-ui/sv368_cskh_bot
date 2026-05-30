#!/usr/bin/env python3
"""
SV368 CSKH Bot - Telegram Bot
Admin panel với mã lệnh bảo mật
Chat 1-1 với khách hàng
"""

import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8999982037:AAFkiBcOAHJ52fW0rwYLmW-1QQCi_wQ0pyg")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin_KaY8386_SV368_CSKH_2024_UpdateData_SecureMode")
ADMIN_ID = os.getenv("ADMIN_ID", "YOUR_ADMIN_ID")
DATA_FILE = "sv368_data.json"

# States
AWAITING_KHUYEN_MAI = 1
AWAITING_QUAT_TAC = 2
AWAITING_LIEN_HE = 3
AWAITING_DANG_KY = 4
CONFIRM_UPDATE = 5

# Default data
DEFAULT_DATA = {
    "khuyến_mãi": "Chưa cập nhật",
    "quy_tắc": "Chưa cập nhật",
    "liên_hệ": "Chưa cập nhật",
    "cách_đăng_ký": "Chưa cập nhật",
    "admin_id": ADMIN_ID,
    "lần_cập_nhật": "Chưa cập nhật"
}

def load_data():
    """Tải dữ liệu từ file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_DATA.copy()

def save_data(data):
    """Lưu dữ liệu vào file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start cho khách hàng"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    logger.info(f"User {user_id} ({user_name}) started bot")
    
    message = f"""👋 Chào {user_name}!

Tôi là bot hỗ trợ khách hàng SV368.

Bạn có thể hỏi tôi về:
✅ Khuyến mãi
✅ Cách đăng ký
✅ Quy tắc tham gia
✅ Liên hệ hỗ trợ

Hãy hỏi tôi gì đó! 😊"""
    
    await update.message.reply_text(message)

async def handle_customer_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn từ khách hàng"""
    user_message = update.message.text.lower()
    data = load_data()
    
    # Khuyến mãi
    if "khuyến mãi" in user_message or "promotion" in user_message or "ưu đãi" in user_message or "giảm giá" in user_message:
        response = f"🎁 KHUYẾN MÃI HIỆN TẠI:\n\n{data['khuyến_mãi']}\n\nCó câu hỏi khác không? 😊"
    
    # Cách đăng ký
    elif "đăng ký" in user_message or "đăng kí" in user_message or "register" in user_message or "tham gia" in user_message:
        response = f"📝 CÁCH ĐĂNG KÝ:\n\n{data['cách_đăng_ký']}\n\nCó câu hỏi khác không? 😊"
    
    # Quy tắc
    elif "quy tắc" in user_message or "điều kiện" in user_message or "rule" in user_message:
        response = f"⚠️ QUY TẮC THAM GIA:\n\n{data['quy_tắc']}\n\nCó câu hỏi khác không? 😊"
    
    # Liên hệ
    elif "liên hệ" in user_message or "contact" in user_message or "hỗ trợ" in user_message or "giúp" in user_message:
        response = f"📞 LIÊN HỆ HỖ TRỢ:\n\n{data['liên_hệ']}\n\nCó câu hỏi khác không? 😊"
    
    # Câu hỏi khác
    else:
        response = """❓ Xin lỗi, tôi chưa hiểu câu hỏi của bạn.

Bạn có thể hỏi tôi về:
✅ Khuyến mãi
✅ Cách đăng ký
✅ Quy tắc tham gia
✅ Liên hệ hỗ trợ

Hãy thử hỏi lại! 😊"""
    
    await update.message.reply_text(response)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel - kiểm tra mã lệnh"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    # Kiểm tra mã lệnh
    if user_message == f"/{ADMIN_PASSWORD}":
        # Vào admin panel
        context.user_data['is_admin'] = True
        
        keyboard = [
            [InlineKeyboardButton("🔄 Cập nhật khuyến mãi", callback_data='update_khuyen_mai')],
            [InlineKeyboardButton("🔄 Cập nhật cách đăng ký", callback_data='update_dang_ky')],
            [InlineKeyboardButton("🔄 Cập nhật quy tắc", callback_data='update_quat_tac')],
            [InlineKeyboardButton("🔄 Cập nhật liên hệ", callback_data='update_lien_he')],
            [InlineKeyboardButton("📊 Xem dữ liệu", callback_data='view_data')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """🔐 ADMIN PANEL ĐƯỢC KÍCH HOẠT!

Xin chào Admin! 👋

Chọn chức năng:"""
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        logger.info(f"Admin {user_id} entered admin panel")
    else:
        # Mã lệnh sai - không phải admin
        pass

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý callback từ nút inline"""
    query = update.callback_query
    await query.answer()
    
    # Kiểm tra nếu là admin
    if not context.user_data.get('is_admin'):
        await query.edit_message_text("❌ Bạn không có quyền truy cập!")
        return
    
    if query.data == 'update_khuyen_mai':
        await query.edit_message_text("📝 Gửi dữ liệu khuyến mãi mới:")
        context.user_data['update_type'] = 'khuyến_mãi'
        return AWAITING_KHUYEN_MAI
    
    elif query.data == 'update_dang_ky':
        await query.edit_message_text("📝 Gửi cách đăng ký mới:")
        context.user_data['update_type'] = 'cách_đăng_ký'
        return AWAITING_DANG_KY
    
    elif query.data == 'update_quat_tac':
        await query.edit_message_text("📝 Gửi quy tắc mới:")
        context.user_data['update_type'] = 'quy_tắc'
        return AWAITING_QUAT_TAC
    
    elif query.data == 'update_lien_he':
        await query.edit_message_text("📝 Gửi liên hệ mới:")
        context.user_data['update_type'] = 'liên_hệ'
        return AWAITING_LIEN_HE
    
    elif query.data == 'view_data':
        data = load_data()
        message = f"""📊 DỮ LIỆU HIỆN TẠI:

🎁 KHUYẾN MÃI:
{data['khuyến_mãi']}

📝 CÁCH ĐĂNG KÝ:
{data['cách_đăng_ký']}

⚠️ QUY TẮC:
{data['quy_tắc']}

📞 LIÊN HỆ:
{data['liên_hệ']}

⏰ Lần cập nhật: {data['lần_cập_nhật']}"""
        
        await query.edit_message_text(message)

async def receive_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhận dữ liệu cập nhật từ admin"""
    if not context.user_data.get('is_admin'):
        return
    
    user_text = update.message.text
    update_type = context.user_data.get('update_type')
    
    # Lưu dữ liệu tạm
    context.user_data['pending_data'] = user_text
    
    # Xác nhận
    keyboard = [
        [InlineKeyboardButton("✅ CÓ", callback_data='confirm_yes')],
        [InlineKeyboardButton("❌ KHÔNG", callback_data='confirm_no')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""📋 DỮ LIỆU NHẬN ĐƯỢC:

{user_text}

✅ CẬP NHẬT DỮ LIỆU NÀY?"""
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def confirm_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xác nhận cập nhật dữ liệu"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_yes':
        # Cập nhật dữ liệu
        data = load_data()
        update_type = context.user_data.get('update_type')
        pending_data = context.user_data.get('pending_data')
        
        data[update_type] = pending_data
        data['lần_cập_nhật'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        save_data(data)
        
        # Xóa trạng thái admin
        context.user_data['is_admin'] = False
        
        message = f"""✅ CẬP NHẬT HOÀN TẤT!

📊 KẾT QUẢ:
✓ Cập nhật {update_type}: THÀNH CÔNG

⏰ Lúc: {data['lần_cập_nhật']}

🔔 Dữ liệu sẽ áp dụng ngay cho khách hàng!"""
        
        await query.edit_message_text(message)
        logger.info(f"Data updated: {update_type}")
    
    elif query.data == 'confirm_no':
        context.user_data['is_admin'] = False
        await query.edit_message_text("❌ ĐÃ HỦY CẬP NHẬT\n\nDữ liệu không thay đổi.")

def main():
    """Chạy bot"""
    # Tạo application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    
    # Admin panel
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_panel), group=0)
    
    # Callback buttons
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^/{ADMIN_PASSWORD}$"), admin_panel))
    app.add_handler(MessageHandler(filters.Callback, button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_update), group=1)
    app.add_handler(MessageHandler(filters.Callback, confirm_update))
    
    # Customer messages (catch-all)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_message), group=2)
    
    # Chạy bot
    logger.info("Bot started!")
    app.run_polling()

if __name__ == '__main__':
    main()
