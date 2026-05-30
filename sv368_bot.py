#!/usr/bin/env python3
"""
SV368 CSKH Bot - Telegram Bot
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

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sv368_data.json")

DEFAULT_DATA = {
    "khuyen_mai": [
        {"id": "nap_dau", "ten": "🎯 Nạp đầu x20", "noi_dung": "Chưa cập nhật"},
        {"id": "hoan_tra", "ten": "💰 Hoàn trả", "noi_dung": "Chưa cập nhật"},
        {"id": "tan_thu", "ten": "🎮 Tân thủ", "noi_dung": "Chưa cập nhật"},
        {"id": "hang_tuan", "ten": "🎲 Hàng tuần", "noi_dung": "Chưa cập nhật"},
        {"id": "vip", "ten": "🏆 VIP", "noi_dung": "Chưa cập nhật"},
    ],
    "cach_dang_ky": "Chưa cập nhật",
    "quy_tac": "Chưa cập nhật",
    "lien_he": "Chưa cập nhật",
    "link_dang_ky": "",
    "lan_cap_nhat": "Chưa cập nhật"
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Đảm bảo có đủ các key
            for key, val in DEFAULT_DATA.items():
                if key not in data:
                    data[key] = val
            return data
    return DEFAULT_DATA.copy()

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_admin(user_id):
    return user_id == ADMIN_ID

# ==================== MENU KHÁCH HÀNG ====================

def menu_khuyen_mai(data):
    """Tạo menu các gói KM"""
    gois = data.get("khuyen_mai", [])
    buttons = []
    row = []
    for i, goi in enumerate(gois):
        row.append(InlineKeyboardButton(goi["ten"], callback_data=f"km_{goi['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("📋 Xem tất cả", callback_data="km_all")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Chào {user_name}!\n\n"
        "Tôi là bot hỗ trợ khách hàng SV368.\n\n"
        "Bạn có thể hỏi tôi về:\n"
        "🎁 Khuyến mãi\n"
        "📝 Cách đăng ký\n"
        "⚠️ Quy tắc tham gia\n"
        "📞 Liên hệ hỗ trợ\n\n"
        "Hãy hỏi tôi gì đó! 😊"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    lower = text.lower().strip()
    user_id = update.effective_user.id

    logger.info(f"[MSG] user_id={user_id}, ADMIN_ID={ADMIN_ID}, text={text[:30]}")

    # Kiểm tra mật khẩu admin
    if text.strip() == f"/{ADMIN_PASSWORD}" or text.strip() == ADMIN_PASSWORD:
        if not is_admin(user_id):
            await update.message.reply_text("❌ Bạn không có quyền admin!")
            return
        await enter_admin(update, context)
        return

    # Nếu admin đang chờ nhập dữ liệu
    if context.user_data.get('is_admin') and context.user_data.get('awaiting'):
        await receive_admin_input(update, context)
        return

    data = load_data()

    # Khuyến mãi
    if any(w in lower for w in ["khuyến mãi", "khuyen mai", "km", "ưu đãi", "promotion", "giảm giá", "thưởng"]):
        await update.message.reply_text(
            "🎁 KHUYẾN MÃI SV368\n\nChọn gói khuyến mãi bạn muốn xem:",
            reply_markup=menu_khuyen_mai(data)
        )
        return

    # Kiểm tra từ khóa từng gói KM
    for goi in data.get("khuyen_mai", []):
        keywords = goi["ten"].lower().replace("🎯","").replace("💰","").replace("🎮","").replace("🎲","").replace("🏆","").strip()
        if keywords in lower or goi["id"] in lower:
            buttons = [[InlineKeyboardButton("🔙 Quay lại KM", callback_data="back_km")]]
            await update.message.reply_text(
                f"{goi['ten']}\n\n{goi['noi_dung']}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

    # Cách đăng ký
    if any(w in lower for w in ["đăng ký", "đăng kí", "dang ky", "register", "tham gia", "tạo tài khoản"]):
        buttons = []
        if data.get("link_dang_ky"):
            buttons.append([InlineKeyboardButton("🔗 Đăng ký ngay", url=data["link_dang_ky"])])
        buttons.append([InlineKeyboardButton("🔙 Quay lại", callback_data="back_main")])
        await update.message.reply_text(
            f"📝 CÁCH ĐĂNG KÝ SV368\n\n{data['cach_dang_ky']}",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )
        return

    # Quy tắc
    if any(w in lower for w in ["quy tắc", "quy tac", "điều kiện", "dieu kien", "rule", "luật"]):
        await update.message.reply_text(
            f"⚠️ QUY TẮC THAM GIA SV368\n\n{data['quy_tac']}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data="back_main")]])
        )
        return

    # Liên hệ
    if any(w in lower for w in ["liên hệ", "lien he", "contact", "hỗ trợ", "ho tro", "giúp", "cskh"]):
        await update.message.reply_text(
            f"📞 LIÊN HỆ HỖ TRỢ SV368\n\n{data['lien_he']}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data="back_main")]])
        )
        return

    # Không hiểu
    await update.message.reply_text(
        "❓ Xin lỗi, tôi chưa hiểu câu hỏi của bạn.\n\n"
        "Bạn có thể hỏi về:\n"
        "🎁 Khuyến mãi\n"
        "📝 Cách đăng ký\n"
        "⚠️ Quy tắc tham gia\n"
        "📞 Liên hệ hỗ trợ"
    )

# ==================== CALLBACK KHÁCH HÀNG ====================

async def customer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    if query.data == "back_km" or query.data == "back_main":
        await query.edit_message_text(
            "🎁 KHUYẾN MÃI SV368\n\nChọn gói khuyến mãi bạn muốn xem:",
            reply_markup=menu_khuyen_mai(data)
        )
        return

    if query.data == "km_all":
        text = "📋 TẤT CẢ KHUYẾN MÃI SV368\n\n"
        for goi in data.get("khuyen_mai", []):
            text += f"{goi['ten']}\n{goi['noi_dung']}\n\n{'─'*20}\n\n"
        buttons = [[InlineKeyboardButton("🔙 Quay lại", callback_data="back_km")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        return

    if query.data.startswith("km_"):
        goi_id = query.data[3:]
        for goi in data.get("khuyen_mai", []):
            if goi["id"] == goi_id:
                buttons = [[InlineKeyboardButton("🔙 Quay lại KM", callback_data="back_km")]]
                await query.edit_message_text(
                    f"{goi['ten']}\n\n{goi['noi_dung']}",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return

# ==================== ADMIN PANEL ====================

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Quản lý Khuyến Mãi", callback_data="adm_km_menu")],
        [InlineKeyboardButton("📝 Cập nhật Cách đăng ký", callback_data="adm_edit_cach_dang_ky")],
        [InlineKeyboardButton("⚠️ Cập nhật Quy tắc", callback_data="adm_edit_quy_tac")],
        [InlineKeyboardButton("📞 Cập nhật Liên hệ", callback_data="adm_edit_lien_he")],
        [InlineKeyboardButton("🔗 Cập nhật Link đăng ký", callback_data="adm_edit_link_dang_ky")],
        [InlineKeyboardButton("📊 Xem tất cả dữ liệu", callback_data="adm_view")],
    ])

def admin_km_keyboard(data):
    gois = data.get("khuyen_mai", [])
    buttons = []
    for goi in gois:
        buttons.append([InlineKeyboardButton(f"✏️ {goi['ten']}", callback_data=f"adm_km_edit_{goi['id']}")])
    buttons.append([InlineKeyboardButton("➕ Thêm gói KM mới", callback_data="adm_km_add")])
    buttons.append([
        InlineKeyboardButton("🗑️ Xóa gói KM", callback_data="adm_km_delete_menu"),
        InlineKeyboardButton("🔙 Quay lại", callback_data="adm_back")
    ])
    return InlineKeyboardMarkup(buttons)

async def enter_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['is_admin'] = True
    context.user_data['awaiting'] = None
    await update.message.reply_text(
        "🔐 ADMIN PANEL\n\nXin chào Admin! 👋\nChọn chức năng:",
        reply_markup=admin_keyboard()
    )
    logger.info(f"Admin {update.effective_user.id} entered admin panel")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not is_admin(user_id) or not context.user_data.get('is_admin'):
        await query.edit_message_text("❌ Bạn không có quyền truy cập!")
        return

    data = load_data()

    # Quay lại admin menu
    if query.data == "adm_back":
        context.user_data['awaiting'] = None
        await query.edit_message_text(
            "🔐 ADMIN PANEL\n\nChọn chức năng:",
            reply_markup=admin_keyboard()
        )
        return

    # Menu quản lý KM
    if query.data == "adm_km_menu":
        await query.edit_message_text(
            "🎁 QUẢN LÝ KHUYẾN MÃI\n\nChọn gói muốn chỉnh sửa:",
            reply_markup=admin_km_keyboard(data)
        )
        return

    # Sửa nội dung gói KM
    if query.data.startswith("adm_km_edit_"):
        goi_id = query.data[12:]
        for goi in data.get("khuyen_mai", []):
            if goi["id"] == goi_id:
                context.user_data['awaiting'] = f"km_edit_{goi_id}"
                await query.edit_message_text(
                    f"✏️ Nhập nội dung mới cho gói:\n{goi['ten']}\n\nNội dung hiện tại:\n{goi['noi_dung']}\n\n📝 Gửi nội dung mới:"
                )
                return

    # Thêm gói KM mới
    if query.data == "adm_km_add":
        context.user_data['awaiting'] = "km_add_ten"
        await query.edit_message_text(
            "➕ THÊM GÓI KM MỚI\n\n📝 Nhập tên gói KM mới:\n(Ví dụ: 🎯 Nạp đầu x10)"
        )
        return

    # Menu xóa gói KM
    if query.data == "adm_km_delete_menu":
        gois = data.get("khuyen_mai", [])
        buttons = []
        for goi in gois:
            buttons.append([InlineKeyboardButton(f"🗑️ {goi['ten']}", callback_data=f"adm_km_del_{goi['id']}")])
        buttons.append([InlineKeyboardButton("🔙 Quay lại", callback_data="adm_km_menu")])
        await query.edit_message_text(
            "🗑️ CHỌN GÓI KM MUỐN XÓA:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Xóa gói KM
    if query.data.startswith("adm_km_del_"):
        goi_id = query.data[11:]
        gois = data.get("khuyen_mai", [])
        ten_goi = next((g["ten"] for g in gois if g["id"] == goi_id), goi_id)
        data["khuyen_mai"] = [g for g in gois if g["id"] != goi_id]
        data["lan_cap_nhat"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        save_data(data)
        await query.edit_message_text(
            f"✅ Đã xóa gói: {ten_goi}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại KM", callback_data="adm_km_menu")]])
        )
        return

    # Sửa các field đơn
    field_map = {
        "adm_edit_cach_dang_ky": ("cach_dang_ky", "📝 Nhập cách đăng ký mới:"),
        "adm_edit_quy_tac": ("quy_tac", "⚠️ Nhập quy tắc mới:"),
        "adm_edit_lien_he": ("lien_he", "📞 Nhập thông tin liên hệ mới:"),
        "adm_edit_link_dang_ky": ("link_dang_ky", "🔗 Nhập link đăng ký mới:"),
    }
    if query.data in field_map:
        field, prompt = field_map[query.data]
        context.user_data['awaiting'] = f"edit_{field}"
        await query.edit_message_text(
            f"{prompt}\n\nHiện tại: {data.get(field, 'Chưa có')}"
        )
        return

    # Xem tất cả dữ liệu
    if query.data == "adm_view":
        gois_text = "\n".join([f"  • {g['ten']}" for g in data.get("khuyen_mai", [])])
        msg = (
            f"📊 DỮ LIỆU HIỆN TẠI:\n\n"
            f"🎁 CÁC GÓI KM ({len(data.get('khuyen_mai',[]))} gói):\n{gois_text}\n\n"
            f"📝 CÁCH ĐĂNG KÝ:\n{data['cach_dang_ky'][:100]}...\n\n"
            f"⚠️ QUY TẮC:\n{data['quy_tac'][:100]}...\n\n"
            f"📞 LIÊN HỆ:\n{data['lien_he'][:100]}...\n\n"
            f"🔗 LINK ĐK: {data.get('link_dang_ky','Chưa có')}\n\n"
            f"⏰ Cập nhật: {data['lan_cap_nhat']}"
        )
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data="adm_back")]])
        )
        return

    # Xác nhận lưu
    if query.data == "adm_confirm_yes":
        awaiting = context.user_data.get('awaiting_confirm_type')
        pending = context.user_data.get('pending_data')
        pending2 = context.user_data.get('pending_data2')

        if awaiting and awaiting.startswith("km_edit_"):
            goi_id = awaiting[8:]
            for goi in data["khuyen_mai"]:
                if goi["id"] == goi_id:
                    goi["noi_dung"] = pending
                    break

        elif awaiting == "km_add":
            import re
            new_id = re.sub(r'[^a-z0-9]', '_', pending2.lower())[:20]
            data["khuyen_mai"].append({"id": new_id, "ten": pending2, "noi_dung": pending})

        elif awaiting and awaiting.startswith("edit_"):
            field = awaiting[5:]
            data[field] = pending

        data["lan_cap_nhat"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        save_data(data)
        context.user_data['awaiting'] = None
        context.user_data['awaiting_confirm_type'] = None

        await query.edit_message_text(
            "✅ CẬP NHẬT THÀNH CÔNG!\n\nNhập mật khẩu để tiếp tục.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back")]])
        )
        logger.info(f"Data updated: {awaiting}")
        return

    if query.data == "adm_confirm_no":
        context.user_data['awaiting'] = None
        context.user_data['awaiting_confirm_type'] = None
        await query.edit_message_text(
            "❌ Đã hủy.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back")]])
        )
        return

async def receive_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    awaiting = context.user_data.get('awaiting')

    if awaiting == "km_add_ten":
        context.user_data['new_km_ten'] = text
        context.user_data['awaiting'] = "km_add_noi_dung"
        await update.message.reply_text(f"✅ Tên gói: {text}\n\n📝 Nhập nội dung chi tiết gói KM này:")
        return

    if awaiting == "km_add_noi_dung":
        ten = context.user_data.get('new_km_ten', 'Gói mới')
        context.user_data['pending_data'] = text
        context.user_data['pending_data2'] = ten
        context.user_data['awaiting_confirm_type'] = "km_add"
        context.user_data['awaiting'] = None
        await update.message.reply_text(
            f"📋 XÁC NHẬN THÊM GÓI KM:\n\nTên: {ten}\nNội dung: {text}\n\n✅ Xác nhận?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ XÁC NHẬN", callback_data="adm_confirm_yes")],
                [InlineKeyboardButton("❌ HỦY", callback_data="adm_confirm_no")],
            ])
        )
        return

    # Các trường hợp sửa khác
    context.user_data['pending_data'] = text
    context.user_data['awaiting_confirm_type'] = awaiting
    context.user_data['awaiting'] = None
    await update.message.reply_text(
        f"📋 XÁC NHẬN CẬP NHẬT:\n\n{text[:200]}\n\n✅ Xác nhận lưu?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ XÁC NHẬN", callback_data="adm_confirm_yes")],
            [InlineKeyboardButton("❌ HỦY", callback_data="adm_confirm_no")],
        ])
    )

# ==================== MAIN ====================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("adm_"):
        await admin_callback(update, context)
    else:
        await customer_callback(update, context)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started!")
    app.run_polling()

if __name__ == '__main__':
    main()
