import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import random
import re
import requests
import json
from urllib.parse import quote

class LinguisticsExpertBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Multilingual Linguistics Expert Bot")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f8f9fa')
        
        # API Configuration
        self.google_api_key = "AIzaSyAvDCc27rtTyueE5cA-ANirxiQpdcBVz4Q"
        self.translate_base_url = "https://translation.googleapis.com/language/translate/v2"
        self.detect_base_url = "https://translation.googleapis.com/language/translate/v2/detect"
        
        # Configure styles
        self.setup_styles()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title and description
        title_label = ttk.Label(main_frame, text="🔍 Multilingual Linguistics Expert Bot", 
                               font=('Arial', 20, 'bold'), foreground='#2c3e50')
        title_label.grid(row=0, column=0, pady=(0, 8))
        
        description_label = ttk.Label(main_frame, 
                                    text="I analyze words and phrases linguistically in English and Arabic with detailed translations and explanations", 
                                    font=('Arial', 11), foreground='#7f8c8d', wraplength=800)
        description_label.grid(row=1, column=0, pady=(0, 15))
        
        # Chat display area
        self.chat_frame = ttk.Frame(main_frame)
        self.chat_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        self.chat_frame.columnconfigure(0, weight=1)
        self.chat_frame.rowconfigure(0, weight=1)
        
        # Chat display with scrollbar
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=30,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50',
            insertbackground='#2c3e50',
            selectbackground='#3498db',
            selectforeground='white'
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_display.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # Message input
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(
            input_frame, 
            textvariable=self.message_var,
            font=('Arial', 12),
            width=70
        )
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        self.message_entry.bind('<Return>', self.send_message)
        
        # Send button
        self.send_button = ttk.Button(
            input_frame, 
            text="Analyze",
            command=self.send_message,
            style='Accent.TButton'
        )
        self.send_button.grid(row=0, column=1)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, pady=(5, 0))
        
        # Clear chat button
        clear_button = ttk.Button(
            control_frame,
            text="Clear Analysis",
            command=self.clear_chat
        )
        clear_button.grid(row=0, column=0, padx=(0, 10))
        
        # New word button
        new_word_button = ttk.Button(
            control_frame,
            text="New Word (nw)",
            command=self.new_word_signal
        )
        new_word_button.grid(row=0, column=1, padx=(0, 10))
        
        # Continue analysis button
        continue_button = ttk.Button(
            control_frame,
            text="Continue Analysis (Yes)",
            command=self.continue_analysis
        )
        continue_button.grid(row=0, column=2)
        
        # Initialize chat with linguistics-focused welcome message
        welcome_msg = ("🔍 **Multilingual Linguistics Expert Bot Ready**\n\n"
                      "I provide detailed linguistic analysis with:\n\n"
                      "📋 **Section 1**: Language detection, origins, field, usage context (English & Arabic)\n"
                      "🇺🇸 **Section 2**: English translations (literal + meaning-based + explanations)\n" 
                      "🇸🇦 **Section 3**: Arabic translations (literal + meaning-based + explanations)\n\n"
                      "**Usage Instructions:**\n"
                      "• Enter any word or phrase for analysis\n"
                      "• Put word in quotes \" \" if analyzing within a phrase\n"
                      "• Type 'Yes' or 'In' for additional details\n"
                      "• Type 'nw' or click 'New Word' for new analysis\n\n"
                      "**Ready to analyze your first word or phrase!**")
        
        self.add_message("Linguistics Expert", welcome_msg, "assistant")
        
        # Focus on input field
        self.message_entry.focus_set()
        
        # Track conversation state
        self.awaiting_continuation = False
        self.current_word = ""
    
    def setup_styles(self):
        """Setup custom styles for the interface"""
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 11, 'bold'), foreground='#3498db')
    
    def add_message(self, sender, message, msg_type="user"):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = time.strftime("%H:%M")
        
        # Color coding for different message types
        if msg_type == "user":
            color = "#e74c3c"  # Red for user
            prefix = "📝 You"
        else:
            color = "#27ae60"  # Green for linguistics expert
            prefix = "🔍 Linguistics Expert"
        
        # Insert the message with formatting
        self.chat_display.insert(tk.END, f"\n[{timestamp}] {prefix}:\n", f"{msg_type}_header")
        self.chat_display.insert(tk.END, f"{message}\n", f"{msg_type}_message")
        
        # Configure text tags for styling
        self.chat_display.tag_config(f"{msg_type}_header", 
                                   foreground=color, 
                                   font=('Arial', 11, 'bold'))
        self.chat_display.tag_config(f"{msg_type}_message", 
                                   foreground="#2c3e50", 
                                   font=('Consolas', 10))
        
        # Add separator line
        self.chat_display.insert(tk.END, "─" * 80 + "\n", "separator")
        self.chat_display.tag_config("separator", foreground="#bdc3c7")
        
        # Scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Handle sending a message"""
        message = self.message_var.get().strip()
        if not message:
            return
        
        # Add user message to chat
        self.add_message("You", message, "user")
        
        # Clear input field
        self.message_var.set("")
        
        # Disable send button temporarily
        self.send_button.config(state="disabled")
        self.message_entry.config(state="disabled")
        
        # Show analysis indicator
        self.show_analysis_indicator()
        
        # Process linguistics analysis in separate thread
        threading.Thread(target=self.process_linguistics_analysis, args=(message,), daemon=True).start()
    
    def show_analysis_indicator(self):
        """Show that linguistic analysis is in progress"""
        self.chat_display.config(state=tk.NORMAL)
        analysis_text = "\n🔍 Performing linguistic analysis and web research..."
        self.chat_display.insert(tk.END, analysis_text, "analyzing")
        self.chat_display.tag_config("analyzing", foreground="gray", font=('Arial', 10, 'italic'))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def remove_analysis_indicator(self):
        """Remove the analysis indicator"""
        self.chat_display.config(state=tk.NORMAL)
        content = self.chat_display.get("1.0", tk.END)
        if "Performing linguistic analysis and web research..." in content:
            lines = content.split('\n')
            filtered_lines = [line for line in lines if "Performing linguistic analysis and web research..." not in line]
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.insert("1.0", '\n'.join(filtered_lines))
        self.chat_display.config(state=tk.DISABLED)
    
    def process_linguistics_analysis(self, user_message):
        """Process the linguistic analysis request"""
        # Simulate analysis time
        time.sleep(random.uniform(2, 4))
        
        # Generate linguistic analysis
        response = self.generate_linguistics_analysis(user_message)
        
        # Update UI in main thread
        self.root.after(0, self.display_analysis_response, response)
    
    def generate_linguistics_analysis(self, message):
        """Generate comprehensive linguistic analysis"""
        message_lower = message.lower().strip()
        
        # Check for continuation signals
        if message_lower in ['yes', 'in']:
            if self.awaiting_continuation:
                return self.generate_continuation_analysis()
            else:
                return "I'm ready to analyze a new word or phrase. Please provide the text you'd like me to analyze linguistically."
        
        # Check for new word signal
        if message_lower == 'nw':
            self.awaiting_continuation = False
            self.current_word = ""
            return "Ready for new linguistic analysis! Please provide the word or phrase you'd like me to analyze."
        
        # Extract word to analyze (check for quotes first)
        word_to_analyze = self.extract_word_from_message(message)
        self.current_word = word_to_analyze
        self.awaiting_continuation = True
        
        # Generate the three-section analysis
        return self.create_full_linguistic_analysis(word_to_analyze, message)
    
    def extract_word_from_message(self, message):
        """Extract the word to analyze from the message"""
        # Look for quoted text first
        quoted_match = re.search(r'"([^"]*)"', message)
        if quoted_match:
            return quoted_match.group(1).strip()
        
        # If no quotes, analyze the entire message
        return message.strip()
    
    def create_full_linguistic_analysis(self, word, context):
        """Create the complete three-section linguistic analysis"""
        
        try:
            # Detect language
            detected_lang = self.detect_language(word)
            lang_name = self.get_language_name(detected_lang)
            
            # Get translations
            english_translation = self.translate_text(word, 'en')
            arabic_translation = self.translate_text(word, 'ar')
            
            # Get literal translations (word-by-word if possible)
            literal_english = self.get_literal_translation(word, 'en')
            literal_arabic = self.get_literal_translation(word, 'ar')
            
            analysis = f"""
🔍 **MULTILINGUAL LINGUISTIC ANALYSIS**

═══════════════════════════════════════════════════════════════════

📋 **SECTION 1: LINGUISTIC INFORMATION (English & Arabic)**

**English Analysis:**
• **Word/Phrase:** "{word}"
• **Detected Language:** {lang_name} ({detected_lang})
• **Source Language:** {lang_name}
• **Etymology/Origins:** {self.get_etymology_info(word, detected_lang)}
• **Field of Usage:** {self.determine_field_of_usage(word)}
• **Used by:** {self.get_speaker_demographics(word, detected_lang)}
• **Time Period:** {self.get_temporal_usage(word)}

**Arabic Analysis (التحليل العربي):**
• **الكلمة/العبارة:** "{word}"
• **اللغة المكتشفة:** {self.get_arabic_language_name(detected_lang)} ({detected_lang})
• **اللغة المصدر:** {self.get_arabic_language_name(detected_lang)}
• **أصل الكلمة:** {self.get_etymology_info_arabic(word, detected_lang)}
• **مجال الاستخدام:** {self.determine_field_of_usage_arabic(word)}
• **يُستخدم من قِبل:** {self.get_speaker_demographics_arabic(word, detected_lang)}
• **الفترة الزمنية:** {self.get_temporal_usage_arabic(word)}

═══════════════════════════════════════════════════════════════════

🇺🇸 **SECTION 2: ENGLISH TRANSLATIONS & EXPLANATIONS**

**a) Literal Translation:**
{literal_english}

**b) Meaning-based Translation:**
{english_translation}

**c) Extra Explanations:**
{self.get_extra_english_explanations(word, detected_lang)}

═══════════════════════════════════════════════════════════════════

🇸🇦 **SECTION 3: ARABIC TRANSLATIONS & EXPLANATIONS (الترجمات والتوضيحات العربية)**

**أ) الترجمة الحرفية:**
{literal_arabic}

**ب) الترجمة المعنوية:**
{arabic_translation}

**ج) توضيحات إضافية:**
{self.get_extra_arabic_explanations(word, detected_lang)}

═══════════════════════════════════════════════════════════════════

❓ **Where did you encounter this word or phrase?**
"""
            
            return analysis.strip()
            
        except Exception as e:
            return f"Error during linguistic analysis: {str(e)}\nPlease check your internet connection and API access."
    
    def generate_continuation_analysis(self):
        """Generate additional analysis when user says 'Yes' or 'In'"""
        if not self.current_word:
            return "Please provide a word or phrase to analyze first."
        
        try:
            detected_lang = self.detect_language(self.current_word)
            
            continuation = f"""
🔍 **ADDITIONAL LINGUISTIC ANALYSIS for "{self.current_word}"**

═══════════════════════════════════════════════════════════════════

📚 **EXTENDED ANALYSIS:**

**Morphological Analysis:**
{self.get_morphological_analysis(self.current_word, detected_lang)}

**Phonological Analysis:**  
{self.get_phonological_analysis(self.current_word, detected_lang)}

**Syntactic Patterns:**
{self.get_syntactic_patterns(self.current_word, detected_lang)}

**Semantic Relations:**
{self.get_semantic_relations(self.current_word, detected_lang)}

**Cultural Significance:**
{self.get_cultural_significance(self.current_word, detected_lang)}

**Regional Variations:**
{self.get_regional_variations(self.current_word, detected_lang)}

**Alternative Translations:**
• **To English:** {self.get_alternative_translations(self.current_word, 'en')}
• **To Arabic:** {self.get_alternative_translations(self.current_word, 'ar')}

═══════════════════════════════════════════════════════════════════
"""
            
            return continuation.strip()
            
        except Exception as e:
            return f"Error during extended analysis: {str(e)}"
    
    # Google Translate API Methods
    
    def detect_language(self, text):
        """Detect the language of the given text"""
        try:
            params = {
                'key': self.google_api_key,
                'q': text
            }
            
            response = requests.post(self.detect_base_url, data=params)
            result = response.json()
            
            if 'data' in result and 'detections' in result['data']:
                return result['data']['detections'][0][0]['language']
            else:
                return 'unknown'
        except Exception as e:
            return 'unknown'
    
    def translate_text(self, text, target_language):
        """Translate text to the target language"""
        try:
            params = {
                'key': self.google_api_key,
                'q': text,
                'target': target_language
            }
            
            response = requests.post(self.translate_base_url, data=params)
            result = response.json()
            
            if 'data' in result and 'translations' in result['data']:
                return result['data']['translations'][0]['translatedText']
            else:
                return f"Translation to {target_language} unavailable"
        except Exception as e:
            return f"Translation error: {str(e)}"
    
    def get_literal_translation(self, text, target_language):
        """Get literal word-by-word translation"""
        try:
            # For literal translation, we'll translate individual words if the text has multiple words
            words = text.split()
            if len(words) > 1:
                literal_parts = []
                for word in words:
                    translated_word = self.translate_text(word, target_language)
                    literal_parts.append(f"{word} → {translated_word}")
                return " | ".join(literal_parts)
            else:
                return self.translate_text(text, target_language)
        except Exception as e:
            return f"Literal translation error: {str(e)}"
    
    # Language Information Methods
    
    def get_language_name(self, lang_code):
        """Get full language name from code"""
        language_names = {
            'en': 'English',
            'ar': 'Arabic (العربية)',
            'fr': 'French (Français)',
            'es': 'Spanish (Español)', 
            'de': 'German (Deutsch)',
            'it': 'Italian (Italiano)',
            'pt': 'Portuguese (Português)',
            'ru': 'Russian (Русский)',
            'zh': 'Chinese (中文)',
            'ja': 'Japanese (日本語)',
            'ko': 'Korean (한국어)',
            'hi': 'Hindi (हिन्दी)',
            'tr': 'Turkish (Türkçe)',
            'nl': 'Dutch (Nederlands)',
            'sv': 'Swedish (Svenska)',
            'da': 'Danish (Dansk)',
            'no': 'Norwegian (Norsk)',
            'fi': 'Finnish (Suomi)',
            'pl': 'Polish (Polski)',
            'cs': 'Czech (Čeština)',
            'hu': 'Hungarian (Magyar)',
            'ro': 'Romanian (Română)',
            'bg': 'Bulgarian (Български)',
            'hr': 'Croatian (Hrvatski)',
            'sk': 'Slovak (Slovenčina)',
            'sl': 'Slovenian (Slovenščina)',
            'et': 'Estonian (Eesti)',
            'lv': 'Latvian (Latviešu)',
            'lt': 'Lithuanian (Lietuvių)',
            'mt': 'Maltese (Malti)',
            'unknown': 'Unknown Language'
        }
        return language_names.get(lang_code, f'Language ({lang_code})')
    
    def get_arabic_language_name(self, lang_code):
        """Get language name in Arabic"""
        arabic_names = {
            'en': 'الإنجليزية',
            'ar': 'العربية',
            'fr': 'الفرنسية',
            'es': 'الإسبانية',
            'de': 'الألمانية',
            'it': 'الإيطالية',
            'pt': 'البرتغالية',
            'ru': 'الروسية',
            'zh': 'الصينية',
            'ja': 'اليابانية',
            'ko': 'الكورية',
            'hi': 'الهندية',
            'tr': 'التركية',
            'unknown': 'لغة غير معروفة'
        }
        return arabic_names.get(lang_code, f'لغة ({lang_code})')
    
    # Linguistic Analysis Helper Methods
    
    def get_etymology_info(self, word, lang_code):
        """Get etymology information"""
        # This would typically require specialized etymology APIs or databases
        etymology_info = {
            'en': f"English word analysis needed for '{word}'",
            'ar': f"Arabic root analysis needed for '{word}'",
            'fr': f"French etymology from Latin/Germanic origins for '{word}'",
            'es': f"Spanish etymology from Latin origins for '{word}'",
            'de': f"German etymology from Proto-Germanic for '{word}'",
            'unknown': "Etymology information requires specialized databases"
        }
        return etymology_info.get(lang_code, f"Etymology research needed for {self.get_language_name(lang_code)} word '{word}'")
    
    def get_etymology_info_arabic(self, word, lang_code):
        """Get etymology information in Arabic"""
        return f"يحتاج تحليل أصل الكلمة '{word}' من {self.get_arabic_language_name(lang_code)} إلى قواعد بيانات متخصصة"
    
    def determine_field_of_usage(self, word):
        """Determine the field or domain where the word is commonly used"""
        # Basic field detection based on common patterns
        word_lower = word.lower()
        if any(tech_word in word_lower for tech_word in ['api', 'code', 'software', 'computer', 'digital']):
            return "Technology/Computing"
        elif any(med_word in word_lower for med_word in ['medical', 'doctor', 'patient', 'health', 'treatment']):
            return "Medical/Healthcare" 
        elif any(sci_word in word_lower for sci_word in ['research', 'study', 'analysis', 'experiment']):
            return "Academic/Scientific"
        else:
            return "General usage - context analysis needed"
    
    def determine_field_of_usage_arabic(self, word):
        """Determine field of usage in Arabic"""
        field = self.determine_field_of_usage(word)
        field_translations = {
            "Technology/Computing": "التكنولوجيا/الحاسوب",
            "Medical/Healthcare": "الطبي/الرعاية الصحية",
            "Academic/Scientific": "أكاديمي/علمي",
            "General usage - context analysis needed": "استخدام عام - يحتاج تحليل السياق"
        }
        return field_translations.get(field, "يحتاج تحديد المجال")
    
    def get_speaker_demographics(self, word, lang_code):
        """Get information about who typically uses this word"""
        return f"Speaker analysis for {self.get_language_name(lang_code)} requires sociolinguistic databases"
    
    def get_speaker_demographics_arabic(self, word, lang_code):
        """Get speaker demographics in Arabic"""
        return f"تحليل المتحدثين لـ {self.get_arabic_language_name(lang_code)} يحتاج قواعد بيانات لغوية اجتماعية"
    
    def get_temporal_usage(self, word):
        """Get information about when the word is/was used"""
        return "Historical usage analysis requires temporal linguistic databases"
    
    def get_temporal_usage_arabic(self, word):
        """Get temporal usage in Arabic"""  
        return "تحليل الاستخدام التاريخي يحتاج قواعد بيانات لغوية زمنية"
    
    def get_extra_english_explanations(self, word, lang_code):
        """Get additional explanations in English"""
        try:
            # Try to get synonyms by translating to English and back
            english_trans = self.translate_text(word, 'en')
            return f"Primary meaning: {english_trans}\nAdditional context analysis available with extended linguistic APIs"
        except:
            return "Extended explanations require comprehensive linguistic databases"
    
    def get_extra_arabic_explanations(self, word, lang_code):
        """Get additional explanations in Arabic"""
        try:
            arabic_trans = self.translate_text(word, 'ar')
            return f"المعنى الأساسي: {arabic_trans}\nتحليل السياق الإضافي متاح مع واجهات برمجة التطبيقات اللغوية المتقدمة"
        except:
            return "التوضيحات الموسعة تحتاج قواعد بيانات لغوية شاملة"
    
    # Extended Analysis Methods
    
    def get_morphological_analysis(self, word, lang_code):
        """Get morphological analysis"""
        return f"Morphological breakdown of '{word}' ({self.get_language_name(lang_code)}) requires specialized morphological analyzers"
    
    def get_phonological_analysis(self, word, lang_code):
        """Get phonological analysis"""
        return f"Phonetic transcription and sound pattern analysis for '{word}' requires phonological databases"
    
    def get_syntactic_patterns(self, word, lang_code):
        """Get syntactic pattern analysis"""
        return f"Syntactic usage patterns for '{word}' in {self.get_language_name(lang_code)} require parsed corpus analysis"
    
    def get_semantic_relations(self, word, lang_code):
        """Get semantic relations"""
        try:
            # Basic semantic relations using translation
            related_terms = []
            if lang_code != 'en':
                en_translation = self.translate_text(word, 'en')
                related_terms.append(f"English equivalent: {en_translation}")
            if lang_code != 'ar':
                ar_translation = self.translate_text(word, 'ar')
                related_terms.append(f"Arabic equivalent: {ar_translation}")
            
            return "\n".join(related_terms) if related_terms else "Semantic relationship analysis requires specialized lexical databases"
        except:
            return "Semantic analysis requires comprehensive lexical databases"
    
    def get_cultural_significance(self, word, lang_code):
        """Get cultural significance"""
        return f"Cultural context analysis for '{word}' in {self.get_language_name(lang_code)} culture requires anthropological linguistic databases"
    
    def get_regional_variations(self, word, lang_code):
        """Get regional variations"""
        return f"Dialectal and regional variations of '{word}' require comprehensive dialectological databases"
    
    def get_alternative_translations(self, word, target_lang):
        """Get alternative translations"""
        try:
            # Get primary translation
            primary = self.translate_text(word, target_lang)
            return f"Primary: {primary} (Alternative translations require thesaurus APIs)"
        except:
            return "Alternative translation analysis requires comprehensive translation databases"
    
    def display_analysis_response(self, response):
        """Display the linguistic analysis response"""
        # Remove analysis indicator
        self.remove_analysis_indicator()
        
        # Add linguistics expert response
        self.add_message("Linguistics Expert", response, "assistant")
        
        # Re-enable input controls
        self.send_button.config(state="normal")
        self.message_entry.config(state="normal")
        self.message_entry.focus_set()
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Reset state
        self.awaiting_continuation = False
        self.current_word = ""
        
        # Add welcome message back
        welcome_msg = ("Analysis cleared! Ready for new linguistic analysis.\n\n"
                      "Please provide a word or phrase for comprehensive multilingual analysis.")
        self.add_message("Linguistics Expert", welcome_msg, "assistant")
    
    def new_word_signal(self):
        """Handle new word button click"""
        self.message_var.set("nw")
        self.send_message()
    
    def continue_analysis(self):
        """Handle continue analysis button click"""
        self.message_var.set("Yes")
        self.send_message()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set window icon (optional)
    try:
        root.iconbitmap('linguistics.ico')
    except:
        pass
    
    app = LinguisticsExpertBot(root)
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()