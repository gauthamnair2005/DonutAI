import sys
import pyttsx3
import threading
import markdown
import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QSizePolicy,QTextEdit,QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextBrowser, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from langchain.llms import GooglePalm
import html
import pygame
import tempfile
from gtts import gTTS
import time

donutai_keywords = ["DonutAI", "donutai", "Donutai", "donutAI", "Donut AI", "donut ai", "donutAi", "donut AI"]
developer_keywords = ["who developed you", "who developed you?", "who created you", "who created you?", "who made you", "who made you?", "who is your developer", "who is your developer?", "who is your creator", "who is your creator?", "who is your father", "who is your father?", "who is your dad", "who is your dad?", "who is your daddy", "who is your daddy?", "Who developed you", "Who developed you?", "Who created you", "Who created you?", "Who made you", "Who made you?", "Who is your developer", "Who is your developer?", "Who is your creator", "Who is your creator?", "Who is your father", "Who is your father?", "Who is your dad", "Who is your dad?", "Who is your daddy", "Who is your daddy?"]


model_id="models/chat-bison-001"
llm=GooglePalm(google_api_key="API")
llm.temperature=0.7

class ChatbotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.stop_flag = False
        self.chat_history = QTextEdit()
        self.message_entry = QLineEdit()
        self.send_button = QPushButton('Send')
        self.voice_button = QPushButton('Voice Input')
        self.stop_speaking_button = QPushButton('Stop')


        # Set window title and icon
        self.setWindowTitle('DonutAI PREVIEW')
        self.setWindowIcon(QIcon('velocity.png'))

        # Create logo
        logo = QPixmap('velocity.png')
        self.logo_label = QLabel()
        self.logo_label.setPixmap(logo)

        # Create heading
        self.heading = QLabel('DonutAI PREVIEW')
        self.heading.setStyleSheet("font-size: 24px; color: darkblue;")

        self.logo_label.setAlignment(Qt.AlignCenter)
        self.heading.setAlignment(Qt.AlignCenter)


        # Initialize pyttsx3
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)


        # Set styles
        self.chat_history.setStyleSheet("font-size: 20px; color: blue; background-color: lightblue;")
        self.message_entry.setStyleSheet("font-size: 16px; color: green; background-color: lightgray;")
        self.send_button.setStyleSheet("font-size: 16px; color: white; background-color: darkviolet;")
        self.voice_button.setStyleSheet("font-size: 16px; color: white; background-color: darkviolet;")
        self.stop_speaking_button.setStyleSheet("font-size: 16px; color: white; background-color: red;")

        self.chat_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the size policy of the prompt box
        self.message_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.chat_history.setReadOnly(True)
        self.message_entry.setFocus()

        # Decrease the size of the buttons and place them beside the prompt box
        self.send_button.setFixedWidth(100)
        self.voice_button.setFixedWidth(100)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.message_entry)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.voice_button)

        # Arrange widgets
        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(self.heading)
        layout.addWidget(self.chat_history,1)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect signals and slots
        self.send_button.clicked.connect(self.send)
        self.voice_button.clicked.connect(self.get_voice_input)

    def send(self):
        msg = self.message_entry.text()
        if msg == "":
            self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
            self.chat_history.append("DonutAI : Prompt cannot be empty.")
            self.chat_history.append("")
            return
        elif msg == "exit":
            self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
            self.chat_history.append("DonutAI : Bye! You can press the 'X' or close button to close the window.")
            self.chat_history.append("")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("Bye! You can press the 'X' or colese button to close the window.",)).start()
        elif msg in donutai_keywords:
            self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
            self.chat_history.append("DonutAI : Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.")
            self.chat_history.append("")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.",)).start()
        elif msg in developer_keywords:
            self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
            self.chat_history.append("DonutAI : I was developed by Gautham Nair.")
            self.chat_history.append("")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("I was developed by Gautham Nair.",)).start()
        else:
            self.chat_history.setStyleSheet("font-size: 20px; color: darkblue; background-color: lightblue;")
            self.chat_history.append("You : ")
            self.chat_history.append(msg)
            self.chat_history.append("")
            self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
            self.chat_history.append("Generating Answers..!")
            self.chat_history.append("")
            threading.Thread(target=self.generate_response, args=(msg,)).start()

    def get_voice_input(self):
        def record_and_process():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
                self.chat_history.append("Listening..!")
                self.chat_history.append("")
                audio = r.listen(source)
            try:
                msg = r.recognize_google(audio)
                if msg == "":
                    self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
                    self.chat_history.append("DonutAI : Prompt cannot be empty.")
                    self.chat_history.append("")
                    return
                elif msg == "exit":
                    self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
                    self.chat_history.append("DonutAI : Bye! You can press the 'X' or close button to close the window.")
                    self.chat_history.append("")
                    self.message_entry.clear()
                    threading.Thread(target=self.speak, args=("Bye! You can press the 'X' or colese button to close the window.",)).start()
                elif msg in donutai_keywords:
                    self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
                    self.chat_history.append("DonutAI : Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.")
                    self.chat_history.append("")
                    self.message_entry.clear()
                    threading.Thread(target=self.speak, args=("Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.",)).start()
                elif msg in developer_keywords:
                    self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
                    self.chat_history.append("DonutAI : I was developed by Gautham Nair.")
                    self.chat_history.append("")
                    self.message_entry.clear()
                    threading.Thread(target=self.speak, args=("I was developed by Gautham Nair.",)).start()
                else:
                    self.chat_history.setStyleSheet("font-size: 20px; color: darkblue; background-color: lightblue;")
                    self.chat_history.append("You : ")
                    self.chat_history.append(msg)
                    self.chat_history.append("")
                    self.chat_history.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightblue;")
                    self.chat_history.append("Generating Answers..!")
                    self.chat_history.append("")
                    threading.Thread(target=self.generate_response, args=(msg,)).start()
            except sr.UnknownValueError:
                threading.Thread(target=self.speak, args=("Sorry, I couldn't understand, or didnt hear what you said. Please try again!",)).start()
                return ""
            except sr.RequestError as e:
                threading.Thread(target=self.speak, args=("Sorry, I couldn't understand, or didnt hear what you said. Please try again!",)).start()
                return ""
            
        threading.Thread(target=record_and_process).start()

    def generate_response(self, msg):
        msg = [msg]
        llm_results= llm._generate(msg)
        response=llm_results.generations

        if response and len(response[0]) > 0:  # Check if response is not empty and contains at least one element
            response_text = html.escape(response[0][0].text)

            # Check if the response is a code snippet
            if response_text.startswith('```') and response_text.endswith('```'):
                # Remove the backticks and wrap the response in a <pre> tag
                response_text = '<pre>' + response_text[3:-3] + '</pre>'
                self.chat_history.append("DonutAI : ")
                self.chat_history.append(response_text)
                self.chat_history.append("")
                self.message_entry.clear()
            else:
                self.chat_history.append("DonutAI : ")
                self.chat_history.append(response_text)
                self.chat_history.append("")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=(response_text,)).start()
                self.message_entry.clear()
        else:
            # Handle the case where response is empty or doesn't contain the expected structure
            # You can customize this part according to your needs
            self.chat_history.append("DonutAI : I'm sorry, I couldn't generate a response.")
            self.message_entry.clear()

    def speak(self, text):
        try:
            self.stop_flag = False  # Reset the flag before starting the speech
            text = text.replace('*', '')
            text = text.replace('`', '')
            text = text.replace('"', '')
            text = text.replace("'", '')
            text = text.replace('<', 'lesser than')
            text = text.replace('>', 'greater than')
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                tts.save("{}.mp3".format(fp.name))
                pygame.mixer.init()
                pygame.mixer.music.load("{}.mp3".format(fp.name))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() and not self.stop_flag:  # Check the flag in the loop
                    time.sleep(0.1)
        except Exception as e:
            print(f"Exception in speak: {e}")

app = QApplication(sys.argv)
window = ChatbotGUI()
window.show()
sys.exit(app.exec_())