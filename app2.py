import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import asyncio
import re
import random

# حل مشكلة خطأ اتصال الويندوز
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# إعدادات الصفحة الأساسية مع اللوجو الجديد كأيقونة للمتصفح (.png)
st.set_page_config(page_title="متجر سهلة للمنتجات اليدوية", page_icon="Free C-10Aug25 S-21Oct25.png", layout="wide")

# ====================================================================
# 🔒 المخزن الثابت (Session State) - ممنوع التصفير نهائياً
# ====================================================================
if 'products' not in st.session_state:
    st.session_state.products = [
        {"id": 1, "name": "حقيبة كروشيه مميزة", "price": 250, "image": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=500", "desc": "صنع يدوي بالكامل من خيوط قطنية عالية الجودة."},
        {"id": 2, "name": "شمعة معطرة طبيعية", "price": 90, "image": "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=500", "desc": "شمع صويا طبيعي 100% برائحة مهدئة."},
        {"id": 3, "name": "إطار خشبي مطرز", "price": 180, "image": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500", "desc": "تطريز يدوي دقيق بخيوط الحرير."}
    ]

if 'social_links' not in st.session_state:
    st.session_state.social_links = [
        {"platform": "فيسبوك", "url": "https://facebook.com"},
        {"platform": "واتساب", "url": "https://wa.me/201000000000"}
    ]

if 'reviews' not in st.session_state:
    st.session_state.reviews = [
        {"customer": "أحمد علي", "stars": 5, "comment": "شغل ممتاز ومتجر سهل الاستخدام جداً!"}
    ]

# حالات التحكم الثابتة
if 'page' not in st.session_state: st.session_state.page = "shop"
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'orders' not in st.session_state: st.session_state.orders = [] 
if 'show_checkout_otp_field' not in st.session_state: st.session_state.show_checkout_otp_field = False
if 'show_review_modal' not in st.session_state: st.session_state.show_review_modal = False
if 'temp_order_data' not in st.session_state: st.session_state.temp_order_data = {}
if 'show_login_section' not in st.session_state: st.session_state.show_login_section = False
if 'show_add_product_section' not in st.session_state: st.session_state.show_add_product_section = False

# الحالات الخاصة بـ Pop-up التعديل الفوري
if 'product_to_edit' not in st.session_state: st.session_state.product_to_edit = None
if 'trigger_edit_popup' not in st.session_state: st.session_state.trigger_edit_popup = False

# ====================================================================
# 🔐 إدارة باسورد الأدمن (جديد - يمكن تغييره من الأدمن)
# ====================================================================
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin13/6"  # الباسورد الافتراضي
if 'show_change_password' not in st.session_state:
    st.session_state.show_change_password = False

# حقن كود CSS المطور - ألوان ثابتة لجميع الأزرار تعمل على الوضع الداكن والفاتح
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none !important;}
    
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stSidebar"], .stApp {
        font-family: 'Cairo', sans-serif !important;
        background-color: #fdfbf7 !important;
    }
    
    /* فرض اللون الأسود على جميع النصوص في الموقع بشكل افتراضي */
    h1, h2, h3, p, span, label, div, .stText { 
        color: #000000 !important;
        text-align: right !important; 
        direction: rtl !important; 
    }
    
    /* تخصيص صناديق الـ Pop-up والمربعات والخلفيات الداكنة لتكون بيضاء تماماً */
    div[role="dialog"], div[data-testid="stDialog"] div, [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border-color: #f4a261 !important;
    }
    
    /* تفتيح حقول الإدخال، القوائم، والمربعات السوداء تماماً */
    div[data-baseweb="input"], div[data-baseweb="select"], textarea, input, select, .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* ضمان وضوح النصوص داخل حقول النصوص والإدخال ومربعات Streamlit */
    input, textarea, select, .stSelectbox [data-testid="stMarkdownContainer"] p, [data-testid="stWidgetLabel"] p {
        color: #000000 !important;
    }
    
    /* جعل أزرار اختيار النجوم تظهر بشكل أفقي مريح للعين */
    div[data-testid="stRadio"] > role[group], div[data-testid="stRadio"] > div {
        flex-direction: row-reverse !important;
        justify-content: flex-end !important;
        gap: 15px !important;
    }
    
    /* ================================================================= */
    /* 🎨 تنسيق الأزرار العامة للموقع - ألوان ثابتة واضحة على كل الوضعيات */
    /* ================================================================= */
    
    /* الأزرار الأساسية - خلفية برتقالية داكنة + نص أبيض */
    .stButton>button {
        width: 100%;
        font-weight: bold !important;
        background-color: #e76f51 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 2px solid #d65a3b !important;
        text-shadow: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
    }
    .stButton>button:hover {
        background-color: #f4a261 !important;
        color: #ffffff !important;
        border-color: #e8954a !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    .stButton>button:active {
        background-color: #d65a3b !important;
        color: #ffffff !important;
    }
    
    /* أزرار الحذف - خلفية حمراء داكنة + نص أبيض */
    button[kind="secondary"], 
    button[data-testid="baseButton-secondary"] {
        background-color: #dc3545 !important;
        color: #ffffff !important;
        border: 2px solid #c82333 !important;
    }
    button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background-color: #e04b59 !important;
        color: #ffffff !important;
    }
    
    /* أزرار النجاح والتأكيد - خلفية خضراء داكنة + نص أبيض */
    button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background-color: #28a745 !important;
        color: #ffffff !important;
        border: 2px solid #218838 !important;
    }
    
    /* أزرار التنبيه والتحذير - خلفية صفراء داكنة + نص أسود */
    .stAlert button {
        background-color: #ffc107 !important;
        color: #000000 !important;
        border: 2px solid #e0a800 !important;
    }
    
    /* أزرار داخل النماذج (form_submit_button) - نفس التنسيق */
    [data-testid="stForm"] .stButton>button {
        background-color: #e76f51 !important;
        color: #ffffff !important;
        border: 2px solid #d65a3b !important;
    }
    
    /* أزرار الأدمن الخاصة - خلفية بنفسجية داكنة + نص أبيض */
    .admin-btn button {
        background-color: #6f42c1 !important;
        color: #ffffff !important;
        border: 2px solid #5a32a3 !important;
    }
    .admin-btn button:hover {
        background-color: #7d52c8 !important;
        color: #ffffff !important;
    }
    
    /* زر تغيير الباسورد - خلفية برتقالية فاتحة + نص أبيض */
    .password-btn button {
        background-color: #fd7e14 !important;
        color: #ffffff !important;
        border: 2px solid #e56b0a !important;
    }
    .password-btn button:hover {
        background-color: #ff922b !important;
        color: #ffffff !important;
    }
    
    /* ================================================================= */
    /* تنسيقات إضافية للوضوح */
    /* ================================================================= */
    
    /* لوحات التنبيه الكلاسيكية */
    .stAlert, div[data-testid="stAlert"] {
        background-color: #ffffff !important;
        border: 1px solid #e76f51 !important;
    }
    .stAlert p {
        color: #264653 !important;
    }
    
    /* تنسيق النجوم في التقييم */
    div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# الـ AI Validator للتحقق من الهاتف والاسم
def ai_validate_customer_data(name, phone):
    name = name.strip()
    phone = phone.strip()
    if len(name.split()) < 2:
        return False, "🤖 الاسم قصير جداً، يرجى كتابته ثنائياً على الأقل."
    if not re.match(r"^01[0125]\d{8}$", phone):
        return False, "🤖 رقم الهاتف المحمول غير صحيح، يجب أن يتكون من 11 رقماً."
    return True, ""

# --- نافذة الـ Pop-up الخاصة بتقييم العميل بنظام النجوم الجديد ---
@st.dialog("⭐ قيم تجربتك معنا ومستوى الخدمة")
def popup_review_form():
    st.write("اختر عدد النجوم المناسب لتقييمك:")
    
    star_options = {
        "⭐": 1,
        "⭐⭐": 2,
        "⭐⭐⭐": 3,
        "⭐⭐⭐⭐": 4,
        "⭐⭐⭐⭐⭐": 5
    }
    
    chosen_stars_label = st.radio(
        label="التقييم بالنجوم:",
        options=list(star_options.keys()),
        index=4, 
        label_visibility="collapsed"
    )
    
    stars = star_options[chosen_stars_label]
    
    comment = st.text_area("أضف تعليقك هنا (اختياري):")
    st.write("")
    if st.button("🚀 إرسال التقييم السريع", key="submit_pop_review"):
        name = st.session_state.temp_order_data.get("customer", "عميل")
        st.session_state.reviews.append({"customer": name, "stars": stars, "comment": comment})
        st.session_state.show_review_modal = False
        st.toast("🎉 تم تسجيل أوردرك وتقييمك بنجاح وبوضوح تام!")
        st.rerun()

# --- نافذة الـ Pop-up الخاصة بتعديل بيانات المنتج للأدمن ---
@st.dialog("📝 تعديل بيانات المنتج")
def popup_edit_product_form(prod_idx):
    prod = st.session_state.products[prod_idx]
    with st.form("edit_product_form_pop"):
        new_name = st.text_input("اسم المنتج", value=prod["name"])
        new_price = st.number_input("السعر الحالي (جنيه)", min_value=1, value=int(prod["price"]))
        new_img = st.text_input("رابط صورة المنتج", value=prod["image"])
        new_desc = st.text_area("وصف تفصيلي للمنتج", value=prod["desc"])
        
        st.write("")
        if st.form_submit_button("💾 حفظ التعديلات الفورية"):
            st.session_state.products[prod_idx] = {
                "id": prod["id"],
                "name": new_name,
                "price": new_price,
                "image": new_img,
                "desc": new_desc
            }
            st.toast("🎉 تم تحديث بيانات المنتج بنجاح!")
            st.rerun()

# --- نافذة الـ Pop-up لعرض تفاصيل المنتج ---
@st.dialog("🔍 تفاصيل المنتج")
def popup_product_details(prod, idx):
    if st.session_state.is_admin:
        head_col1, head_col2 = st.columns([2, 1])
        with head_col1:
            st.write("") 
        with head_col2:
            if st.button("📝 تعديل المنتج", key="admin_edit_prod_btn"):
                st.session_state.product_to_edit = idx
                st.session_state.trigger_edit_popup = True
                st.rerun()

    det_c1, det_c2 = st.columns([1, 1.5])
    with det_c1:
        st.image(prod["image"], use_container_width=True)
    with det_c2:
        st.subheader(prod["name"])
        st.write(prod["desc"])
        st.write(f"**السعر الأساسي:** {prod['price']} جنيه")
        
        st.write("")
        if st.button("🛒 إضافة للسلة وتأكيد", key="confirm_add_to_cart_pop"):
            cart_key = f"{prod['id']}_default"
            if cart_key in st.session_state.cart: 
                st.session_state.cart[cart_key]['qty'] += 1
            else: 
                st.session_state.cart[cart_key] = {"name": prod["name"], "price": prod["price"], "qty": 1}
            st.success("تم الحفظ في السلة!")
            st.rerun()

# التحقق من تشغيل نوافذ الـ Pop-up الشرطية
if st.session_state.trigger_edit_popup and st.session_state.product_to_edit is not None:
    st.session_state.trigger_edit_popup = False
    popup_edit_product_form(st.session_state.product_to_edit)

if st.session_state.show_review_modal:
    popup_review_form()

# --- الهيدر وشريط التنقل العلوي مع عرض اللوجو بالاسم والامتداد الصحيح ---
col_logo, col_title, col_nav_buttons = st.columns([1.2, 2.3, 2.5])

with col_logo:
    st.image("Free C-10Aug25 S-21Oct25.png", use_container_width=True)

with col_title:
    st.markdown("<h1>متجر سهلة</h1>", unsafe_allow_html=True)
    st.write("أهلاً بك في متجرك المفضل للمنتجات اليدوية")

with col_nav_buttons:
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏪 المتجر الرئيسي", key="b_nav_shop"):
            st.session_state.page = "shop"
            st.rerun()
    with c2:
        if st.button("🌐 قنوات التواصل", key="b_nav_social"):
            st.session_state.page = "social"
            st.rerun()
    with c3:
        if st.button("⭐ آراء العملاء", key="b_nav_reviews"):
            st.session_state.page = "reviews"
            st.rerun()
            
    st.write("")
    ca1, ca2 = st.columns(2)
    with ca1:
        if st.session_state.is_admin:
            if st.button("🚪 خروج الأدمن", key="admin_logout_top"):
                st.session_state.is_admin = False
                st.rerun()
        else:
            if st.button("🔑 دخول الأدمن", key="admin_login_top"):
                st.session_state.show_login_section = not st.session_state.show_login_section
    with ca2:
        if st.session_state.is_admin and st.session_state.page == "shop":
            if st.button("➕ إضافة منتج جديد", key="admin_add_prod_top"):
                st.session_state.show_add_product_section = not st.session_state.show_add_product_section

st.write("---")

# ====================================================================
# 🔐 نموذج تسجيل دخول الأدمن المدمج بالصفحة
# ====================================================================
if st.session_state.show_login_section and not st.session_state.is_admin:
    with st.form("login_form_embedded"):
        secret_input = st.text_input("أدخل كود الأدمن السري", type="password")
        
        if st.form_submit_button("🔓 تأكيد الدخول"):
            if secret_input.strip() == st.session_state.admin_password:
                st.session_state.is_admin = True
                st.session_state.show_login_section = False
                st.rerun()
            else:
                st.error("❌ كود خاطئ!")

# ====================================================================
# 🔐 صندوق تغيير الباسورد (يظهر فقط للأدمن المسجل)
# ====================================================================
if st.session_state.is_admin:
    st.markdown('<div class="password-btn">', unsafe_allow_html=True)
    if st.button("🔐 تغيير كلمة مرور الأدمن", key="show_change_pass_btn"):
        st.session_state.show_change_password = not st.session_state.show_change_password
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.show_change_password:
        with st.form("change_password_form"):
            st.markdown("### 🔐 تغيير كلمة المرور")
            current_pass = st.text_input("كلمة المرور الحالية", type="password")
            new_pass = st.text_input("كلمة المرور الجديدة", type="password")
            confirm_pass = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
            
            if st.form_submit_button("💾 حفظ كلمة المرور الجديدة"):
                if current_pass.strip() != st.session_state.admin_password:
                    st.error("❌ كلمة المرور الحالية غير صحيحة!")
                elif len(new_pass.strip()) < 4:
                    st.error("❌ كلمة المرور الجديدة قصيرة جداً (4 أحرف على الأقل)")
                elif new_pass.strip() != confirm_pass.strip():
                    st.error("❌ كلمة المرور الجديدة غير متطابقة!")
                else:
                    st.session_state.admin_password = new_pass.strip()
                    st.session_state.show_change_password = False
                    st.success("✅ تم تغيير كلمة المرور بنجاح!")
                    st.balloons()

# --- صندوق إدارة الطلبات (للأدمن فقط) ---
if st.session_state.is_admin:
    with st.expander("📦 صندوق إدارة الطلبات الواردة والأوردرات الحالية", expanded=True):
        if not st.session_state.orders:
            st.info("لا توجد أوردرات معلقة حالياً.")
        else:
            for idx, order in enumerate(st.session_state.orders):
                st.markdown(f"### 📋 طلب رقم: #{order['id']} | التوقيت: {order['time']}")
                st.write(f"👤 **العميل:** {order['customer']} | 📞 {order['phone']} | 📍 {order['address']}")
                st.write("🛍️ **المنتجات:**")
                for p in order['items']:
                    st.write(f"- {p['name']} × {p['qty']}")
                st.markdown(f"💰 **إجمالي الحساب:** **{order['total']} جنيه**")
                if st.button(f"✅ تم الشحن والتسليم", key=f"clear_order_{idx}"):
                    st.session_state.orders.pop(idx)
                    st.rerun()
                st.write("---")

# ====================================================================
# --- توجيه الصفحات ---
# ====================================================================

if st.session_state.page == "social":
    st.markdown("<h2 style='text-align: center;'>🌐 روابط وقنوات التواصل الاجتماعي الخاصة بنا</h2>", unsafe_allow_html=True)
    if st.session_state.is_admin:
        with st.form("add_social_link_form"):
            p_name = st.text_input("اسم المنصة")
            p_url = st.text_input("الرابط المباشر")
            if st.form_submit_button("➕ إضافة الرابط"):
                st.session_state.social_links.append({"platform": p_name, "url": p_url})
                st.rerun()
    for s_idx, link in enumerate(st.session_state.social_links):
        st.markdown(f"### 🔗 [{link['platform']}]({link['url']})")
        if st.session_state.is_admin:
            if st.button("🗑️ حذف الرابط", key=f"del_link_{s_idx}"):
                st.session_state.social_links.pop(s_idx)
                st.rerun()

elif st.session_state.page == "reviews":
    st.markdown("<h2 style='text-align: center;'>⭐ تقييمات وآراء عملائنا الكرام</h2>", unsafe_allow_html=True)
    for rev in st.session_state.reviews:
        st.markdown(f"##### 👤 العميل: **{rev['customer']}** | {'⭐' * rev['stars']}")
        if rev["comment"]: st.info(f"💬 {rev['comment']}")
        st.write("---")

else:
    # --- صفحة المتجر الرئيسية ---
    if st.session_state.is_admin and st.session_state.show_add_product_section:
        with st.form("add_p_form_embedded"):
            p_name = st.text_input("اسم المنتج الجديد")
            p_price = st.number_input("السعر الحالي", min_value=1)
            p_img = st.text_input("رابط مباشر لصورة المنتج")
            p_desc = st.text_area("وصف تفصيلي للمنتج")
            if st.form_submit_button("✅ تنفيذ النشر بالمتجر"):
                st.session_state.products.append({
                    "id": len(st.session_state.products) + 1, "name": p_name, "price": p_price, "image": p_img, "desc": p_desc
                })
                st.session_state.show_add_product_section = False
                st.rerun()

    # تقسيم الشبكة الإفتراضي للمتجر والسلة
    col_products, col_cart = st.columns([2.6, 1.4])

    with col_products:
        st.header("✨ المنتجات المتاحة")
        products = st.session_state.products
        for i in range(0, len(products), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(products):
                    idx = i + j
                    prod = products[idx]
                    with cols[j]:
                        st.image(prod["image"], use_container_width=True)
                        st.markdown(f"### {prod['name']}")
                        st.write(f"**السعر:** {prod['price']} جنيه")
                        if st.session_state.is_admin:
                            if st.button("🗑️ حذف المنتج", key=f"del_p_{idx}"):
                                st.session_state.products.pop(idx)
                                st.rerun()
                        if st.button("🔎 تفاصيل وشراء", key=f"det_{prod['id']}_{idx}"):
                            popup_product_details(prod, idx)
                        st.write("---")

    with col_cart:
        st.header("🛒 السلة")
        if not st.session_state.cart:
            st.info("سلتك فارغة حالياً.")
        else:
            total = 0
            cart_list = []
            for k, item in list(st.session_state.cart.items()):
                st.write(f"**{item['name']}** × {item['qty']}")
                if st.button("❌ إزالة", key=f"rm_{k}"):
                    del st.session_state.cart[k]
                    st.rerun()
                total += (item['price'] * item['qty'])
                cart_list.append(item)
            
            st.markdown(f"### 💰 الإجمالي: {total} ج.م")
            
            if not st.session_state.show_checkout_otp_field:
                with st.form("checkout_form_final"):
                    c_name = st.text_input("الاسم ثنائي")
                    c_phone = st.text_input("رقم الهاتف")
                    c_addr = st.text_area("العنوان بالتفصيل")
                    if st.form_submit_button("✅ إرسال الأوردر الفوري"):
                        v, msg = ai_validate_customer_data(c_name, c_phone)
                        if not v: st.error(msg)
                        elif len(c_addr.strip()) < 10: st.error("يرجى كتابة عنوان تفصيلي")
                        else:
                            st.session_state.checkout_otp = str(random.randint(100000, 999999))
                            st.session_state.temp_order_data = {"customer": c_name, "phone": c_phone, "address": c_addr, "items": cart_list, "total": total}
                            st.session_state.show_checkout_otp_field = True
                            st.rerun()
            else:
                st.warning("🔒 يرجى كتابة كود التحقق لتأكيد طلبك:")
                st.info(f"🔑 كود التفعيل الخاص بك هو: {st.session_state.checkout_otp}")
                u_code = st.text_input("اكتب الكود المكون من 6 أرقام هنا")
                if st.button("🚀 تأكيد نهائي وإرسال الأوردر"):
                    if u_code.strip() == st.session_state.checkout_otp:
                        final_order = st.session_state.temp_order_data
                        final_order["id"] = random.randint(1000, 9999)
                        final_order["time"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        st.session_state.orders.append(final_order)
                        st.session_state.cart = {}
                        st.session_state.show_checkout_otp_field = False
                        st.session_state.show_review_modal = True
                        st.rerun()
                    else: st.error("الكود خاطئ!")