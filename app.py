import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
import random
import json
import os
import sys
import datetime
from tkinter import Canvas
import math

# PDF-tuen tarkistus
try:
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.pagesizes import A4
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Matplotlib-tuen tarkistus
try:
    import matplotlib
    matplotlib.use('TkAgg')  # Tkinter-yhteensopiva backend
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# --- TIEDOSTOJEN KÄSITTELY ---

def get_appdata_path(filename):
    """Luo ja palauttaa polun ohjelman data-kansioon AppData-kansiossa."""
    app_data_folder = os.path.join(os.getenv('APPDATA'), 'LOVE-Harjoitussovellus')
    os.makedirs(app_data_folder, exist_ok=True)
    return os.path.join(app_data_folder, filename)

def resolve_bundled_path(relative_path):
    """Etsii tiedoston polun .exe-paketista."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Määritellään polut
EXTERNAL_QUESTIONS_FILE = get_appdata_path("kysymykset.json")
STATS_FILE = get_appdata_path("love_stats.json")
ACHIEVEMENTS_FILE = get_appdata_path("achievements.json")
STREAKS_FILE = get_appdata_path("streaks.json")
BUNDLED_QUESTIONS_FILE = resolve_bundled_path("kysymykset.json")
all_questions = []

# Väriteemat ja tyylit (parannettu)
COLORS = {
    'primary': '#2E86AB',      # Sininen
    'secondary': '#A23B72',    # Violetti
    'success': '#1B7340',      # Vihreä
    'warning': '#F18F01',      # Oranssi
    'danger': '#C73E1D',       # Punainen
    'light': '#F2F4F8',        # Vaalea harmaa
    'dark': '#2D3436',         # Tumma harmaa
    'white': '#FFFFFF',
    'accent': '#6C5CE7',       # Violetti accent
    'gold': '#FFD700',         # Kulta badgeille
    'silver': '#C0C0C0',       # Hopea
    'bronze': '#CD7F32'        # Pronssi
}

# GAMIFICATION: Saavutukset ja merkit
ACHIEVEMENTS = {
    'first_question': {'name': 'Ensimmäinen askel', 'desc': 'Vastasit ensimmäiseen kysymykseen', 'icon': '🌟'},
    'streak_7': {'name': 'Viikon sarja', 'desc': '7 päivää putkeen harjoitusta', 'icon': '🔥'},
    'streak_30': {'name': 'Kuukauden sarja', 'desc': '30 päivää putkeen harjoitusta', 'icon': '🏆'},
    'perfect_simulation': {'name': 'Täydellinen', 'desc': 'Täydet pisteet simulaatiosta', 'icon': '💯'},
    'math_master': {'name': 'Laskumestari', 'desc': '90% oikein lääkelaskuissa', 'icon': '🧮'},
    'safety_expert': {'name': 'Turvallisuusekspertti', 'desc': '95% oikein turvallisuudessa', 'icon': '🛡️'},
    'hundred_questions': {'name': 'Satanen täynnä', 'desc': '100 kysymystä vastattu', 'icon': '📚'},
    'speed_demon': {'name': 'Nopeusdemoni', 'desc': 'Vastasit 10 sek sisään', 'icon': '⚡'},
    'dedicated_learner': {'name': 'Omistautunut oppija', 'desc': '5 tuntia harjoitusta', 'icon': '📖'},
}

def load_questions_from_json():
    """Lataa kysymykset käyttäjän AppData-kansiosta tai luo laajemman kysymyspankin."""
    global all_questions
    
    # Laajennettu kysymyspankki vaikeustasoineen
    extended_questions = [
        # LÄÄKELASKUT (vaikeustasot lisätty)
        [
            "Potilaalle on määrätty 12,5 mg metoprololia. Saatavilla on 50 mg tabletteja. Kuinka monta tablettia annat?",
            "Ratkaisu: 12,5 mg ÷ 50 mg = 0,25 tablettia. Aina varmista laskutoimituksen oikeellisuus kahdesti.",
            ["0,25 tablettia", "0,5 tablettia", "1 tabletti", "4 tablettia"],
            0,
            "laskut",
            "aloittelija"
        ],
        [
            "Infuusionopeus on 75 ml/h. Potilaan tulee saada yhteensä 1000 ml nestettä. Kuinka kauan infuusio kestää?",
            "Ratkaisu: 1000 ml ÷ 75 ml/h ≈ 13,33 tuntia = 13 h 20 min. Pyöristä aina järkevästi.",
            ["10 h 30 min", "12 h 15 min", "13 h 20 min", "15 h 00 min"],
            2,
            "laskut",
            "aloittelija"
        ],
        [
            "Lapsi painaa 25 kg. Lääkemäärätys on 50 mg/kg/vrk jaettuna neljään annokseen. Kuinka suuri on kerta-annos?",
            "Ratkaisu: (25 kg × 50 mg/kg) ÷ 4 = 1250 mg ÷ 4 = 312,5 mg per kerta.",
            ["250 mg", "312,5 mg", "500 mg", "1250 mg"],
            1,
            "laskut",
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
            "Laimennat 2 ml lääkettä (50 mg/ml) 8 ml:aan keittosuolaa. Mikä on lopullinen pitoisuus?",
            "Ratkaisu: Lääkemäärä: 2 ml × 50 mg/ml = 100 mg. Kokonaistilavuus: 2+8=10 ml. Pitoisuus: 100 mg ÷ 10 ml = 10 mg/ml.",
            ["5 mg/ml", "10 mg/ml", "20 mg/ml", "25 mg/ml"],
            1,
            "laskut",
            "edistynyt"
        ],

        # LÄÄKETURVALLISUUS
        [
            "Mitkä ovat lääkehoidon '5 oikeaa'?",
            "Oikea potilas, oikea lääke, oikea annos, oikea antotapa ja oikea aika. Perusperiaate turvalliselle lääkehoidolle.",
            ["Potilas, lääke, annos, aika, paikka", "Potilas, lääke, annos, antotapa, aika", "Lääke, annos, aika, tapa, hinta", "Potilas, annos, aika, lääkäri, hoitaja"],
            1,
            "turvallisuus",
            "aloittelija"
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
            "Mitä 'High Alert' -lääkkeet tarkoittavat?",
            "Lääkkeitä, jotka voivat aiheuttaa vakavaa haittaa virheellisesti käytettyinä. Esim. insuliini, antikoagulantit.",
            ["Erittäin kalliita lääkkeitä", "Suuren riskin lääkkeitä", "Uusia lääkkeitä", "Reseptivapaita lääkkeitä"],
            1,
            "turvallisuus",
            "keskitaso"
        ],

        # FARMAKOLOGIA
        [
            "Mitä tarkoittaa lääkkeen puoliintumisaika?",
            "Aika, jossa lääkeaineen pitoisuus elimistössä laskee puoleen alkuperäisestä.",
            ["Lääkkeen vaikutuksen kesto", "Pitoisuuden puolittumisaika", "Lääkkeen imeytymisaika", "Lääkkeen poistumisaika"],
            1,
            "farmakologia",
            "keskitaso"
        ],
        [
            "Mikä on lääkkeen agonisti?",
            "Aine, joka sitoutuu reseptoriin ja aktivoi sen aikaansaaden biologisen vasteen.",
            ["Estää reseptorin", "Aktivoi reseptorin", "Poistaa lääkkeen", "Ei vaikuta reseptoriin"],
            1,
            "farmakologia",
            "edistynyt"
        ],

        # INJEKTIOT
        [
            "Mikä on oikea pistokulma ihonalaisessa injektiossa (s.c.)?",
            "Ihonalainen injektio annetaan 45-90 asteen kulmassa ihoon riippuen neulan pituudesta ja potilaan rasvakudoksesta.",
            ["30 astetta", "45-90 astetta", "90 astetta aina", "15 astetta"],
            1,
            "injektiot",
            "keskitaso"
        ],

        # ANNOSJAKELU
        [
            "Mitä tulee tarkistaa uuden annosjakelupussirullan käyttöönotossa?",
            "Ensimmäisen ja viimeisen pussin oikeellisuus tulee aina tarkistaa. Myös QR-koodien toimivuus varmistetaan.",
            ["Vain ensimmäinen pussi", "Ensimmäisen ja viimeisen pussin oikeellisuus", "Vain viimeinen pussi", "Pelkästään QR-koodi"],
            1,
            "annosjakelu",
            "aloittelija"
        ],

        # INHALAATIOT
        [
            "Mikä on oikea tekniikka jauheinhalaattorin käytössä?",
            "Napakka sisäänhengitys, hengityksen pidättäminen 10 sekuntia ja uloshengitys nenän kautta.",
            ["Hidas sisäänhengitys", "Napakka sisäänhengitys ja 10 s pidätys", "Normaali hengitys", "Nopea puhallus"],
            1,
            "inhalaatiot",
            "keskitaso"
        ]
    ]
    
    if os.path.exists(EXTERNAL_QUESTIONS_FILE):
        try:
            with open(EXTERNAL_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                existing_questions = json.load(f)
                # Päivitä vanhat kysymykset lisäämällä vaikeustaso jos puuttuu
                for q in existing_questions:
                    if len(q) == 5:  # Vanha formaatti ilman vaikeustasoa
                        q.append("keskitaso")  # Lisätään oletustaso
                all_questions = existing_questions + extended_questions
        except json.JSONDecodeError:
            all_questions = extended_questions
    else:
        all_questions = extended_questions
    
    # Tallennetaan laajennettu kysymyspankki
    with open(EXTERNAL_QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=4, ensure_ascii=False)

def save_questions_to_json():
    """Tallentaa globaalin kysymyslistan."""
    with open(EXTERNAL_QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=4, ensure_ascii=False)

class AchievementManager:
    def __init__(self):
        self.achievements = self.load_achievements()
        self.streaks = self.load_streaks()
    
    def load_achievements(self):
        if not os.path.exists(ACHIEVEMENTS_FILE):
            return {}
        try:
            with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def load_streaks(self):
        if not os.path.exists(STREAKS_FILE):
            return {'current_streak': 0, 'last_practice_date': None, 'longest_streak': 0}
        try:
            with open(STREAKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'current_streak': 0, 'last_practice_date': None, 'longest_streak': 0}
    
    def save_data(self):
        with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.achievements, f, indent=4, ensure_ascii=False)
        with open(STREAKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.streaks, f, indent=4, ensure_ascii=False)
    
    def check_achievements(self, stats, context=None):
        """Tarkistaa ja palauttaa uudet saavutukset"""
        new_achievements = []
        
        # Ensimmäinen kysymys
        if stats.get('total_answered', 0) >= 1 and 'first_question' not in self.achievements:
            self.achievements['first_question'] = True
            new_achievements.append('first_question')
        
        # 100 kysymystä
        if stats.get('total_answered', 0) >= 100 and 'hundred_questions' not in self.achievements:
            self.achievements['hundred_questions'] = True
            new_achievements.append('hundred_questions')
        
        # Kategoriakohtaiset saavutukset
        categories = stats.get('categories', {})
        
        # Laskumestari
        if 'laskut' in categories:
            cat_data = categories['laskut']
            if cat_data.get('answered', 0) >= 20:
                success_rate = (cat_data.get('correct', 0) / cat_data['answered']) * 100
                if success_rate >= 90 and 'math_master' not in self.achievements:
                    self.achievements['math_master'] = True
                    new_achievements.append('math_master')
        
        # Turvallisuusekspertti
        if 'turvallisuus' in categories:
            cat_data = categories['turvallisuus']
            if cat_data.get('answered', 0) >= 20:
                success_rate = (cat_data.get('correct', 0) / cat_data['answered']) * 100
                if success_rate >= 95 and 'safety_expert' not in self.achievements:
                    self.achievements['safety_expert'] = True
                    new_achievements.append('safety_expert')
        
        # Omistautunut oppija (5 tuntia = 18000 s)
        if stats.get('time_spent', 0) >= 18000 and 'dedicated_learner' not in self.achievements:
            self.achievements['dedicated_learner'] = True
            new_achievements.append('dedicated_learner')
        
        # Streak-saavutukset
        current_streak = self.streaks.get('current_streak', 0)
        if current_streak >= 7 and 'streak_7' not in self.achievements:
            self.achievements['streak_7'] = True
            new_achievements.append('streak_7')
        
        if current_streak >= 30 and 'streak_30' not in self.achievements:
            self.achievements['streak_30'] = True
            new_achievements.append('streak_30')
        
        # Kontekstikohtaiset saavutukset
        if context:
            # Täydellinen simulaatio
            if context.get('simulation_perfect') and 'perfect_simulation' not in self.achievements:
                self.achievements['perfect_simulation'] = True
                new_achievements.append('perfect_simulation')
            
            # Nopeusdemoni
            if context.get('fast_answer') and 'speed_demon' not in self.achievements:
                self.achievements['speed_demon'] = True
                new_achievements.append('speed_demon')
        
        if new_achievements:
            self.save_data()
        
        return new_achievements
    
    def update_streak(self):
        """Päivittää streak-laskuria"""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        last_date = self.streaks.get('last_practice_date')
        
        if last_date == today:
            # Harjoiteltu jo tänään
            return self.streaks.get('current_streak', 0)
        elif last_date:
            last_datetime = datetime.datetime.strptime(last_date, '%Y-%m-%d')
            today_datetime = datetime.datetime.strptime(today, '%Y-%m-%d')
            days_diff = (today_datetime - last_datetime).days
            
            if days_diff == 1:
                # Peräkkäinen päivä
                self.streaks['current_streak'] = self.streaks.get('current_streak', 0) + 1
            else:
                # Streak katkeaa
                self.streaks['current_streak'] = 1
        else:
            # Ensimmäinen kerta
            self.streaks['current_streak'] = 1
        
        # Päivitä pisin streak
        if self.streaks['current_streak'] > self.streaks.get('longest_streak', 0):
            self.streaks['longest_streak'] = self.streaks['current_streak']
        
        self.streaks['last_practice_date'] = today
        self.save_data()
        return self.streaks['current_streak']

class AdaptiveLearningManager:
    """Adaptiivinen oppiminen - keskittyy heikoimpiin aiheisiin"""
    
    def __init__(self, stats_manager):
        self.stats_manager = stats_manager
    
    def get_weak_categories(self, min_questions=5):
        """Palauttaa kategoriat joissa menestys on heikompaa"""
        categories = self.stats_manager.stats.get('categories', {})
        weak_categories = []
        
        for cat, data in categories.items():
            if data.get('answered', 0) >= min_questions:
                success_rate = (data.get('correct', 0) / data['answered']) * 100
                if success_rate < 75:  # Alle 75% oikein
                    weak_categories.append((cat, success_rate))
        
        # Järjestä heikoimmat ensin
        weak_categories.sort(key=lambda x: x[1])
        return [cat for cat, rate in weak_categories]
    
    def get_adaptive_questions(self, question_count=20):
        """Palauttaa kysymyksiä jotka keskittyvät heikoimpiin alueisiin"""
        weak_categories = self.get_weak_categories()
        
        adaptive_questions = []
        
        if weak_categories:
            # 70% kysymyksistä heikoista kategorioista
            weak_count = int(question_count * 0.7)
            for i in range(weak_count):
                cat = weak_categories[i % len(weak_categories)]
                cat_questions = [q for q in all_questions if q[4] == cat]
                if cat_questions:
                    adaptive_questions.append(random.choice(cat_questions))
            
            # 30% satunnaisia
            remaining_count = question_count - len(adaptive_questions)
            other_questions = [q for q in all_questions if q[4] not in weak_categories]
            if other_questions:
                adaptive_questions.extend(random.sample(other_questions, 
                                                      min(remaining_count, len(other_questions))))
        else:
            # Jos ei heikkoja kategorioita, satunnaisia kysymyksiä
            adaptive_questions = random.sample(all_questions, 
                                             min(question_count, len(all_questions)))
        
        # Täytä puuttuvat satunnaisilla jos tarvetta
        while len(adaptive_questions) < question_count and len(adaptive_questions) < len(all_questions):
            remaining_questions = [q for q in all_questions if q not in adaptive_questions]
            if remaining_questions:
                adaptive_questions.append(random.choice(remaining_questions))
            else:
                break
        
        return adaptive_questions

class PDFExporter:
    """PDF-vienti tilastoille ja kysymyksille"""
    
    @staticmethod
    def export_stats(stats, filename):
        if not PDF_AVAILABLE:
            messagebox.showerror("Virhe", "PDF-vienti ei ole käytettävissä. Asenna reportlab-kirjasto:\npip install reportlab")
            return False
        
        try:
            c = pdf_canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
            # Otsikko
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, height - 50, "LOVe - Tilastoraportti")
            
            # Päivämäärä
            c.setFont("Helvetica", 12)
            now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            c.drawString(50, height - 80, f"Luotu: {now}")
            
            y_pos = height - 120
            
            # Yleiset tilastot
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_pos, "Yleiset tilastot")
            y_pos -= 30
            
            c.setFont("Helvetica", 12)
            total_answered = stats.get('total_answered', 0)
            total_correct = stats.get('total_correct', 0)
            overall_perc = (total_correct / total_answered * 100) if total_answered > 0 else 0
            
            c.drawString(70, y_pos, f"Kysymyksiä vastattu: {total_answered}")
            y_pos -= 20
            c.drawString(70, y_pos, f"Oikeita vastauksia: {total_correct}")
            y_pos -= 20
            c.drawString(70, y_pos, f"Onnistumisprosentti: {overall_perc:.1f}%")
            y_pos -= 40
            
            # Kategoriat
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_pos, "Kategoriakohtaiset tulokset")
            y_pos -= 30
            
            c.setFont("Helvetica", 12)
            for cat, data in sorted(stats.get("categories", {}).items()):
                cat_answered = data.get("answered", 0)
                cat_correct = data.get("correct", 0)
                cat_perc = (cat_correct / cat_answered * 100) if cat_answered > 0 else 0
                
                c.drawString(70, y_pos, f"{cat.capitalize()}: {cat_perc:.1f}% ({cat_correct}/{cat_answered})")
                y_pos -= 20
                
                if y_pos < 100:  # Uusi sivu
                    c.showPage()
                    y_pos = height - 50
            
            c.save()
            return True
        except Exception as e:
            messagebox.showerror("Virhe", f"PDF-luonti epäonnistui: {str(e)}")
            return False
    
    @staticmethod
    def export_questions(questions, filename):
        if not PDF_AVAILABLE:
            messagebox.showerror("Virhe", "PDF-vienti ei ole käytettävissä. Asenna reportlab-kirjasto:\npip install reportlab")
            return False
        
        try:
            c = pdf_canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
            # Otsikko
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, height - 50, "LOVe - Kysymyskokoelma")
            
            y_pos = height - 100
            question_num = 1
            
            for q in questions:
                if y_pos < 150:  # Uusi sivu
                    c.showPage()
                    y_pos = height - 50
                
                # Kysymys
                c.setFont("Helvetica-Bold", 12)
                question_text = q[0][:100] + "..." if len(q[0]) > 100 else q[0]
                c.drawString(50, y_pos, f"{question_num}. {question_text}")
                y_pos -= 25
                
                # Vaihtoehdot
                c.setFont("Helvetica", 10)
                for i, option in enumerate(q[2]):
                    marker = "*" if i == q[3] else " "
                    c.drawString(70, y_pos, f"{marker} {chr(65+i)}. {option}")
                    y_pos -= 15
                
                y_pos -= 10
                question_num += 1
            
            c.save()
            return True
        except Exception as e:
            messagebox.showerror("Virhe", f"PDF-luonti epäonnistui: {str(e)}")
            return False

class StatsManager:
    def __init__(self):
        self.stats = self.load_stats()
        self.achievement_manager = AchievementManager()
    
    def load_stats(self):
        if not os.path.exists(STATS_FILE): 
            return {"total_answered": 0, "total_correct": 0, "categories": {}, "simulations": [], "time_spent": 0}
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f: 
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError): 
            return {"total_answered": 0, "total_correct": 0, "categories": {}, "simulations": [], "time_spent": 0}
    
    def save_stats(self):
        with open(STATS_FILE, 'w', encoding='utf-8') as f: 
            json.dump(self.stats, f, indent=4, ensure_ascii=False)
    
    def update(self, category, is_correct, time_taken=0, context=None):
        self.stats["total_answered"] = self.stats.get("total_answered", 0) + 1
        self.stats["time_spent"] = self.stats.get("time_spent", 0) + time_taken
        
        if category not in self.stats["categories"]: 
            self.stats["categories"][category] = {"answered": 0, "correct": 0, "time_spent": 0}
        
        self.stats["categories"][category]["answered"] += 1
        self.stats["categories"][category]["time_spent"] = self.stats["categories"][category].get("time_spent", 0) + time_taken
        
        if is_correct:
            self.stats["total_correct"] = self.stats.get("total_correct", 0) + 1
            self.stats["categories"][category]["correct"] += 1
        
        # Päivitä streak
        current_streak = self.achievement_manager.update_streak()
        
        # Tarkista saavutukset
        achievement_context = context or {}
        if time_taken <= 10:  # Alle 10 sekuntia = nopea vastaus
            achievement_context['fast_answer'] = True
        
        new_achievements = self.achievement_manager.check_achievements(self.stats, achievement_context)
        
        self.save_stats()
        return new_achievements, current_streak
    
    def add_simulation_result(self, score, total_questions, time_taken=0):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        result = {"date": now, "score": score, "total": total_questions, "time": time_taken}
        self.stats["simulations"] = self.stats.get("simulations", [])
        self.stats["simulations"].append(result)
        
        # Tarkista täydellinen simulaatio
        context = {}
        if score == total_questions:
            context['simulation_perfect'] = True
        
        new_achievements = self.achievement_manager.check_achievements(self.stats, context)
        self.save_stats()
        return new_achievements

class AchievementPopup(tk.Toplevel):
    """Popup-ikkuna saavutusten näyttämiseen"""
    
    def __init__(self, master, achievement_id):
        super().__init__(master)
        self.achievement_id = achievement_id
        achievement = ACHIEVEMENTS[achievement_id]
        
        self.title("Uusi saavutus!")
        self.geometry("400x200")
        self.configure(bg=COLORS['gold'])
        self.resizable(False, False)
        
        # Keskitä ikkuna
        self.transient(master)
        self.grab_set()
        
        # Sisältö
        main_frame = tk.Frame(self, bg=COLORS['gold'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Ikoni
        icon_label = tk.Label(main_frame, text=achievement['icon'], 
                             font=('Segoe UI', 36),
                             bg=COLORS['gold'], fg=COLORS['white'])
        icon_label.pack(pady=(0, 10))
        
        # Otsikko
        title_label = tk.Label(main_frame, text="🎉 Uusi saavutus saavutettu!", 
                              font=('Segoe UI', 14, 'bold'),
                              bg=COLORS['gold'], fg=COLORS['white'])
        title_label.pack()
        
        # Saavutuksen nimi
        name_label = tk.Label(main_frame, text=achievement['name'], 
                             font=('Segoe UI', 16, 'bold'),
                             bg=COLORS['gold'], fg=COLORS['white'])
        name_label.pack(pady=5)
        
        # Kuvaus
        desc_label = tk.Label(main_frame, text=achievement['desc'], 
                             font=('Segoe UI', 11),
                             bg=COLORS['gold'], fg=COLORS['white'],
                             wraplength=350)
        desc_label.pack(pady=5)
        
        # Sulje-painike
        close_btn = tk.Button(main_frame, text="Jatka", 
                             font=('Segoe UI', 11, 'bold'),
                             bg=COLORS['white'], fg=COLORS['dark'],
                             relief='flat', padx=30, pady=8,
                             command=self.destroy)
        close_btn.pack(pady=(20, 0))
        
        # Automaattinen sulkeminen 5 sekunnin kuluttua
        self.after(5000, self.destroy)

class ModernCalculatorWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Laskin")
        self.geometry("320x480")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.configure(bg=COLORS['light'])
        
        self.expression = ""
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        self.create_modern_calculator()
    
    def create_modern_calculator(self):
        # Display
        display_frame = tk.Frame(self, bg=COLORS['light'], pady=20)
        display_frame.pack(fill='x', padx=20)
        
        display = tk.Entry(display_frame, textvariable=self.display_var, 
                          font=('Segoe UI', 24, 'bold'), justify='right', 
                          state='readonly', bg=COLORS['white'], 
                          relief='flat', bd=10)
        display.pack(fill='x', ipady=10)
        
        # Buttons
        button_frame = tk.Frame(self, bg=COLORS['light'])
        button_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        buttons = [
            ['C', '±', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '−'],
            ['1', '2', '3', '+'],
            ['0', '.', '=']
        ]
        
        for i, row in enumerate(buttons):
            for j, btn_text in enumerate(row):
                if i == 4 and j == 0:  # '0' button spanning two columns
                    self.create_button(button_frame, btn_text, i, j, columnspan=2)
                    continue
                elif i == 4 and j == 1:  # Skip this position as '0' spans it
                    continue
                elif i == 4 and j >= 2:  # Adjust column for buttons after '0'
                    self.create_button(button_frame, btn_text, i, j+1)
                else:
                    self.create_button(button_frame, btn_text, i, j)
        
        # Configure grid weights
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            button_frame.grid_columnconfigure(j, weight=1)
    
    def create_button(self, parent, text, row, col, columnspan=1):
        # Determine button style
        if text in ['C', '±', '%']:
            bg_color = COLORS['warning']
            fg_color = COLORS['white']
        elif text in ['÷', '×', '−', '+', '=']:
            bg_color = COLORS['primary']
            fg_color = COLORS['white']
        else:
            bg_color = COLORS['white']
            fg_color = COLORS['dark']
        
        btn = tk.Button(parent, text=text, font=('Segoe UI', 18, 'bold'),
                       bg=bg_color, fg=fg_color, relief='flat',
                       command=lambda t=text: self.on_button_click(t))
        
        btn.grid(row=row, column=col, columnspan=columnspan, 
                sticky='nsew', padx=2, pady=2)
        
        # Hover effects
        def on_enter(e):
            btn.configure(bg=self.lighten_color(bg_color))
        def on_leave(e):
            btn.configure(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def lighten_color(self, color):
        # Simple color lightening
        if color == COLORS['primary']:
            return '#4A9FD1'
        elif color == COLORS['warning']:
            return '#F5A623'
        else:
            return '#F8F9FA'
    
    def on_button_click(self, char):
        if char == 'C':
            self.expression = ""
            self.display_var.set("0")
        elif char == '=':
            try:
                # Replace display symbols with calculation symbols
                calc_expr = self.expression.replace('×', '*').replace('÷', '/').replace('−', '-')
                result = str(eval(calc_expr))
                self.expression = result
                self.display_var.set(result)
            except:
                self.display_var.set("Virhe")
                self.expression = ""
        elif char == '±':
            if self.expression and self.expression[0] == '-':
                self.expression = self.expression[1:]
            else:
                self.expression = '-' + self.expression
            self.display_var.set(self.expression)
        elif char == '%':
            try:
                result = str(float(self.expression) / 100)
                self.expression = result
                self.display_var.set(result)
            except:
                pass
        else:
            if self.display_var.get() == "Virhe" or self.display_var.get() == "0":
                self.expression = ""
            self.expression += char
            self.display_var.set(self.expression)

class LoveTrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOVe Enhanced - Lääkehoidon osaaminen verkossa")
        self.geometry("1200x800")
        self.configure(bg=COLORS['light'])
        
        # Set modern style
        self.setup_styles()
        
        self.stats_manager = StatsManager()
        self.adaptive_manager = AdaptiveLearningManager(self.stats_manager)
        self.calculator = ModernCalculatorWindow(self)
        self.calculator.withdraw()
        
        # Main container
        self.container = tk.Frame(self, bg=COLORS['light'])
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for F in (MainMenu, PracticeView, SimulationView, StatsView, QuestionManagementView, 
                  DifficultySelectionView, DailyChallengeView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("MainMenu")
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure modern button style
        self.style.configure("Modern.TButton",
                           background=COLORS['primary'],
                           foreground=COLORS['white'],
                           font=('Segoe UI', 11, 'bold'),
                           padding=(20, 12))
        
        self.style.map("Modern.TButton",
                      background=[('active', COLORS['accent']),
                                ('pressed', COLORS['secondary'])])
    
    def show_frame(self, page_name, questions=None, mode=None, **kwargs):
        frame = self.frames[page_name]
        if hasattr(frame, 'start'): 
            frame.start(questions, mode, **kwargs)
        frame.tkraise()
    
    def open_calculator(self):
        self.calculator.deiconify()
    
    def show_achievements(self, achievement_ids):
        """Näyttää saavutuspopupit"""
        for achievement_id in achievement_ids:
            popup = AchievementPopup(self, achievement_id)

class DifficultySelectionView(tk.Frame):
    """Vaikeustason valinta"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['light'])
        self.controller = controller
        self.category = None
        self.create_interface()
    
    def create_interface(self):
        # Header
        header_frame = tk.Frame(self, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        self.title_label = tk.Label(header_frame, text="Valitse vaikeustaso", 
                                   font=('Segoe UI', 20, 'bold'),
                                   bg=COLORS['primary'], fg=COLORS['white'])
        self.title_label.pack(pady=25)
        
        # Content
        content_frame = tk.Frame(self, bg=COLORS['light'])
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)
        
        # Difficulty cards
        cards_frame = tk.Frame(content_frame, bg=COLORS['light'])
        cards_frame.pack(expand=True)
        
        # Configure grid
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)
        
        # Aloittelija
        self.create_difficulty_card(cards_frame, "🌱 Aloittelija", 
                                   "Perusasiat ja yksinkertaiset kysymykset\nSopii aloittelijoille",
                                   lambda: self.start_practice("aloittelija"), 0, 0, COLORS['success'])
        
        # Keskitaso
        self.create_difficulty_card(cards_frame, "⚡ Keskitaso", 
                                   "Soveltavia kysymyksiä\nKohtuullinen haaste",
                                   lambda: self.start_practice("keskitaso"), 0, 1, COLORS['warning'])
        
        # Edistynyt
        self.create_difficulty_card(cards_frame, "🔥 Edistynyt", 
                                   "Haastavat kysymykset\nSyvällistä osaamista",
                                   lambda: self.start_practice("edistynyt"), 0, 2, COLORS['danger'])
        
        # Adaptiivinen oppiminen
        adaptive_frame = tk.Frame(content_frame, bg=COLORS['white'], relief='solid', bd=2)
        adaptive_frame.pack(fill='x', pady=20, padx=50)
        
        adaptive_title = tk.Label(adaptive_frame, text="🎯 Adaptiivinen oppiminen", 
                                 font=('Segoe UI', 16, 'bold'),
                                 bg=COLORS['white'], fg=COLORS['accent'])
        adaptive_title.pack(pady=10)
        
        adaptive_desc = tk.Label(adaptive_frame, text="Keskittyy automaattisesti heikoimpiin aiheisiin", 
                               font=('Segoe UI', 11),
                               bg=COLORS['white'], fg=COLORS['dark'])
        adaptive_desc.pack()
        
        adaptive_btn = tk.Button(adaptive_frame, text="Aloita adaptiivinen harjoittelu",
                               font=('Segoe UI', 11, 'bold'),
                               bg=COLORS['accent'], fg=COLORS['white'],
                               relief='flat', padx=30, pady=10,
                               command=self.start_adaptive_practice)
        adaptive_btn.pack(pady=15)
        
        # Back button
        back_button = tk.Button(content_frame, text="← Takaisin",
                               font=('Segoe UI', 10),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               relief='flat', padx=20, pady=8,
                               command=lambda: self.controller.show_frame("MainMenu"))
        back_button.pack(side='bottom', pady=20)
    
    def create_difficulty_card(self, parent, title, description, command, row, col, color):
        card = tk.Frame(parent, bg=COLORS['white'], relief='solid', bd=1)
        card.grid(row=row, column=col, padx=15, pady=20, sticky='nsew', ipadx=15, ipady=20)
        
        title_label = tk.Label(card, text=title, 
                              font=('Segoe UI', 16, 'bold'),
                              bg=COLORS['white'], fg=color)
        title_label.pack(pady=(10, 5))
        
        desc_label = tk.Label(card, text=description, 
                             font=('Segoe UI', 10),
                             bg=COLORS['white'], fg=COLORS['dark'],
                             wraplength=200, justify='center')
        desc_label.pack(pady=(0, 15))
        
        start_btn = tk.Button(card, text="Valitse",
                             font=('Segoe UI', 11, 'bold'),
                             bg=color, fg=COLORS['white'],
                             relief='flat', padx=30, pady=8,
                             command=command)
        start_btn.pack()
    
    def start(self, questions=None, mode=None, category=None):
        self.category = category
        if category:
            self.title_label.config(text=f"Valitse vaikeustaso - {category.capitalize()}")
    
    def start_practice(self, difficulty):
        if not all_questions:
            messagebox.showwarning("Tyhjä kysymyspankki", "Kysymyspankki on tyhjä.")
            return
        
        # Suodata kysymykset kategorian ja vaikeustason mukaan
        if self.category == "all":
            questions = [q for q in all_questions if len(q) > 5 and q[5] == difficulty]
        else:
            questions = [q for q in all_questions if q[4] == self.category and len(q) > 5 and q[5] == difficulty]
        
        if not questions:
            messagebox.showinfo("Ei kysymyksiä", f"Ei kysymyksiä vaikeustasolla '{difficulty}'.")
            return
        
        random.shuffle(questions)
        self.controller.show_frame("PracticeView", questions, "practice")
    
    def start_adaptive_practice(self):
        questions = self.controller.adaptive_manager.get_adaptive_questions(20)
        if not questions:
            messagebox.showinfo("Ei kysymyksiä", "Ei riittävästi dataa adaptiiviseen oppimiseen.")
            return
        
        self.controller.show_frame("PracticeView", questions, "adaptive")

class DailyChallengeView(tk.Frame):
    """Päivittäiset haasteet"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['light'])
        self.controller = controller
        self.create_interface()
    
    def create_interface(self):
        # Header
        header_frame = tk.Frame(self, bg=COLORS['accent'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🌟 Päivittäinen haaste", 
                              font=('Segoe UI', 20, 'bold'),
                              bg=COLORS['accent'], fg=COLORS['white'])
        title_label.pack(pady=25)
        
        # Content
        content_frame = tk.Frame(self, bg=COLORS['light'])
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)
        
        # Challenge info
        challenge_card = tk.Frame(content_frame, bg=COLORS['white'], relief='solid', bd=1)
        challenge_card.pack(fill='x', pady=20, padx=50)
        
        today = datetime.datetime.now()
        challenge_title = self.get_daily_challenge_title(today)
        
        challenge_label = tk.Label(challenge_card, text=challenge_title, 
                                  font=('Segoe UI', 18, 'bold'),
                                  bg=COLORS['white'], fg=COLORS['accent'])
        challenge_label.pack(pady=20)
        
        challenge_desc = tk.Label(challenge_card, text="Vastaa 10 kysymykseen 90% tarkkuudella", 
                                 font=('Segoe UI', 12),
                                 bg=COLORS['white'], fg=COLORS['dark'])
        challenge_desc.pack(pady=(0, 20))
        
        start_btn = tk.Button(challenge_card, text="Aloita haaste",
                             font=('Segoe UI', 11, 'bold'),
                             bg=COLORS['accent'], fg=COLORS['white'],
                             relief='flat', padx=30, pady=10,
                             command=self.start_challenge)
        start_btn.pack(pady=20)
        
        # Back button
        back_button = tk.Button(content_frame, text="← Takaisin",
                               font=('Segoe UI', 10),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               relief='flat', padx=20, pady=8,
                               command=lambda: self.controller.show_frame("MainMenu"))
        back_button.pack(side='bottom', pady=20)
    
    def get_daily_challenge_title(self, date):
        # Generoi eri haaste eri päiville
        challenges = [
            "Lääkelaskujen mestari",
            "Turvallisuusasiantuntija",
            "Farmakologian tuntija",
            "Injektiotekniikan osaaja",
            "Annosjakelun ammattilainen"
        ]
        return challenges[date.day % len(challenges)]
    
    def start_challenge(self):
        # Valitse 10 satunnaista kysymystä
        if len(all_questions) < 10:
            messagebox.showwarning("Ei riittävästi kysymyksiä", "Tarvitaan vähintään 10 kysymystä haasteeseen.")
            return
        
        questions = random.sample(all_questions, 10)
        self.controller.show_frame("PracticeView", questions, "daily_challenge")

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['light'])
        self.controller = controller
        
        self.create_modern_menu()
    
    def create_modern_menu(self):
        # Header
        header_frame = tk.Frame(self, bg=COLORS['primary'], height=120)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=COLORS['primary'])
        header_content.pack(expand=True, fill='both', padx=30)
        
        title_label = tk.Label(header_content, text="LOVe Enhanced", 
                              font=('Segoe UI', 32, 'bold'),
                              bg=COLORS['primary'], fg=COLORS['white'])
        title_label.pack(side='left', pady=30)
        
        # Streak info oikealla
        streak_frame = tk.Frame(header_content, bg=COLORS['primary'])
        streak_frame.pack(side='right', pady=30)
        
        current_streak = self.controller.stats_manager.achievement_manager.streaks.get('current_streak', 0)
        longest_streak = self.controller.stats_manager.achievement_manager.streaks.get('longest_streak', 0)
        
        streak_label = tk.Label(streak_frame, text=f"🔥 {current_streak} päivää", 
                               font=('Segoe UI', 14, 'bold'),
                               bg=COLORS['primary'], fg=COLORS['white'])
        streak_label.pack()
        
        best_label = tk.Label(streak_frame, text=f"Paras: {longest_streak}", 
                             font=('Segoe UI', 10),
                             bg=COLORS['primary'], fg=COLORS['white'])
        best_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Lääkehoidon osaaminen verkossa - Enhanced Edition", 
                                 font=('Segoe UI', 14),
                                 bg=COLORS['primary'], fg=COLORS['white'])
        subtitle_label.pack()
        
        # Main content
        main_frame = tk.Frame(self, bg=COLORS['light'])
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Cards container
        cards_frame = tk.Frame(main_frame, bg=COLORS['light'])
        cards_frame.pack(expand=True)
        
        # Menu cards (3x3 grid)
        self.create_menu_card(cards_frame, "📚 Harjoittele kaikkia", 
                             "Tee monivalintakysymyksiä kaikista osa-alueista",
                             lambda: self.show_difficulty_selection("all"), 0, 0)
        
        self.create_menu_card(cards_frame, "🧮 Lääkelaskut", 
                             "Harjoittele lääkelaskujen tekemistä",
                             lambda: self.show_difficulty_selection("laskut"), 0, 1)
        
        self.create_menu_card(cards_frame, "💊 Farmakologia", 
                             "Lääkkeiden vaikutusmekanismit",
                             lambda: self.show_difficulty_selection("farmakologia"), 0, 2)
        
        self.create_menu_card(cards_frame, "🛡️ Lääketurvallisuus", 
                             "Turvallinen lääkehoito",
                             lambda: self.show_difficulty_selection("turvallisuus"), 1, 0)
        
        self.create_menu_card(cards_frame, "🎯 Koesimulaatio", 
                             "50 kysymyksen koe (60 min)",
                             self.start_simulation, 1, 1)
        
        self.create_menu_card(cards_frame, "🌟 Päivittäinen haaste", 
                             "Päivän erikoishaaste",
                             lambda: self.controller.show_frame("DailyChallengeView"), 1, 2)
        
        self.create_menu_card(cards_frame, "📊 Tilastot & Saavutukset", 
                             "Seuraa edistymistäsi",
                             lambda: self.controller.show_frame("StatsView"), 2, 0)
        
        self.create_menu_card(cards_frame, "⚙️ Hallitse kysymyksiä", 
                             "Muokkaa kysymyspankkia",
                             lambda: self.controller.show_frame("QuestionManagementView"), 2, 1)
        
        self.create_menu_card(cards_frame, "📄 Vie PDF/Teksti", 
                             "Luo raportti tai kysymyskokoelma",
                             self.show_export_options, 2, 2)
    
    def create_menu_card(self, parent, title, description, command, row, col):
        card = tk.Frame(parent, bg=COLORS['white'], relief='solid', bd=1)
        card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew', ipadx=15, ipady=15)
        
        # Configure grid weights
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = tk.Label(card, text=title, 
                              font=('Segoe UI', 14, 'bold'),
                              bg=COLORS['white'], fg=COLORS['dark'])
        title_label.pack(pady=(10, 5))
        
        desc_label = tk.Label(card, text=description, 
                             font=('Segoe UI', 9),
                             bg=COLORS['white'], fg=COLORS['dark'],
                             wraplength=180, justify='center')
        desc_label.pack(pady=(0, 15))
        
        start_btn = tk.Button(card, text="Aloita",
                             font=('Segoe UI', 10, 'bold'),
                             bg=COLORS['primary'], fg=COLORS['white'],
                             relief='flat', padx=25, pady=6,
                             command=command)
        start_btn.pack()
        
        # Card hover effect
        def on_enter(e):
            card.configure(bg='#F8F9FA')
            title_label.configure(bg='#F8F9FA')
            desc_label.configure(bg='#F8F9FA')
        
        def on_leave(e):
            card.configure(bg=COLORS['white'])
            title_label.configure(bg=COLORS['white'])
            desc_label.configure(bg=COLORS['white'])
        
        for widget in [card, title_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def show_difficulty_selection(self, category):
        self.controller.show_frame("DifficultySelectionView", category=category)
    
    def start_simulation(self):
        if len(all_questions) < 50:
            messagebox.showerror("Virhe", f"Kysymyksiä ei ole riittävästi simulaatioon (väh. 50, nyt {len(all_questions)}).")
            return
        
        questions = random.sample(all_questions, 50)
        self.controller.show_frame("SimulationView", questions, "simulation")
    
    def show_export_options(self):
        """Näyttää vienti-valinnat"""
        export_window = tk.Toplevel(self)
        export_window.title("Vienti-valinnat")
        export_window.geometry("400x300")
        export_window.configure(bg=COLORS['light'])
        export_window.transient(self)
        export_window.grab_set()
        
        # Otsikko
        title_label = tk.Label(export_window, text="📄 Vienti-valinnat", 
                              font=('Segoe UI', 16, 'bold'),
                              bg=COLORS['light'], fg=COLORS['dark'])
        title_label.pack(pady=20)
        
        # Tilastoraportti
        stats_frame = tk.Frame(export_window, bg=COLORS['white'], relief='solid', bd=1)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        stats_title = tk.Label(stats_frame, text="📊 Tilastoraportti", 
                              font=('Segoe UI', 12, 'bold'),
                              bg=COLORS['white'], fg=COLORS['dark'])
        stats_title.pack(pady=10)
        
        # PDF ja teksti painikkeet vierekkäin
        stats_btn_frame = tk.Frame(stats_frame, bg=COLORS['white'])
        stats_btn_frame.pack(pady=10)
        
        pdf_stats_btn = tk.Button(stats_btn_frame, text="PDF-raportti",
                                 font=('Segoe UI', 10),
                                 bg=COLORS['primary'], fg=COLORS['white'],
                                 relief='flat', padx=15, pady=8,
                                 command=lambda: [self.export_pdf_stats(), export_window.destroy()])
        pdf_stats_btn.pack(side='left', padx=5)
        
        text_stats_btn = tk.Button(stats_btn_frame, text="Teksti-raportti",
                                  font=('Segoe UI', 10),
                                  bg=COLORS['secondary'], fg=COLORS['white'],
                                  relief='flat', padx=15, pady=8,
                                  command=lambda: [self.export_text_report(), export_window.destroy()])
        text_stats_btn.pack(side='left', padx=5)
        
        # Kysymyskokoelma
        questions_frame = tk.Frame(export_window, bg=COLORS['white'], relief='solid', bd=1)
        questions_frame.pack(fill='x', padx=20, pady=10)
        
        questions_title = tk.Label(questions_frame, text="📚 Kysymyskokoelma", 
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=COLORS['white'], fg=COLORS['dark'])
        questions_title.pack(pady=10)
        
        pdf_questions_btn = tk.Button(questions_frame, text="Vie kysymykset PDF:ksi",
                                     font=('Segoe UI', 10),
                                     bg=COLORS['accent'], fg=COLORS['white'],
                                     relief='flat', padx=20, pady=8,
                                     command=lambda: [self.export_questions_pdf(), export_window.destroy()])
        pdf_questions_btn.pack(pady=10)
        
        # Sulje-painike
        close_btn = tk.Button(export_window, text="Sulje",
                             font=('Segoe UI', 10),
                             bg=COLORS['light'], fg=COLORS['dark'],
                             relief='flat', padx=20, pady=8,
                             command=export_window.destroy)
        close_btn.pack(pady=20)
    
    def export_pdf_stats(self):
        """Vie tilastot PDF:ksi"""
        if not PDF_AVAILABLE:
            messagebox.showerror("Virhe", "PDF-vienti ei ole käytettävissä.\nAsenna 'reportlab' kirjasto:\npip install reportlab")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Tallenna tilastoraportti"
        )
        
        if filename:
            if PDFExporter.export_stats(self.controller.stats_manager.stats, filename):
                messagebox.showinfo("Onnistui", f"Tilastoraportti viety PDF-tiedostoon:\n{filename}")
    
    def export_questions_pdf(self):
        """Vie kysymykset PDF:ksi"""
        if not PDF_AVAILABLE:
            messagebox.showerror("Virhe", "PDF-vienti ei ole käytettävissä.\nAsenna 'reportlab' kirjasto:\npip install reportlab")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Tallenna kysymyskokoelma"
        )
        
        if filename:
            if PDFExporter.export_questions(all_questions, filename):
                messagebox.showinfo("Onnistui", f"Kysymykset viety PDF-tiedostoon:\n{filename}")
    
    def export_text_report(self):
        """Vie tilastot tekstitiedostoon"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Tallenna tilastoraportti"
        )
        
        if filename:
            try:
                stats = self.controller.stats_manager.stats
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("LOVe - Tilastoraportti\n")
                    f.write("=" * 30 + "\n\n")
                    f.write(f"Luotu: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
                    
                    # Yleiset tilastot
                    f.write("YLEISET TILASTOT\n")
                    f.write("-" * 15 + "\n")
                    total_answered = stats.get('total_answered', 0)
                    total_correct = stats.get('total_correct', 0)
                    overall_perc = (total_correct / total_answered * 100) if total_answered > 0 else 0
                    
                    f.write(f"Kysymyksiä vastattu: {total_answered}\n")
                    f.write(f"Oikeita vastauksia: {total_correct}\n")
                    f.write(f"Onnistumisprosentti: {overall_perc:.1f}%\n")
                    f.write(f"Käytetty aika: {int(stats.get('time_spent', 0)//60)} minuuttia\n\n")
                    
                    # Kategoriat
                    f.write("KATEGORIAKOHTAISET TULOKSET\n")
                    f.write("-" * 28 + "\n")
                    for cat, data in sorted(stats.get("categories", {}).items()):
                        cat_answered = data.get("answered", 0)
                        cat_correct = data.get("correct", 0)
                        cat_perc = (cat_correct / cat_answered * 100) if cat_answered > 0 else 0
                        f.write(f"{cat.capitalize()}: {cat_perc:.1f}% ({cat_correct}/{cat_answered})\n")
                    
                    # Saavutukset
                    f.write("\nSAAVUTUKSET\n")
                    f.write("-" * 10 + "\n")
                    achievements = self.controller.stats_manager.achievement_manager.achievements
                    if achievements:
                        for ach_id, unlocked in achievements.items():
                            if unlocked and ach_id in ACHIEVEMENTS:
                                ach = ACHIEVEMENTS[ach_id]
                                f.write(f"{ach['icon']} {ach['name']}: {ach['desc']}\n")
                    else:
                        f.write("Ei saavutuksia vielä\n")
                
                messagebox.showinfo("Onnistui", f"Tilastoraportti viety tiedostoon:\n{filename}")
            except Exception as e:
                messagebox.showerror("Virhe", f"Raportin luonti epäonnistui: {str(e)}")

class PracticeView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['light'])
        self.controller = controller
        self.start_time = None
        self.question_start_time = None
        
        self.create_practice_interface()
    
    def create_practice_interface(self):
        # Header
        header_frame = tk.Frame(self, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        self.progress_label = tk.Label(header_frame, text="", 
                                      font=('Segoe UI', 16, 'bold'),
                                      bg=COLORS['primary'], fg=COLORS['white'])
        self.progress_label.pack(pady=25)
        
        # Main content
        content_frame = tk.Frame(self, bg=COLORS['light'])
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)
        
        # Question area
        question_frame = tk.Frame(content_frame, bg=COLORS['white'], relief='solid', bd=1)
        question_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.question_label = tk.Label(question_frame, text="", 
                                      font=('Segoe UI', 14),
                                      bg=COLORS['white'], fg=COLORS['dark'],
                                      wraplength=800, justify="left")
        self.question_label.pack(pady=30, padx=30)
        
        # Options area
        self.options_frame = tk.Frame(content_frame, bg=COLORS['light'])
        self.options_frame.pack(pady=10)
        
        self.selected_option = tk.IntVar(value=-1)
        
        # Feedback
        self.feedback_label = tk.Label(content_frame, text="", 
                                      font=('Segoe UI', 12, 'bold'),
                                      bg=COLORS['light'])
        self.feedback_label.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(content_frame, bg=COLORS['light'])
        btn_frame.pack(pady=20)
        
        self.check_button = tk.Button(btn_frame, text="Tarkista vastaus",
                                     font=('Segoe UI', 11, 'bold'),
                                     bg=COLORS['success'], fg=COLORS['white'],
                                     relief='flat', padx=30, pady=10,
                                     command=self.check_answer)
        
        self.next_button = tk.Button(btn_frame, text="Seuraava kysymys",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg=COLORS['primary'], fg=COLORS['white'],
                                    relief='flat', padx=30, pady=10,
                                    command=self.display_question, state="disabled")
        
        self.check_button.grid(row=0, column=0, padx=10)
        self.next_button.grid(row=0, column=1, padx=10)
        
        # Bottom navigation
        bottom_frame = tk.Frame(content_frame, bg=COLORS['light'])
        bottom_frame.pack(side="bottom", fill='x', pady=20)
        
        calc_button = tk.Button(bottom_frame, text="🧮 Laskin",
                               font=('Segoe UI', 10),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               relief='flat', padx=20, pady=8,
                               command=self.controller.open_calculator)
        calc_button.pack(side="left")
        
        back_button = tk.Button(bottom_frame, text="← Palaa päävalikkoon",
                               font=('Segoe UI', 10),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               relief='flat', padx=20, pady=8,
                               command=lambda: self.controller.show_frame("MainMenu"))
        back_button.pack(side="right")
    
    def start(self, questions, mode, **kwargs):
        self.questions = questions
        self.mode = mode
        self.current_q_index = 0
        self.start_time = datetime.datetime.now()
        
        if not questions:
            messagebox.showinfo("Ei kysymyksiä", "Valitussa kategoriassa ei ole kysymyksiä.")
            self.controller.show_frame("MainMenu")
            return
        
        self.display_question()
    
    def display_question(self):
        if self.current_q_index >= len(self.questions):
            if self.mode == "daily_challenge":
                self.finish_daily_challenge()
            else:
                messagebox.showinfo("Harjoitus valmis", "Kaikki tämän osion kysymykset käyty läpi!")
                self.controller.show_frame("MainMenu")
            return
        
        self.question_start_time = datetime.datetime.now()
        
        # Update progress
        self.progress_label.config(text=f"Kysymys {self.current_q_index + 1} / {len(self.questions)}")
        
        # Clear feedback
        self.feedback_label.config(text="")
        self.check_button.config(state="normal")
        self.next_button.config(state="disabled")
        
        # Display question
        q_data = self.questions[self.current_q_index]
        self.question_label.config(text=q_data[0])
        
        # Clear and create options
        for widget in self.options_frame.winfo_children(): 
            widget.destroy()
        
        self.selected_option.set(-1)
        
        for i, option_text in enumerate(q_data[2]):
            option_frame = tk.Frame(self.options_frame, bg=COLORS['white'], relief='solid', bd=1)
            option_frame.pack(fill='x', pady=5, padx=20)
            
            rb = tk.Radiobutton(option_frame, text=f"{chr(65+i)}. {option_text}",
                               variable=self.selected_option, value=i,
                               font=('Segoe UI', 11),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               selectcolor=COLORS['primary'])
            rb.pack(anchor="w", padx=15, pady=10)
    
    def check_answer(self):
        q_data = self.questions[self.current_q_index]
        user_choice = self.selected_option.get()
        
        if user_choice == -1:
            messagebox.showwarning("Ei valintaa", "Valitse yksi vastausvaihtoehdoista.")
            return
        
        # Calculate time taken for this question
        current_time = datetime.datetime.now()
        time_taken = (current_time - self.question_start_time).total_seconds() if self.question_start_time else 0
        
        correct_index = q_data[3]
        is_correct = user_choice == correct_index
        
        # Update stats and check achievements
        context = {'fast_answer': time_taken <= 10} if time_taken <= 10 else {}
        new_achievements, current_streak = self.controller.stats_manager.update(q_data[4], is_correct, time_taken, context)
        
        # Show achievements
        if new_achievements:
            self.controller.show_achievements(new_achievements)
        
        # Show feedback
        if is_correct:
            self.feedback_label.config(text="✅ Oikein! Hyvä!", fg=COLORS['success'])
        else:
            correct_answer = q_data[2][correct_index]
            self.feedback_label.config(text=f"❌ Väärin. Oikea vastaus: {chr(65+correct_index)}. {correct_answer}", 
                                     fg=COLORS['danger'])
        
        # Show explanation
        messagebox.showinfo("Selitys", q_data[1])
        
        self.check_button.config(state="disabled")
        self.next_button.config(state="normal")
        self.current_q_index += 1
    
    def finish_daily_challenge(self):
        messagebox.showinfo("Haaste valmis", "Päivittäinen haaste suoritettu!\n🎉 Hyvää työtä!")
        self.controller.show_frame("MainMenu")

class SimulationView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['light'])
        self.controller = controller
        self.timer_id = None
        self.start_time = None
        
        self.content_frame = tk.Frame(self, bg=COLORS['light'])
        self.content_frame.pack(fill="both", expand=True)
    
    def start(self, questions, mode, **kwargs):
        for widget in self.content_frame.winfo_children(): 
            widget.destroy()
        
        self.questions = questions
        self.current_q_index = 0
        self.answers = []
        self.time_left = 3600  # 60 minutes
        self.start_time = datetime.datetime.now()
        
        self.create_simulation_interface()
        self.display_question()
        self.update_timer()
    
    def create_simulation_interface(self):
        # Header with timer and progress
        header_frame = tk.Frame(self.content_frame, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=COLORS['primary'])
        header_content.pack(expand=True, fill='both', padx=30)
        
        self.timer_label = tk.Label(header_content, text="", 
                                   font=('Segoe UI', 14, 'bold'),
                                   bg=COLORS['primary'], fg=COLORS['white'])
        self.timer_label.pack(side="left", pady=25)
        
        self.progress_label = tk.Label(header_content, text="", 
                                      font=('Segoe UI', 14, 'bold'),
                                      bg=COLORS['primary'], fg=COLORS['white'])
        self.progress_label.pack(side="right", pady=25)
        
        # Progress bar
        progress_frame = tk.Frame(self.content_frame, bg=COLORS['light'], height=10)
        progress_frame.pack(fill='x')
        progress_frame.pack_propagate(False)
        
        self.progress_canvas = tk.Canvas(progress_frame, height=6, bg=COLORS['light'], highlightthickness=0)
        self.progress_canvas.pack(fill='x', padx=30, pady=2)
        
        # Question content
        content_frame = tk.Frame(self.content_frame, bg=COLORS['light'])
        content_frame.pack(expand=True, fill='both', padx=40, pady=20)
        
        # Question area
        question_frame = tk.Frame(content_frame, bg=COLORS['white'], relief='solid', bd=1)
        question_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.question_label = tk.Label(question_frame, text="", 
                                      font=('Segoe UI', 14),
                                      bg=COLORS['white'], fg=COLORS['dark'],
                                      wraplength=800, justify="left")
        self.question_label.pack(pady=30, padx=30)
        
        # Options
        self.options_frame = tk.Frame(content_frame, bg=COLORS['light'])
        self.options_frame.pack(pady=10)
        
        self.selected_option = tk.IntVar(value=-1)
        
        # Navigation buttons
        btn_frame = tk.Frame(content_frame, bg=COLORS['light'])
        btn_frame.pack(pady=20)
        
        self.next_button = tk.Button(btn_frame, text="Seuraava kysymys",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg=COLORS['primary'], fg=COLORS['white'],
                                    relief='flat', padx=30, pady=10,
                                    command=self.next_sim_question)
        self.next_button.pack(side="left", padx=10)
        
        calc_button = tk.Button(btn_frame, text="🧮 Laskin",
                               font=('Segoe UI', 10),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               relief='flat', padx=20, pady=8,
                               command=self.controller.open_calculator)
        calc_button.pack(side="left", padx=10)
    
    def display_question(self):
        # Update progress
        progress = (self.current_q_index / len(self.questions)) * 100
        self.progress_label.config(text=f"Kysymys {self.current_q_index + 1} / {len(self.questions)}")
        
        # Draw progress bar
        self.progress_canvas.delete("all")
        canvas_width = self.progress_canvas.winfo_width()
        if canvas_width > 1:
            progress_width = (canvas_width * progress) / 100
            self.progress_canvas.create_rectangle(0, 0, progress_width, 6, 
                                                fill=COLORS['success'], outline="")
            self.progress_canvas.create_rectangle(progress_width, 0, canvas_width, 6, 
                                                fill='#E0E0E0', outline="")
        
        # Display question
        q_data = self.questions[self.current_q_index]
        self.question_label.config(text=q_data[0])
        
        # Create options
        for widget in self.options_frame.winfo_children(): 
            widget.destroy()
        
        self.selected_option.set(-1)
        
        for i, option_text in enumerate(q_data[2]):
            option_frame = tk.Frame(self.options_frame, bg=COLORS['white'], relief='solid', bd=1)
            option_frame.pack(fill='x', pady=5, padx=20)
            
            rb = tk.Radiobutton(option_frame, text=f"{chr(65+i)}. {option_text}",
                               variable=self.selected_option, value=i,
                               font=('Segoe UI', 11),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               selectcolor=COLORS['primary'])
            rb.pack(anchor="w", padx=15, pady=10)
        
        # Update next button text
        if self.current_q_index == len(self.questions) - 1:
            self.next_button.config(text="Lopeta koe")
    
    def next_sim_question(self):
        self.answers.append(self.selected_option.get())
        self.current_q_index += 1
        
        if self.current_q_index >= len(self.questions):
            self.end_simulation()
        else:
            self.display_question()
    
    def update_timer(self):
        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f"⏱️ {mins:02d}:{secs:02d}")
            self.time_left -= 1
            self.timer_id = self.after(1000, self.update_timer)
        else:
            self.end_simulation()
    
    def end_simulation(self):
        if self.timer_id: 
            self.after_cancel(self.timer_id)
            self.timer_id = None
        
        # Clear content
        for widget in self.content_frame.winfo_children(): 
            widget.destroy()
        
        # Calculate results
        while len(self.answers) < len(self.questions): 
            self.answers.append(-1)
        
        score = sum(1 for i, q in enumerate(self.questions) if self.answers[i] == q[3])
        total = len(self.questions)
        percentage = (score / total) * 100 if total > 0 else 0
        passed = percentage >= 90
        
        # Calculate time taken
        time_taken = (datetime.datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        # Save results and check achievements
        new_achievements = self.controller.stats_manager.add_simulation_result(score, total, time_taken)
        
        # Show achievements
        if new_achievements:
            self.controller.show_achievements(new_achievements)
        
        # Create results screen
        self.create_results_screen(score, total, percentage, passed, time_taken)
    
    def create_results_screen(self, score, total, percentage, passed, time_taken):
        # Header
        header_frame = tk.Frame(self.content_frame, bg=COLORS['success'] if passed else COLORS['danger'], height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        result_text = "🎉 HYVÄKSYTTY!" if passed else "❌ HYLÄTTY"
        result_label = tk.Label(header_frame, text=result_text, 
                               font=('Segoe UI', 24, 'bold'),
                               bg=COLORS['success'] if passed else COLORS['danger'], 
                               fg=COLORS['white'])
        result_label.pack(pady=30)
        
        # Results content
        content_frame = tk.Frame(self.content_frame, bg=COLORS['light'])
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)
        
        # Results card
        results_card = tk.Frame(content_frame, bg=COLORS['white'], relief='solid', bd=1)
        results_card.pack(expand=True, fill='both', padx=100, pady=50)
        
        # Score
        score_label = tk.Label(results_card, text=f"{score} / {total}",
                              font=('Segoe UI', 48, 'bold'),
                              bg=COLORS['white'], fg=COLORS['primary'])
        score_label.pack(pady=(40, 20))
        
        percentage_label = tk.Label(results_card, text=f"{percentage:.1f}%",
                                   font=('Segoe UI', 24),
                                   bg=COLORS['white'], fg=COLORS['dark'])
        percentage_label.pack(pady=(0, 20))
        
        # Time
        mins, secs = divmod(int(time_taken), 60)
        time_label = tk.Label(results_card, text=f"Aika: {mins}:{secs:02d}",
                             font=('Segoe UI', 14),
                             bg=COLORS['white'], fg=COLORS['dark'])
        time_label.pack(pady=(0, 40))
        
        # Return button
        return_btn = tk.Button(results_card, text="Palaa päävalikkoon",
                              font=('Segoe UI', 11, 'bold'),
                              bg=COLORS['primary'], fg=COLORS['white'],
                              relief='flat', padx=30, pady=10,
                              command=lambda: self.controller.show_frame("MainMenu"))
        return_btn.pack(pady=20)

class StatsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['light'])
        self.controller = controller
    
    def tkraise(self, aboveThis=None):
        # Clear previous content
        for widget in self.winfo_children(): 
            widget.destroy()
        
        self.create_stats_interface()
        super().tkraise(aboveThis)
    
    def create_stats_interface(self):
        # Header
        header_frame = tk.Frame(self, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="📊 Tilastot & Saavutukset", 
                              font=('Segoe UI', 20, 'bold'),
                              bg=COLORS['primary'], fg=COLORS['white'])
        title_label.pack(pady=25)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Tilastot tab
        stats_tab = tk.Frame(notebook, bg=COLORS['light'])
        notebook.add(stats_tab, text="📈 Tilastot")
        self.create_stats_tab(stats_tab)
        
        # Graafit tab (jos matplotlib saatavilla)
        if MATPLOTLIB_AVAILABLE:
            charts_tab = tk.Frame(notebook, bg=COLORS['light'])
            notebook.add(charts_tab, text="📊 Graafit")
            self.create_charts_tab(charts_tab)
        
        # Saavutukset tab
        achievements_tab = tk.Frame(notebook, bg=COLORS['light'])
        notebook.add(achievements_tab, text="🏆 Saavutukset")
        self.create_achievements_tab(achievements_tab)
        
        # Back button
        back_button = tk.Button(self, text="← Palaa päävalikkoon",
                               font=('Segoe UI', 11),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               relief='flat', padx=20, pady=10,
                               command=lambda: self.controller.show_frame("MainMenu"))
        back_button.pack(pady=10)
    
    def create_stats_tab(self, parent):
        # Scrollable frame
        canvas = tk.Canvas(parent, bg=COLORS['light'])
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        stats = self.controller.stats_manager.stats
        
        # Overview cards
        overview_frame = tk.Frame(scrollable_frame, bg=COLORS['light'])
        overview_frame.pack(fill='x', pady=(10, 30), padx=20)
        
        total_answered = stats.get('total_answered', 0)
        total_correct = stats.get('total_correct', 0)
        overall_perc = (total_correct / total_answered * 100) if total_answered > 0 else 0
        total_time = stats.get('time_spent', 0)
        
        self.create_stat_card(overview_frame, "Kysymyksiä vastattu", str(total_answered), "📝", 0)
        self.create_stat_card(overview_frame, "Onnistumisprosentti", f"{overall_perc:.1f}%", "✅", 1)
        self.create_stat_card(overview_frame, "Käytetty aika", f"{int(total_time//3600)}h {int((total_time%3600)//60)}min", "⏱️", 2)
        
        # Streak info
        streaks = self.controller.stats_manager.achievement_manager.streaks
        current_streak = streaks.get('current_streak', 0)
        longest_streak = streaks.get('longest_streak', 0)
        
        self.create_stat_card(overview_frame, "Nykyinen sarja", f"{current_streak} päivää", "🔥", 3)
        
        # Categories section
        categories_frame = tk.Frame(scrollable_frame, bg=COLORS['white'], relief='solid', bd=1)
        categories_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        cat_title = tk.Label(categories_frame, text="Kategoriakohtaiset tulokset", 
                            font=('Segoe UI', 16, 'bold'),
                            bg=COLORS['white'], fg=COLORS['dark'])
        cat_title.pack(pady=20)
        
        # Categories list
        for cat, data in sorted(stats.get("categories", {}).items()):
            cat_answered = data.get("answered", 0)
            cat_correct = data.get("correct", 0)
            cat_perc = (cat_correct / cat_answered * 100) if cat_answered > 0 else 0
            
            cat_frame = tk.Frame(categories_frame, bg=COLORS['light'])
            cat_frame.pack(fill='x', padx=30, pady=5)
            
            cat_name = tk.Label(cat_frame, text=cat.capitalize(),
                               font=('Segoe UI', 12, 'bold'),
                               bg=COLORS['light'], fg=COLORS['dark'])
            cat_name.pack(side='left')
            
            cat_stats = tk.Label(cat_frame, text=f"{cat_perc:.1f}% ({cat_correct}/{cat_answered})",
                                font=('Segoe UI', 12),
                                bg=COLORS['light'], fg=COLORS['primary'])
            cat_stats.pack(side='right')
        
        # Recent simulations
        sim_frame = tk.Frame(scrollable_frame, bg=COLORS['white'], relief='solid', bd=1)
        sim_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        sim_title = tk.Label(sim_frame, text="Viimeisimmät koesimulaatiot", 
                            font=('Segoe UI', 16, 'bold'),
                            bg=COLORS['white'], fg=COLORS['dark'])
        sim_title.pack(pady=20)
        
        simulations = stats.get("simulations", [])[-5:]
        if simulations:
            for sim in simulations:
                perc = (sim['score'] / sim['total'] * 100) if sim['total'] > 0 else 0
                result = "Hyväksytty" if perc >= 90 else "Hylätty"
                result_color = COLORS['success'] if perc >= 90 else COLORS['danger']
                
                sim_item = tk.Frame(sim_frame, bg=COLORS['light'])
                sim_item.pack(fill='x', padx=30, pady=5)
                
                date_label = tk.Label(sim_item, text=sim['date'],
                                     font=('Segoe UI', 10),
                                     bg=COLORS['light'], fg=COLORS['dark'])
                date_label.pack(side='left')
                
                result_label = tk.Label(sim_item, text=f"{sim['score']}/{sim['total']} ({perc:.1f}%) - {result}",
                                       font=('Segoe UI', 10, 'bold'),
                                       bg=COLORS['light'], fg=result_color)
                result_label.pack(side='right')
        else:
            no_sims = tk.Label(sim_frame, text="Ei simulaatioita vielä suoritettu",
                              font=('Segoe UI', 11, 'italic'),
                              bg=COLORS['white'], fg=COLORS['dark'])
            no_sims.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_charts_tab(self, parent):
        """Luo matplotlib-kaaviot"""
        if not MATPLOTLIB_AVAILABLE:
            error_label = tk.Label(parent, text="Matplotlib ei ole saatavilla.\nAsenna: pip install matplotlib",
                                  font=('Segoe UI', 12),
                                  bg=COLORS['light'], fg=COLORS['danger'])
            error_label.pack(expand=True)
            return
        
        # Scrollable frame
        canvas = tk.Canvas(parent, bg=COLORS['light'])
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        stats = self.controller.stats_manager.stats
        categories = stats.get("categories", {})
        
        if not categories:
            no_data_label = tk.Label(scrollable_frame, text="Ei tilastoja näytettäväksi.\nVastaa ensin muutama kysymys!",
                                    font=('Segoe UI', 12),
                                    bg=COLORS['light'], fg=COLORS['dark'])
            no_data_label.pack(expand=True, pady=50)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            return
        
        # Kategoriajakauma (ympyräkaavio)
        if categories:
            fig1 = Figure(figsize=(10, 6), dpi=100)
            fig1.patch.set_facecolor(COLORS['light'])
            
            # Vastausmäärät kategorioidttain
            ax1 = fig1.add_subplot(121)
            cat_names = []
            cat_answers = []
            
            for cat, data in categories.items():
                cat_names.append(cat.capitalize())
                cat_answers.append(data.get('answered', 0))
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
            ax1.pie(cat_answers, labels=cat_names, autopct='%1.1f%%', startangle=90, colors=colors[:len(cat_names)])
            ax1.set_title('Vastausmäärät kategorioittain', fontsize=14, fontweight='bold')
            
            # Onnistumisprosentit kategorioidttain (pylväskaavio)
            ax2 = fig1.add_subplot(122)
            cat_percentages = []
            
            for cat, data in categories.items():
                answered = data.get('answered', 0)
                correct = data.get('correct', 0)
                percentage = (correct / answered * 100) if answered > 0 else 0
                cat_percentages.append(percentage)
            
            bars = ax2.bar(range(len(cat_names)), cat_percentages, color=colors[:len(cat_names)])
            ax2.set_title('Onnistumisprosentit kategorioittain', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Onnistumisprosentti (%)')
            ax2.set_xticks(range(len(cat_names)))
            ax2.set_xticklabels([name[:8] + '..' if len(name) > 8 else name for name in cat_names], 
                              rotation=45, ha='right')
            ax2.set_ylim(0, 100)
            
            # Lisää prosenttiarvot pylväiden päälle
            for bar, percentage in zip(bars, cat_percentages):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{percentage:.1f}%', ha='center', va='bottom', fontsize=10)
            
            fig1.tight_layout()
            
            # Lisää kaavio tkinteriin
            chart_frame1 = tk.Frame(scrollable_frame, bg=COLORS['white'], relief='solid', bd=1)
            chart_frame1.pack(fill='x', padx=20, pady=10)
            
            chart_title1 = tk.Label(chart_frame1, text="📊 Kategoriatilastot", 
                                   font=('Segoe UI', 14, 'bold'),
                                   bg=COLORS['white'], fg=COLORS['dark'])
            chart_title1.pack(pady=10)
            
            canvas1 = FigureCanvasTkAgg(fig1, chart_frame1)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # Simulaatiotulosten kehitys (viivakaavio)
        simulations = stats.get("simulations", [])
        if len(simulations) >= 2:
            fig2 = Figure(figsize=(10, 4), dpi=100)
            fig2.patch.set_facecolor(COLORS['light'])
            ax3 = fig2.add_subplot(111)
            
            # Ota viimeiset 10 simulaatiota
            recent_sims = simulations[-10:]
            dates = [sim['date'][-5:] for sim in recent_sims]  # Ota vain aika-osuus
            percentages = [(sim['score'] / sim['total'] * 100) for sim in recent_sims]
            
            ax3.plot(dates, percentages, marker='o', linewidth=2, markersize=6, color='#4ECDC4')
            ax3.set_title('Simulaatiotulosten kehitys', fontsize=14, fontweight='bold')
            ax3.set_ylabel('Onnistumisprosentti (%)')
            ax3.set_xlabel('Päivämäärä ja aika')
            ax3.grid(True, alpha=0.3)
            ax3.set_ylim(0, 100)
            
            # Lisää viiva 90% kohdalle (hyväksymisraja)
            ax3.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='Hyväksymisraja (90%)')
            ax3.legend()
            
            plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
            fig2.tight_layout()
            
            # Lisää kaavio tkinteriin
            chart_frame2 = tk.Frame(scrollable_frame, bg=COLORS['white'], relief='solid', bd=1)
            chart_frame2.pack(fill='x', padx=20, pady=10)
            
            chart_title2 = tk.Label(chart_frame2, text="📈 Edistyminen simulaatioissa", 
                                   font=('Segoe UI', 14, 'bold'),
                                   bg=COLORS['white'], fg=COLORS['dark'])
            chart_title2.pack(pady=10)
            
            canvas2 = FigureCanvasTkAgg(fig2, chart_frame2)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_achievements_tab(self, parent):
        # Scrollable frame
        canvas = tk.Canvas(parent, bg=COLORS['light'])
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Achievement grid
        achievements = self.controller.stats_manager.achievement_manager.achievements
        
        # Title
        title_label = tk.Label(scrollable_frame, text="Saavutukset", 
                              font=('Segoe UI', 18, 'bold'),
                              bg=COLORS['light'], fg=COLORS['dark'])
        title_label.pack(pady=20)
        
        # Achievement cards
        achievements_frame = tk.Frame(scrollable_frame, bg=COLORS['light'])
        achievements_frame.pack(fill='both', expand=True, padx=20)
        
        row = 0
        col = 0
        for ach_id, ach_data in ACHIEVEMENTS.items():
            unlocked = achievements.get(ach_id, False)
            
            self.create_achievement_card(achievements_frame, ach_data, unlocked, row, col)
            
            col += 1
            if col >= 3:  # 3 saavutusta per rivi
                col = 0
                row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_achievement_card(self, parent, ach_data, unlocked, row, col):
        # Väri riippuen siitä onko avattu
        bg_color = COLORS['gold'] if unlocked else COLORS['white']
        text_color = COLORS['white'] if unlocked else COLORS['dark']
        border_color = COLORS['gold'] if unlocked else '#CCCCCC'
        
        card = tk.Frame(parent, bg=bg_color, relief='solid', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew', ipadx=15, ipady=15)
        
        # Configure grid weights
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Ikoni
        icon_label = tk.Label(card, text=ach_data['icon'], 
                             font=('Segoe UI', 24),
                             bg=bg_color, fg=text_color)
        icon_label.pack(pady=(5, 10))
        
        # Nimi
        name_label = tk.Label(card, text=ach_data['name'], 
                             font=('Segoe UI', 12, 'bold'),
                             bg=bg_color, fg=text_color,
                             wraplength=150)
        name_label.pack()
        
        # Kuvaus
        desc_label = tk.Label(card, text=ach_data['desc'], 
                             font=('Segoe UI', 9),
                             bg=bg_color, fg=text_color,
                             wraplength=150, justify='center')
        desc_label.pack(pady=(5, 5))
        
        # Status
        status_text = "✅ Avattu" if unlocked else "🔒 Lukittu"
        status_label = tk.Label(card, text=status_text, 
                               font=('Segoe UI', 8),
                               bg=bg_color, fg=text_color)
        status_label.pack()
    
    def create_stat_card(self, parent, title, value, icon, col):
        card = tk.Frame(parent, bg=COLORS['white'], relief='solid', bd=1)
        card.grid(row=0, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_columnconfigure(col, weight=1)
        
        icon_label = tk.Label(card, text=icon, font=('Segoe UI', 24),
                             bg=COLORS['white'])
        icon_label.pack(pady=(20, 10))
        
        value_label = tk.Label(card, text=value, 
                              font=('Segoe UI', 20, 'bold'),
                              bg=COLORS['white'], fg=COLORS['primary'])
        value_label.pack()
        
        title_label = tk.Label(card, text=title, 
                              font=('Segoe UI', 10),
                              bg=COLORS['white'], fg=COLORS['dark'])
        title_label.pack(pady=(5, 20))

class QuestionManagementView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['light'])
        self.controller = controller
        self.currently_editing_index = None
        self.filtered_question_map = []
        
        self.create_management_interface()
    
    def create_management_interface(self):
        # Header
        header_frame = tk.Frame(self, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="⚙️ Kysymysten hallinta", 
                              font=('Segoe UI', 20, 'bold'),
                              bg=COLORS['primary'], fg=COLORS['white'])
        title_label.pack(pady=25)
        
        # Content
        content_frame = tk.Frame(self, bg=COLORS['light'])
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Selection frame
        selection_frame = tk.LabelFrame(content_frame, text="Valitse kysymys",
                                       font=('Segoe UI', 12, 'bold'),
                                       bg=COLORS['light'], fg=COLORS['dark'])
        selection_frame.pack(fill="x", pady=(0, 20))
        
        filter_frame = tk.Frame(selection_frame, bg=COLORS['light'])
        filter_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(filter_frame, text="Kategoria:", font=('Segoe UI', 10),
                bg=COLORS['light']).pack(side="left")
        
        self.category_filter_combo = ttk.Combobox(filter_frame, state="readonly", width=20)
        self.category_filter_combo.pack(side="left", padx=(5, 20))
        self.category_filter_combo.bind("<<ComboboxSelected>>", self.on_category_filter_selected)
        
        self.question_selector_combo = ttk.Combobox(filter_frame, state="readonly", width=60)
        self.question_selector_combo.pack(side="left", fill="x", expand=True, padx=5)
        
        load_button = tk.Button(filter_frame, text="Lataa", 
                               font=('Segoe UI', 10),
                               bg=COLORS['primary'], fg=COLORS['white'],
                               relief='flat', padx=15, pady=5,
                               command=self.load_selected_question)
        load_button.pack(side="left", padx=(10, 0))
        
        # Edit frame
        edit_frame = tk.LabelFrame(content_frame, text="Kysymyksen tiedot",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=COLORS['light'], fg=COLORS['dark'])
        edit_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Form fields
        form_frame = tk.Frame(edit_frame, bg=COLORS['light'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        fields = ["Kysymys:", "Ratkaisu/Perustelu:", "Vaihtoehto 1:", "Vaihtoehto 2:", "Vaihtoehto 3:", "Vaihtoehto 4:"]
        self.entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(form_frame, text=field, font=('Segoe UI', 10, 'bold'),
                    bg=COLORS['light']).grid(row=i, column=0, sticky="w", pady=5)
            
            if field == "Kysymys:" or field == "Ratkaisu/Perustelu:":
                entry = tk.Text(form_frame, width=60, height=3, font=('Segoe UI', 10))
            else:
                entry = tk.Entry(form_frame, width=60, font=('Segoe UI', 10))
            
            entry.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=5)
            self.entries[field] = entry
        
        # Correct answer and category
        tk.Label(form_frame, text="Oikea vastaus:", font=('Segoe UI', 10, 'bold'),
                bg=COLORS['light']).grid(row=6, column=0, sticky="w", pady=5)
        
        self.correct_answer_combo = ttk.Combobox(form_frame, values=[1, 2, 3, 4], 
                                               state="readonly", width=10)
        self.correct_answer_combo.grid(row=6, column=1, sticky="w", padx=(10, 0), pady=5)
        
        tk.Label(form_frame, text="Kategoria:", font=('Segoe UI', 10, 'bold'),
                bg=COLORS['light']).grid(row=7, column=0, sticky="w", pady=5)
        
        self.category_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.category_combo.grid(row=7, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Vaikeustasojen lisäys
        tk.Label(form_frame, text="Vaikeustaso:", font=('Segoe UI', 10, 'bold'),
                bg=COLORS['light']).grid(row=8, column=0, sticky="w", pady=5)
        
        self.difficulty_combo = ttk.Combobox(form_frame, values=["aloittelija", "keskitaso", "edistynyt"], 
                                           state="readonly", width=15)
        self.difficulty_combo.grid(row=8, column=1, sticky="w", padx=(10, 0), pady=5)
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Action buttons
        action_frame = tk.Frame(content_frame, bg=COLORS['light'])
        action_frame.pack(fill="x", pady=10)
        
        save_changes_btn = tk.Button(action_frame, text="💾 Tallenna muutokset",
                                    font=('Segoe UI', 10),
                                    bg=COLORS['success'], fg=COLORS['white'],
                                    relief='flat', padx=20, pady=8,
                                    command=self.save_changes_to_question)
        save_changes_btn.pack(side="left", padx=10)
        
        save_new_btn = tk.Button(action_frame, text="➕ Tallenna uutena",
                                font=('Segoe UI', 10),
                                bg=COLORS['primary'], fg=COLORS['white'],
                                relief='flat', padx=20, pady=8,
                                command=self.add_question)
        save_new_btn.pack(side="left", padx=10)
        
        delete_btn = tk.Button(action_frame, text="🗑️ Poista",
                              font=('Segoe UI', 10),
                              bg=COLORS['danger'], fg=COLORS['white'],
                              relief='flat', padx=20, pady=8,
                              command=self.delete_question)
        delete_btn.pack(side="left", padx=10)
        
        clear_btn = tk.Button(action_frame, text="🔄 Tyhjennä",
                             font=('Segoe UI', 10),
                             bg=COLORS['warning'], fg=COLORS['white'],
                             relief='flat', padx=20, pady=8,
                             command=self.clear_form)
        clear_btn.pack(side="left", padx=10)
        
        # Back button
        back_button = tk.Button(content_frame, text="← Palaa päävalikkoon",
                               font=('Segoe UI', 11),
                               bg=COLORS['white'], fg=COLORS['dark'],
                               relief='flat', padx=20, pady=10,
                               command=lambda: self.controller.show_frame("MainMenu"))
        back_button.pack(pady=20)
    
    def start(self, questions=None, mode=None, **kwargs):
        self.update_category_filter_combo()
        self.on_category_filter_selected()
        self.update_add_category_combo()
        self.clear_form()
    
    def update_category_filter_combo(self):
        base_categories = ["Kaikki kategoriat"]
        existing_categories = sorted(list(set(q[4] for q in all_questions if len(q) > 4)))
        self.category_filter_combo['values'] = base_categories + existing_categories
        self.category_filter_combo.set(base_categories[0])
    
    def on_category_filter_selected(self, event=None):
        selected_category = self.category_filter_combo.get()
        self.filtered_question_map = []
        
        for i, q in enumerate(all_questions):
            if selected_category == "Kaikki kategoriat" or q[4] == selected_category:
                self.filtered_question_map.append({'original_index': i, 'question_text': q[0]})
        
        display_texts = []
        for item in self.filtered_question_map:
            text = item['question_text']
            if len(text) > 80:
                text = text[:80] + "..."
            display_texts.append(text)
        
        self.question_selector_combo['values'] = display_texts
        self.clear_form()
    
    def update_add_category_combo(self):
        base_categories = ["laskut", "farmakologia", "turvallisuus", "annosjakelu", "injektiot", 
                          "inhalaatiot", "silmalääkkeet", "pkv_lääkkeet", "n_lääkkeet", 
                          "infuusiot", "korva_nenä", "peräsuoli_emätin", "iholääkkeet"]
        existing_categories = sorted(list(set(q[4] for q in all_questions if len(q) > 4)))
        all_possible_categories = sorted(list(set(base_categories + existing_categories)))
        self.category_combo['values'] = all_possible_categories
    
    def clear_form(self):
        self.currently_editing_index = None
        
        for field, entry in self.entries.items():
            if isinstance(entry, tk.Text):
                entry.delete(1.0, tk.END)
            else:
                entry.delete(0, tk.END)
        
        self.correct_answer_combo.set(1)
        if self.category_combo['values']: 
            self.category_combo.set(self.category_combo['values'][0])
        self.difficulty_combo.set("keskitaso")
        self.question_selector_combo.set("")
    
    def get_selected_original_index(self):
        selection_idx = self.question_selector_combo.current()
        if selection_idx == -1: 
            return None
        if 0 <= selection_idx < len(self.filtered_question_map):
            return self.filtered_question_map[selection_idx]['original_index']
        return None
    
    def load_selected_question(self):
        original_index = self.get_selected_original_index()
        if original_index is None:
            messagebox.showwarning("Ei valintaa", "Valitse ensin kysymys pudotusvalikosta.")
            return
        
        self.currently_editing_index = original_index
        q_data = all_questions[original_index]
        
        # Load data into form
        question_entry = self.entries["Kysymys:"]
        if isinstance(question_entry, tk.Text):
            question_entry.delete(1.0, tk.END)
            question_entry.insert(1.0, q_data[0])
        
        solution_entry = self.entries["Ratkaisu/Perustelu:"]
        if isinstance(solution_entry, tk.Text):
            solution_entry.delete(1.0, tk.END)
            solution_entry.insert(1.0, q_data[1])
        
        for i in range(4):
            entry = self.entries[f"Vaihtoehto {i+1}:"]
            entry.delete(0, tk.END)
            entry.insert(0, q_data[2][i])
        
        self.correct_answer_combo.set(q_data[3] + 1)
        self.category_combo.set(q_data[4])
        
        # Vaikeustaso (jos olemassa)
        if len(q_data) > 5:
            self.difficulty_combo.set(q_data[5])
        else:
            self.difficulty_combo.set("keskitaso")
    
    def get_data_from_form(self):
        question_entry = self.entries["Kysymys:"]
        if isinstance(question_entry, tk.Text):
            q_text = question_entry.get(1.0, tk.END).strip()
        else:
            q_text = question_entry.get().strip()
        
        solution_entry = self.entries["Ratkaisu/Perustelu:"]
        if isinstance(solution_entry, tk.Text):
            solution = solution_entry.get(1.0, tk.END).strip()
        else:
            solution = solution_entry.get().strip()
        
        options = [self.entries[f"Vaihtoehto {i+1}:"].get().strip() for i in range(4)]
        correct_answer_str = self.correct_answer_combo.get()
        category = self.category_combo.get()
        difficulty = self.difficulty_combo.get()
        
        if not all([q_text, solution, category, correct_answer_str, difficulty] + options):
            messagebox.showwarning("Puutteelliset tiedot", "Täytä kaikki kentät ennen tallentamista.")
            return None
        
        correct_index = int(correct_answer_str) - 1
        return [q_text, solution, options, correct_index, category, difficulty]
    
    def add_question(self):
        new_question_data = self.get_data_from_form()
        if new_question_data:
            all_questions.append(new_question_data)
            save_questions_to_json()
            self.start()
            messagebox.showinfo("Onnistui", "Uusi kysymys tallennettu!")
    
    def save_changes_to_question(self):
        if self.currently_editing_index is None:
            messagebox.showwarning("Ei kysymystä ladattuna", "Lataa ensin muokattava kysymys.")
            return
        
        updated_question_data = self.get_data_from_form()
        if updated_question_data:
            all_questions[self.currently_editing_index] = updated_question_data
            save_questions_to_json()
            self.start()
            messagebox.showinfo("Onnistui", "Muutokset tallennettu!")
    
    def delete_question(self):
        original_index = self.get_selected_original_index()
        if original_index is None:
            messagebox.showwarning("Ei valintaa", "Valitse poistettava kysymys pudotusvalikosta.")
            return
        
        question_text = all_questions[original_index][0]
        display_text = question_text[:80] + "..." if len(question_text) > 80 else question_text
        
        if messagebox.askyesno("Vahvista poisto", f"Haluatko varmasti poistaa kysymyksen:\n\n'{display_text}'?"):
            all_questions.pop(original_index)
            save_questions_to_json()
            self.start()
            messagebox.showinfo("Onnistui", "Kysymys poistettu.")

if __name__ == "__main__":
    load_questions_from_json()
    app = LoveTrainerApp()
    app.mainloop()