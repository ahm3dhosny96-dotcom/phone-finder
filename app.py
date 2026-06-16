import streamlit as st
import urllib.request
import urllib.parse
import re

# إعدادات واجهة الموقع
st.set_page_config(page_title="مستخرج أرقام الشركات", page_icon="📞", layout="centered")

st.title("📞 مستخرج أرقام الشركات (النسخة المجانية المفتوحة)")
st.write("ابحث عن رقم تليفون أي شركة أو مستشفى أو مكان في مصر بدون أي اشتراكات أو كروت.")

# خانة البحث
company_name = st.text_input("اكتب اسم الشركة (مثال: فودافون القرية الذكية أو مستشفى البرج بالجيزة):")

if st.button("ابحث عن الرقم الآن", use_container_width=True):
    if not company_name:
        st.warning("⚠️ من فضلك اكتب اسم الشركة أولاً.")
    else:
        with st.spinner("جاري البحث وجلب الأرقام أونلاين..."):
            try:
                # تجهيز جملة البحث وتشفيرها ليفهمها السيرفر
                query = f"{company_name} رقم تليفون تليفونات الخط الساخن"
                encoded_query = urllib.parse.quote(query)
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                # إرسال الطلب كأننا متصفح عادي لمنع الحظر
                req = urllib.request.Request(
                    url, 
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    html_content = response.read().decode('utf-8')
                
                # استخراج النصوص والملخصات من نتائج البحث
                snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html_content, re.DOTALL)
                
                if snippets:
                    st.success("✅ تم العثور على معلومات ونتايج للمكان:")
                    
                    all_numbers = []
                    
                    for snippet in snippets:
                        # تنظيف النص من أي أكواد داخلية
                        clean_text = re.sub(r'<[^>]+>', '', snippet).strip()
                        
                        # تصفية الأرقام (موبايل مصر، أرضي، أو خطوط ساخنة خماسية)
                        phone_pattern = r'(01[0125]\d{8}|02\d{7,8}|\b1[69]\d{3}\b)'
                        numbers = re.findall(phone_pattern, clean_text)
                        
                        if numbers:
                            for num in numbers:
                                if num not in all_numbers:
                                    all_numbers.append(num)
                            # عرض سياق النص عشان تتأكد
                            st.info(f"🔹 {clean_text}")
                    
                    # عرض الأرقام المستخرجة في النهاية بشكل شيك
                    if all_numbers:
                        st.write("---")
                        st.subheader("📱 الأرقام المباشرة التي تم العثور عليها:")
                        for n in all_numbers:
                            st.success(f"📞 **{n}**")
                    else:
                        st.warning("⚠️ تم العثور على تفاصيل الشركة أونلاين ولكن لم نجد رقم تليفون واضح مكتوب في الملخصات فوق. جرب تعديل اسم البحث.")
                else:
                    st.error("❌ لم نجد أي نتائج لهذه الشركة، تأكد من كتابة الاسم الصحيح.")
                    
            except Exception as e:
                st.error("حدث ضغط مؤقت على السيرفر، برجاء الضغط على زر البحث مرة أخرى.")
