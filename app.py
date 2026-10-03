
import os
import tempfile

import streamlit as st
from faster_whisper import WhisperModel


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Voice to Text AI",
    page_icon="🎙️",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 50%, #ecfeff 100%);
}

/* Hide default Streamlit menu/footer */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* Main container */
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* Main title */
.main-title {
    text-align: center;
    font-size: 45px;
    font-weight: 800;
    margin-bottom: 5px;
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #0891b2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}


/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 17px;
    color: #64748b;
    margin-bottom: 30px;
}


/* Feature cards */
.feature-container {
    display: flex;
    gap: 18px;
    margin-bottom: 30px;
}

.feature-card {
    flex: 1;
    background: rgba(255,255,255,0.85);
    padding: 22px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 25px rgba(15,23,42,0.07);
    transition: 0.3s;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(79,70,229,0.15);
}

.feature-icon {
    font-size: 32px;
    margin-bottom: 8px;
}

.feature-title {
    font-size: 17px;
    font-weight: 700;
    color: #1e293b;
}

.feature-text {
    font-size: 13px;
    color: #64748b;
}


/* Section card */
.section-card {
    background: rgba(255,255,255,0.92);
    border-radius: 22px;
    padding: 25px;
    margin-bottom: 25px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 30px rgba(15,23,42,0.07);
}


/* Upload area */
[data-testid="stFileUploader"] {
    background: #f8fafc;
    border: 2px dashed #818cf8;
    border-radius: 18px;
    padding: 15px;
}


/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: none;
    padding: 12px 20px;
    font-weight: 600;
    font-size: 15px;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(79,70,229,0.25);
}


/* Primary button */
button[kind="primary"] {
    background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
    color: white !important;
}


/* Text area */
textarea {
    border-radius: 15px !important;
    border: 1px solid #cbd5e1 !important;
    background: #f8fafc !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}


/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #1e1b4b);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}


/* Sidebar title */
.sidebar-title {
    text-align: center;
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 25px;
}


/* Result box */
.result-box {
    background: linear-gradient(135deg, #eef2ff, #ecfeff);
    border-left: 5px solid #4f46e5;
    padding: 18px;
    border-radius: 14px;
    margin: 15px 0;
}


/* Status */
.status {
    text-align: center;
    background: #ecfdf5;
    color: #047857;
    padding: 12px;
    border-radius: 12px;
    font-weight: 600;
    margin-bottom: 20px;
}


/* Footer */
.footer {
    text-align: center;
    margin-top: 40px;
    color: #64748b;
    font-size: 13px;
}

.footer strong {
    color: #4f46e5;
}


/* Mobile */
@media (max-width: 768px) {

    .main-title {
        font-size: 32px;
    }

    .feature-container {
        flex-direction: column;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LANGUAGES
# =========================================================

LANGUAGES = {
    "Auto detect": None,
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Bengali": "bn",
    "Marathi": "mr",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Gujarati": "gu",
    "Urdu": "ur",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Japanese": "ja",
}


# =========================================================
# SESSION STATE
# =========================================================

if "widget_key" not in st.session_state:
    st.session_state.widget_key = 0

if "result" not in st.session_state:
    st.session_state.result = None


def clear_audio():
    st.session_state.widget_key += 1
    st.session_state.result = None


# =========================================================
# LOAD WHISPER MODEL
# =========================================================

@st.cache_resource(show_spinner="Loading Whisper AI model...")
def load_model(size: str):

    return WhisperModel(
        size,
        device="cpu",
        compute_type="int8"
    )


# =========================================================
# TIME FORMAT
# =========================================================

def fmt_time(seconds: float) -> str:

    h, rem = divmod(int(seconds), 3600)

    m, s = divmod(rem, 60)

    ms = int(
        (seconds - int(seconds)) * 1000
    )

    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# =========================================================
# SRT CREATOR
# =========================================================

def to_srt(segments):

    lines = []

    for i, seg in enumerate(segments, 1):

        lines.append(
            f"{i}\n"
            f"{fmt_time(seg['start'])} --> "
            f"{fmt_time(seg['end'])}\n"
            f"{seg['text']}\n"
        )

    return "\n".join(lines)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    '<div class="sidebar-title">⚙️ AI Settings</div>',
    unsafe_allow_html=True
)

size = st.sidebar.selectbox(
    "🧠 Whisper Model",
    ["tiny", "base", "small", "medium"],
    index=1
)

lang_name = st.sidebar.selectbox(
    "🌐 Language",
    list(LANGUAGES.keys())
)

task = st.sidebar.radio(
    "📝 Task",
    ["Transcribe", "Translate to English"]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "🎙️ This application runs locally using "
    "Faster-Whisper. No API key required."
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🎙️ Voice to Text AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Convert speech into accurate text using AI-powered Whisper technology'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# FEATURE CARDS
# =========================================================

st.markdown("""
<div class="feature-container">

<div class="feature-card">
<div class="feature-icon">🎤</div>
<div class="feature-title">Live Recording</div>
<div class="feature-text">Record your voice directly</div>
</div>

<div class="feature-card">
<div class="feature-icon">🌐</div>
<div class="feature-title">Multiple Languages</div>
<div class="feature-text">Telugu, Hindi, English & more</div>
</div>

<div class="feature-card">
<div class="feature-icon">⚡</div>
<div class="feature-title">AI Powered</div>
<div class="feature-text">Powered by Whisper AI</div>
</div>

<div class="feature-card">
<div class="feature-icon">📄</div>
<div class="feature-title">Export</div>
<div class="feature-text">TXT & SRT downloads</div>
</div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# AUDIO SECTION
# =========================================================

st.markdown(
    '<div class="section-card">',
    unsafe_allow_html=True
)

st.subheader("📥 Add Your Audio")

st.write(
    "Upload an audio file or record your voice using your microphone."
)

key = st.session_state.widget_key

tab_upload, tab_record = st.tabs(
    ["📁 Upload Audio", "🎤 Record Voice"]
)

audio = None


# =========================================================
# UPLOAD
# =========================================================

with tab_upload:

    up = st.file_uploader(
        "Choose an audio file",
        type=[
            "mp3",
            "wav",
            "m4a",
            "ogg",
            "flac",
            "webm",
            "mp4"
        ],
        key=f"upload_{key}"
    )

    if up:

        audio = up


# =========================================================
# RECORD
# =========================================================

with tab_record:

    rec = st.audio_input(
        "Click to record your voice",
        key=f"record_{key}"
    )

    if rec:

        audio = rec


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# PROCESS AUDIO
# =========================================================

if audio is not None:

    st.audio(audio)

    audio_id = (
        f"{getattr(audio, 'name', 'rec')}_{audio.size}"
    )

    col1, col2 = st.columns(2)

    convert = col1.button(
        "📝 Convert to Text",
        type="primary",
        use_container_width=True
    )

    clear = col2.button(
        "🗑️ Clear / New Audio",
        use_container_width=True
    )

    if clear:

        clear_audio()

        st.rerun()


    # =====================================================
    # TRANSCRIPTION
    # =====================================================

    if convert:

        suffix = (
            os.path.splitext(
                getattr(audio, "name", "")
            )[1]
            or ".wav"
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            tmp.write(
                audio.getvalue()
            )

            path = tmp.name


        try:

            model = load_model(size)

            with st.spinner(
                "🤖 AI is converting your speech into text..."
            ):

                seg_iter, info = model.transcribe(
                    path,
                    language=LANGUAGES[lang_name],
                    task=(
                        "translate"
                        if task.startswith("Translate")
                        else "transcribe"
                    ),
                    beam_size=5,
                    vad_filter=True
                )

                segments = [
                    {
                        "start": s.start,
                        "end": s.end,
                        "text": s.text.strip()
                    }
                    for s in seg_iter
                ]

        finally:

            os.remove(path)


        # =================================================
        # SAVE RESULT
        # =================================================

        st.session_state.result = {

            "audio_id": audio_id,

            "text": " ".join(
                s["text"]
                for s in segments
            ),

            "segments": segments,

            "language": info.language,

            "prob": info.language_probability,

            "duration": info.duration
        }


    # =====================================================
    # SHOW RESULT
    # =====================================================

    res = st.session_state.result


    if res and res["audio_id"] == audio_id:

        st.markdown(
            '<div class="status">'
            '✅ Speech successfully converted to text!'
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="result-box">',
            unsafe_allow_html=True
        )

        st.write(
            f"🌐 **Detected Language:** "
            f"{res['language']}  "
            f"• 🎯 **Confidence:** "
            f"{res['prob'] * 100:.0f}%  "
            f"• ⏱️ **Duration:** "
            f"{res['duration']:.1f} seconds"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        # =================================================
        # TRANSCRIPT
        # =================================================

        st.subheader("📄 Transcript")

        st.text_area(
            "Generated Text",
            res["text"],
            height=220
        )


        # =================================================
        # TIMESTAMPS
        # =================================================

        with st.expander("⏱️ View Timestamps"):

            for s in res["segments"]:

                st.write(
                    f"**[{s['start']:6.1f}s → "
                    f"{s['end']:6.1f}s]** "
                    f"{s['text']}"
                )


        # =================================================
        # DOWNLOAD
        # =================================================

        st.subheader("📥 Download")

        c1, c2 = st.columns(2)

        c1.download_button(
            "⬇️ Download TXT",
            res["text"],
            "transcript.txt",
            "text/plain",
            use_container_width=True
        )

        c2.download_button(
            "⬇️ Download SRT",
            to_srt(res["segments"]),
            "transcript.srt",
            "text/plain",
            use_container_width=True
        )


else:

    st.info(
        "👆 Upload an audio file or record your voice to begin."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
🎙️ <strong>Voice to Text AI</strong>
<br>
Built with Streamlit + Faster-Whisper
<br><br>
💡 Speech Recognition • Translation • Subtitles
</div>
""", unsafe_allow_html=True)

