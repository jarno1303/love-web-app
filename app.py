import streamlit as st
import json
import random
import datetime
import pandas as pd
import plotly.express as px
from pathlib import Path

# Streamlit page config
st.set_page_config(
    page_title="LOVe - Lääkehoidon osaaminen verkossa",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kysymyspankki (sama kuin tkinter-versiossa)
QUESTIONS = [
    [
        "Potilaalle on määrätty 12,5 mg metoprololia. Saatavilla on 50 mg tabletteja. Kuinka monta tablettia annat?",
        "Ratkaisu: 12,5 mg ÷ 50 mg = 0,25 tablettia. Aina varmista laskutoimituksen oikeellisuus kahdesti.",
        ["0,25 tablettia", "0,5 tablettia", "1 tabletti", "4 tablettia"],
        0,
        "laskut",
        "aloittelija"
    ],
    [
        "Mitkä ovat lääkehoidon '5 oikeaa'?",
        "Oikea potilas, oikea lääke, oikea annos, oikea antotapa ja oikea aika. Perusperiaate turvalliselle lääkehoidolle.",
        ["Potilas, lääke, annos, aika, paikka", "Potilas, lääke, annos, antotapa, aika", "Lääke, annos, aika, tapa, hinta", "Potilas, annos, aika, lääkäri, hoitaja"],
        1,
        "turvallisuus",
        "aloittelija"
    ],
    [
        "Mitä tarkoittaa lääkkeen puoliintumisaika?",
        "Aika, jossa lääkeaineen pitoisuus elimistössä laskee puoleen alkuperäisestä.",
        ["Lääkkeen vaikutuksen kesto", "Pitoisuuden puolittumisaika", "Lääkkeen imeytymisaika", "Lääkkeen poistumisaika"],
        1,
        "farmakologia",
        "keskitaso"
    ],
    [
        "Insuliinia annetaan 0,5 yksikköä/kg. Potilas painaa 70 kg. Kuinka monta yksikköä annetaan?",
        "Ratkaisu: 70 kg × 0,5 yks/kg = 35 yksikköä. Insuliini on 'High Alert' -lääke, vaatii kaksoistarkastuksen.",
        ["30 yks", "35 yks", "40 yks", "70 yks"],
        1,
        "laskut",
        "keskitaso"
    ],
    [
        "Milloin potilaan henkilöllisyys tulee varmistaa?",
        "Aina ennen jokaista lääkkeenantoa vähintään kahdella tunnistetiedolla (nimi + henkilötunnus tai syntymäaika).",
        ["Vain ensimmäisellä kerralla", "Jos potilas näyttää vieraalta", "Aina ennen lääkkeenantoa", "Vain PKV-lääkkeiden yhteydessä"],
        2,
        "turvallisuus",
        "aloittelija"
    ],
    [
        "Mikä on oikea pistokulma ihonalaisessa injektiossa (s.c.)?",
        "Ihonalainen injektio annetaan 45-90 asteen kulmassa ihoon riippuen neulan pituudesta ja potilaan rasvakudoksesta.",
        ["30 astetta", "45-90 astetta", "90 astetta aina", "15 astetta"],
        1,
        "injektiot",
        "keskitaso"
    ]
]

# Session state initialization
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'total_answered': 0,
        'total_correct': 0,
        'categories': {},
        'streak': 0
    }

if 'current_question' not in st.session_state:
    st.session_state.current_question = None

if 'question_index' not in st.session_state:
    st.session_state.question_index = 0

if 'questions_for_practice' not in st.session_state:
    st.session_state.questions_for_practice = []

if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False

if 'user_answer' not in st.session_state:
    st.session_state.user_answer = None

def update_stats(category, is_correct):
    """Päivitä tilastoja"""
    st.session_state.stats['total_answered'] += 1
    
    if category not in st.session_state.stats['categories']:
        st.session_state.stats['categories'][category] = {'answered': 0, 'correct': 0}
    
    st.session_state.stats['categories'][category]['answered'] += 1
    
    if is_correct:
        st.session_state.stats['total_correct'] += 1
        st.session_state.stats['categories'][category]['correct'] += 1
        st.session_state.stats['streak'] += 1
    else:
        st.session_state.stats['streak'] = 0

def start_practice(category, difficulty):
    """Aloita harjoittelu"""
    if category == "all":
        questions = [q for q in QUESTIONS if q[5] == difficulty]
    else:
        questions = [q for q in QUESTIONS if q[4] == category and q[5] == difficulty]
    
    if questions:
        random.shuffle(questions)
        st.session_state.questions_for_practice = questions
        st.session_state.question_index = 0
        st.session_state.current_question = questions[0]
        st.session_state.show_feedback = False
        st.session_state.user_answer = None
        st.rerun()
    else:
        st.error(f"Ei kysymyksiä kategoriassa '{category}' vaikeustasolla '{difficulty}'")

def check_answer():
    """Tarkista vastaus"""
    if st.session_state.user_answer is not None:
        question = st.session_state.current_question
        is_correct = st.session_state.user_answer == question[3]
        update_stats(question[4], is_correct)
        st.session_state.show_feedback = True
        return is_correct
    return False

def next_question():
    """Siirry seuraavaan kysymykseen"""
    st.session_state.question_index += 1
    if st.session_state.question_index < len(st.session_state.questions_for_practice):
        st.session_state.current_question = st.session_state.questions_for_practice[st.session_state.question_index]
        st.session_state.show_feedback = False
        st.session_state.user_answer = None
    else:
        st.session_state.current_question = None
        st.success("🎉 Kaikki kysymykset käyty läpi!")

def reset_practice():
    """Lopeta harjoittelu"""
    st.session_state.current_question = None
    st.session_state.questions_for_practice = []
    st.session_state.show_feedback = False
    st.session_state.user_answer = None

# HEADER
st.title("💊 LOVe Enhanced")
st.markdown("### *Lääkehoidon osaaminen verkossa - Web Edition*")

# SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("## 🧭 Navigaatio")
    
    if st.session_state.current_question is None:
        page = st.radio(
            "Valitse sivu:",
            ["🏠 Etusivu", "📚 Harjoittelu", "📊 Tilastot", "ℹ️ Tietoja"]
        )
    else:
        st.markdown("**📚 Harjoittelu käynnissä**")
        if st.button("🏠 Lopeta harjoittelu"):
            reset_practice()
            st.rerun()
        page = "📚 Harjoittelu"

# MAIN CONTENT
if page == "🏠 Etusivu" and st.session_state.current_question is None:
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📝 Vastattu", 
            st.session_state.stats['total_answered']
        )
    
    with col2:
        correct_rate = 0
        if st.session_state.stats['total_answered'] > 0:
            correct_rate = (st.session_state.stats['total_correct'] / st.session_state.stats['total_answered']) * 100
        st.metric(
            "✅ Onnistumis-%", 
            f"{correct_rate:.1f}%"
        )
    
    with col3:
        st.metric(
            "🏆 Kategorioita", 
            len(st.session_state.stats['categories'])
        )
    
    with col4:
        st.metric(
            "🔥 Streak", 
            st.session_state.stats['streak']
        )
    
    st.markdown("---")
    
    # Quick start options
    st.subheader("🚀 Pika-aloitus")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧮 Lääkelaskut (Aloittelija)", use_container_width=True, type="primary"):
            start_practice("laskut", "aloittelija")
    
    with col2:
        if st.button("🛡️ Turvallisuus (Aloittelija)", use_container_width=True, type="secondary"):
            start_practice("turvallisuus", "aloittelija")
    
    st.markdown("---")
    st.markdown("**💡 Vinkki:** Valitse 'Harjoittelu' sivupalkista lisää vaihtoehtoja!")

elif page == "📚 Harjoittelu":
    if st.session_state.current_question is None:
        # Valitse kategoria ja vaikeustaso
        st.subheader("📚 Valitse harjoitustyyppi")
        
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "Kategoria:",
                ["all", "laskut", "turvallisuus", "farmakologia", "injektiot"],
                format_func=lambda x: {
                    "all": "🎯 Kaikki kategoriat",
                    "laskut": "🧮 Lääkelaskut", 
                    "turvallisuus": "🛡️ Lääketurvallisuus",
                    "farmakologia": "💊 Farmakologia",
                    "injektiot": "💉 Injektiot"
                }[x]
            )
        
        with col2:
            difficulty = st.selectbox(
                "Vaikeustaso:",
                ["aloittelija", "keskitaso", "edistynyt"],
                format_func=lambda x: {
                    "aloittelija": "🌱 Aloittelija",
                    "keskitaso": "⚡ Keskitaso", 
                    "edistynyt": "🔥 Edistynyt"
                }[x]
            )
        
        if st.button("🎯 Aloita harjoittelu", type="primary", use_container_width=True):
            start_practice(category, difficulty)
    
    else:
        # Näytä kysymys
        question = st.session_state.current_question
        progress = (st.session_state.question_index + 1) / len(st.session_state.questions_for_practice)
        
        st.progress(progress)
        st.caption(f"Kysymys {st.session_state.question_index + 1} / {len(st.session_state.questions_for_practice)}")
        
        st.markdown(f"### {question[0]}")
        
        # Vastausvaihtoehdot
        if not st.session_state.show_feedback:
            st.session_state.user_answer = st.radio(
                "Valitse vastaus:",
                range(len(question[2])),
                format_func=lambda x: f"{chr(65+x)}. {question[2][x]}",
                key=f"q_{st.session_state.question_index}",
                index=None
            )
        else:
            # Näytä vastaukset lukittuina feedbackin aikana
            for i, option in enumerate(question[2]):
                if i == question[3]:
                    st.success(f"✅ {chr(65+i)}. {option} (Oikea vastaus)")
                elif i == st.session_state.user_answer:
                    st.error(f"❌ {chr(65+i)}. {option} (Sinun vastauksesi)")
                else:
                    st.write(f"⚪ {chr(65+i)}. {option}")
        
        # Painikkeet
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.show_feedback:
                if st.button("✅ Tarkista vastaus", disabled=st.session_state.user_answer is None, type="primary"):
                    is_correct = check_answer()
                    st.rerun()
        
        with col2:
            if st.session_state.show_feedback:
                if st.button("➡️ Seuraava kysymys", type="primary"):
                    next_question()
                    st.rerun()
        
        # Näytä feedback
        if st.session_state.show_feedback:
            is_correct = st.session_state.user_answer == question[3]
            
            if is_correct:
                st.success("🎉 Oikein! Hyvä!")
            else:
                st.error("❌ Väärin!")
            
            # Näytä selitys
            st.info(f"**Selitys:** {question[1]}")

elif page == "📊 Tilastot":
    st.subheader("📊 Tilastot")
    
    # Yleiset tilastot
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Kysymyksiä vastattu", st.session_state.stats['total_answered'])
    
    with col2:
        st.metric("✅ Oikeita vastauksia", st.session_state.stats['total_correct'])
    
    with col3:
        if st.session_state.stats['total_answered'] > 0:
            rate = (st.session_state.stats['total_correct'] / st.session_state.stats['total_answered']) * 100
            st.metric("📈 Onnistumisprosentti", f"{rate:.1f}%")
        else:
            st.metric("📈 Onnistumisprosentti", "0%")
    
    with col4:
        st.metric("🔥 Nykyinen streak", st.session_state.stats['streak'])
    
    # Kategoriakohtaiset tilastot
    if st.session_state.stats['categories']:
        st.subheader("📋 Kategoriakohtaiset tulokset")
        
        # Luo DataFrame visualisointia varten
        cat_data = []
        for cat, data in st.session_state.stats['categories'].items():
            answered = data['answered']
            correct = data['correct']
            percentage = (correct / answered * 100) if answered > 0 else 0
            
            cat_data.append({
                'Kategoria': cat.capitalize(),
                'Vastattu': answered,
                'Oikein': correct,
                'Onnistumis-%': round(percentage, 1)
            })
        
        df = pd.DataFrame(cat_data)
        st.dataframe(df, use_container_width=True)
        
        # Pylväskaavio
        if len(cat_data) > 1:
            fig = px.bar(
                df, 
                x='Kategoria', 
                y='Onnistumis-%',
                title='📊 Onnistumisprosentit kategorioittain',
                color='Onnistumis-%',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📝 Ei tilastoja vielä. Aloita harjoittelu keräämään dataa!")
    
    # Nollaa tilastot
    if st.session_state.stats['total_answered'] > 0:
        st.markdown("---")
        if st.button("🗑️ Nollaa tilastot", type="secondary"):
            st.session_state.stats = {
                'total_answered': 0,
                'total_correct': 0,
                'categories': {},
                'streak': 0
            }
            st.success("Tilastot nollattu!")
            st.rerun()

elif page == "ℹ️ Tietoja":
    st.subheader("ℹ️ Tietoja sovelluksesta")
    
    st.markdown("""
    ## 💊 LOVe Enhanced Web Edition
    
    **Lääkehoidon osaaminen verkossa** - interaktiivinen harjoitussovellus lääkehoidon perusteiden opiskeluun.
    
    ### ✨ Ominaisuudet:
    - 🎯 **Eri vaikeustasojen kysymykset** (aloittelija, keskitaso, edistynyt)
    - 📊 **Reaaliaikainen tilastointi** ja edistymisen seuranta
    - 🏆 **Kategoriakohtaiset tulokset** 
    - 🔥 **Streak-seuranta** motivaation ylläpitämiseksi
    - 📱 **Responsiivinen design** - toimii kaikilla laitteilla
    
    ### 📚 Kategoriat:
    - 🧮 **Lääkelaskut** - Annostus ja laskutoimitukset
    - 🛡️ **Lääketurvallisuus** - 5 oikeaa ja turvalliset käytännöt  
    - 💊 **Farmakologia** - Lääkkeiden vaikutusmekanismit
    - 💉 **Injektiot** - Pistotekniikat ja -kulmat
    
    ### 🚀 Teknologia:
    - **Frontend:** Streamlit & Python
    - **Visualisointi:** Plotly & Pandas
    - **Deployment:** Streamlit Cloud
    
    ### 👨‍💻 Kehittäjä:
    Alkuperäinen Tkinter-versio muokattuna web-sovellukseksi.
    
    ---
    *Versio 1.0 - Web Edition*
    """)

# Footer
st.markdown("---")
st.markdown("*🌐 LOVe Enhanced Web Edition - Rakennettu ❤️:llä Streamlit-teknologialla*")