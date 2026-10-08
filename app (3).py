import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re, html

st.set_page_config(page_title="SSUET Electrical AI Agent", page_icon="⚡", layout="wide")

BASE="https://www.ssuet.edu.pk"
BS=f"{BASE}/program/foece/bs-electrical-engineering/"
MS=f"{BASE}/program/foece/ms-electrical-engineering/"
BET=f"{BASE}/program/foece/be-tech-electrical/"
ADMISSION=f"{BASE}/wp-content/uploads/UG-Admission-Policy-2025-26.pdf"

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:linear-gradient(135deg,#f7fbff,#eef7ff 48%,#f8f0ff)}
.hero{padding:32px;border-radius:26px;color:white;background:linear-gradient(135deg,#082f49,#087f8c,#6d28d9);box-shadow:0 18px 45px #0f172a22;margin-bottom:22px}
.hero h1{font-size:38px;margin:5px 0}.hero p{font-size:16px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:20px;padding:20px;margin:10px 0;box-shadow:0 8px 25px #0f172a10}
.metric{background:#fff;border-radius:18px;padding:18px;text-align:center;border:1px solid #e2e8f0}
.metric b{display:block;font-size:28px;color:#087f8c}
.fac{background:#fff;border-radius:18px;border:1px solid #e2e8f0;padding:14px;text-align:center;min-height:220px;box-shadow:0 8px 22px #0f172a0d}
.fac img{width:105px;height:105px;border-radius:50%;object-fit:cover;border:4px solid #e0f2fe}
.small{color:#64748b;font-size:13px}
</style>""",unsafe_allow_html=True)

HEAD={"User-Agent":"Mozilla/5.0 SSUET-Electrical-AI-Agent/1.0"}

@st.cache_data(ttl=3600)
def fetch(url):
    try:
        r=requests.get(url,headers=HEAD,timeout=20)
        r.raise_for_status()
        return r.text
    except Exception:
        return ""

def text_of(url):
    raw=fetch(url)
    if not raw:return ""
    s=BeautifulSoup(raw,"html.parser")
    for x in s(["script","style","noscript","svg"]):x.decompose()
    return re.sub(r"\s+"," ",html.unescape(s.get_text(" ",strip=True)))

@st.cache_data(ttl=3600)
def faculty():
    s=BeautifulSoup(fetch(BS),"html.parser")
    out=[];seen=set()
    roles=["Chairperson","Professor","Associate Professor","Assistant Professor","Senior Lecturer","Lecturer","Junior Lecturer"]
    for a in s.find_all("a",href=True):
        name=re.sub(r"\s+"," ",a.get_text(" ",strip=True))
        if len(name)<5 or name in seen:continue
        ctx=re.sub(r"\s+"," ",a.parent.get_text(" ",strip=True))
        if not any(k in name.lower() for k in ["dr.","engr.","bineesh","muhammad","syed","faiza","aamir","rabika","jeffery"]):continue
        role=next((r for r in roles if r.lower() in ctx.lower()),"Faculty Member")
        img=None
        for p in [a]+list(a.parents)[:3]:
            im=p.find("img") if hasattr(p,"find") else None
            if im and im.get("src"):
                img=urljoin(BASE,im["src"]);break
        out.append((name,role,img,urljoin(BASE,a["href"])))
        seen.add(name)
    if len(out)<5:
        names=[("Dr. Muhammad Ibrar ul Haque","Chairperson, Professor"),("Dr. Tarique Aziz","Assistant Professor"),("Dr. Manzar Ahmed","Assistant Professor"),("Engr. M. Nadeem Iqbal","Assistant Professor"),("Engr. Syed Faisal Hoda","Assistant Professor"),("Engr. Fawad Shaukat","Assistant Professor"),("Engr. Sheikh Junaid Yawar","Assistant Professor"),("Engr. Zafar Ahmed","Assistant Professor"),("Engr. Muhammad Javeed","Assistant Professor"),("Dr. Andaleeb Ali","Senior Lecturer"),("Engr. Faiza Waqqas","Senior Lecturer"),("Engr. Aamir Ali","Senior Lecturer"),("Engr. Jawad Ali Arshad","Senior Lecturer"),("Engr. Jeffery Ali Rizvi","Senior Lecturer"),("Bineesh Fayyaz","Senior Lecturer"),("Engr. Rabika Tariq","Lecturer"),("Engr. Muhammad Muzammil","Lecturer"),("Engr. Muhammad Tanveer","Lecturer"),("Engr. Mr. Syed Faraz Liaquat","Junior Lecturer")]
        out=[(n,r,None,BS) for n,r in names]
    return out

sources=[("BS Electrical Engineering",BS),("MS Electrical Engineering",MS),("B.E Tech Electrical",BET),("SSUET Home",BASE+"/")]

@st.cache_data(ttl=3600)
def knowledge():
    return [(n,u,text_of(u)) for n,u in sources]

def agent(q):
    q=q.lower().strip()
    if any(x in q for x in ["vision"]):
        return "The Electrical Engineering Department vision is to enhance teaching and research, provide excellent education, equip students with professional and entrepreneurial skills, contribute to the national economy, cope with market challenges, and meet international requirements."
    if "mission" in q:
        return "The department mission is to connect practical environment with theoretical knowledge for high-quality education and research, promote excellence in education and industrial practices, build a strong foundation for future challenges, and promote morals, dignity and ethical professional practice."
    if any(x in q for x in ["faculty","teacher","professor","lecturer"]):
        return "Open **Faculty Directory** to see the current faculty list, designation and available official photos."
    if any(x in q for x in ["admission","eligibility","apply","entry test","merit"]):
        return "The official UG Admission Policy includes **BS Electrical Engineering** and **B.E Tech (Electrical)** under FoECE. Admission is subject to eligibility, merit and seat availability. Use the official policy link in the Admissions tab for exact current requirements, dates and fees."
    if any(x in q for x in ["program","degree","bs electrical","ms electrical","renewable","b.e tech"]):
        return "The Electrical Engineering Department page lists **BS Electrical Engineering, BS Renewable Energy System, B.E Tech (Electrical), and MS Electrical Engineering**."
    if "peo" in q or "plo" in q:
        return "I will not invent official PEO/PLO statements. They were not verified on the current publicly indexed Electrical Department page. Upload the approved department PEO/PLO document to make this a controlled accreditation knowledge base."
    if "contact" in q or "phone" in q:
        return "The SSUET website currently displays the main contact number **+92 21 34988000-1**."
    words=set(re.findall(r"[a-z0-9]+",q))
    best=[]
    for n,u,t in knowledge():
        score=sum(t.lower().count(w) for w in words if len(w)>2)
        if score:best.append((score,n,u,t))
    best.sort(reverse=True)
    if not best:return "Try: faculty, admission, programs, vision, mission, PEO, PLO, curriculum, facilities, or contact."
    return "\n\n".join(f"**{n}**\n{t[:900]}...\nSource: {u}" for _,n,u,t in best[:3])

st.markdown("""<div class="hero"><div>⚡ API-FREE • SSUET ELECTRICAL ENGINEERING</div><h1>SSUET Electrical Engineering AI Agent</h1><p>Faculty • Programs • Admissions • Vision • Mission • PEO/PLO discovery • Official-source search</p></div>""",unsafe_allow_html=True)

page=st.sidebar.radio("⚡ Electrical Agent",["🏠 Dashboard","👨‍🏫 Faculty","🎓 Programs","📝 Admissions","🎯 Vision & Mission","📚 PEO / PLO","🤖 AI Agent","🔎 Source Search"])
if st.sidebar.button("🔄 Refresh SSUET Data"):
    st.cache_data.clear();st.rerun()
st.sidebar.info("API-free mode: no Groq/OpenAI key required.")

if page=="🏠 Dashboard":
    a,b,c,d=st.columns(4)
    a.markdown('<div class="metric"><b>19+</b>Faculty</div>',unsafe_allow_html=True)
    b.markdown('<div class="metric"><b>4</b>Programs</div>',unsafe_allow_html=True)
    c.markdown('<div class="metric"><b>2014</b>Established</div>',unsafe_allow_html=True)
    d.markdown('<div class="metric"><b>0</b>API Keys</div>',unsafe_allow_html=True)
    st.markdown('<div class="card"><h2>⚡ Department Intelligence Center</h2><p>This application turns the public SSUET Electrical Engineering information into one searchable, colorful dashboard. It uses deterministic retrieval and rules instead of a paid/secret LLM API.</p></div>',unsafe_allow_html=True)
    st.success("Best practice: verify changing admission dates, fees and eligibility on the official SSUET website before applying.")

elif page=="👨‍🏫 Faculty":
    st.header("👨‍🏫 Electrical Engineering Faculty")
    q=st.text_input("Search faculty")
    data=faculty()
    if q:data=[x for x in data if q.lower() in (x[0]+" "+x[1]).lower()]
    cols=st.columns(4)
    for i,(n,r,img,link) in enumerate(data):
        with cols[i%4]:
            if img:st.image(img,width=105)
            else:st.markdown('<div style="font-size:70px">⚡</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="fac"><b>{html.escape(n)}</b><br><span class="small">{html.escape(r)}</span></div>',unsafe_allow_html=True)
            st.link_button("Official Profile",link,use_container_width=True)

elif page=="🎓 Programs":
    st.header("🎓 Electrical Engineering Programs")
    for n,l,u in [("BS Electrical Engineering","Undergraduate",BS),("BS Renewable Energy System","Undergraduate",BASE+"/"),("B.E Tech (Electrical)","Undergraduate",BET),("MS Electrical Engineering","Postgraduate",MS)]:
        st.markdown(f'<div class="card"><h3>⚡ {n}</h3><p>{l}</p></div>',unsafe_allow_html=True);st.link_button("Open Official Page",u)

elif page=="📝 Admissions":
    st.header("📝 Admission Information")
    st.markdown('<div class="card"><h3>🎓 Undergraduate Electrical Admissions</h3><p>The official SSUET UG Admission Policy 2025-26 includes BS Electrical Engineering and B.E Tech (Electrical) under the Faculty of Electrical & Computer Engineering. Admission is subject to eligibility, merit and seat availability.</p><p>Exact requirements, fees and dates can change; use the official policy/announcement.</p></div>',unsafe_allow_html=True)
    st.link_button("📄 Official UG Admission Policy",ADMISSION)
    st.link_button("🌐 SSUET Admissions",BASE+"/admissions/undergraduate-admissions/")

elif page=="🎯 Vision & Mission":
    st.header("🎯 Electrical Engineering Department")
    st.markdown('<div class="card"><h2>🌟 Vision</h2><p>The Department of Electrical Engineering endeavours to enhance the quality of teaching and research in order to provide an excellent education and equip the students with professional and entrepreneurial skills, while contributing to the national economy, cope with the market challenges and to meet the international requirements.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="card"><h2>🚀 Mission</h2><p>The Department of Electrical Engineering believes to produce practical environment in connection with theoretical background knowledge for the highest class education and research. Our mission is to provide excellence in education and industrial practices by providing strong foundation to face the future challenges. We promote high level morals, dignity and ethical practice to the profession.</p></div>',unsafe_allow_html=True)
    st.link_button("Verify Official Source",BS)

elif page=="📚 PEO / PLO":
    st.header("📚 PEO / PLO")
    st.warning("Source-control enabled: the agent does not invent official accreditation statements.")
    st.markdown('<div class="card"><h3>PEO</h3><p>Official Electrical Department PEO statements were not verified from the current publicly indexed department page.</p><h3>PLO</h3><p>Official Electrical Department PLO statements were not verified from the current publicly indexed department page.</p><p>For accreditation use, upload the approved SSUET Electrical PEO/PLO document and add it as a controlled source.</p></div>',unsafe_allow_html=True)
    st.link_button("Official Electrical Department Page",BS)

elif page=="🤖 AI Agent":
    st.header("🤖 Ask the Electrical Department Agent")
    st.caption("Deterministic • API-free • source-first")
    q=st.text_input("Ask anything about SSUET Electrical Engineering",placeholder="What is the mission of Electrical Engineering?")
    if q:st.markdown(f'<div class="card">{agent(q).replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)

else:
    st.header("🔎 Official Website Search")
    q=st.text_input("Search indexed SSUET Electrical pages",placeholder="e.g. OBE, instrumentation, labs, curriculum")
    if q:
        rows=[]
        for n,u,t in knowledge():
            score=sum(t.lower().count(w) for w in set(re.findall(r"[a-z0-9]+",q.lower())) if len(w)>2)
            if score:rows.append((score,n,u,t))
        rows.sort(reverse=True)
        for _,n,u,t in rows[:5]:
            st.markdown(f'<div class="card"><h3>{n}</h3><p>{t[:1200]}...</p><span class="small">{u}</span></div>',unsafe_allow_html=True)
            st.link_button("Open Source",u)

st.markdown("---")
st.caption("SSUET Electrical Engineering AI Agent | Public-source information | Verify time-sensitive information on ssuet.edu.pk")
