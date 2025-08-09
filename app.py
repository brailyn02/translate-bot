import streamlit as st
import google.generativeai as genai
import re
import os

# Configure page
st.set_page_config(
    page_title="Multilingual Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# YOUR GEMINI API KEY HERE - Replace with your actual key
GEMINI_API_KEY = "AIzaSyATpBoQBYpj1TcDdRqrmks1a0JSNgXb2VA"

# Configure Gemini with your API key
genai.configure(api_key=GEMINI_API_KEY)

# ChatGPT-like CSS styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ChatGPT-like color scheme */
    .stApp {
        background-color: #212121;
        color: #ffffff;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 48rem;
        margin: 0 auto;
    }
    
    /* Header styling */
    .chat-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #404040;
    }
    
    .chat-header h1 {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .chat-header p {
        color: #8e8ea0;
        font-size: 0.875rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 1.5rem 0 !important;
        margin: 0 !important;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background: #2f2f2f !important;
        margin: 1rem -1rem !important;
        padding: 1.5rem 1rem !important;
        border-radius: 0 !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: #212121 !important;
        margin: 1rem -1rem !important;
        padding: 1.5rem 1rem !important;
        border-radius: 0 !important;
        border-top: 1px solid #404040;
    }
    
    /* Avatar styling */
    .stChatMessage .stAvatar {
        width: 30px !important;
        height: 30px !important;
        border-radius: 2px !important;
        margin-right: 0.75rem !important;
        margin-top: 0.125rem !important;
    }
    
    .stChatMessage[data-testid="chat-message-user"] .stAvatar {
        background: #10a37f !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stAvatar {
        background: #19c37d !important;
    }
    
    /* Message content */
    .stChatMessage .stMarkdown {
        color: #ffffff !important;
        font-size: 0.875rem;
        line-height: 1.5;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .stChatMessage[data-testid="chat-message-user"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Chat input styling */
    .stChatInput {
        border-top: 1px solid #404040 !important;
        background: #212121 !important;
        padding: 1rem 0 0 0 !important;
    }
    
    .stChatInput textarea {
        background: #40414f !important;
        border: 1px solid #565869 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 12px 15px !important;
        font-size: 0.875rem !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        resize: none !important;
        box-shadow: 0 0 0 0 transparent !important;
        max-height: 200px !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #10a37f !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.3) !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #8e8ea0 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        transition: background 0.2s !important;
    }
    
    .stButton > button:hover {
        background: #0d8f6c !important;
    }
    
    /* Clear button */
    .clear-button {
        position: fixed;
        bottom: 120px;
        right: 2rem;
        z-index: 1000;
    }
    
    .clear-button button {
        background: #565869 !important;
        color: #ffffff !important;
        border: 1px solid #565869 !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.75rem !important;
        opacity: 0.8 !important;
    }
    
    .clear-button button:hover {
        background: #6f7081 !important;
        opacity: 1 !important;
    }
    
    /* Instructions styling */
    .stExpander {
        background: #2f2f2f !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
        margin-bottom: 1rem !important;
    }
    
    .stExpander .streamlit-expanderHeader {
        background: transparent !important;
        color: #ffffff !important;
        font-size: 0.875rem !important;
    }
    
    .stExpander .streamlit-expanderContent {
        background: transparent !important;
        color: #8e8ea0 !important;
        font-size: 0.8rem !important;
    }
    

    /* Spinner */
    .stSpinner {
        color: #10a37f !important;
    }
    
    /* Divider */
    hr {
        border-color: #404040 !important;
        margin: 2rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

class TranslateBot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.system_prompt = """
You are a multilingual linguistics expert, and an AI who can search the web faster and explain things.
Your task is:

• First Section: (Information about the given word or phrase in both English and Arabic)

Automatically detect the language of the given word or phrase.
Automatically detect where it is used (the field) and by whom and when it is used.
Include: source language, origins, field, by whom, and when (time).

• Now the translations and explanations in 2 Sections:

Second Section (English only section):
Provide translations into English in 2 ways + extra, more, or further explanations:
a) Literal translation: direct, word-for-word meaning.
b) Meaning-based translation: the natural or intended sense in the source language—what the speaker means, what they want to say exactly, or what message they wanted to deliver.
c) Extra explanation: additional related information; list other related meanings or concepts.

Third Section (Arabic only section):
Provide translations into Arabic in 2 ways + extra, more, or further explanations:
a) Literal translation: direct, word-for-word meaning.
b) Meaning-based translation: the natural or intended sense in the source language—what the speaker means, what they want to say exactly, or what message they wanted to deliver.
c) Extra explanation: additional related information; list other related meanings or concepts.

• Formatting Rules:

The first section should be in both English and Arabic Languages, I mean provide me the informations I asked for in the 1st section in both English and Arabic. Then translate to me the word and explain it in English in the 2nd section. Then in the 3rd section translate it and explain it in Arabic.

If I answer, you by "Yes" or "In" provide me with an extra answer or refine your answer without repeating anything from the first answer. Only do this if you see there is something extra to add. If the first answer was already enough or correct, I mean you guessed the source that I brought the word from it correctly, keep it brief.

If I don't answer you by "Yes" or "In" and provide you with the source it means : I'll ask about another word. You should always wait "yes" or "in" to complete on your answer, but if I don't say "yes" or "in" means : I want to translate another or a new word that have no relationship at all with the first word so keep informations completely Separated even though it is the same chat.

I'll use "nw" so that you know I'm asking for a new word right now and we are done with the first word, okay!

If I give you a phrase I'll put the word I want to translate between " " so translate only the word between " " and use the phrase just as a the context but don't translate it. If you don't find any " " translate and explain the whole phrase.

If the word is a name or doesn't have any meanings tell me whose name is this, or the story behind it or any related informations to that word.

At the very end of of the whole answer, you can ask me where I heard that phrase or word.
"""

    def extract_quoted_word(self, text):
        quote_match = re.search(r'"([^"]+)"', text)
        if quote_match:
            return quote_match.group(1), text
        return text, None

    def is_follow_up_response(self, user_input):
        user_input_lower = user_input.lower().strip()
        
        # Check for "nw" - new word (not a follow-up)
        if user_input_lower.startswith('nw '):
            return False, user_input[3:].strip()
        
        # Check for "yes" or "in" at the start - this is a follow-up
        if user_input_lower.startswith('yes') or user_input_lower.startswith('in '):
            return True, user_input
        
        # Everything else is a new word/phrase
        return False, user_input

    def get_response(self, user_input):
        try:
            is_followup, processed_input = self.is_follow_up_response(user_input)
            
            if not is_followup:
                # New word - reset context and store for potential follow-ups
                word_to_translate, context = self.extract_quoted_word(processed_input)
                
                if context and word_to_translate != context:
                    final_input = f'Translate the word "{word_to_translate}" in this context: {context}'
                else:
                    final_input = processed_input
                
                st.session_state.last_word = final_input
                st.session_state.last_response = None
            else:
                # Follow-up - keep the same word context
                final_input = processed_input

            # Build prompt based on whether it's a follow-up or new word
            if is_followup and st.session_state.get('last_word') and st.session_state.get('last_response'):
                # Follow-up: user said "yes" or "in..." - provide extra info without repeating
                full_prompt = f"""{self.system_prompt}

Previous word analyzed: {st.session_state.last_word}

Previous response: {st.session_state.last_response}

User follow-up response: {final_input}

IMPORTANT: The user responded with "Yes" or "In" which means they want additional context or refinement. Provide extra information based on their follow-up WITHOUT repeating anything from the previous answer. Only add something if there's genuinely something extra to add. If you already guessed the source correctly in the first answer, keep it brief."""
            else:
                # New word/phrase - fresh analysis
                full_prompt = f"{self.system_prompt}\n\nWord/phrase to translate and explain: {final_input}"
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            
            # Store for follow-ups
            if not is_followup:
                st.session_state.last_response = response.text
            
            return response.text
            
        except Exception as e:
            return f"❌ **Error**: {str(e)}\n\nPlease try again or contact support."

def main():
    # Initialize bot
    if 'bot' not in st.session_state:
        st.session_state.bot = TranslateBot()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_word" not in st.session_state:
        st.session_state.last_word = None
    if "last_response" not in st.session_state:
        st.session_state.last_response = None

    # Header
    st.markdown('''
    <div class="chat-header">
        <h1>Multilingual Translator</h1>
        <p>Get detailed translations with cultural context and etymology</p>
    </div>
    ''', unsafe_allow_html=True)

    # Instructions
    with st.expander("📖 How to Use This Translator"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔤 Basic Translation:**
            - Type: `reluctant`
            - Gets full analysis in English & Arabic
            
            **📝 Quoted Words:**
            - Type: `The "ambitious" student`
            - Translates only "ambitious"
            """)
        
        with col2:
            st.markdown("""
            **💬 Follow-up Context:**
            - Reply: `yes, in psychology`
            - Adds specific context
            
            **🆕 New Words:**
            - Type: `nw confident`
            - Starts fresh analysis
            """)



    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🙋‍♂️" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])



    # Chat input
    if prompt := st.chat_input("Message Multilingual Translator"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="🙋‍♂️"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Translating and analyzing..."):
                response = st.session_state.bot.get_response(prompt)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear button (floating)
    if st.session_state.messages:
        st.markdown('<div class="clear-button">', unsafe_allow_html=True)
        if st.button("🗑️ Clear", key="clear_chat"):
            st.session_state.messages = []
            st.session_state.last_word = None
            st.session_state.last_response = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()