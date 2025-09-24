import streamlit as st
import pandas as pd
import io
from datetime import datetime
import base64

# إعداد الصفحة
st.set_page_config(
    page_title="فاتورة زيت زيتون سيوة",
    page_icon="🫒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS للتصميم العربي
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2F4F2F 0%, #228B22 50%, #32CD32 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .company-name {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .company-slogan {
        font-size: 1rem;
        opacity: 0.9;
        font-style: italic;
    }
    
    .info-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #32CD32;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }
    
    .total-card {
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #32CD32;
        box-shadow: 0 5px 15px rgba(50, 205, 50, 0.1);
    }
    
    .final-total {
        background: linear-gradient(90deg, #32CD32, #228B22);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        margin-top: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .footer-style {
        background: linear-gradient(135deg, #2F4F2F, #228B22);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 2rem;
    }
    
    /* Right-to-left support */
    .rtl {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'products' not in st.session_state:
    st.session_state.products = []

if 'customer_data' not in st.session_state:
    st.session_state.customer_data = {
        'name': 'أحمد محمد علي',
        'phone': '01234567890', 
        'address': 'القاهرة، مصر',
        'order_id': 'SW-2024-001'
    }

if 'shipping_cost' not in st.session_state:
    st.session_state.shipping_cost = 50.0

# Header
st.markdown("""
<div class="main-header">
    <div style="font-size: 3rem; margin-bottom: 1rem;">🫒</div>
    <div class="company-name">شركة زيت زيتون سيوة</div>
    <div class="company-slogan">من أجود بساتين واحة سيوة المصرية</div>
</div>
""", unsafe_allow_html=True)

# Sidebar for data management
with st.sidebar:
    st.header("🌿 إدارة الفاتورة")
    
    # File upload/download section
    st.subheader("📊 إدارة الملفات")
    
    # Download template button
    def create_template():
        template_data = {
            'اسم العميل': ['', '', '', ''],
            'رقم الهاتف': ['', '', '', ''],
            'العنوان': ['', '', '', ''],
            'رقم الطلب': ['', '', '', ''],
            'مصاريف الشحن': [50, '', '', ''],
            'اسم المنتج': ['', '', '', ''],
            'الحجم': ['', '', '', ''],
            'الكمية': ['', '', '', ''],
            'السعر': ['', '', '', '']
        }
        return pd.DataFrame(template_data)
    
    if st.button("📥 تحميل شيت فارغ"):
        template_df = create_template()
        
        # Convert to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            template_df.to_excel(writer, sheet_name='الفاتورة', index=False)
        
        st.download_button(
            label="📁 حفظ الملف",
            data=output.getvalue(),
            file_name="فاتورة_زيت_زيتون_سيوة.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("✅ تم إنشاء الشيت! اضغط 'حفظ الملف' لتحميله")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📤 رفع شيت مكتمل", 
        type=['xlsx', 'xls'],
        help="ارفع ملف Excel يحتوي على بيانات العميل والمنتجات"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            
            # Clear existing products
            st.session_state.products = []
            
            # Extract customer data (from first non-empty row)
            customer_name = ''
            customer_phone = ''
            customer_address = ''
            order_id = ''
            shipping = 50.0
            
            for idx, row in df.iterrows():
                if not customer_name and pd.notna(row['اسم العميل']) and row['اسم العميل']:
                    customer_name = str(row['اسم العميل'])
                if not customer_phone and pd.notna(row['رقم الهاتف']) and row['رقم الهاتف']:
                    customer_phone = str(row['رقم الهاتف'])
                if not customer_address and pd.notna(row['العنوان']) and row['العنوان']:
                    customer_address = str(row['العنوان'])
                if not order_id and pd.notna(row['رقم الطلب']) and row['رقم الطلب']:
                    order_id = str(row['رقم الطلب'])
                if pd.notna(row['مصاريف الشحن']) and row['مصاريف الشحن']:
                    try:
                        shipping = float(row['مصاريف الشحن'])
                    except:
                        pass
                
                # Extract product data
                if (pd.notna(row['اسم المنتج']) and row['اسم المنتج'] and
                    pd.notna(row['الحجم']) and row['الحجم'] and
                    pd.notna(row['الكمية']) and row['الكمية'] and
                    pd.notna(row['السعر']) and row['السعر']):
                    
                    try:
                        product = {
                            'name': str(row['اسم المنتج']),
                            'size': str(row['الحجم']),
                            'quantity': float(row['الكمية']),
                            'price': float(row['السعر'])
                        }
                        if product['quantity'] > 0 and product['price'] > 0:
                            st.session_state.products.append(product)
                    except:
                        continue
            
            # Update session state
            if customer_name:
                st.session_state.customer_data['name'] = customer_name
            if customer_phone:
                st.session_state.customer_data['phone'] = customer_phone
            if customer_address:
                st.session_state.customer_data['address'] = customer_address
            if order_id:
                st.session_state.customer_data['order_id'] = order_id
            st.session_state.shipping_cost = shipping
            
            st.success(f"✅ تم تحميل البيانات!\n🧑‍💼 العميل: {customer_name or 'غير محدد'}\n📦 المنتجات: {len(st.session_state.products)}")
            
        except Exception as e:
            st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
    
    st.divider()
    
    # Manual product entry
    st.subheader("📝 إضافة منتج يدوياً")
    
    with st.form("add_product_form", clear_on_submit=True):
        product_name = st.text_input("اسم المنتج", placeholder="زيت زيتون بكر ممتاز")
        
        col1, col2 = st.columns(2)
        with col1:
            product_size = st.text_input("الحجم", placeholder="500 مل")
        with col2:
            product_quantity = st.number_input("الكمية", min_value=1, value=1)
        
        product_price = st.number_input("السعر", min_value=0.0, value=0.0, step=1.0)
        
        submitted = st.form_submit_button("➕ إضافة المنتج")
        
        if submitted:
            if product_name and product_size and product_price > 0:
                new_product = {
                    'name': product_name,
                    'size': product_size,
                    'quantity': product_quantity,
                    'price': product_price
                }
                st.session_state.products.append(new_product)
                st.success("✅ تم إضافة المنتج!")
                st.rerun()
            else:
                st.error("⚠️ يرجى ملء جميع البيانات")
    
    # Sample products
    if st.button("📦 تحميل منتجات تجريبية"):
        st.session_state.products = [
            {'name': 'زيت زيتون بكر ممتاز - عضوي', 'size': '500 مل', 'quantity': 3, 'price': 175},
            {'name': 'زيت زيتون مضغوط على البارد', 'size': '1 لتر', 'quantity': 2, 'price': 320},
            {'name': 'زيت زيتون للطبخ - درجة أولى', 'size': '750 مل', 'quantity': 4, 'price': 145}
        ]
        st.success("✅ تم تحميل المنتجات التجريبية!")
        st.rerun()
    
    st.divider()
    
    # Customer info
    st.subheader("👤 بيانات العميل")
    
    st.session_state.customer_data['name'] = st.text_input(
        "اسم العميل", 
        value=st.session_state.customer_data['name']
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.customer_data['phone'] = st.text_input(
            "رقم الهاتف", 
            value=st.session_state.customer_data['phone']
        )
    with col2:
        st.session_state.customer_data['order_id'] = st.text_input(
            "رقم الطلب", 
            value=st.session_state.customer_data['order_id']
        )
    
    st.session_state.customer_data['address'] = st.text_area(
        "العنوان", 
        value=st.session_state.customer_data['address'],
        height=80
    )
    
    st.session_state.shipping_cost = st.number_input(
        "مصاريف الشحن", 
        min_value=0.0, 
        value=st.session_state.shipping_cost, 
        step=1.0
    )
    
    if st.button("🗑️ مسح جميع البيانات"):
        if st.button("✅ تأكيد المسح", key="confirm_clear"):
            st.session_state.products = []
            st.session_state.customer_data = {
                'name': '',
                'phone': '', 
                'address': '',
                'order_id': ''
            }
            st.session_state.shipping_cost = 50.0
            st.success("✅ تم مسح جميع البيانات!")
            st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Company and customer info
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        <div class="info-card">
            <h4>🏢 بيانات الشركة</h4>
            <p><strong>العنوان:</strong> واحة سيوة، مصر</p>
            <p><strong>الهاتف:</strong> +20 123 456 7890</p>
            <p><strong>البريد:</strong> info@siwa-olive.com</p>
            <p><strong>التاريخ:</strong> """ + datetime.now().strftime('%Y-%m-%d') + """</p>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown(f"""
        <div class="info-card">
            <h4>👤 بيانات العميل</h4>
            <p><strong>الاسم:</strong> {st.session_state.customer_data['name'] or 'غير محدد'}</p>
            <p><strong>الهاتف:</strong> {st.session_state.customer_data['phone'] or 'غير محدد'}</p>
            <p><strong>العنوان:</strong> {st.session_state.customer_data['address'] or 'غير محدد'}</p>
            <p><strong>رقم الطلب:</strong> {st.session_state.customer_data['order_id'] or 'غير محدد'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Products table
    st.subheader("🛒 تفاصيل الطلبية")
    
    if st.session_state.products:
        # Create DataFrame for products
        products_data = []
        for i, product in enumerate(st.session_state.products):
            products_data.append({
                'المنتج': product['name'],
                'الحجم': product['size'],
                'الكمية': product['quantity'],
                'السعر': f"{product['price']:.2f} ج",
                'الإجمالي': f"{product['quantity'] * product['price']:.2f} ج"
            })
        
        products_df = pd.DataFrame(products_data)
        
        # Display table with edit/delete options
        for i, product in enumerate(st.session_state.products):
            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
            
            with col1:
                st.text(product['name'])
            with col2:
                st.text(product['size'])
            with col3:
                new_quantity = st.number_input(
                    "الكمية", 
                    min_value=1, 
                    value=int(product['quantity']), 
                    key=f"qty_{i}"
                )
                if new_quantity != product['quantity']:
                    st.session_state.products[i]['quantity'] = new_quantity
                    st.rerun()
            with col4:
                new_price = st.number_input(
                    "السعر", 
                    min_value=0.0, 
                    value=float(product['price']), 
                    step=1.0,
                    key=f"price_{i}"
                )
                if new_price != product['price']:
                    st.session_state.products[i]['price'] = new_price
                    st.rerun()
            with col5:
                st.text(f"{product['quantity'] * product['price']:.2f} ج")
            with col6:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.products.pop(i)
                    st.rerun()
        
    else:
        st.info("📦 لا توجد منتجات مضافة بعد. استخدم الشريط الجانبي لإضافة المنتجات.")

with col2:
    # Totals calculation
    if st.session_state.products:
        subtotal = sum(product['quantity'] * product['price'] for product in st.session_state.products)
        final_total = subtotal + st.session_state.shipping_cost
        
        st.markdown(f"""
        <div class="total-card">
            <h4>💰 ملخص الفاتورة</h4>
            <p><strong>المجموع الفرعي:</strong> {subtotal:.2f} ج</p>
            <p><strong>الشحن والتوصيل:</strong> {st.session_state.shipping_cost:.2f} ج</p>
            <div class="final-total">
                إجمالي المبلغ المطلوب: {final_total:.2f} ج
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Export to Excel
        if st.button("📊 تصدير إلى Excel"):
            # Create export data
            export_data = []
            for product in st.session_state.products:
                export_data.append({
                    'اسم العميل': st.session_state.customer_data['name'],
                    'رقم الهاتف': st.session_state.customer_data['phone'],
                    'العنوان': st.session_state.customer_data['address'],
                    'رقم الطلب': st.session_state.customer_data['order_id'],
                    'مصاريف الشحن': st.session_state.shipping_cost,
                    'اسم المنتج': product['name'],
                    'الحجم': product['size'],
                    'الكمية': product['quantity'],
                    'السعر': product['price'],
                    'إجمالي المنتج': product['quantity'] * product['price']
                })
            
            # Add totals row
            export_data.append({
                'اسم العميل': 'المجموع الفرعي',
                'رقم الهاتف': '',
                'العنوان': '',
                'رقم الطلب': '',
                'مصاريف الشحن': st.session_state.shipping_cost,
                'اسم المنتج': '',
                'الحجم': '',
                'الكمية': sum(p['quantity'] for p in st.session_state.products),
                'السعر': '',
                'إجمالي المنتج': subtotal
            })
            
            export_data.append({
                'اسم العميل': 'الإجمالي النهائي',
                'رقم الهاتف': '',
                'العنوان': '',
                'رقم الطلب': '',
                'مصاريف الشحن': '',
                'اسم المنتج': '',
                'الحجم': '',
                'الكمية': '',
                'السعر': '',
                'إجمالي المنتج': final_total
            })
            
            df_export = pd.DataFrame(export_data)
            
            # Convert to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, sheet_name='الفاتورة', index=False)
            
            st.download_button(
                label="💾 حفظ الفاتورة",
                data=output.getvalue(),
                file_name=f"فاتورة_{st.session_state.customer_data['order_id']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    else:
        st.markdown("""
        <div class="total-card">
            <h4>💰 ملخص الفاتورة</h4>
            <p><strong>المجموع الفرعي:</strong> 0.00 ج</p>
            <p><strong>الشحن والتوصيل:</strong> 50.00 ج</p>
            <div class="final-total">
                إجمالي المبلغ المطلوب: 50.00 ج
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer-style">
    <p><strong>🌿 شكراً لثقتكم في منتجات زيت زيتون سيوة 🌿</strong></p>
    <p>زيت زيتون طبيعي 100% • مضغوط على البارد • خالي من المواد الحافظة</p>
    <p>للاستفسارات والطلبات: info@siwa-olive.com | واتساب: +20 123 456 7890</p>
    <p>🫒 "من قلب الصحراء.. إلى مائدتكم" 🫒</p>
</div>
""", unsafe_allow_html=True)