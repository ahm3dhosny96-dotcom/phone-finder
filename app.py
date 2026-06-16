import streamlit as st
import requests
import re

# إعدادات واجهة الموقع
st.set_page_config(page_title="مستخرج أرقام الشركات العالمي", page_icon="📞", layout="centered")

st.title("📞 مستخرج أرقام الشركات العالمي (النسخة الاحترافية)")
st.write("اكتب اسم أي شركة عالمية، والسيستم هيجيبلك رقم تليفونها مباشرة من نتائج جوجل الرسمية وبدون حظر.")

# القائمة الجانبية لإدخال المفتاح المجاني
with st.sidebar:
    st.header("⚙️ إعدادات الربط المجاني")
    serper_api_key = st.text_input("أدخل مفتاح Serper API الخاص بك:", type="password")
    st.markdown("[اضغط هنا للحصول على مفتاح مجاني في ثوانٍ](https://serper.dev)")
    st.caption("ملاحظة: الموقع يعطيك 2500 عملية بحث مجاناً بالكامل وبدون طلب كارت فيزا.")

# خانة البحث الرئيسية
company_name = st.text_input("اكتب اسم الشركة هنا (مثال: Prometheus Group أو Caldwell Tanks):")

if st.button("ابحث عن الرقم الآن", use_container_width=True):
    if not serper_api_key:
        st.error("❌ من فضلك أدخل مفتاح Serper API في القائمة الجانبية أولاً.")
    elif not company_name:
        st.warning("⚠️ من فضلك اكتب اسم الشركة أولاً.")
    else:
        with st.spinner("جاري البحث في جوجل جيتواي العالمي..."):
            try:
                url = "https://google.serper.dev/search"
                # صياغة بحث ذكية جداً للوصول للمقرات الرئيسية للشركات العالمية
                query = f"{company_name} corporate headquarters phone number"
                payload = {"q": query, "gl": "us", "hl": "en"}
                headers = {
                    'X-API-KEY': serper_api_key,
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    all_numbers = []
                    
                    # 1. فحص كارت معلومات جوجل (Knowledge Graph) - ده بيجيب الرقم الرسمي للشركة بدقة شديدة
                    kg = data.get("knowledgeGraph", {})
                    if kg:
                        attributes = kg.get("attributes", {})
                        # محاولة استخراج التليفون بأكثر من صيغة مسمية جوه جوجل
                        phone_from_kg = attributes.get("Phone") or attributes.get("phone") or kg.get("phone")
                        if phone_from_kg:
                            all_numbers.append(phone_from_kg)
                            st.success(f"🏢 تم العثور على الشركة في كارت معرفة جوجل: **{kg.get('title', company_name)}**")
                    
                    # 2. فحص نتائج البحث العادية واستخراج الأرقام منها عبر الـ Regex
                    organic = data.get("organic", [])
                    if organic:
                        # نمط Regex متطور جداً لجلب الأرقام الدولية والـ 1-800 الأمريكي بجميع الصيغ
                        phone_pattern = r'(\+\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}|\b\d{3}[-.]\d{3}[-.]\d{4}\b|\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b)'
                        
                        for res in organic:
                            snippet = res.get("snippet", "")
                            title = res.get("title", "")
                            full_text = f"{title} {snippet}"
                            
                            found = re.findall(phone_pattern, full_text)
                            for num in found:
                                num_clean = num.strip()
                                digits_only = re.sub(r'\D', '', num_clean)
                                # التأكد من إنه رقم حقيقي وليس تاريخ أو رقم قصير
                                if len(digits_only) >= 7 and num_clean not in all_numbers:
                                    all_numbers.append(num_clean)
                            
                            # عرض ملخص النتيجة
                            st.info(f"🔗 **{res.get('title')}**\n{snippet}")
                    
                    # عرض الأرقام المستخرجة النهائية
                    if all_numbers:
                        st.write("---")
                        st.subheader("📱 الأرقام المباشرة المكتشفة للشركة:")
                        for n in all_numbers:
                            st.success(f"📞 **{n}**")
                    else:
                        st.warning("⚠️ تم جلب تفاصيل وروابط الشركة بنجاح (موضحة بالأعلى)، ولكن لم يتم العثور على رقم تليفون واضح مكتوب في ملخص الصفحة الأولى.")
                else:
                    st.error("❌ مفتاح الـ API غير صحيح، أو انتهت صلاحيته.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال: {e}")
