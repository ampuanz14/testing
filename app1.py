import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import json

# ---------------- SESSION STATE ----------------
if "participants" not in st.session_state:
    st.session_state.participants = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "change_count" not in st.session_state:
    st.session_state.change_count = 0

# ---------------- GLOBAL STYLING ----------------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
}

/* Section box */
.section-box {
    background: #ffffffcc;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}

/* Text input */
input[type="text"] {
    padding: 10px !important;
    border-radius: 12px !important;
    border: 1px solid #ccc !important;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}

/* Selectbox */
div[data-baseweb="select"] {
    border-radius: 12px;
    border: 1px solid #ccc;
    padding: 5px;
}

/* Radio buttons */
div[role="radiogroup"] > label {
    background-color: #ffffff;
    padding: 10px 15px;
    border-radius: 12px;
    margin: 5px;
    border: 1px solid #ddd;
    display: inline-block;
    cursor: pointer;
    transition: 0.3s;
}
div[role="radiogroup"] > label:hover {
    background-color: #e6f0ff;
    border: 1px solid #4a90e2;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 12px;
    padding: 10px 18px;
    border: none;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
}

/* Cards */
.participant-card {
    background: white;
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["Home", "Add Participant", "View Participants", "Print Badge"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Database")

# -------- EXPORT --------
json_data = json.dumps(st.session_state.participants, indent=4)
st.sidebar.download_button(
    label="Export JSON",
    data=json_data,
    file_name="participants.json",
    mime="application/json"
)

# -------- IMPORT --------
uploaded_file = st.sidebar.file_uploader("Import JSON", type="json")
if uploaded_file:
    try:
        st.session_state.participants = json.load(uploaded_file)
        st.session_state.change_count = 0
        st.sidebar.success("Imported successfully!")
        st.rerun()
    except:
        st.sidebar.error("Invalid JSON file")

# -------- CHANGE REMINDER --------
if st.session_state.change_count >= 3:
    st.sidebar.warning("⚠️ Reminder: Please export your data!")

# ---------------- HOME ----------------
if page == "Home":
    st.title("🎉 Event Registration System")
    st.write("Welcome! Use the sidebar to navigate.")

# ---------------- ADD ----------------
elif page == "Add Participant":
    st.title("Add Participant")

    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    with st.form("add_form"):
        name = st.text_input("Enter your name:")
        category = st.radio(
            "Select category:",
            ["Student", "Professor", "External", "Others"]
        )
        submitted = st.form_submit_button("Register")

    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if name.strip() == "":
            st.warning("Enter a name.")
        else:
            duplicate = any(
                p["name"].lower() == name.lower() and p["category"] == category
                for p in st.session_state.participants
            )

            if duplicate:
                st.error("Duplicate entry.")
            else:
                st.session_state.participants.append({
                    "name": name,
                    "category": category
                })
                st.session_state.change_count += 1
                st.success("Added successfully.")

# ---------------- VIEW ----------------
elif page == "View Participants":
    st.title("Participants")

    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    search_name = st.text_input("Search")
    selected_category = st.selectbox(
        "Filter",
        ["All", "Student", "Professor", "External", "Others"]
    )

    st.markdown('</div>', unsafe_allow_html=True)

    filtered = st.session_state.participants

    if search_name:
        filtered = [p for p in filtered if search_name.lower() in p["name"].lower()]

    if selected_category != "All":
        filtered = [p for p in filtered if p["category"] == selected_category]

    if not filtered:
        st.write("No data.")
    else:
        for i, p in enumerate(filtered):
            st.markdown(f"""
            <div class="participant-card">
                <b>{p['name']}</b> ({p['category']})
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            if col1.button("Edit", key=f"edit_{i}"):
                st.session_state.edit_index = st.session_state.participants.index(p)

            if col2.button("Delete", key=f"delete_{i}"):
                idx = st.session_state.participants.index(p)
                st.session_state.participants.pop(idx)
                st.session_state.change_count += 1
                st.success("Deleted.")
                st.rerun()

            if col3.button("Badge", key=f"badge_{i}"):
                st.session_state.selected = p
                st.switch_page("Print Badge")

    # EDIT
    if st.session_state.edit_index is not None:
        p = st.session_state.participants[st.session_state.edit_index]

        with st.form("edit_form"):
            new_name = st.text_input("Edit name:", value=p["name"])
            new_category = st.radio(
                "Edit category:",
                ["Student", "Professor", "External", "Others"],
                index=["Student", "Professor", "External", "Others"].index(p["category"])
            )
            save = st.form_submit_button("Save")

        if save:
            st.session_state.participants[st.session_state.edit_index] = {
                "name": new_name,
                "category": new_category
            }
            st.session_state.change_count += 1
            st.session_state.edit_index = None
            st.success("Updated.")
            st.rerun()

# ---------------- BADGE ----------------
elif page == "Print Badge":
    st.title("Print Badge")

    if not st.session_state.participants:
        st.warning("No participants.")
    else:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)

        options = [f"{p['name']} ({p['category']})" for p in st.session_state.participants]
        selected = st.selectbox("Select participant:", options)

        bg_color = st.color_picker("Background", "#FFFFFF")
        text_color = st.color_picker("Text Color", "#000000")
        font_size = st.slider("Font Size", 15, 50, 25)
        border = st.checkbox("Border")

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Generate Badge"):
            index = options.index(selected)
            p = st.session_state.participants[index]

            img = Image.new("RGB", (400, 200), color=bg_color)
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            draw.text((20, 60), f"Name: {p['name']}", fill=text_color, font=font)
            draw.text((20, 110), f"Category: {p['category']}", fill=text_color, font=font)

            if border:
                draw.rectangle([(0, 0), (399, 199)], outline=text_color, width=3)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            buffer.seek(0)

            st.image(buffer)
            st.download_button(
                "Download Badge",
                buffer,
                f"{p['name']}_badge.jpg"
            )