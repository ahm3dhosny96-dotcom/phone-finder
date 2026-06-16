import streamlit as st
import urllib.request
import urllib.parse
import re

# إعدادات واجهة الموقع
st.set_page_config(page_title="مستخرج أرقام الشركات العالمي", page_icon="📞", layout="centered")

st.title("📞 مستخرج أرقام الشركات العالمي")
st.write("اكتب اسم أي شركة (محلية أو عالمية بالإنجليزي) وهيستخرج لك أرقام التليفونات المتاحة ليها أونلاين.")

# خانة البحث
company_name = st.text_input("اكتب اسم الشركة (مثال: Prometheus Group أو Actalent):")

if st.button("ابحث عن الرقم الآن", use_container_width=True):
    if not company_name:
        st.warning("⚠️ من فضلك اكتب اسم الشركة أولاً.")
    else:
        with st.spinner("جاري البحث في السيرفرات العالمية وجلب الأرقام..."):
            try:
                # تحديد نوع البحث بناءً على لغة اسم الشركة
                # لو الاسم فيه حروف إنجليزي، هيقرب البحث للصيغة الدولية
                if re.search(r'[a-zA-Z]', company_name):
                    query = f"{company_name} corporate headquarters phone number contact hotline"
                else:
                    query = f"{company_name} رقم تليفون تليفونات الخط الساخن الرئيسي"
                
                encoded_query = urllib.parse.quote(query)
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                # إرسال الطلب بحماية متصفح كاملة
                req = urllib.request.Request(
                    url, 
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    html_content = response.read().decode('utf-8')
                
                # استخراج نصوص نتائج البحث
                snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html_content, re.DOTALL)
                
                if snippets:
                    st.success("✅ تم العثور على معلومات الشركة أونلاين:")
                    
                    all_numbers = []
                    
                    # الـ Regex الجديد لالتقاط الأرقام الدولية والمحلية والـ 1-800 الأمريكي
                    # بيجيب الأرقام اللي فيها مفاتيح دولية أو صيغ أمريكية وأوروبية والمصرية برضه
                    phone_pattern = r'(\+\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}|\b\d{3}[-.]\d{3}[-.]\d{4}\b|01[0125]\d{8}|02\d{7,8})'
                    
                    for snippet in snippets:
                        clean_text = re.sub(r'<[^>]+>', '', snippet).strip()
                        
                        # استخراج الأرقام من النص
                        numbers = re.findall(phone_pattern, clean_text)
                        
                        if numbers:
                            for num in numbers:
                                # تنظيف الرقم من أي مسافات زيادة والتأكد إنه مش سنة (زي 2026)
                                num_clean = num.strip()
                                if len(re.sub(r'\D', '', num_clean)) >= 7 and num_clean not in all_numbers:
                                    all_numbers.append(num_clean)
                        
                        # عرض النص المستخرج عشان المستخدم يقدر يقراه بنفسه لو الرقم جوه السياق
                        st.info(f"🔹 {clean_text}")
                    
                    # عرض قائمة الأرقام المصفاة في النهاية بشكل واضح
                    if all_numbers:
                        st.write("---")
                        st.subheader("📱 الأرقام المباشرة المكتشفة:")
                        for n in all_numbers:
                            st.success(f"📞 **{n}**")
                    else:
                        st.warning("⚠️ تم العثور على بيانات الشركة، لكن الأرقام لم يتم تصفيتها تلقائياً. يمكنك مراجعة النصوص الزرقاء فوق لمعرفة الرقم يدوياً.")
                else:
                    st.error("❌ لم نجد أي نتائج لهذه الشركة، تأكد من صحة الحروف.")
                    
            except Exception as e:
                st.error("حدث ضغط مؤقت على السيرفر، يرجى الضغط على زر البحث مرة أخرى.")
