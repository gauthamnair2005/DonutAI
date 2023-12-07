import sys
import pyttsx3
import threading
import markdown
import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QSizePolicy,QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QTextDocument
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from langchain.llms import GooglePalm
import time
import wolframalpha
import json
import subprocess

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
                    .user-bubble {
                        position: relative;
                        background: #adcbe3;
                        border-radius: 1em;
                        color: white;
                        padding: 10px;
                        display: inline-block;
                        margin: 10px;
                        margin-bottom: 15px;
                        float: right;
                        clear: both;
                        box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.2);
                    }

                    .user-bubble:after {
                        content: '';
                        position: absolute;
                        right: 0;
                        top: 50%;
                        width: 0;
                        height: 0;
                        border: 20px solid transparent;
                        border-left-color: #0084ff;
                        border-right: 0;
                        border-left: 0;
                        margin-top: -10px;
                        margin-right: -20px;
                    }

                    .ai-bubble {
                        position: relative;
                        background: #f6cd61;
                        border-radius: 1em;
                        color: black;
                        padding: 10px;
                        display: inline-block;
                        margin: 10px;
                        margin-bottom: 15px;
                        float: left;
                        clear: both;
                        box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.2);
                    }

                    .ai-bubble:after {
                        content: '';
                        position: absolute;
                        left: 0;
                        top: 50%;
                        width: 0;
                        height: 0;
                        border: 20px solid transparent;
                        border-right-color: #f0f0f0;
                        border-left: 0;
                        border-right: 0;
                        margin-top: -10px;
                        margin-left: -20px;
                    }
                    .genmessage {
                        position: center;
                        background: white;
                        border-radius: 0.4em;
                        color: black;
                        padding: 10px;
                        display: inline-block;
                        margin: 10px;
                        margin-bottom: 15px;
                        float: left;
                        clear: both;
                        box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.2);                                 
                    }
                    .genmesage:after {
                        content: '';
                        position: absolute;
                        left: 0;
                        top: 50%;
                        width: 0;
                        height: 0;
                        border: 20px solid transparent;
                        border-right-color: #f0f0f0;
                        border-left: 0;
                        border-right: 0;
                        margin-top: -10px;
                        margin-left: -20px;
                    }
                    body {
                        font-family: Segoe UI;
                        font-size: 16px;
                        color: black;
                        background-color: #F0F0F0;
                    }
                </style>
            </head>
            <body>
                <p style='font-family: Segoe UI; text-align:center;color:gray;'>Message from Developer (Gautham Nair), DonutAI is still in Preview, it might make mistakes</p>                      
            </body>
            </html>
        """)
        


        self.message_entry = QLineEdit()
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon('send.png'))
        self.send_button.setStyleSheet("QPushButton {background-color: lightblue; border-radius: 10%; padding: 15px; font-size : 20px} QPushButton:pressed {background-color: white;}")
        self.voice_button = QPushButton()
        self.voice_button.setIcon(QIcon('voice.png'))
        self.voice_button.setStyleSheet("QPushButton {background-color: lightblue; border-radius: 10%; padding: 15px; font-size : 20px} QPushButton:pressed {background-color: white;}")
        
        # Set window title and icon
        self.setWindowTitle('DonutAI PREVIEW')
        self.setWindowIcon(QIcon('velocity.png'))

        # Create logo
        logo = QPixmap('velocity.png')
        self.logo_label = QLabel()
        self.logo_label.setPixmap(logo)

        # Create heading
        self.heading = QLabel('DonutAI <sup>Preview</sup>')
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
        self.chat_history.setStyleSheet("font-size: 20px; color: blue; background-color: white;")
        self.message_entry.setStyleSheet("font-size: 20px; color: black; background-color: white;")

        self.chat_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the size policy of the prompt box
        self.message_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.message_entry.setFocus()

        # Decrease the size of the buttons and place them beside the prompt box
        self.send_button.setFixedWidth(50)
        self.voice_button.setFixedWidth(50)

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

    def scroll_to_bottom(self):
        js_code = "window.scrollTo(0, document.body.scrollHeight);"
        self.chat_history.page().runJavaScript(js_code)

    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        

    def append_to_chat_history(self, text, is_user_message):
        plain_text = QTextDocument(text).toPlainText()
        if is_user_message == True:
            escaped_text = json.dumps("<div class='user-bubble'>" + plain_text + "</div><br>")
        elif is_user_message == False:
            escaped_text = json.dumps("<div class='ai-bubble'>" + plain_text + "</div><br>")
        else:
            escaped_text = json.dumps("<div class='genmessage'>" + plain_text + "</div><br>")
        self.chat_history.page().runJavaScript("document.body.innerHTML += " + escaped_text + ";")
        self.scroll_to_bottom()

    def wolf(self, msg):
        try:
            client = wolframalpha.Client('UL8UPY-4EHX5683WH')
            res = client.query(msg)
            response = next(res.results).text
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>"+response+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=(response,)).start()
        except:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",  False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>Could not give response </p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()


    def record_and_process(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Recognizing..!</p>", False)
            msg = r.recognize_google(audio)
            if msg == "":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Prompt cannot be empty.</p>", False)
                self.append_to_chat_history("", False)
                self.message_entry.clear()
                return
            elif 'weather' in msg:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:darkviolet;'>You : </p>", True)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:darkviolet;'>"+msg+"</p>", True)
                self.append_to_chat_history("","Type")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Fatching Latest Weather..!</p>", "Random")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.wolf, args=(msg,)).start()
            elif msg == "Whats is time" or msg == "What is time" or msg == "what is time" or msg == "whats is time":
                strTime = time.strftime("%H:%M:%S")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The time is "+strTime+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("The time is "+strTime,)).start()
            elif msg == "Whats is date" or msg == "What is date" or msg == "what is date" or msg == "whats is date":
                strDate = time.strftime("%d/%m/%Y")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The date is "+strDate+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("The date is "+strDate,)).start()
            elif msg == "Whats is day" or msg == "What is day" or msg == "what is day" or msg == "whats is day":
                strDay = time.strftime("%A")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The day is "+strDay+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("The day is "+strDay,)).start()
            elif msg == "Whats is month" or msg == "What is month" or msg == "what is month" or msg == "whats is month":
                strMonth = time.strftime("%B")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The month is "+strMonth+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("The month is "+strMonth,)).start()
            elif msg == "Whats is year" or msg == "What is year" or msg == "what is year" or msg == "whats is year":
                strYear = time.strftime("%Y")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The year is "+strYear+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("The year is "+strYear,)).start()
            elif msg == "Whats is hour" or msg == "What is hour" or msg == "what is hour" or msg == "whats is hour":
                strHour = time.strftime("%H")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The hour is "+strHour+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("The hour is "+strHour,)).start()
            elif msg == "Whats is minute" or msg == "What is minute" or msg == "what is minute" or msg == "whats is minute":
                strMinute = time.strftime("%M")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The minute is "+strMinute+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("The minute is "+strMinute,)).start()
            elif msg == "Whats is second" or msg == "What is second" or msg == "what is second" or msg == "whats is second":
                strSecond = time.strftime("%S")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The second is "+strSecond+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("The second is "+strSecond,)).start()
            elif msg == "log off" or msg == "Log off" or msg == "Log Off" or msg == "log Off" or msg == "Log Off" or msg == "log off":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Logging off your PC!</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                subprocess.call(["shutdown", "/l"])
            elif msg == "restart" or msg == "Restart":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Restarting your PC!</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                subprocess.call(["shutdown", "/r"])
            elif msg == "shutdown" or msg == "Shutdown":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Shutting down your PC!</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                subprocess.call(["shutdown", "/s"])
            elif msg == "exit":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Bye! You can press the 'X' or close button to close the window.</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("Bye! You can press the 'X' or colese button to close the window.",)).start()
            elif msg in donutai_keywords:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.",)).start()
            elif msg in developer_keywords:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : I was developed by Gautham Nair.</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=("I was developed by Gautham Nair.",)).start()
            else:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:darkviolet;'>You : </p>", True)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:darkviolet;'>"+msg+"</p>", True)
                self.append_to_chat_history("","Type")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.generate_response, args=(msg,)).start()
        except sr.UnknownValueError:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>Sorry, I couldn't understand, or didnt hear what you said. Please try again!</p>", False)
            threading.Thread(target=self.speak, args=("Sorry, I couldn't understand, or didnt hear what you said. Please try again!",)).start()
            return ""
        except sr.RequestError as e:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>Sorry, I couldn't understand, or didnt hear what you said. Please try again!</p>", False)
            threading.Thread(target=self.speak, args=("Sorry, I couldn't understand, or didnt hear what you said. Please try again!",)).start()
            return ""
            
    def get_voice_input(self):
        self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Listening..!</p>", False)
        self.append_to_chat_history("","Type")
        threading.Thread(target=self.record_and_process).start()
    
    def send(self):
        msg = self.message_entry.text()
        if msg == "":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Prompt cannot be empty.</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            return
        elif 'weather' in msg:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:darkviolet;'>You : </p>", True)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:darkviolet;'>"+msg+"</p>", True)
            self.append_to_chat_history("","Type")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Fatching Latest Weather..!</p>", "Random")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.wolf, args=(msg,)).start()
        elif msg == "Whats is time" or msg == "What is time" or msg == "what is time" or msg == "whats is time":
            strTime = time.strftime("%H:%M:%S")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",  False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The time is "+strTime+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("The time is "+strTime,)).start()
        elif msg == "Whats is date" or msg == "What is date" or msg == "what is date" or msg == "whats is date":
            strDate = time.strftime("%d/%m/%Y")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The date is "+strDate+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("The date is "+strDate,)).start()
        elif msg == "Whats is day" or msg == "What is day" or msg == "what is day" or msg == "whats is day":
            strDay = time.strftime("%A")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The day is "+strDay+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("The day is "+strDay,)).start()
        elif msg == "Whats is month" or msg == "What is month" or msg == "what is month" or msg == "whats is month":
            strMonth = time.strftime("%B")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The month is "+strMonth+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("The month is "+strMonth,)).start()
        elif msg == "Whats is year" or msg == "What is year" or msg == "what is year" or msg == "whats is year":
            strYear = time.strftime("%Y")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The year is "+strYear+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("The year is "+strYear,)).start()
        elif msg == "Whats is hour" or msg == "What is hour" or msg == "what is hour" or msg == "whats is hour":
            strHour = time.strftime("%H")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The hour is "+strHour+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("The hour is "+strHour,)).start()
        elif msg == "Whats is minute" or msg == "What is minute" or msg == "what is minute" or msg == "whats is minute":
            strMinute = time.strftime("%M")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The minute is "+strMinute+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("The minute is "+strMinute,)).start()
        elif msg == "Whats is second" or msg == "What is second" or msg == "what is second" or msg == "whats is second":
            strSecond = time.strftime("%S")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The second is "+strSecond+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("The second is "+strSecond,)).start()
        elif msg == "log off" or msg == "Log off" or msg == "Log Off" or msg == "log Off" or msg == "Log Off" or msg == "log off":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Logging off your PC!</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            subprocess.call(["shutdown", "/l"])
        elif msg == "restart" or msg == "Restart":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Restarting your PC!</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            subprocess.call(["shutdown", "/r"])
        elif msg == "shutdown" or msg == "Shutdown":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Shutting down your PC!</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            subprocess.call(["shutdown", "/s"])

        elif msg == "exit":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Bye! You can press the 'X' or close button to close the window.</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("Bye! You can press the 'X' or colese button to close the window.",)).start()
        elif msg in donutai_keywords:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("Hi! I am DonutAI. I am a chatbot created by Gautham Nair. I am still in development, so please forgive me if I make any mistakes.",)).start()
        elif msg in developer_keywords:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : I was developed by Gautham Nair.</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.speak, args=("I was developed by Gautham Nair.",)).start()
        else:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:darkviolet;'>You : </p>", True)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:darkviolet;'>"+msg+"</p>", True)
            self.append_to_chat_history("","Type")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.generate_response, args=(msg,)).start()
    
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
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:#FFA500;'>"+response_text+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
            else:
                response_text = response_text.replace('&quot;', '"')
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:#FFA500;'>"+response_text+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()

            engine.say(response_text)
            engine.runAndWait()
        else:
            try:
                client = wolframalpha.Client('UL8UPY-4EHX5683WH')
                res = client.query(msg)
                response = next(res.results).text
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:#FFA500;'>"+response+"</p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
                threading.Thread(target=self.speak, args=(response,)).start()
            except:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : </p>",  False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>Could not give response </p>", False)
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
    

app = QApplication(sys.argv)
window = ChatbotGUI()
window.show()
sys.exit(app.exec_())