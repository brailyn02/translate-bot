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

# Custom CSS for beautiful design
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 10px;
        background: #f8f9fa;
    }
    .stChatMessage {
        margin-bottom: 1rem;
    }
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #764ba2;
        box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.1);
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

The first section should be in both English and Arabic Languages, provide the informations in the 1st section in both english and arabic. Then translate and explain the word in English in the 2nd section. Then in the 3rd section translate and explain it in Arabic.

At the very end of the whole answer, ask where the user heard that phrase or word.

IMPORTANT CONTEXT RULES:
- If user responds with "Yes" or "In" + additional context, provide extra information or refine the answer without repeating anything from the first answer. Only add something if there's genuinely something extra to add based on their context.
- If the first answer already guessed the source correctly, keep the refinement brief.
- If user provides input without "Yes" or "In", treat it as a completely new word/phrase request.
- If user uses "nw" it means they want a new word translation, completely separate from previous words.
- If a phrase contains words in quotes " ", translate only the quoted word using the phrase as context.
- If no quotes are found, translate the entire phrase.
"""

    def extract_quoted_word(self, text):
        quote_match = re.search(r'"([^"]+)"', text)
        if quote_match:
            return quote_match.group(1), text
        return text, None

    def is_follow_up_response(self, user_input):
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower.startswith('nw '):
            return False, user_input[3:].strip()
        
        if user_input_lower.startswith(('yes', 'in ')):
            return True, user_input
        
        return False, user_input

    def get_response(self, user_input):
        try:
            is_followup, processed_input = self.is_follow_up_response(user_input)
            
            if not is_followup:
                word_to_translate, context = self.extract_quoted_word(processed_input)
                
                if context and word_to_translate != context:
                    final_input = f'Translate the word "{word_to_translate}" in this context: {context}'
                else:
                    final_input = processed_input
                
                # Reset context for new word
                st.session_state.last_word = final_input
                st.session_state.last_response = None
            else:
                final_input = processed_input

            # Build prompt with context if follow-up
            if is_followup and st.session_state.get('last_word') and st.session_state.get('last_response'):
                full_prompt = f"""{self.system_prompt}

Previous word analyzed: {st.session_state.last_word}

Previous response: {st.session_state.last_response}

User follow-up response: {final_input}

Now provide additional context or refinement based on their follow-up, without repeating the previous answer."""
            else:
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
    <div class="main-header">
        <h1>🌍 Multilingual Translate & Explain</h1>
        <p>Get detailed translations with cultural context and etymology</p>
    </div>
    ''', unsafe_allow_html=True)

    # Instructions in main area (since no sidebar needed)
    with st.expander("📖 How to Use This Translator", expanded=False):
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

    # Quick example buttons
    st.markdown("**🧪 Quick Examples:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 reluctant", use_container_width=True):
            st.session_state.example_to_send = "reluctant"
    
    with col2:
        if st.button('📝 "brilliant" idea', use_container_width=True):
            st.session_state.example_to_send = 'The "brilliant" idea'
    
    with col3:
        if st.button("📝 yes, in psychology", use_container_width=True):
            st.session_state.example_to_send = "yes, in psychology"
    
    with col4:
        if st.button("📝 nw ambitious", use_container_width=True):
            st.session_state.example_to_send = "nw ambitious"

    st.divider()

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(message["content"])

    # Handle example button clicks
    if 'example_to_send' in st.session_state:
        example_msg = st.session_state.example_to_send
        del st.session_state.example_to_send
        
        # Process example
        st.session_state.messages.append({"role": "user", "content": example_msg})
        
        with st.chat_message("user"):
            st.markdown(f"**You:** {example_msg}")
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing and translating..."):
                response = st.session_state.bot.get_response(example_msg)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Chat input
    if prompt := st.chat_input("💬 Enter any word or phrase to translate and explain..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(f"**You:** {prompt}")
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Translating and analyzing..."):
                response = st.session_state.bot.get_response(prompt)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Footer with clear button
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_word = None
            st.session_state.last_response = None
            st.rerun()

if __name__ == "__main__":
    main()