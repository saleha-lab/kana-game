import streamlit as st
import random
from kana_data import hiragana, katakana, madlibs_templates, kana_groups

# Configure page
st.set_page_config(layout="centered", page_title="Kana Mad Libs")

# App title and description
st.title("🎌 Kana Mad Libs")
st.write("Learn hiragana and katakana through fun fill-in-the-blank games!")

# Initialize session state
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'practice_history' not in st.session_state:
    st.session_state.practice_history = {}
if 'incorrect_history' not in st.session_state:
    st.session_state.incorrect_history = {}
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'current_kana' not in st.session_state:
    st.session_state.current_kana = None

# Sidebar controls
st.sidebar.title("Settings")
kana_type = st.sidebar.radio("Select kana type:", ["Hiragana", "Katakana", "Both"])
difficulty = st.sidebar.selectbox("Select difficulty:", ["basic", "intermediate", "advanced"])
group_filter = st.sidebar.multiselect("Select kana groups:", ["basic", "dakuten", "combinations"], default=["basic"])

def get_filtered_kana(kana_dict, groups):
    """Filter kana based on selected groups"""
    filtered = {}
    for char, romaji in kana_dict.items():
        for group in groups:
            if group in kana_groups and char in kana_groups[group]:
                filtered[char] = romaji
                break
    return filtered

def practice_kana(kana_dict):
    """Practice individual kana characters"""
    if not kana_dict:
        st.warning("No kana selected with current filters. Please adjust your settings.")
        return

    if st.session_state.current_kana is None:
        st.session_state.current_kana = random.choice(list(kana_dict.items()))

    kana, romaji = st.session_state.current_kana

    st.subheader("What is this character?")
    st.markdown(f"<h1 style='text-align: center; font-size: 96px; margin-bottom: 30px;'>{kana}</h1>", 
                unsafe_allow_html=True)

    def handle_input():
        user_input = st.session_state.practice_input.strip().lower()
        if user_input:
            st.session_state.practice_history[kana] = st.session_state.practice_history.get(kana, 0) + 1
            if user_input == romaji:
                st.session_state.score += 1
                st.session_state.streak += 1
                st.session_state.correct_answer = True
            else:
                st.session_state.incorrect_history[kana] = st.session_state.incorrect_history.get(kana, 0) + 1
                st.session_state.streak = 0
                st.session_state.correct_answer = False
            st.session_state.total += 1

    st.text_input(
        "Type the romanji:",
        key="practice_input",
        on_change=handle_input,
        value="",
        placeholder="Type here and press Enter"
    )

    if hasattr(st.session_state, 'correct_answer'):
        if st.session_state.correct_answer:
            st.success("Correct! 🎉")
            if st.session_state.streak % 5 == 0:
                st.balloons()
        else:
            st.error(f"Oops! It's '{romaji}'")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
    with col2:
        accuracy = (st.session_state.score / st.session_state.total * 100) if st.session_state.total > 0 else 0
        st.metric("Accuracy", f"{accuracy:.1f}%")
    with col3:
        st.metric("Current Streak", st.session_state.streak)

    if st.button("Next character"):
        st.session_state.current_kana = random.choice(list(kana_dict.items()))
        if hasattr(st.session_state, 'practice_input'):
            del st.session_state.practice_input
        if hasattr(st.session_state, 'correct_answer'):
            del st.session_state.correct_answer
        st.rerun()

def madlibs_challenge(kana_dict):
    """Mad Libs style sentence completion"""
    if not kana_dict:
        st.warning("No kana selected with current filters. Please adjust your settings.")
        return

    template_list = madlibs_templates.get(difficulty, [])
    if not template_list:
        st.error("No Mad Libs templates found for the selected difficulty.")
        return

    template = random.choice(template_list)
    blank_count = template.count('___')

    st.subheader("Complete the sentence:")
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 30px;'>{template}</h3>", 
                unsafe_allow_html=True)

    blanks = []
    for _ in range(blank_count):
        kana, romaji = random.choice(list(kana_dict.items()))
        blanks.append((kana, romaji))

    user_answers = []
    cols = st.columns(blank_count)
    for i, (kana, romaji) in enumerate(blanks):
        with cols[i]:
            user_input = st.text_input(
                f"Blank {i+1}",
                key=f"madlibs_{i}",
                placeholder="Enter kana"
            ).strip()
            user_answers.append((kana, romaji, user_input))

    if all(answer[2] for answer in user_answers):
        all_correct = True
        feedback = []
        for kana, romaji, user_input in user_answers:
            if user_input != kana:
                all_correct = False
                feedback.append(f"✗ {romaji} = {kana} (you wrote: {user_input})")

        if all_correct:
            st.success("All correct! Here's your completed sentence:")
            completed = template
            for kana, _, _ in user_answers:
                completed = completed.replace('___', kana, 1)
            st.markdown(f"<h3 style='text-align: center; color: green;'>{completed}</h3>", 
                        unsafe_allow_html=True)
            st.session_state.score += blank_count
            st.session_state.streak += 1
            if st.session_state.streak % 3 == 0:
                st.balloons()
        else:
            st.error("Some answers were incorrect:")
            for item in feedback:
                st.write(item)
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
    """Focus on frequently missed characters"""
    if not st.session_state.incorrect_history:
        st.warning("You haven't made any mistakes yet! Try regular practice first.")
        return

    top_missed = sorted(st.session_state.incorrect_history.items(), key=lambda x: x[1], reverse=True)[:5]
    missed_kana = [k[0] for k in top_missed]

    st.subheader("Practice your weak areas")
    st.write("These are the characters you've missed most often:")

    cols = st.columns(len(top_missed))
    for i, (kana, count) in enumerate(top_missed):
        with cols[i]:
            st.markdown(f"<h2 style='text-align: center;'>{kana}</h2>", unsafe_allow_html=True)
            st.caption(f"{kana_dict.get(kana, '?')} (missed {count} times)")

    kana = random.choice(missed_kana)
    romaji = kana_dict[kana]

    st.markdown(f"<h1 style='text-align: center; font-size: 96px; margin-bottom: 30px;'>{kana}</h1>", 
                unsafe_allow_html=True)

    def handle_weakness_input():
        user_input = st.session_state.weakness_input.strip().lower()
        if user_input:
            if user_input == romaji:
                st.session_state.score += 1
                st.session_state.streak += 1
                st.session_state.incorrect_history[kana] = max(0, st.session_state.incorrect_history.get(kana, 1) - 1)
                st.session_state.correct_weakness = True
            else:
                st.session_state.incorrect_history[kana] = st.session_state.incorrect_history.get(kana, 0) + 1
                st.session_state.streak = 0
                st.session_state.correct_weakness = False
            st.session_state.total += 1

    st.text_input(
        "Type the romanji:", 
        key="weakness_input",
        on_change=handle_weakness_input,
        value="",
        placeholder="Type here and press Enter"
    )

    if hasattr(st.session_state, 'correct_weakness'):
        if st.session_state.correct_weakness:
            st.success("Correct! 🎯")
        else:
            st.error(f"Oops! It's '{romaji}'")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
        with col2:
            st.metric("Current Streak", st.session_state.streak)

        if st.button("Next character"):
            st.session_state.weakness_input = ""
            del st.session_state.correct_weakness
            st.rerun()

# Get filtered kana based on selections
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
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.practice_history = {}
    st.session_state.incorrect_history = {}
    st.session_state.streak = 0
    st.session_state.current_kana = None
    st.sidebar.success("Progress reset!")
    st.rerun()
