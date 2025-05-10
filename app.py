import streamlit as st
import random
from kana_data import hiragana, katakana, madlibs_templates, kana_groups

# ===== CORE SETUP =====
def reset_game_state():
    """Completely reset all game state"""
    st.session_state.update({
        'score': 0,
        'total': 0,
        'streak': 0,
        'practice_history': {},
        'incorrect_history': {},
        'current_kana': None,
        'current_madlib': None,
        'last_input': ""
    })

if 'score' not in st.session_state:
    reset_game_state()

# ===== GAME LOGIC =====
def get_filtered_kana(selected_type, groups):
    """Get kana based on selected type and groups"""
    base_dict = {}
    if selected_type in ["Hiragana", "Both"]:
        base_dict.update(hiragana)
    if selected_type in ["Katakana", "Both"]:
        base_dict.update(katakana)

    # Handle no groups selected or invalid group names
    if not groups:
        return {}

    valid_groups = [group for group in groups if group in kana_groups]

    return {
        char: romaji 
        for char, romaji in base_dict.items()
        if any(char in kana_groups[group] for group in valid_groups)
    }

def select_next_kana(kana_dict):
    """Smart selection prioritizing missed kana"""
    # Prioritize incorrect kana
    incorrect = {
        char: count
        for char, count in st.session_state['incorrect_history'].items()
        if char in kana_dict and count > 0
    }

    if incorrect:
        most_missed = max(incorrect.items(), key=lambda x: x[1])[0]
        return most_missed, kana_dict[most_missed]

    if kana_dict:
        return random.choice(list(kana_dict.items()))
    
    return None

# ===== GAME MODE: PRACTICE =====
def practice_mode(kana_dict):
    """100% reliable character practice"""
    if not kana_dict:
        st.warning("No kana match your filters.")
        return

    # Load new character if needed
    if st.session_state['current_kana'] is None:
        next_kana = select_next_kana(kana_dict)
        if not next_kana:
            st.warning("No available kana to practice.")
            return
        st.session_state['current_kana'] = next_kana

    kana, romaji = st.session_state['current_kana']

    # Display character
    st.subheader("What is this character?")
    st.markdown(
        f"<div style='font-size: 96px; text-align: center; margin: 20px 0;'>{kana}</div>",
        unsafe_allow_html=True
    )

    # Input field
    user_input = st.text_input(
        "Type the romaji:", 
        key="practice_input", 
        value=st.session_state['last_input']
    ).strip().lower()

    if user_input and user_input != st.session_state['last_input']:
        st.session_state['last_input'] = user_input

        # Update history
        st.session_state['practice_history'][kana] = st.session_state['practice_history'].get(kana, 0) + 1

        if user_input == romaji:
            st.success("Correct! 🎉")
            st.session_state['score'] += 1
            st.session_state['streak'] += 1
            st.session_state['incorrect_history'][kana] = max(
                0, st.session_state['incorrect_history'].get(kana, 0) - 1
            )
        else:
            st.error(f"Incorrect. Answer: '{romaji}'")
            st.session_state['incorrect_history'][kana] = st.session_state['incorrect_history'].get(kana, 0) + 1
            st.session_state['streak'] = 0

        st.session_state['total'] += 1
        st.session_state['current_kana'] = None
        st.rerun()

    # Progress display
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{st.session_state['score']}/{st.session_state['total']}")
    col2.metric("Accuracy", f"{(st.session_state['score']/st.session_state['total']*100):.1f}%" if st.session_state['total'] else "0%")
    col3.metric("Streak", st.session_state['streak'])

    # Manual next
    if st.button("Next Character"):
        st.session_state['current_kana'] = None
        st.session_state['last_input'] = ""
        st.rerun()

# ===== MAIN APP =====
def main():
    st.set_page_config(layout="centered", page_title="Kana Practice")
    st.title("🎌 Kana Practice")
    st.caption("Learn hiragana and katakana through interactive games")

    # Sidebar controls
    with st.sidebar:
        st.title("Settings")
        kana_type = st.radio("Kana Type", ["Hiragana", "Katakana", "Both"])
        groups = st.multiselect(
            "Kana Groups", 
            ["basic", "dakuten", "combinations"], 
            default=["basic"]
        )

        st.title("Progress")
        st.write(f"Practiced: {len(st.session_state['practice_history'])} kana")
        st.write(f"Needing practice: {len([k for k, v in st.session_state['incorrect_history'].items() if v > 0])}")

        if st.button("Reset All Progress"):
            reset_game_state()
            st.rerun()

    # Load filtered kana set
    kana_dict = get_filtered_kana(kana_type, groups)

    # Launch game mode
    practice_mode(kana_dict)

if __name__ == "__main__":
    main()
