import streamlit as st
import requests
import re

# إعدادات واجهة الموقع
st.set_page_config(page_title="مستخرج أرقام الشركات العالمي", page_icon="📞", layout="centered")

st.title("📞 مستخرج أرقام الشركات العالمي (النسخة الذكية)")
st.write("اكتب اسم أي شركة عالمية من القائمة بتاعتك، والسيستم هيلف على شبكة سيرفرات مفتوحة عشان يضمن جلب الأرقام بدون حظر.")

# خانة البحث
company_name = st.text_input("اكتب اسم الشركة هنا (مثال: Prometheus Group أو Caldwell Tanks):")

# قائمة بالسيرفرات الوسيطة العامة المفتوحة لتفادي الحظر أوتوماتيكياً
INSTANCES = [
    "https://searx.be",
    "https://search.mdcnet.de",
    "https://searx.priv.tech",
    "https://baresearch.org"
]

if st.button("ابحث عن الرقم الآن", use_container_width=True):
    if not company_name:
        st.warning("⚠️ من فضلك اكتب اسم الشركة أولاً.")
    else:
        with st.spinner("جاري الاتصال بالشبكة الآمنة وجلب أرقام الشركة..."):
            # صياغة جملة البحث للوصول للمقرات الرئيسية للشركات العالمية
            query = f"{company_name} corporate headquarters phone number contact"
            success = False
            results = []
            
            # المحاولة عبر السيرفرات الوسيطة المتاحة واحد تلو الآخر
            for instance in INSTANCES:
                try:
                    response = requests.get(
                        f"{instance}/search", 
                        params={"q": query, "format": "json", "lang": "en"},
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        if results:
                            success = True
                            break  # وجدنا نتائج بنجاح، اخرج من اللوب فوراً
                except:
                    continue  # لو السيرفر ده واقع أو بطيء جرب اللي بعده تلقائياً
            
            if success:
                st.success("✅ تم الاتصال بنجاح واستخراج بيانات الشركة أونلاين:")
                all_numbers = []
                
                # نمط Regex متطور جداً لالتقاط الأرقام الدولية والأمريكية بجميع صيغها (مثل 1-800 أو أرقام المكاتب)
                phone_pattern = r'(\+\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}|\b\d{3}[-.]\d{3}[-.]\d{4}\b|\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b)'
                
                for res in results:
                    title = res.get("title", "")
                    content = res.get("content", "")
                    full_text = f"{title} {content}"
                    
                    # استخراج الأرقام من العنوان أو الخلاصة
                    found = re.findall(phone_pattern, full_text)
                    for num in found:
                        num_clean = num.strip()
                        # فلترة الأرقام عشان نتأكد إنها مش تواريخ (مثل 2026) أو أرقام عشوائية قصيرة
                        digits_only = re.sub(r'\D', '', num_clean)
                        if len(digits_only) >= 7 and num_clean not in all_numbers:
                            all_numbers.append(num_clean)
                    
                    # عرض خلاصة النتيجة للمستخدم ليراها بنفسه كدليل
                    st.info(f"🔗 **المصدر:** {content}")
                
                # عرض قائمة الأرقام المستخرجة بشكل منظم وجذاب
                if all_numbers:
                    st.write("---")
                    st.subheader("📱 الأرقام المباشرة المكتشفة للشركة:")
                    for n in all_numbers:
                        st.success(f"📞 **{n}**")
                else:
                    st.warning("⚠️ جلبنا تفاصيل الشركة بنجاح (موضحة في السطور الزرقاء فوق)، لكن لم نجد رقم تليفون واضح مكتوب وسط النصوص المتاحة. يمكنك مراجعة النصوص بالأعلى يدوياً.")
            else:
                st.error("❌ السيرفرات مشغولة حالياً أو لم تعثر على نتائج دقيقة. يرجى الضغط على زر البحث مرة أخرى بعد ثوانٍ قليلة.")
