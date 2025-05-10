import streamlit as st
import random
from kana_data import hiragana, katakana, madlibs_templates, kana_groups
from collections import defaultdict

# Configure page
st.set_page_config(layout="centered", page_title="Kana Mad Libs")

# Initialize all session state variables
def init_session_state():
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total' not in st.session_state:
        st.session_state.total = 0
    if 'streak' not in st.session_state:
        st.session_state.streak = 0
    if 'practice_history' not in st.session_state:
        st.session_state.practice_history = defaultdict(int)
    if 'incorrect_history' not in st.session_state:
        st.session_state.incorrect_history = defaultdict(int)
    if 'current_kana' not in st.session_state:
        st.session_state.current_kana = None
    if 'last_input' not in st.session_state:
        st.session_state.last_input = ""

init_session_state()

# App title and description
st.title("🎌 Kana Mad Libs")
st.write("Learn hiragana and katakana through fun fill-in-the-blank games!")

# Sidebar controls
st.sidebar.title("Settings")
kana_type = st.sidebar.radio("Select kana type:", ["Hiragana", "Katakana", "Both"])
difficulty = st.sidebar.selectbox("Select difficulty:", ["basic", "intermediate", "advanced"])
group_filter = st.sidebar.multiselect("Select kana groups:", ["basic", "dakuten", "combinations"], default=["basic"])

def get_filtered_kana(kana_dict, groups):
    filtered = {}
    for char, romaji in kana_dict.items():
        for group in groups:
            if char in kana_groups[group]:
                filtered[char] = romaji
                break
    return filtered

def get_new_kana(kana_dict):
    if not kana_dict:
        return None, None
    if st.session_state.incorrect_history:
        most_missed = max(st.session_state.incorrect_history.items(), key=lambda x: x[1])[0]
        if most_missed in kana_dict:
            return most_missed, kana_dict[most_missed]
    return random.choice(list(kana_dict.items()))

def practice_kana(kana_dict):
    if not kana_dict:
        st.warning("No kana selected with current filters. Please adjust your settings.")
        return
    
    if st.session_state.current_kana is None:
        st.session_state.current_kana = get_new_kana(kana_dict)
    
    kana, romaji = st.session_state.current_kana
    
    st.subheader("What is this character?")
    st.markdown(f"<h1 style='text-align: center; font-size: 96px; margin-bottom: 30px;'>{kana}</h1>", 
                unsafe_allow_html=True)
    
    user_input = st.text_input(
        "Type the romanji:", 
        key="practice_input",
        value=st.session_state.last_input
    ).strip().lower()
    
    if user_input and user_input != st.session_state.last_input:
        st.session_state.last_input = user_input
        st.session_state.practice_history[kana] += 1
        
        if user_input == romaji:
            st.success("Correct! 🎉")
            st.session_state.score += 1
            st.session_state.streak += 1
            st.session_state.incorrect_history[kana] = max(0, st.session_state.incorrect_history.get(kana, 0) - 1)
            if st.session_state.streak % 5 == 0:
                st.balloons()
        else:
            st.error(f"Oops! It's '{romaji}'")
            st.session_state.incorrect_history[kana] += 1
            st.session_state.streak = 0
        
        st.session_state.total += 1
        st.session_state.current_kana = get_new_kana(kana_dict)
        st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
    with col2:
        accuracy = (st.session_state.score/st.session_state.total*100) if st.session_state.total > 0 else 0
        st.metric("Accuracy", f"{accuracy:.1f}%")
    with col3:
        st.metric("Current Streak", st.session_state.streak)
    
    if st.button("Next character"):
        st.session_state.current_kana = get_new_kana(kana_dict)
        st.session_state.last_input = ""
        st.rerun()

def madlibs_challenge(kana_dict):
    if not kana_dict:
        st.warning("No kana selected with current filters. Please adjust your settings.")
        return
    
    template = random.choice(madlibs_templates[difficulty])
    blank_count = template.count('___')
    
    st.subheader("Complete the sentence:")
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 30px;'>{template}</h3>", 
                unsafe_allow_html=True)
    
    blanks = []
    cols = st.columns(blank_count)
    for i in range(blank_count):
        kana, romaji = random.choice(list(kana_dict.items()))
        with cols[i]:
            user_input = st.text_input(
                f"Blank {i+1} (type: {romaji})", 
                key=f"madlibs_{i}",
                value=""
            ).strip()
            blanks.append((kana, romaji, user_input))
    
    if all(answer[2] for answer in blanks):
        all_correct = True
        for kana, romaji, user_input in blanks:
            if user_input != kana:
                all_correct = False
                break
        
        if all_correct:
            st.success("All correct! Here's your completed sentence:")
            completed = template
            for kana, _, _ in blanks:
                completed = completed.replace('___', kana, 1)
            st.markdown(f"<h3 style='text-align: center; color: green;'>{completed}</h3>", 
                        unsafe_allow_html=True)
            st.session_state.score += blank_count
            st.session_state.streak += 1
            if st.session_state.streak % 3 == 0:
                st.balloons()
        else:
            st.error("Some answers were incorrect:")
            for kana, romaji, user_input in blanks:
                if user_input != kana:
                    st.write(f"✗ {romaji} = {kana} (you wrote: {user_input})")
            st.session_state.streak = 0
        
        st.session_state.total += blank_count
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
        with col2:
            st.metric("Current Streak", st.session_state.streak)
        
        if st.button("Next sentence"):
            st.rerun()

def weakness_drill(kana_dict):
    if not st.session_state.incorrect_history:
        st.warning("You haven't made any mistakes yet! Try regular practice first.")
        return
    
    top_missed = sorted(st.session_state.incorrect_history.items(), 
                       key=lambda x: x[1], reverse=True)[:5]
    
    st.subheader("Practice your weak areas")
    st.write("These are the characters you've missed most often:")
    
    cols = st.columns(5)
    for i, (kana, count) in enumerate(top_missed):
        with cols[i]:
            st.markdown(f"<h2 style='text-align: center;'>{kana}</h2>", 
                       unsafe_allow_html=True)
            st.caption(f"{kana_dict[kana]} (missed {count} times)")
    
    kana, romaji = random.choice(top_missed)[0], kana_dict[random.choice(top_missed)[0]]
    
    st.markdown(f"<h1 style='text-align: center; font-size: 96px; margin-bottom: 30px;'>{kana}</h1>", 
                unsafe_allow_html=True)
    
    user_input = st.text_input(
        "Type the romanji:", 
        key="weakness_input",
        value=""
    ).strip().lower()
    
    if user_input:
        st.session_state.practice_history[kana] += 1
        
        if user_input == romaji:
            st.success("Correct! 🎯")
            st.session_state.score += 1
            st.session_state.streak += 1
            st.session_state.incorrect_history[kana] = max(0, st.session_state.incorrect_history[kana] - 1)
        else:
            st.error(f"Oops! It's '{romaji}'")
            st.session_state.incorrect_history[kana] += 1
            st.session_state.streak = 0
        
        st.session_state.total += 1
        st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
    with col2:
        st.metric("Current Streak", st.session_state.streak)
    
    if st.button("Next character"):
        st.rerun()

# Get filtered kana
if kana_type == "Hiragana":
    current_kana = get_filtered_kana(hiragana, group_filter)
elif kana_type == "Katakana":
    current_kana = get_filtered_kana(katakana, group_filter)
else:
    current_kana = {**get_filtered_kana(hiragana, group_filter), 
                   **get_filtered_kana(katakana, group_filter)}

# Game mode selection
mode = st.radio("Select game mode:", 
               ["Character Practice", "Mad Libs Challenge", "Weakness Drill"],
               horizontal=True)

# Run selected mode
if mode == "Character Practice":
    practice_kana(current_kana)
elif mode == "Mad Libs Challenge":
    madlibs_challenge(current_kana)
else:
    weakness_drill(current_kana)

# Progress sidebar
st.sidebar.title("Progress")
if st.session_state.practice_history:
    st.sidebar.write(f"Practiced {len(st.session_state.practice_history)} unique kana")
if st.session_state.incorrect_history:
    st.sidebar.write(f"Characters needing practice: {len(st.session_state.incorrect_history)}")

if st.sidebar.button("Reset Progress"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()
    st.rerun()
