import sys
import pyttsx3
import threading
import markdown
import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QSizePolicy,QTextEdit,QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextBrowser, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QTextDocument
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from langchain.llms import GooglePalm
import html
import time
import wolframalpha
import json

donutai_keywords = ["DonutAI", "donutai", "Donutai", "donutAI", "Donut AI", "donut ai", "donutAi", "donut AI"]
developer_keywords = ["who developed you", "who developed you?", "who created you", "who created you?", "who made you", "who made you?", "who is your developer", "who is your developer?", "who is your creator", "who is your creator?", "who is your father", "who is your father?", "who is your dad", "who is your dad?", "who is your daddy", "who is your daddy?", "Who developed you", "Who developed you?", "Who created you", "Who created you?", "Who made you", "Who made you?", "Who is your developer", "Who is your developer?", "Who is your creator", "Who is your creator?", "Who is your father", "Who is your father?", "Who is your dad", "Who is your dad?", "Who is your daddy", "Who is your daddy?"]

key = input("Insert Google PaLM API Key: ")
llm=GooglePalm(google_api_key=key)
llm.temperature=1.0

class ChatbotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.stop_flag = False
        self.chat_history = QWebEngineView()
        self.chat_history.setHtml("""
            <html>
            <head>
                <style>
                    body {
                        font-family: Arial;
                        font-size: 20px;
                        color: orange;
                        background-color: #F0F0F0;
                    }
                </style>
            </head>
            <body></body>
            </html>
        """)

        self.message_entry = QLineEdit()
        self.send_button = QPushButton('Send')
        self.send_button.setStyleSheet("QPushButton {background-color: lightgreen; border-radius: 30%; padding: 15px; font-size : 20px} QPushButton:pressed {background-color: white;}")
        self.voice_button = QPushButton('Voice')
        self.voice_button.setStyleSheet("QPushButton {background-color: lightblue; border-radius: 30%; padding: 15px; font-size : 20px} QPushButton:pressed {background-color: white;}")
        
        # Set window title and icon
        self.setWindowTitle('DonutAI PREVIEW')
        self.setWindowIcon(QIcon('velocity.png'))

        # Create logo
        logo = QPixmap('velocity.png')
        self.logo_label = QLabel()
        self.logo_label.setPixmap(logo)

        # Create heading
        self.heading = QLabel('<b>Donut</b>AI <sup>PREVIEW</sup>')
        self.heading.setStyleSheet("font-size: 24px; color: orange;")

        self.logo_label.setAlignment(Qt.AlignCenter)
        self.heading.setAlignment(Qt.AlignCenter)


        # Initialize pyttsx3
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.send_button.setFixedSize(60, 60)
        self.voice_button.setFixedSize(60, 60)

        # Set styles
        self.chat_history.setStyleSheet("font-size: 20px; color: blue;background-color: black;")
        self.message_entry.setStyleSheet("font-size: 20px; color: darkviolet; background-color: lightgray;")

        self.chat_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the size policy of the prompt box
        self.message_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.message_entry.setFocus()

        # Decrease the size of the buttons and place them beside the prompt box
        self.send_button.setFixedWidth(100)
        self.voice_button.setFixedWidth(100)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.voice_button)
        button_layout.addWidget(self.message_entry)
        button_layout.addWidget(self.send_button)
        

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

    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        

    def append_to_chat_history(self, text):
        escaped_text = json.dumps(QTextDocument(text).toPlainText())
        self.chat_history.page().runJavaScript("document.body.innerHTML += " + escaped_text + ";")

    def wolf(self, msg):
        try:
            client = wolframalpha.Client('UL8UPY-4EHX5683WH')
            res = client.query(msg)
            response = next(res.results).text
            self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : </p>")
            self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>"+response+"</p>")
            self.append_to_chat_history("")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=(response,)).start()
        except:
            self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : </p>")
            self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>Could not give response </p>")
            self.append_to_chat_history("")
            self.message_entry.clear()

    def send(self):
        msg = self.message_entry.text()
        if msg == "":
            self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : Prompt cannot be empty.</p>")
            self.append_to_chat_history("")
            self.message_entry.clear()
            return
        elif 'weather' in msg:
            self.append_to_chat_history("<p style='font-family: arial; text-align:right;color:darkviolet;'>You : </p>")
            self.append_to_chat_history("<p style='font-family: arial; text-align:right;color:darkviolet;'>"+msg+"</p>")
            self.append_to_chat_history("")
            self.append_to_chat_history("<p style='font-family: arial; text-align:center;color:green;'>Fetching Latest Weather..!</p>")
            self.append_to_chat_history("<p style='font-family: arial; text-align:center;color:green;'>Generating Answers..!</p>")
            self.append_to_chat_history("")
            self.message_entry.clear()
            threading.Thread(target=self.wolf, args=(msg,)).start()
        elif msg == "exit":
            self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : Bye! You can press the 'X' or close button to close the window.</p>")
            self.append_to_chat_history("")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("Bye! You can press the 'X' or colese button to close the window.",)).start()
        elif msg in donutai_keywords:
            self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.</p>")
            self.append_to_chat_history("")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.",)).start()
        elif msg in developer_keywords:
            self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : I was developed by Gautham Nair.</p>")
            self.append_to_chat_history("")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("I was developed by Gautham Nair.",)).start()
        else:
            self.append_to_chat_history("<p style='font-family: arial; text-align:right;color:darkviolet;'>You : </p>")
            self.append_to_chat_history("<p style='font-family: arial; text-align:right;color:darkviolet;'>"+msg+"</p>")
            self.append_to_chat_history("")
            self.append_to_chat_history("<p style='font-family: arial; text-align:center;color:green;'>Generating Answers..!</p>")
            self.append_to_chat_history("")
            self.message_entry.clear()
            threading.Thread(target=self.generate_response, args=(msg,)).start()

    def get_voice_input(self):
        def record_and_process():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.append_to_chat_history("<p style='font-family: arial; text-align:center;color:green;'>Listening..!</p>")
                self.append_to_chat_history("")
                audio = r.listen(source)
            try:
                msg = r.recognize_google(audio)
                if msg == "":
                    self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : Prompt cannot be empty.</p>")
                    self.append_to_chat_history("")
                    self.message_entry.clear()
                    return
                elif 'weather' in msg:
                    self.append_to_chat_history("<p style='font-family: arial; text-align:right;color:darkviolet;'>You : </p>")
                    self.append_to_chat_history("<p style='font-family: arial; text-align:right;color:darkviolet;'>"+msg+"</p>")
                    self.append_to_chat_history("")
                    self.append_to_chat_history("<p style='font-family: arial; text-align:center;color:green;'>Fetching Latest Weather..!</p>")
                    self.append_to_chat_history("<p style='font-family: arial; text-align:center;color:green;'>Generating Answers..!</p>")
                    self.append_to_chat_history("")
                    self.message_entry.clear()
                    threading.Thread(target=self.wolf, args=(msg,)).start()
                elif msg == "exit":
                    self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : Bye! You can press the 'X' or close button to close the window.</p>")
                    self.append_to_chat_history("")
                    self.message_entry.clear()
                    threading.Thread(target=self.speak, args=("Bye! You can press the 'X' or colese button to close the window.",)).start()
                elif msg in donutai_keywords:
                    self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.</p>")
                    self.append_to_chat_history("")
                    self.message_entry.clear()
                    threading.Thread(target=self.speak, args=("Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.",)).start()
                elif msg in developer_keywords:
                    self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : I was developed by Gautham Nair.</p>")
                    self.append_to_chat_history("")
                    self.message_entry.clear()
                    threading.Thread(target=self.speak, args=("I was developed by Gautham Nair.",)).start()
                else:
                    self.append_to_chat_history("<p style='font-family: arial; text-align:right;color:darkviolet;'>You : </p>")
                    self.append_to_chat_history("<p style='font-family: arial; text-align:right;color:darkviolet;'>"+msg+"</p>")
                    self.append_to_chat_history("")
                    self.append_to_chat_history("<p style='font-family: arial; text-align:center;color:green;'>Generating Answers..!</p>")
                    self.append_to_chat_history("")
                    self.message_entry.clear()
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

        engine = pyttsx3.init()

        if response and len(response[0]) > 0:  # Check if response is not empty and contains at least one element
            response_text = markdown.markdown(response[0][0].text, extensions=['extra'])

            # Check if the response is a code snippet
            if response_text.startswith('```') and response_text.endswith('```'):
                # Remove the backticks and wrap the response in a <pre> tag
                response_text = '<pre>' + response_text[3:-3] + '</pre>'
                self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : </p>")
                self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:#FFA500;'>"+response_text+"</p>")
                self.append_to_chat_history("")
                self.message_entry.clear()
            else:
                response_text = response_text.replace('&quot;', '"')
                self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : </p>")
                self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:#FFA500;'>"+response_text+"</p>")
                self.append_to_chat_history("")
                self.message_entry.clear()

            engine.say(response_text)
            engine.runAndWait()
        else:
            try:
                client = wolframalpha.Client('UL8UPY-4EHX5683WH')
                res = client.query(msg)
                response = next(res.results).text
                self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : </p>")
                self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:#FFA500;'>"+response+"</p>")
                self.append_to_chat_history("")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=(response,)).start()
            except:
                self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>DonutAI : </p>")
                self.append_to_chat_history("<p style='font-family: arial; text-align:left;color:orange;'>Could not give response </p>")
                self.append_to_chat_history("")
                self.message_entry.clear()
    

app = QApplication(sys.argv)
window = ChatbotGUI()
window.show()
sys.exit(app.exec_())