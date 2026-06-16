import streamlit as st
import requests

# إعدادات الصفحة
st.set_page_config(page_title="مستخرج أرقام الشركات", page_icon="📞", layout="centered")

# تصميم الواجهة
st.title("📞 مستخرج أرقام تليفونات الشركات")
st.write("اكتب اسم الشركة بدقة (ويفضل كتابة المحافظة أو المنطقة مع الاسم) وهيطلعلك رقم التليفون والعنوان من جوجل مابس.")

# القائمة الجانبية لإدخال الـ API Key لحماية بياناتك
with st.sidebar:
    st.header("⚙️ إعدادات الربط")
    api_key = st.text_input("أدخل مفتاح Google Places API:", type="password")
    st.markdown("""
    [اضغط هنا لمعرفة كيف تحصل على مفتاح API مجاني](https://developers.google.com/maps/documentation/places/web-service/overview)
    """)
    st.write("---")
    st.caption("ملاحظة: يتم استخدام المفتاح مباشرة للاتصال بجوجل ولا يتم حفظه لدينا.")

# الخانة الرئيسية للبحث
company_name = st.text_input("اسم الشركة (مثال: فودافون القرية الذكية أو مستشفى البرج بالجيزة):")

# زر البدء
if st.button("ابحث عن الرقم الآن", use_container_width=True):
    if not api_key:
        st.error("❌ من فضلك أدخل مفتاح Google Places API في القائمة الجانبية أولاً.")
    elif not company_name:
        st.warning("⚠️ من فضلك اكتب اسم الشركة التي تريد البحث عنها.")
    else:
        with st.spinner("جاري البحث في قاعدة بيانات جوجل مابس..."):
            try:
                # الخطوة 1: البحث عن الشركة لجلب الـ Place ID
                search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={company_name}&key={api_key}&language=ar"
                search_response = requests.get(search_url).json()

                if search_response.get("status") == "OK":
                    results = search_response.get("results", [])
                    if results:
                        place_id = results[0]["place_id"]
                        
                        # الخطوة 2: جلب تفاصيل الشركة ورقم التليفون باستخدام الـ Place ID
                        details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number,formatted_address,rating&key={api_key}&language=ar"
                        details_response = requests.get(details_url).json()
                        
                        if details_response.get("status") == "OK":
                            result = details_response.get("result", {})
                            name = result.get("name", "غير معروف")
                            phone = result.get("formatted_phone_number", "🚫 لا يوجد رقم تليفون مسجل لهذه الشركة على جوجل")
                            address = result.get("formatted_address", "غير متوفر")
                            rating = result.get("rating", "لا يوجد تقييم")

                            # عرض النتائج بشكل منظم
                            st.success("✅ تم العثور على البيانات بنجاح!")
                            
                            st.subheader(f"🏢 {name}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(label="📞 رقم التليفون", value=phone)
                            with col2:
                                st.metric(label="⭐ التقييم على جوجل", value=str(rating))
                            
                            st.info(f"📍 **العنوان:** {address}")
                        else:
                            st.error("حدث خطأ أثناء جلب تفاصيل الشركة من جوجل.")
                    else:
                        st.error("لم يتم العثور على أي شركة بهذا الاسم.")
                elif search_response.get("status") == "REQUEST_DENIED":
                    st.error("❌ مفتاح الـ API غير صحيح أو لم يتم تفعيل الـ Places API عليه.")
                else:
                    st.error(f"خطأ من جوجل مابس: {search_response.get('status')}")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
