#!/usr/bin/env python3
"""
SV368 CSKH Bot - Telegram Bot
Admin panel với mã lệnh bảo mật
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
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATA_FILE = "sv368_data.json"

DEFAULT_DATA = {
    "khuyến_mãi": "Chưa cập nhật",
    "quy_tắc": "Chưa cập nhật",
    "liên_hệ": "Chưa cập nhật",
    "cách_đăng_ký": "Chưa cập nhật",
    "lần_cập_nhật": "Chưa cập nhật"
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_DATA.copy()

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Cập nhật khuyến mãi", callback_data='update_khuyen_mai')],
        [InlineKeyboardButton("📝 Cập nhật cách đăng ký", callback_data='update_dang_ky')],
        [InlineKeyboardButton("⚠️ Cập nhật quy tắc", callback_data='update_quat_tac')],
        [InlineKeyboardButton("📞 Cập nhật liên hệ", callback_data='update_lien_he')],
        [InlineKeyboardButton("📊 Xem dữ liệu hiện tại", callback_data='view_data')],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Chào {user_name}!\n\n"
        "Tôi là bot hỗ trợ khách hàng SV368.\n\n"
        "Bạn có thể hỏi tôi về:\n"
        "✅ Khuyến mãi\n"
        "✅ Cách đăng ký\n"
        "✅ Quy tắc tham gia\n"
        "✅ Liên hệ hỗ trợ\n\n"
        "Hãy hỏi tôi gì đó! 😊"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Kiểm tra mật khẩu admin
    if text == f"/{ADMIN_PASSWORD}" or text == ADMIN_PASSWORD:
        if not is_admin(user_id):
            await update.message.reply_text("❌ Bạn không có quyền admin!")
            logger.warning(f"Unauthorized admin attempt by user {user_id}")
            return
        # Đúng mật khẩu + đúng ID
        context.user_data['is_admin'] = True
        context.user_data['update_type'] = None
        await update.message.reply_text(
            "🔐 ADMIN PANEL\n\nXin chào Admin! 👋\nChọn chức năng:",
            reply_markup=admin_keyboard()
        )
        logger.info(f"Admin {user_id} entered admin panel")
        return

    # Nếu đang chờ nhập dữ liệu cập nhật
    if context.user_data.get('is_admin') and context.user_data.get('update_type'):
        context.user_data['pending_data'] = text
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ XÁC NHẬN", callback_data='confirm_yes')],
            [InlineKeyboardButton("❌ HỦY", callback_data='confirm_no')],
        ])
        await update.message.reply_text(
            f"📋 Dữ liệu mới:\n\n{text}\n\n✅ Xác nhận cập nhật?",
            reply_markup=keyboard
        )
        return

    # Tin nhắn khách hàng thông thường
    data = load_data()
    msg = text.lower()

    if any(k in msg for k in ["khuyến mãi", "ưu đãi", "promotion", "giảm giá"]):
        response = f"🎁 KHUYẾN MÃI HIỆN TẠI:\n\n{data['khuyến_mãi']}"
    elif any(k in msg for k in ["đăng ký", "đăng kí", "register", "tham gia"]):
        response = f"📝 CÁCH ĐĂNG KÝ:\n\n{data['cách_đăng_ký']}"
    elif any(k in msg for k in ["quy tắc", "điều kiện", "rule"]):
        response = f"⚠️ QUY TẮC THAM GIA:\n\n{data['quy_tắc']}"
    elif any(k in msg for k in ["liên hệ", "contact", "hỗ trợ", "giúp"]):
        response = f"📞 LIÊN HỆ HỖ TRỢ:\n\n{data['liên_hệ']}"
    else:
        response = (
            "❓ Xin lỗi, tôi chưa hiểu câu hỏi của bạn.\n\n"
            "Bạn có thể hỏi về:\n"
            "✅ Khuyến mãi\n"
            "✅ Cách đăng ký\n"
            "✅ Quy tắc tham gia\n"
            "✅ Liên hệ hỗ trợ"
        )

    await update.message.reply_text(response + "\n\nCó câu hỏi khác không? 😊")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not is_admin(user_id) or not context.user_data.get('is_admin'):
        await query.edit_message_text("❌ Bạn không có quyền truy cập!")
        return

    if query.data == 'view_data':
        data = load_data()
        await query.edit_message_text(
            f"📊 DỮ LIỆU HIỆN TẠI:\n\n"
            f"🎁 KHUYẾN MÃI:\n{data['khuyến_mãi']}\n\n"
            f"📝 CÁCH ĐĂNG KÝ:\n{data['cách_đăng_ký']}\n\n"
            f"⚠️ QUY TẮC:\n{data['quy_tắc']}\n\n"
            f"📞 LIÊN HỆ:\n{data['liên_hệ']}\n\n"
            f"⏰ Cập nhật lúc: {data['lần_cập_nhật']}"
        )
        return

    type_map = {
        'update_khuyen_mai': ('khuyến_mãi', '🎁 khuyến mãi'),
        'update_dang_ky': ('cách_đăng_ký', '📝 cách đăng ký'),
        'update_quat_tac': ('quy_tắc', '⚠️ quy tắc'),
        'update_lien_he': ('liên_hệ', '📞 liên hệ'),
    }

    if query.data in type_map:
        key, label = type_map[query.data]
        context.user_data['update_type'] = key
        await query.edit_message_text(f"📝 Gửi nội dung {label} mới:\n\n(Nhập tin nhắn bên dưới)")
        return

    if query.data == 'confirm_yes':
        data = load_data()
        update_type = context.user_data.get('update_type')
        pending_data = context.user_data.get('pending_data')

        data[update_type] = pending_data
        data['lần_cập_nhật'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        save_data(data)

        context.user_data['update_type'] = None
        context.user_data['pending_data'] = None

        await query.edit_message_text(
            f"✅ CẬP NHẬT THÀNH CÔNG!\n\n"
            f"✓ {update_type}: đã lưu\n"
            f"⏰ Lúc: {data['lần_cập_nhật']}\n\n"
            f"Nhập lại mật khẩu để tiếp tục cập nhật."
        )
        logger.info(f"Data updated: {update_type}")

    elif query.data == 'confirm_no':
        context.user_data['update_type'] = None
        context.user_data['pending_data'] = None
        await query.edit_message_text(
            "❌ ĐÃ HỦY\n\nNhập lại mật khẩu để quay lại admin panel."
        )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started!")
    app.run_polling()

if __name__ == '__main__':
    main()
