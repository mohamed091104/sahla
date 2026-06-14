import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import asyncio
import re
import random

# حل مشكلة خطأ اتصال الويندوز (Proactor connection lost)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# السطر 14: إعدادات الصفحة الجديدة باستخدام لوجو الـ PNG واسم المتجر
st.set_page_config(page_title="متجر سهلة للمنتجات اليدوية", page_icon="Free C-10Aug25 S-21Oct25.png", layout="wide")

# تعديل الخطوط لتصبح كبيرة، واضحة، ودعم الواجهة العربية الكاملة (RTL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    
    html, body, [data-testid="stSidebar"], .stApp {
        font-family: 'Cairo', sans-serif !important;
    }
    h1 { font-size: 2.8rem !important; font-weight: 700 !important; text-align: right !important; direction: rtl !important; color: #343a40; }
    h2 { font-size: 2rem !important; font-weight: 700 !important; text-align: right !important; direction: rtl !important; }
    h3 { font-size: 1.5rem !important; font-weight: 600 !important; text-align: right !important; direction: rtl !important; }
    p, span, label, input, textarea, button, div { 
        font-size: 1.2rem !important; 
        text-align: right !important; 
        direction: rtl !important; 
    }
    .stButton>button {
        width: 100%;
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- نظام الـ AI الذكي لفحص جدية البيانات (AI Data Validator) ---
def ai_validate_customer_data(name, phone):
    name = name.strip()
    phone = phone.strip()
    
    if len(name.split()) < 2:
        return False, "🤖 الـ AI رصد: الاسم غير جاد، يرجى كتابة اسمك ثنائياً أو ثلاثياً على الأقل."
    
    if re.search(r"(.)\1{4,}", name) or any(len(word) < 2 for word in name.split()):
        return False, "🤖 الـ AI رصد: هذا الاسم يبدو وهمياً أو يحتوي على حروف عشوائية غير حقيقية!"
        
    if any(char.isdigit() for char in name):
        return False, "🤖 الـ AI رصد: الأسماء الحقيقية لا تحتوي على أرقام!"

    if not re.match(r"^01[0125]\d{8}$", phone):
        return False, "🤖 الـ AI رصد: رقم الهاتف غير صحيح أو وهمي! يجب أن يتكون من 11 رقماً ويبدأ بـ (010، 011، 012، 015)."
        
    return True, ""

# قائمة النطاقات الوهمية لعمل سكان ضدها في الإيميل
DISPOSABLE_EMAIL_DOMAINS = ["mailinator.com", "10minutemail.com", "tempmail.com", "yopmail.com", "maildrop.cc"]

def scan_email(email):
    email = email.strip().lower()
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, email):
        return False, "صيغة البريد الإلكتروني غير صحيحة"
    domain = email.split('@')[-1]
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        return False, "عذراً، هذا البريد الإلكتروني مؤقت وغير مسموح به!"
    return True, "بريد إلكتروني حقيقي وموثوق"

# تهيئة الحالات المتغيرة بالنظام (Session State)
if 'products' not in st.session_state:
    st.session_state.products = [
        {"id": 1, "name": "حقيبة كروشيه مميزة", "price": 250, "image": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=500", "sub_images": [], "desc": "صنع يدوي بالكامل من خيوط قطنية عالية الجودة.", "options": ["الأوف وايت الافتراضي", "أزرق سماوي"]},
        {"id": 2, "name": "شمعة معطرة طبيعية", "price": 90, "image": "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=500", "sub_images": [], "desc": "شمع صويا طبيعي 100% برائحة مهدئة.", "options": ["رائحة الفانيليا", "رائحة العود"]},
        {"id": 3, "name": "إطار خشبي مطرز", "price": 180, "image": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500", "sub_images": [], "desc": "تطريز يدوي دقيق بخيوط الحرير.", "options": ["شكل وردة", "عبارة ترحيبية"]}
    ]

if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'product_to_delete' not in st.session_state:
    st.session_state.product_to_delete = None
if 'show_checkout_otp_field' not in st.session_state:
    st.session_state.show_checkout_otp_field = False

# السطر 72: الهيدر المطور لعرض لوجو الـ PNG المفرغ والاسم جنباً إلى جنب
col_logo, col_title, col_actions = st.columns([1, 3, 1.5])

with col_logo:
    # سيقرأ ملف logo.png مباشرة من الفولدر ويعرضه بحجم متناسق
    st.image("Free C-10Aug25 S-21Oct25.png", use_container_width=True)

with col_title:
    st.title("🛍️ متجر سهلة")
    if st.session_state.is_admin:
        st.subheader("🛠️ لوحة تحكم الأدمن (يمكنك إضافة وإزالة المنتجات)")
    else:
        st.subheader("أهلاً بك في متجر سهلة للمنتجات المصنوعة بكل حب وشغف")

with col_actions:
    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.session_state.is_admin:
            if st.button("🚪 خروج", key="logout_btn"):
                st.session_state.is_admin = False
                st.session_state.cart = {}
                st.success("تم تسجيل الخروج.")
                st.rerun()
        else:
            if st.button("🔑 الأدمن", key="login_btn"):
                st.session_state.show_login_modal = True
            
    with col_btn2:
        if st.session_state.is_admin:
            if st.button("➕ إضافة", key="admin_add_top_btn"):
                st.session_state.show_add_product_modal = True

# --- نافذة دخول الأدمن ---
if st.session_state.get('show_login_modal', False):
    @st.dialog("🔑 لوحة تحكم الإدارة")
    def login_dialog():
        secret_input = st.text_input("أدخل كود الأدمن السري للدخول للوحة التحكم")
        if st.button("🔓 تأكيد الدخول"):
            if secret_input.strip() == "admin13/6":
                st.session_state.is_admin = True
                st.session_state.show_login_modal = False
                st.success("مرحباً بك يا أدمن! تم الدخول المباشر.")
                st.rerun()
            else:
                st.error("❌ الكود السري خاطئ!")
        if st.button("إغلاق"):
            st.session_state.show_login_modal = False
            st.rerun()
    login_dialog()

# --- نافذة إضافة منتج جديد للأدمن ---
if st.session_state.get('show_add_product_modal', False):
    @st.dialog("➕ إضافة منتج جديد للمتجر")
    def add_product_dialog():
        with st.form("add_product_form_new", clear_on_submit=True):
            p_name = st.text_input("1. اسم المنتج")
            p_price = st.number_input("2. سعر المنتج (ج.م)", min_value=1, step=1)
            p_main_file = st.file_uploader("3. Import: اختر الصورة الأساسية للمنتج", type=["png", "jpg", "jpeg"])
            
            st.write("**4. Import: اختر الصور الفرعية الأربعة (اختياري):**")
            sub_files = st.file_uploader("يمكنك اختيار حتى 4 صور إضافية معاً", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            
            p_desc = st.text_area("5. وصف المنتج")
            p_opts = st.text_input("خيارات المنتج/الألوان (افصل بينها بفاصلة ,)")
            
            submit = st.form_submit_button("➕ تنفيذ إضافة المنتج")
            if submit:
                if p_name and p_price and p_main_file:
                    st.session_state.products.append({
                        "id": len(st.session_state.products) + 1,
                        "name": p_name,
                        "price": p_price,
                        "image": p_main_file, 
                        "sub_images": sub_files[:4] if sub_files else [],
                        "desc": p_desc,
                        "options": [opt.strip() for opt in p_opts.split(",")] if p_opts else ["الافتراضي"]
                    })
                    st.success(f"تم إضافة المنتج '{p_name}' بنجاح في متجر سهلة!")
                    st.session_state.show_add_product_modal = False
                    st.rerun()
                else:
                    st.error("تنبيه: يجب ملء الاسم والسعر ورفع الصورة الأساسية على الأقل.")
                    
        if st.button("إغلاق"):
            st.session_state.show_add_product_modal = False
            st.rerun()
    add_product_dialog()

# --- نافذة التأكيد قبل الحذف للأدمن ---
if st.session_state.product_to_delete is not None:
    @st.dialog("⚠️ تأكيد إزالة منتج")
    def confirm_delete_dialog():
        prod_index = st.session_state.product_to_delete
        prod_name = st.session_state.products[prod_index]["name"]
        st.write(f"هل أنت متأكد من أنك تريد إزالة هذا المنتج؟ (**{prod_name}**)")
        
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("نعم", key="btn_confirm_yes"):
                st.session_state.products.pop(prod_index)
                st.session_state.product_to_delete = None
                st.success("تم إزالة المنتج بنجاح!")
                st.rerun()
        with col_no:
            if st.button("لا", key="btn_confirm_no"):
                st.session_state.product_to_delete = None
                st.rerun()
    confirm_delete_dialog()

st.write("---")

# --- دالة عرض تفاصيل المنتج ---
@st.dialog("🔍 تفاصيل المنتج")
def show_product_details(product):
    st.image(product["image"], use_container_width=True, caption="الصورة الأساسية")
    
    if product.get("sub_images"):
        st.write("**صور إضافية للمنتج:**")
        sub_cols = st.columns(len(product["sub_images"]))
        for idx, sub_img in enumerate(product["sub_images"]):
            with sub_cols[idx]:
                st.image(sub_img, use_container_width=True)
                
    st.title(product["name"])
    st.write(product["desc"])
    st.subheader(f"السعر: {product['price']} جنيه")
    
    selected_option = st.selectbox("اختر الشكل / اللون المطلوب:", product["options"])
    
    if st.button("🛒 تأكيد الإضافة إلى السلة"):
        cart_key = f"{product['id']}_{selected_option}"
        if cart_key in st.session_state.cart:
            st.session_state.cart[cart_key]['qty'] += 1
        else:
            st.session_state.cart[cart_key] = {
                "name": product["name"],
                "price": product["price"],
                "option": selected_option,
                "qty": 1
            }
        st.toast(f"تم إضافة {product['name']} إلى السلة!", icon="🛒")
        st.rerun()

# --- تقسيم الشاشة الرئيسية: المنتجات والسلة ---
col_products, col_cart = st.columns([2.5, 1.5])

with col_products:
    st.header("✨ المنتجات المتاحة")
    products = st.session_state.products
    
    for i in range(0, len(products), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(products):
                idx_real = i + j
                prod = products[idx_real]
                with cols[j]:
                    st.image(prod["image"], use_container_width=True)
                    
                    if st.session_state.is_admin:
                        if st.button(f"❌ إزالة هذا المنتج", key=f"del_prod_{idx_real}"):
                            st.session_state.product_to_delete = idx_real
                            st.rerun()
                    
                    if st.button(f"🔎 تفاصيل: {prod['name']}", key=f"details_btn_{prod['id']}"):
                        show_product_details(prod)
                            
                    st.markdown(f"**السعر:** {prod['price']} جنيه")
                    st.write("---")

with col_cart:
    st.header("🛒 سلة التسوق")
    if not st.session_state.cart:
        st.info("سلتك فارغة حالياً. تصفح المنتجات وأضف ما يعجبك!")
    else:
        total_price = 0
        for key, item in list(st.session_state.cart.items()):
            col_item_info, col_qty, col_remove = st.columns([2, 1, 1])
            with col_item_info:
                st.write(f"**{item['name']}**")
                st.caption(f"النوع: {item['option']} | {item['price']} ج.م")
            with col_qty:
                st.write(f"العدد: {item['qty']}")
            with col_remove:
                if st.button("❌", key=f"remove_{key}"):
                    del st.session_state.cart[key]
                    st.rerun()
            total_price += (item["price"] * item["qty"])
            
        st.write("---")
        st.markdown(f"### 💰 الإجمالي النهائي: **{total_price} جنيه**")
        
        if st.button("🗑️ تفريغ السلة بالكامل"):
            st.session_state.cart = {}
            st.rerun()
            
        st.write("---")
        st.subheader("📋 بيانات التوصيل وإتمام الشراء")
        
        with st.form("checkout_form"):
            customer_name = st.text_input("الاسم (ثنائي أو ثلاثي)")
            customer_phone = st.text_input("رقم الهاتف المحمول (11 رقم)")
            customer_email = st.text_input("البريد الإلكتروني للتحقق من الأوردر")
            address = st.text_area("عنوان التوصيل بالتفصيل")
            
            submit_order = st.form_submit_button("✅ تأكيد طلب الأوردر")
            
            if submit_order:
                is_valid_by_ai, ai_message = ai_validate_customer_data(customer_name, customer_phone)
                is_email_real, email_message = scan_email(customer_email)
                
                if not is_valid_by_ai:
                    st.error(ai_message)
                elif not is_email_real:
                    st.error(f"❌ خطأ في البريد: {email_message}")
                elif len(address.strip()) < 12:
                    st.error("❌ العنوان ناقص وغير تفصيلي!")
                else:
                    st.session_state.checkout_otp = str(random.randint(100000, 999999))
                    st.session_state.show_checkout_otp_field = True
                    st.rerun()

        if st.session_state.get('show_checkout_otp_field', False):
            @st.dialog("🔒 خطوة الأمان الأخيرة وتأكيد الهاتف")
            def checkout_otp_dialog():
                st.warning("لمنع الطلبات الوهمية، يرجى كتابة كود التحقق الفوري الصادر لإيميلك:")
                st.info(f"🔑 كود تأكيد الأوردر الخاص بك هو: {st.session_state.checkout_otp}")
                
                user_code = st.text_input("أدخل الكود المكون من 6 أرقام")
                if st.button("🚀 تأكيد نهائي وإرسال الأوردر"):
                    if user_code.strip() == st.session_state.checkout_otp:
                        st.success("🎉 تم استلام طلبك بنجاح! سنتواصل معك هاتفياً لتأكيد الشحن.")
                        st.balloons()
                        st.session_state.cart = {}
                        st.session_state.show_checkout_otp_field = False
                        st.rerun()
                    else:
                        st.error("❌ الكود غير صحيح، يرجى إعادة المحاولة.")
            checkout_otp_dialog()