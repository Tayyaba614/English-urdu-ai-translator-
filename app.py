import streamlit as st
from google import genai

st.set_page_config(
    page_title="Urdu-English AI Translator",
    page_icon="🌐",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7ff 0%, #ffffff 70%);
    }
    .main-title {
        text-align: center;
        color: #243b80;
        font-size: 2.35rem;
        font-weight: 800;
        padding-top: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #667085;
        margin-bottom: 1.5rem;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">🌐 Lingua AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Your smart Urdu-English translation assistant</div>',
    unsafe_allow_html=True,
)
st.info(
    "Translate Urdu and English, try example sentences, and download your translation."
)

if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = ""

left, right = st.columns(2)
with left:
    source_language = st.selectbox("Translate from", ["Urdu", "English"])
with right:
    target_language = st.selectbox("Translate into", ["English", "Urdu"])

examples = {
    "Urdu": [
        "آپ کیسے ہیں؟",
        "مجھے انگریزی سیکھنی ہے۔",
        "محنت کامیابی کی کنجی ہے۔",
    ],
    "English": [
        "How are you?",
        "I want to learn Urdu.",
        "Hard work is the key to success.",
    ],
}

example_choice = st.selectbox(
    "Try an example (optional)",
    ["Choose an example"] + examples[source_language],
)
default_text = "" if example_choice == "Choose an example" else example_choice

user_text = st.text_area(
    "Enter your text",
    value=default_text,
    height=150,
    placeholder="Type or paste your text here...",
)

def translate_text(text, source, target, api_key):
    client = genai.Client(api_key=api_key)
    prompt = f"""
You are a professional Urdu-English translator.
Translate the user's text from {source} into {target}.

Rules:
1. Preserve the original meaning and tone.
2. Use natural, grammatically correct language.
3. For Urdu, use Urdu script, not Roman Urdu.
4. Return only the translation, with no extra explanation.
5. Preserve names, numbers, and formatting where possible.

Text:
{text}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    translated = (response.text or "").strip()
    if not translated:
        raise ValueError("The model returned an empty translation.")
    return translated

if st.button("✨ Translate Now", type="primary", use_container_width=True):
    if source_language == target_language:
        st.warning("Please choose two different languages.")
    elif not user_text.strip():
        st.warning("Please enter some text first.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            with st.spinner("Translating your text..."):
                result = translate_text(
                    user_text.strip(),
                    source_language,
                    target_language,
                    api_key,
                )
            st.session_state.result = result
            st.session_state.history.insert(
                0,
                {
                    "source": source_language,
                    "target": target_language,
                    "original": user_text.strip(),
                    "translation": result,
                },
            )
            st.session_state.history = st.session_state.history[:10]
        except KeyError:
            st.error(
                "The API key is missing. Add GEMINI_API_KEY in "
                "your Streamlit app's Secrets settings."
            )
        except Exception as error:
            st.error(
                "Translation failed. Check your API key, model availability, "
                "internet connection, and API quota."
            )
            st.caption(f"Technical detail: {error}")

if st.session_state.result:
    st.divider()
    st.subheader("📝 Translation Result")
    st.text_area(
        "Translated text",
        value=st.session_state.result,
        height=150,
        key="translation_output",
    )
    st.download_button(
        "⬇️ Download Translation",
        data=st.session_state.result,
        file_name="translation.txt",
        mime="text/plain",
        use_container_width=True,
    )

with st.expander("📚 Recent Translation History"):
    if st.session_state.history:
        for index, item in enumerate(st.session_state.history, start=1):
            st.markdown(
                f"**{index}. {item['source']} → {item['target']}**"
            )
            st.write("Original:", item["original"])
            st.write("Translation:", item["translation"])
            st.divider()
    else:
        st.write("Your recent translations will appear here during this session.")

if st.button("🗑️ Clear History"):
    st.session_state.history = []
    st.session_state.result = ""
    st.rerun()

st.divider()
st.caption("Lingua AI | Built with Python, Streamlit, and Gemini")
