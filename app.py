import streamlit as st
import random
from kana_data import hiragana, katakana, madlibs_templates, kana_groups
from collections import defaultdict

# ========== INITIALIZATION ==========
def initialize_app():
    """One-time setup of all session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'score': 0,
            'total': 0,
            'streak': 0,
            'practice_history': defaultdict(int),
            'incorrect_history': defaultdict(int),
            'current_kana': None,
            'current_madlibs': None,
            'initialized': True
        })

# ========== CORE FUNCTIONS ==========
def get_filtered_kana(kana_dict, groups):
    """Safely filter kana based on selected groups"""
    return {
        char: romaji 
        for char, romaji in kana_dict.items()
        if any(char in kana_groups[group] for group in groups)
    }

def select_new_kana(kana_dict):
    """Intelligently selects next kana to practice"""
    if not kana_dict:
        return None, None
    
    # Prioritize missed characters
    if st.session_state.incorrect_history:
        most_missed = max(st.session_state.incorrect_history.items(), key=lambda x: x[1])[0]
        if most_missed in kana_dict:
            return most_missed, kana_dict[most_missed]
    
    # Fallback to random selection
    return random.choice(list(kana_dict.items()))

# ========== GAME MODES ==========
def practice_kana(kana_dict):
    """Bug-free character practice mode"""
    if not kana_dict:
        st.warning("No kana available with current filters")
        return
    
    # Get or refresh current kana
    if st.session_state.current_kana is None:
        st.session_state.current_kana = select_new_kana(kana_dict)
    
    kana, romaji = st.session_state.current_kana
    
    # Display
    st.subheader("What is this character?")
    st.markdown(f"<h1 style='text-align: center; font-size: 96px; margin: 20px 0;'>{kana}</h1>", 
                unsafe_allow_html=True)
    
    # Input handling
    user_input = st.text_input(
        "Type the romaji:", 
        key="practice_input",
        value="",
        on_change=lambda: None  # Prevents premature submission
    ).strip().lower()
    
    # Process answer
    if user_input:
        st.session_state.practice_history[kana] += 1
        
        if user_input == romaji:
            st.success("Correct! 🎉")
            st.session_state.score += 1
            st.session_state.streak += 1
            st.session_state.incorrect_history[kana] = max(0, st.session_state.incorrect_history.get(kana, 0) - 1)
        else:
            st.error(f"Correct answer: '{romaji}'")
            st.session_state.incorrect_history[kana] += 1
            st.session_state.streak = 0
        
        st.session_state.total += 1
        st.session_state.current_kana = None  # Force new character next run
        st.experimental_rerun()
    
    # Progress display
    cols = st.columns(3)
    with cols[0]:
        st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
    with cols[1]:
        accuracy = (st.session_state.score/st.session_state.total*100) if st.session_state.total > 0 else 0
        st.metric("Accuracy", f"{accuracy:.1f}%")
    with cols[2]:
        st.metric("Streak", st.session_state.streak)

def madlibs_challenge(kana_dict):
    """Completely stable Mad Libs mode"""
    if not kana_dict:
        st.warning("No kana available with current filters")
        return
    
    # Initialize or reuse current madlib
    if st.session_state.current_madlibs is None:
        template = random.choice(madlibs_templates[difficulty])
        blanks_needed = template.count('___')
        blanks = [random.choice(list(kana_dict.items())) for _ in range(blanks_needed)]
        st.session_state.current_madlibs = (template, blanks)
    
    template, blanks = st.session_state.current_madlibs
    
    # Display
    st.subheader("Complete the sentence:")
    st.markdown(f"<h3 style='text-align: center; margin: 20px 0;'>{template}</h3>", 
                unsafe_allow_html=True)
    
    # Input fields
    user_answers = []
    cols = st.columns(len(blanks))
    for i, (kana, romaji) in enumerate(blanks):
        with cols[i]:
            user_input = st.text_input(
                f"Blank {i+1} (type: {romaji})",
                key=f"madlib_{i}",
                value=""
            ).strip()
            user_answers.append((kana, romaji, user_input))
    
    # Check completion
    if all(answer[2] for answer in user_answers):
        correct = all(user_input == kana for kana, _, user_input in user_answers)
        
        if correct:
            st.success("Perfect! Here's your sentence:")
            completed = template
            for kana, _, _ in user_answers:
                completed = completed.replace('___', kana, 1)
            st.markdown(f"<h3 style='text-align: center; color: green;'>{completed}</h3>",
                        unsafe_allow_html=True)
            st.session_state.score += len(blanks)
            st.session_state.streak += 1
        else:
            st.error("Some mistakes:")
            for kana, romaji, user_input in user_answers:
                if user_input != kana:
                    st.write(f"• {romaji} should be '{kana}' (you wrote: {user_input})")
            st.session_state.streak = 0
        
        st.session_state.total += len(blanks)
        st.session_state.current_madlibs = None
        st.experimental_rerun()
    
    # Progress display
    cols = st.columns(2)
    with cols[0]:
        st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
    with cols[1]:
        st.metric("Streak", st.session_state.streak)

# ========== UI SETUP ==========
def setup_sidebar():
    """Configure all sidebar controls"""
    st.sidebar.title("Settings")
    kana_type = st.sidebar.radio("Kana Type:", ["Hiragana", "Katakana", "Both"])
    difficulty = st.sidebar.selectbox("Difficulty:", ["basic", "intermediate", "advanced"])
    group_filter = st.sidebar.multiselect(
        "Kana Groups:", 
        ["basic", "dakuten", "combinations"], 
        default=["basic"]
    )
    
    st.sidebar.title("Progress")
    if st.session_state.practice_history:
        st.sidebar.write(f"Practiced: {len(st.session_state.practice_history)} kana")
    if st.session_state.incorrect_history:
        st.sidebar.write(f"Needing practice: {len(st.session_state.incorrect_history)}")
    
    if st.sidebar.button("Reset All Progress"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_app()
        st.experimental_rerun()
    
    return kana_type, difficulty, group_filter

# ========== MAIN APP ==========
def main():
    initialize_app()
    st.title("🎌 Kana Mad Libs")
    st.write("Learn Japanese characters through fun games!")
    
    # Setup UI and get settings
    kana_type, difficulty, group_filter = setup_sidebar()
    
    # Get filtered kana
    if kana_type == "Hiragana":
        current_kana = get_filtered_kana(hiragana, group_filter)
    elif kana_type == "Katakana":
        current_kana = get_filtered_kana(katakana, group_filter)
    else:
        current_kana = {
            **get_filtered_kana(hiragana, group_filter),
            **get_filtered_kana(katakana, group_filter)
        }
    
    # Game mode selection
    mode = st.radio(
        "Select Mode:",
        ["Character Practice", "Mad Libs Challenge"],
        horizontal=True
    )
    
    # Run selected mode
    if mode == "Character Practice":
        practice_kana(current_kana)
    else:
        madlibs_challenge(current_kana)

if __name__ == "__main__":
    main()
