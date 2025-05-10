import streamlit as st
import random
from kana_data import hiragana, katakana, madlibs_templates, kana_groups
from collections import defaultdict

# App title and description
st.title("🎌 Kana Mad Libs")
st.write("Learn hiragana and katakana through fun fill-in-the-blank games!")

# Initialize session state
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'practice_history' not in st.session_state:
    st.session_state.practice_history = defaultdict(int)
if 'incorrect_history' not in st.session_state:
    st.session_state.incorrect_history = defaultdict(int)
if 'streak' not in st.session_state:
    st.session_state.streak = 0

# Sidebar controls
st.sidebar.title("Settings")
kana_type = st.sidebar.radio("Select kana type:", ["Hiragana", "Katakana", "Both"])
difficulty = st.sidebar.selectbox("Select difficulty:", ["basic", "intermediate", "advanced"])
group_filter = st.sidebar.multiselect("Select kana groups:", ["basic", "dakuten", "combinations"], default=["basic"])

# Get filtered kana based on selections
def get_filtered_kana(kana_dict, groups):
    filtered = {}
    for char, romaji in kana_dict.items():
        for group in groups:
            if char in kana_groups[group]:
                filtered[char] = romaji
                break
    return filtered

# Game mode selection
mode = st.radio("Select game mode:", 
                ["Character Practice", "Mad Libs Challenge", "Weakness Drill"])

def practice_kana(kana_dict):
    """Practice individual kana characters"""
    if not kana_dict:
        st.warning("No kana selected with current filters. Please adjust your settings.")
        return
    
    # Weight selection toward less practiced characters
    if st.session_state.practice_history:
        min_practiced = min(st.session_state.practice_history.values())
        candidates = [k for k in kana_dict.keys() 
                    if st.session_state.practice_history.get(k, 0) == min_practiced]
        if candidates:
            kana = random.choice(candidates)
        else:
            kana = random.choice(list(kana_dict.keys()))
    else:
        kana = random.choice(list(kana_dict.keys()))
    
    romaji = kana_dict[kana]
    
    st.subheader(f"What is this character?")
    st.markdown(f"<h1 style='text-align: center; font-size: 96px;'>{kana}</h1>", 
                unsafe_allow_html=True)
    
    user_input = st.text_input("Type the romanji:", key="practice_input").strip().lower()
    
    if user_input:
        st.session_state.practice_history[kana] = st.session_state.practice_history.get(kana, 0) + 1
        
        if user_input == romaji:
            st.success("Correct! 🎉")
            st.session_state.score += 1
            st.session_state.streak += 1
            if st.session_state.streak > 0 and st.session_state.streak % 5 == 0:
                st.balloons()
        else:
            st.error(f"Oops! It's '{romaji}'")
            st.session_state.incorrect_history[kana] = st.session_state.incorrect_history.get(kana, 0) + 1
            st.session_state.streak = 0
            
        st.session_state.total += 1
        
        # Show progress
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
        with col2:
            st.metric("Accuracy", 
                     f"{(st.session_state.score/st.session_state.total*100):.1f}%"
                     if st.session_state.total > 0 else "0%")
        with col3:
            st.metric("Current Streak", st.session_state.streak)
        
        # Add a button to continue
        if st.button("Next character"):
            st.experimental_rerun()

def madlibs_challenge(kana_dict):
    """Mad Libs style sentence completion"""
    if not kana_dict:
        st.warning("No kana selected with current filters. Please adjust your settings.")
        return
    
    templates = madlibs_templates[difficulty]
    template = random.choice(templates)
    blank_count = template.count('___')
    
    st.subheader("Complete the sentence:")
    st.markdown(f"<h3 style='text-align: center;'>{template}</h3>", 
                unsafe_allow_html=True)
    
    # Get kana for each blank
    blanks = []
    for _ in range(blank_count):
        kana, romaji = random.choice(list(kana_dict.items()))
        blanks.append((kana, romaji))
    
    user_answers = []
    cols = st.columns(blank_count)
    for i, (kana, romaji) in enumerate(blanks):
        with cols[i]:
            user_input = st.text_input(f"Blank {i+1} (type: {romaji})", 
                                     key=f"madlibs_{i}").strip()
            user_answers.append((kana, romaji, user_input))
    
    if all(answer[2] for answer in user_answers):
        all_correct = True
        feedback = []
        for kana, romaji, user_input in user_answers:
            if user_input == kana:
                feedback.append(f"✓ {romaji} = {kana}")
            else:
                feedback.append(f"✗ {romaji} = {kana} (you wrote: {user_input})")
                all_correct = False
        
        if all_correct:
            st.success("All correct! Here's your completed sentence:")
            completed = template
            for kana, _, _ in user_answers:
                completed = completed.replace('___', kana, 1)
            st.markdown(f"<h3 style='text-align: center; color: green;'>{completed}</h3>", 
                        unsafe_allow_html=True)
            st.session_state.score += blank_count
            st.session_state.streak += 1
            if st.session_state.streak > 0 and st.session_state.streak % 3 == 0:
                st.balloons()
        else:
            st.error("Some answers were incorrect:")
            for item in feedback:
                st.write(item)
            st.session_state.streak = 0
        
        st.session_state.total += blank_count
        
        # Show progress
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
        with col2:
            st.metric("Current Streak", st.session_state.streak)
        
        if st.button("Next sentence"):
            st.experimental_rerun()

def weakness_drill(kana_dict):
    """Focus on characters the user gets wrong often"""
    if not st.session_state.incorrect_history:
        st.warning("You haven't made any mistakes yet! Try regular practice first.")
        return
    
    # Get top 5 most frequently missed characters
    top_missed = sorted(st.session_state.incorrect_history.items(), 
                       key=lambda x: x[1], reverse=True)[:5]
    missed_kana = [k[0] for k in top_missed]
    
    st.subheader("Practice your weak areas")
    st.write("These are the characters you've missed most often:")
    
    # Display the characters with their romanji
    cols = st.columns(5)
    for i, (kana, count) in enumerate(top_missed):
        with cols[i]:
            st.markdown(f"<h2 style='text-align: center;'>{kana}</h2>", 
                       unsafe_allow_html=True)
            st.caption(f"{kana_dict[kana]} (missed {count} times)")
    
    # Practice one of them
    kana = random.choice(missed_kana)
    romaji = kana_dict[kana]
    
    st.markdown(f"<h1 style='text-align: center; font-size: 96px;'>{kana}</h1>", 
                unsafe_allow_html=True)
    
    user_input = st.text_input("Type the romanji:", key="weakness_input").strip().lower()
    
    if user_input:
        if user_input == romaji:
            st.success("Correct! 🎯")
            st.session_state.score += 1
            st.session_state.streak += 1
            # Reduce the mistake count
            st.session_state.incorrect_history[kana] = max(0, st.session_state.incorrect_history[kana] - 1)
        else:
            st.error(f"Oops! It's '{romaji}'")
            st.session_state.incorrect_history[kana] += 1
            st.session_state.streak = 0
            
        st.session_state.total += 1
        
        # Show progress
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
        with col2:
            st.metric("Current Streak", st.session_state.streak)
        
        if st.button("Next character"):
            st.experimental_rerun()

# Get the appropriate kana dictionary based on selection
if kana_type == "Hiragana":
    current_kana = get_filtered_kana(hiragana, group_filter)
elif kana_type == "Katakana":
    current_kana = get_filtered_kana(katakana, group_filter)
else:
    current_kana = {**get_filtered_kana(hiragana, group_filter), 
                   **get_filtered_kana(katakana, group_filter)}

# Run the selected mode
if mode == "Character Practice":
    practice_kana(current_kana)
elif mode == "Mad Libs Challenge":
    madlibs_challenge(current_kana)
else:
    weakness_drill(current_kana)

# Progress visualization
st.sidebar.title("Progress")
if st.session_state.practice_history:
    st.sidebar.write(f"Practiced {len(st.session_state.practice_history)} unique kana")
    most_practiced = max(st.session_state.practice_history.items(), key=lambda x: x[1])
    st.sidebar.write(f"Most practiced: {most_practiced[0]} ({most_practiced[1]} times)")
if st.session_state.incorrect_history:
    most_missed = max(st.session_state.incorrect_history.items(), key=lambda x: x[1])
    st.sidebar.write(f"Most missed: {most_missed[0]} ({most_missed[1]} times)")

# Reset button
if st.sidebar.button("Reset Progress"):
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.practice_history = defaultdict(int)
    st.session_state.incorrect_history = defaultdict(int)
    st.session_state.streak = 0
    st.sidebar.success("Progress reset!")