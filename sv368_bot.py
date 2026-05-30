#!/usr/bin/env python3
"""
SV368 CSKH Bot - Telegram Bot
Hệ thống danh mục động - thêm/xóa tự do
"""

import os
import json
import logging
import re
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

# Dữ liệu mặc định - danh mục động
DEFAULT_DATA = {
    "link_dang_ky": "",
    "lan_cap_nhat": "Chưa cập nhật",
    "danh_muc": [
        {
            "id": "khuyen_mai",
            "ten": "🎁 Khuyến Mãi",
            "tu_khoa": ["khuyến mãi", "khuyen mai", "km", "ưu đãi", "promotion", "giảm giá", "thưởng"],
            "muc": [
                {"id": "nap_dau", "ten": "🎯 Nạp đầu x20", "noi_dung": "Chưa cập nhật"},
                {"id": "hoan_tra", "ten": "💰 Hoàn trả", "noi_dung": "Chưa cập nhật"},
                {"id": "tan_thu", "ten": "🎮 Tân thủ", "noi_dung": "Chưa cập nhật"},
                {"id": "hang_tuan", "ten": "🎲 Hàng tuần", "noi_dung": "Chưa cập nhật"},
                {"id": "vip", "ten": "🏆 VIP", "noi_dung": "Chưa cập nhật"},
            ]
        },
        {
            "id": "dang_ky",
            "ten": "📝 Cách đăng ký",
            "tu_khoa": ["đăng ký", "đăng kí", "dang ky", "register", "tham gia", "tạo tài khoản"],
            "muc": [
                {"id": "dk_taikhoan", "ten": "📱 Đăng ký tài khoản", "noi_dung": "Chưa cập nhật"},
                {"id": "dk_app", "ten": "📲 Đăng ký App mobile", "noi_dung": "Chưa cập nhật"},
                {"id": "dk_daily", "ten": "🤝 Đăng ký đại lý", "noi_dung": "Chưa cập nhật"},
            ]
        },
        {
            "id": "quy_tac",
            "ten": "⚠️ Quy tắc tham gia",
            "tu_khoa": ["quy tắc", "quy tac", "điều kiện", "dieu kien", "rule", "luật"],
            "muc": [
                {"id": "qt_chung", "ten": "📌 Quy tắc chung", "noi_dung": "Chưa cập nhật"},
                {"id": "qt_napru", "ten": "💳 Nạp/Rút tiền", "noi_dung": "Chưa cập nhật"},
                {"id": "qt_km", "ten": "🎁 Quy tắc nhận KM", "noi_dung": "Chưa cập nhật"},
                {"id": "qt_cuoc", "ten": "🎲 Quy tắc cược", "noi_dung": "Chưa cập nhật"},
            ]
        },
        {
            "id": "lien_he",
            "ten": "📞 Liên hệ hỗ trợ",
            "tu_khoa": ["liên hệ", "lien he", "contact", "hỗ trợ", "ho tro", "giúp", "cskh"],
            "muc": [
                {"id": "lh_telegram", "ten": "✈️ Telegram CSKH", "noi_dung": "Chưa cập nhật"},
                {"id": "lh_zalo", "ten": "💬 Zalo hỗ trợ", "noi_dung": "Chưa cập nhật"},
                {"id": "lh_facebook", "ten": "📘 Facebook", "noi_dung": "Chưa cập nhật"},
                {"id": "lh_website", "ten": "🌐 Website chính thức", "noi_dung": "Chưa cập nhật"},
            ]
        },
    ]
}

# ==================== DATA ====================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
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

def make_id(text):
    return re.sub(r'[^a-z0-9]', '_', text.lower())[:20] + f"_{int(datetime.now().timestamp())%10000}"

# ==================== KHÁCH HÀNG ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    data = load_data()
    dm_list = "\n".join([f"  {dm['ten']}" for dm in data.get("danh_muc", [])])
    await update.message.reply_text(
        f"👋 Chào {user_name}!\n\n"
        "Tôi là bot hỗ trợ khách hàng SV368.\n\n"
        f"Bạn có thể hỏi tôi về:\n{dm_list}\n\n"
        "Hãy hỏi tôi gì đó! 😊"
    )

def customer_menu(dm):
    """Tạo menu các mục trong danh mục"""
    mucs = dm.get("muc", [])
    buttons = []
    row = []
    for i, muc in enumerate(mucs):
        row.append(InlineKeyboardButton(muc["ten"], callback_data=f"xem_{dm['id']}_{muc['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    if len(mucs) > 1:
        buttons.append([InlineKeyboardButton("📋 Xem tất cả", callback_data=f"xem_{dm['id']}_all")])
    return InlineKeyboardMarkup(buttons)

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

    # Nếu admin đang chờ nhập
    if context.user_data.get('is_admin') and context.user_data.get('awaiting'):
        await receive_admin_input(update, context)
        return

    data = load_data()

    # Tìm danh mục khớp từ khóa
    for dm in data.get("danh_muc", []):
        tu_khoa = dm.get("tu_khoa", [])
        if any(kw in lower for kw in tu_khoa):
            mucs = dm.get("muc", [])
            if not mucs:
                await update.message.reply_text(f"{dm['ten']}\n\nChưa có nội dung.")
                return
            if len(mucs) == 1:
                await update.message.reply_text(
                    f"{mucs[0]['ten']}\n\n{mucs[0]['noi_dung']}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data=f"back_{dm['id']}")]])
                )
            else:
                btn = []
                if data.get("link_dang_ky") and dm["id"] == "dang_ky":
                    btn.append([InlineKeyboardButton("🔗 Đăng ký ngay", url=data["link_dang_ky"])])
                await update.message.reply_text(
                    f"{dm['ten']}\n\nChọn mục bạn muốn xem:",
                    reply_markup=customer_menu(dm)
                )
            return

    # Không hiểu
    data = load_data()
    dm_list = " | ".join([dm['ten'] for dm in data.get("danh_muc", [])])
    await update.message.reply_text(
        f"❓ Xin lỗi, tôi chưa hiểu câu hỏi của bạn.\n\n"
        f"Bạn có thể hỏi về:\n{dm_list}"
    )

async def customer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    # Quay lại menu danh mục
    if query.data.startswith("back_"):
        dm_id = query.data[5:]
        for dm in data.get("danh_muc", []):
            if dm["id"] == dm_id:
                await query.edit_message_text(
                    f"{dm['ten']}\n\nChọn mục bạn muốn xem:",
                    reply_markup=customer_menu(dm)
                )
                return

    # Xem mục cụ thể
    if query.data.startswith("xem_"):
        parts = query.data[4:].split("_", 1)
        if len(parts) < 2:
            return
        dm_id = parts[0]
        muc_id = parts[1]

        for dm in data.get("danh_muc", []):
            if dm["id"] == dm_id:
                back_btn = [[InlineKeyboardButton("🔙 Quay lại", callback_data=f"back_{dm_id}")]]

                if muc_id == "all":
                    text = f"📋 {dm['ten']} - TẤT CẢ\n\n"
                    for muc in dm.get("muc", []):
                        text += f"{muc['ten']}\n{muc['noi_dung']}\n\n{'─'*20}\n\n"
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_btn))
                else:
                    for muc in dm.get("muc", []):
                        if muc["id"] == muc_id:
                            await query.edit_message_text(
                                f"{muc['ten']}\n\n{muc['noi_dung']}",
                                reply_markup=InlineKeyboardMarkup(back_btn)
                            )
                            return
                return

# ==================== ADMIN ====================

def admin_main_keyboard(data):
    buttons = []
    for dm in data.get("danh_muc", []):
        buttons.append([InlineKeyboardButton(f"📂 Quản lý {dm['ten']}", callback_data=f"adm_dm_{dm['id']}")])
    buttons.append([InlineKeyboardButton("➕ Thêm danh mục mới", callback_data="adm_add_dm")])
    buttons.append([InlineKeyboardButton("🗑️ Xóa danh mục", callback_data="adm_del_dm_menu")])
    buttons.append([InlineKeyboardButton("🔗 Cập nhật Link đăng ký", callback_data="adm_edit_link")])
    buttons.append([InlineKeyboardButton("📊 Xem tất cả dữ liệu", callback_data="adm_view")])
    return InlineKeyboardMarkup(buttons)

def admin_dm_keyboard(dm):
    buttons = []
    for muc in dm.get("muc", []):
        buttons.append([InlineKeyboardButton(f"✏️ {muc['ten']}", callback_data=f"adm_edit_muc_{dm['id']}_{muc['id']}")])
    buttons.append([InlineKeyboardButton("➕ Thêm mục mới", callback_data=f"adm_add_muc_{dm['id']}")])
    buttons.append([
        InlineKeyboardButton("🗑️ Xóa mục", callback_data=f"adm_del_muc_menu_{dm['id']}"),
        InlineKeyboardButton("🔙 Quay lại", callback_data="adm_back")
    ])
    return InlineKeyboardMarkup(buttons)

async def enter_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['is_admin'] = True
    context.user_data['awaiting'] = None
    data = load_data()
    await update.message.reply_text(
        "🔐 ADMIN PANEL\n\nXin chào Admin! 👋\nChọn chức năng:",
        reply_markup=admin_main_keyboard(data)
    )
    logger.info(f"Admin {update.effective_user.id} entered panel")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not is_admin(user_id) or not context.user_data.get('is_admin'):
        await query.edit_message_text("❌ Bạn không có quyền!")
        return

    data = load_data()

    # Quay lại menu chính
    if query.data == "adm_back":
        context.user_data['awaiting'] = None
        await query.edit_message_text(
            "🔐 ADMIN PANEL\n\nChọn chức năng:",
            reply_markup=admin_main_keyboard(data)
        )
        return

    # Vào quản lý danh mục
    if query.data.startswith("adm_dm_"):
        dm_id = query.data[7:]
        for dm in data.get("danh_muc", []):
            if dm["id"] == dm_id:
                await query.edit_message_text(
                    f"📂 QUẢN LÝ: {dm['ten']}\n\nChọn mục muốn chỉnh sửa:",
                    reply_markup=admin_dm_keyboard(dm)
                )
                return

    # Sửa nội dung mục
    if query.data.startswith("adm_edit_muc_"):
        rest = query.data[13:]
        parts = rest.split("_", 1)
        if len(parts) < 2:
            return
        dm_id, muc_id = parts[0], parts[1]
        for dm in data.get("danh_muc", []):
            if dm["id"] == dm_id:
                for muc in dm.get("muc", []):
                    if muc["id"] == muc_id:
                        context.user_data['awaiting'] = f"edit_muc_{dm_id}_{muc_id}"
                        await query.edit_message_text(
                            f"✏️ Nhập nội dung mới cho:\n{muc['ten']}\n\nHiện tại:\n{muc['noi_dung']}\n\n📝 Gửi nội dung mới:"
                        )
                        return

    # Thêm mục mới vào danh mục
    if query.data.startswith("adm_add_muc_"):
        dm_id = query.data[12:]
        context.user_data['awaiting'] = f"add_muc_ten_{dm_id}"
        await query.edit_message_text("➕ Nhập tên mục mới:\n(Ví dụ: 🎯 Khuyến mãi đặc biệt)")
        return

    # Menu xóa mục
    if query.data.startswith("adm_del_muc_menu_"):
        dm_id = query.data[17:]
        for dm in data.get("danh_muc", []):
            if dm["id"] == dm_id:
                buttons = []
                for muc in dm.get("muc", []):
                    buttons.append([InlineKeyboardButton(f"🗑️ {muc['ten']}", callback_data=f"adm_del_muc_{dm_id}_{muc['id']}")])
                buttons.append([InlineKeyboardButton("🔙 Quay lại", callback_data=f"adm_dm_{dm_id}")])
                await query.edit_message_text(
                    f"🗑️ Chọn mục muốn xóa trong {dm['ten']}:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return

    # Xóa mục
    if query.data.startswith("adm_del_muc_"):
        rest = query.data[12:]
        parts = rest.split("_", 1)
        if len(parts) < 2:
            return
        dm_id, muc_id = parts[0], parts[1]
        for dm in data.get("danh_muc", []):
            if dm["id"] == dm_id:
                ten = next((m["ten"] for m in dm["muc"] if m["id"] == muc_id), muc_id)
                dm["muc"] = [m for m in dm["muc"] if m["id"] != muc_id]
                data["lan_cap_nhat"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                save_data(data)
                await query.edit_message_text(
                    f"✅ Đã xóa mục: {ten}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data=f"adm_dm_{dm_id}")]])
                )
                return

    # Thêm danh mục mới
    if query.data == "adm_add_dm":
        context.user_data['awaiting'] = "add_dm_ten"
        await query.edit_message_text(
            "➕ THÊM DANH MỤC MỚI\n\n📝 Nhập tên danh mục:\n(Ví dụ: 🏆 Giải đấu)"
        )
        return

    # Menu xóa danh mục
    if query.data == "adm_del_dm_menu":
        buttons = []
        for dm in data.get("danh_muc", []):
            buttons.append([InlineKeyboardButton(f"🗑️ {dm['ten']}", callback_data=f"adm_del_dm_{dm['id']}")])
        buttons.append([InlineKeyboardButton("🔙 Quay lại", callback_data="adm_back")])
        await query.edit_message_text(
            "🗑️ Chọn danh mục muốn xóa:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Xóa danh mục
    if query.data.startswith("adm_del_dm_"):
        dm_id = query.data[11:]
        ten = next((dm["ten"] for dm in data["danh_muc"] if dm["id"] == dm_id), dm_id)
        data["danh_muc"] = [dm for dm in data["danh_muc"] if dm["id"] != dm_id]
        data["lan_cap_nhat"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        save_data(data)
        await query.edit_message_text(
            f"✅ Đã xóa danh mục: {ten}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data="adm_back")]])
        )
        return

    # Sửa link đăng ký
    if query.data == "adm_edit_link":
        context.user_data['awaiting'] = "edit_link"
        await query.edit_message_text(
            f"🔗 Nhập link đăng ký mới:\n\nHiện tại: {data.get('link_dang_ky', 'Chưa có')}"
        )
        return

    # Xem tất cả
    if query.data == "adm_view":
        text = "📊 DỮ LIỆU HIỆN TẠI:\n\n"
        for dm in data.get("danh_muc", []):
            text += f"{dm['ten']} ({len(dm.get('muc',[]))} mục)\n"
        text += f"\n🔗 Link ĐK: {data.get('link_dang_ky','Chưa có')}"
        text += f"\n⏰ Cập nhật: {data['lan_cap_nhat']}"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data="adm_back")]])
        )
        return

    # Xác nhận lưu
    if query.data == "adm_confirm_yes":
        await process_confirm(query, context, data)
        return

    if query.data == "adm_confirm_no":
        context.user_data['awaiting'] = None
        context.user_data['pending'] = None
        await query.edit_message_text(
            "❌ Đã hủy.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back")]])
        )
        return

async def process_confirm(query, context, data):
    action = context.user_data.get('confirm_action')
    pending = context.user_data.get('pending')
    pending2 = context.user_data.get('pending2')

    if action and action.startswith("edit_muc_"):
        rest = action[9:]
        parts = rest.split("_", 1)
        dm_id, muc_id = parts[0], parts[1]
        for dm in data.get("danh_muc", []):
            if dm["id"] == dm_id:
                for muc in dm.get("muc", []):
                    if muc["id"] == muc_id:
                        muc["noi_dung"] = pending

    elif action and action.startswith("add_muc_"):
        dm_id = action[8:]
        new_id = make_id(pending2)
        for dm in data.get("danh_muc", []):
            if dm["id"] == dm_id:
                dm["muc"].append({"id": new_id, "ten": pending2, "noi_dung": pending})

    elif action == "add_dm":
        ten_dm = pending2
        tu_khoa_dm = pending
        new_id = make_id(ten_dm)
        data["danh_muc"].append({
            "id": new_id,
            "ten": ten_dm,
            "tu_khoa": [kw.strip() for kw in tu_khoa_dm.split(",")],
            "muc": []
        })

    elif action == "edit_link":
        data["link_dang_ky"] = pending

    data["lan_cap_nhat"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    save_data(data)

    context.user_data['awaiting'] = None
    context.user_data['confirm_action'] = None
    context.user_data['pending'] = None
    context.user_data['pending2'] = None

    await query.edit_message_text(
        "✅ CẬP NHẬT THÀNH CÔNG!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back")]])
    )

async def receive_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    awaiting = context.user_data.get('awaiting')

    # Sửa nội dung mục
    if awaiting and awaiting.startswith("edit_muc_"):
        context.user_data['confirm_action'] = awaiting
        context.user_data['pending'] = text
        context.user_data['awaiting'] = None
        await update.message.reply_text(
            f"📋 Xác nhận cập nhật nội dung:\n\n{text[:300]}\n\n✅ Lưu?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ XÁC NHẬN", callback_data="adm_confirm_yes")],
                [InlineKeyboardButton("❌ HỦY", callback_data="adm_confirm_no")],
            ])
        )
        return

    # Thêm mục mới - bước 1: tên
    if awaiting and awaiting.startswith("add_muc_ten_"):
        dm_id = awaiting[12:]
        context.user_data['pending2'] = text
        context.user_data['awaiting'] = f"add_muc_noi_dung_{dm_id}"
        await update.message.reply_text(f"✅ Tên mục: {text}\n\n📝 Nhập nội dung chi tiết:")
        return

    # Thêm mục mới - bước 2: nội dung
    if awaiting and awaiting.startswith("add_muc_noi_dung_"):
        dm_id = awaiting[17:]
        ten = context.user_data.get('pending2', 'Mục mới')
        context.user_data['pending'] = text
        context.user_data['confirm_action'] = f"add_muc_{dm_id}"
        context.user_data['awaiting'] = None
        await update.message.reply_text(
            f"📋 Xác nhận thêm mục mới:\nTên: {ten}\nNội dung: {text[:200]}\n\n✅ Xác nhận?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ XÁC NHẬN", callback_data="adm_confirm_yes")],
                [InlineKeyboardButton("❌ HỦY", callback_data="adm_confirm_no")],
            ])
        )
        return

    # Thêm danh mục mới - bước 1: tên
    if awaiting == "add_dm_ten":
        context.user_data['pending2'] = text
        context.user_data['awaiting'] = "add_dm_tu_khoa"
        await update.message.reply_text(
            f"✅ Tên danh mục: {text}\n\n📝 Nhập từ khóa để khách nhận ra danh mục này:\n(Cách nhau bằng dấu phẩy. Ví dụ: giải đấu, tournament, thi đấu)"
        )
        return

    # Thêm danh mục mới - bước 2: từ khóa
    if awaiting == "add_dm_tu_khoa":
        ten = context.user_data.get('pending2', 'Danh mục mới')
        context.user_data['pending'] = text
        context.user_data['confirm_action'] = "add_dm"
        context.user_data['awaiting'] = None
        await update.message.reply_text(
            f"📋 Xác nhận thêm danh mục:\nTên: {ten}\nTừ khóa: {text}\n\n✅ Xác nhận?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ XÁC NHẬN", callback_data="adm_confirm_yes")],
                [InlineKeyboardButton("❌ HỦY", callback_data="adm_confirm_no")],
            ])
        )
        return

    # Sửa link
    if awaiting == "edit_link":
        context.user_data['pending'] = text
        context.user_data['confirm_action'] = "edit_link"
        context.user_data['awaiting'] = None
        await update.message.reply_text(
            f"📋 Xác nhận link mới:\n{text}\n\n✅ Xác nhận?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ XÁC NHẬN", callback_data="adm_confirm_yes")],
                [InlineKeyboardButton("❌ HỦY", callback_data="adm_confirm_no")],
            ])
        )
        return

# ==================== ROUTER ====================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith("adm_"):
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
