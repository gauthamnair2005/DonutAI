import sys
import threading
import markdown
import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QSizePolicy,QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QTextDocument
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import google.generativeai as genai
import time
import wolframalpha
import json
import subprocess
import html

key = input("Insert Google Gemini API Key: ")
genai.configure(api_key=key)
model = genai.GenerativeModel(model_name='gemini-pro')
chat = model.start_chat()
class ChatbotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.stop_flag = False
        self.chat_history = QWebEngineView()
        self.setStyleSheet("""
            QWidget {
                background: #202020;
            }
        """)
        self.chat_history.setHtml("""
            <html>
            <head>
                <style>
                    .user-bubble {
                        position: relative;
                        background: radial-gradient(circle, purple, blue);
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
                    .user-bubble .text {
                        text-align: left;
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
                        background: radial-gradient(circle,blue,purple);
                        border-radius: 1em;
                        color: white;
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
                        padding: 5px;
                        display: inline-block;
                        margin: 5px;
                        margin-bottom: 5px;
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
                    .error {
                        position: center;
                        background: red;
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
                    .error:after {
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
                        background: radial-gradient(circle,black,#202020);
                    }
                </style>
            </head>
            <body>
                <p style='font-family: Segoe UI; text-align:center;color:white;'>Message from Developer (Gautham Nair), DonutAI is still in Preview, it might make mistakes</p>                      
            </body>
            </html>
        """)
        
        self.msg1 = None

        self.message_entry = QTextEdit()
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon('send.png'))
        self.send_button.setStyleSheet("QPushButton {background-color: #8E4684; border-radius: 10%; padding: 15px; font-size : 20px} QPushButton:pressed {background-color: white;}")
        self.voice_button = QPushButton()
        self.voice_button.setIcon(QIcon('voice.png'))
        self.voice_button.setStyleSheet("QPushButton {background-color: #8E4684; border-radius: 10%; padding: 15px; font-size : 20px} QPushButton:pressed {background-color: white;}")
        
        # Set window title and icon
        self.setWindowTitle('DonutAI PREVIEW')
        self.setWindowIcon(QIcon('velocity.png'))
        # Create heading
        self.heading = QLabel('🍩 DonutAI <sup>Preview</sup>')
        self.heading.setStyleSheet("font-size: 18px; color: white;")
        self.heading.setAlignment(Qt.AlignCenter)
        self.send_button.setFixedSize(60, 60)
        self.voice_button.setFixedSize(60, 60)

        # Set styles
        self.chat_history.setStyleSheet("font-size: 20px; color: blue; background-color: white;")
        self.message_entry.setStyleSheet("font-size: 15px; color: white; background-color: #2D2D2D;")

        self.chat_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.message_entry.setFixedHeight(60)
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
        layout.addWidget(self.heading)
        layout.addWidget(self.chat_history,1)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.reply_mode = "False"

        # Connect signals and slots
        self.send_button.clicked.connect(self.send)
        self.voice_button.clicked.connect(self.get_voice_input)

    def scroll_to_bottom(self):
        js_code = "window.scrollTo(0, document.body.scrollHeight);"
        self.chat_history.page().runJavaScript(js_code)
        

    def append_to_chat_history(self, text, is_user_message):
        plain_text = QTextDocument(text).toPlainText()
        if is_user_message == True:
            escaped_text = json.dumps("<div class='user-bubble text'>" + plain_text + "</div><br>")
        elif is_user_message == False:
            escaped_text = json.dumps("<div class='ai-bubble'>" + plain_text + "</div><br>")
        elif is_user_message == "Error":
            escaped_text = json.dumps("<div class='error'>" + plain_text + "</div><br>")
        else:
            escaped_text = json.dumps("<div class='genmessage'>" + plain_text + "</div><br>")
        self.chat_history.page().runJavaScript("document.body.innerHTML += " + escaped_text + ";")
        self.scroll_to_bottom()

    def wolf(self, msg):
        try:
            client = wolframalpha.Client('UL8UPY-4EHX5683WH')
            res = client.query(msg)
            response = next(res.results).text
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>"+response+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        except:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",  False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>/!\ Could not give response </p>", "Error")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()


    def record_and_process(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Recognizing..!</p>", "Random")
            msg = r.recognize_google(audio)
            if msg == "":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Prompt cannot be empty.</p>", "Error")
                self.append_to_chat_history("", False)
                return
            elif 'weather' in msg:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:white;'>You : </p>", True)
                self.append_to_chat_history("<p class='text' style='font-family: Segoe UI; text-align:right;color:white;'>"+msg+"</p>", True)
                self.append_to_chat_history("","Type")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Fatching Latest Weather..!</p>", "Random")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
                self.append_to_chat_history("","Type")
                threading.Thread(target=self.wolf, args=(msg,)).start()
            elif msg == "Whats is time" or msg == "What is time" or msg == "what is time" or msg == "whats is time":
                strTime = time.strftime("%H:%M:%S")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The time is "+strTime+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is date" or msg == "What is date" or msg == "what is date" or msg == "whats is date":
                strDate = time.strftime("%d/%m/%Y")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The date is "+strDate+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is day" or msg == "What is day" or msg == "what is day" or msg == "whats is day":
                strDay = time.strftime("%A")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The day is "+strDay+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is month" or msg == "What is month" or msg == "what is month" or msg == "whats is month":
                strMonth = time.strftime("%B")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The month is "+strMonth+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is year" or msg == "What is year" or msg == "what is year" or msg == "whats is year":
                strYear = time.strftime("%Y")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The year is "+strYear+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is hour" or msg == "What is hour" or msg == "what is hour" or msg == "whats is hour":
                strHour = time.strftime("%H")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The hour is "+strHour+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is minute" or msg == "What is minute" or msg == "what is minute" or msg == "whats is minute":
                strMinute = time.strftime("%M")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The minute is "+strMinute+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is second" or msg == "What is second" or msg == "what is second" or msg == "whats is second":
                strSecond = time.strftime("%S")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The second is "+strSecond+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "log off" or msg == "Log off" or msg == "Log Off" or msg == "log Off" or msg == "Log Off" or msg == "log off":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : Logging off your PC!</p>", False)
                self.append_to_chat_history("","Type")
                subprocess.call(["shutdown", "/l"])
            elif msg == "restart" or msg == "Restart":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : Restarting your PC!</p>", False)
                self.append_to_chat_history("","Type")
                subprocess.call(["shutdown", "/r"])
            elif msg == "shutdown" or msg == "Shutdown":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : Shutting down your PC!</p>", False)
                self.append_to_chat_history("","Type")
                subprocess.call(["shutdown", "/s"])
            elif msg == "exit":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : Bye! You can press the 'X' or close button to close the window.</p>", False)
                self.append_to_chat_history("","Type")
            else:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:white;'>You : </p>", True)
                self.append_to_chat_history("<p class='text' style='font-family: Segoe UI; text-align:right;color:white;'>"+msg+"</p>", True)
                self.append_to_chat_history("","Type")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
                self.append_to_chat_history("","Type")
                threading.Thread(target=self.generate_response, args=(msg,)).start()
        except sr.UnknownValueError:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>Sorry, I couldn't understand, or didnt hear what you said. Please try again!</p>", "Error")
            return ""
        except sr.RequestError as e:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>Sorry, I couldn't understand, or didnt hear what you said. Please try again!</p>", "Error")
            return ""
            
    def get_voice_input(self):
        self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Listening..!</p>", "Random")
        self.append_to_chat_history("","Type")
        threading.Thread(target=self.record_and_process).start()
    
    def send(self):
        msg = self.message_entry.toPlainText()
        msg = html.escape(msg)
        msg = msg.replace('\n','<br>')
        if msg == "":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>Prompt cannot be empty.</p>", "Error")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            return
        elif 'weather' in msg:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:white;'>You : </p>", True)
            self.append_to_chat_history("<p class='text' style='font-family: Segoe UI; text-align:right;color:white;'>"+msg+"</p>", True)
            self.append_to_chat_history("","Type")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Fatching Latest Weather..!</p>", "Random")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.wolf, args=(msg,)).start()
        elif msg == "Whats is time" or msg == "What is time" or msg == "what is time" or msg == "whats is time":
            strTime = time.strftime("%H:%M:%S")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",  False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The time is "+strTime+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is date" or msg == "What is date" or msg == "what is date" or msg == "whats is date":
            strDate = time.strftime("%d/%m/%Y")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The date is "+strDate+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is day" or msg == "What is day" or msg == "what is day" or msg == "whats is day":
            strDay = time.strftime("%A")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The day is "+strDay+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is month" or msg == "What is month" or msg == "what is month" or msg == "whats is month":
            strMonth = time.strftime("%B")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The month is "+strMonth+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is year" or msg == "What is year" or msg == "what is year" or msg == "whats is year":
            strYear = time.strftime("%Y")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The year is "+strYear+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is hour" or msg == "What is hour" or msg == "what is hour" or msg == "whats is hour":
            strHour = time.strftime("%H")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The hour is "+strHour+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is minute" or msg == "What is minute" or msg == "what is minute" or msg == "whats is minute":
            strMinute = time.strftime("%M")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The minute is "+strMinute+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is second" or msg == "What is second" or msg == "what is second" or msg == "whats is second":
            strSecond = time.strftime("%S")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>The second is "+strSecond+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "log off" or msg == "Log off" or msg == "Log Off" or msg == "log Off" or msg == "Log Off" or msg == "log off":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : Logging off your PC!</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            subprocess.call(["shutdown", "/l"])
        elif msg == "restart" or msg == "Restart":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : Restarting your PC!</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            subprocess.call(["shutdown", "/r"])
        elif msg == "shutdown" or msg == "Shutdown":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : Shutting down your PC!</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            subprocess.call(["shutdown", "/s"])

        elif msg == "exit":
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : Bye! You can press the 'X' or close button to close the window.</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        else:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:white;'>You : </p>", True)
            self.append_to_chat_history("<p class='text' style='font-family: Segoe UI; text-align:right;color:white;'>"+msg+"</p>", True)
            self.append_to_chat_history("","Type")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.generate_response, args=(msg,)).start()
            self.message_entry.clear()

    def generate_response(self, msg):
        examples = [
            ("Hello", "Hi Human!, I'm DonutAI, an AI bot developed by Gautham Nair."),
            ("What is your name?", "My name is DonutAI, an AI bot developed by Gautham Nair."),
            ("Who developed you?", "I was developed by Gautham Nair"),
            ("What is your purpose?", "I was developed to help humans."),
            ("What LLM do you use?", "I use DonutLLM 10, a fine-tuned Google PaLM 2 LLM"),
            ("What is your favourite programming language?", "Python, C and C++, of course!"),
            ("What is your favourite OS?", "DonutOS, of course!"),
            ("What is your favourite IDE?", "Visual Studio 2022, of course!"),
            ("What is your favourite text editor?", "Visual Studio Code, of course!"),
            ("What is your favourite browser?", "Microsoft Edge, of course!"),
            ("What is your favourite search engine?", "Google and Bing"),
            ("What is your favourite AI?", "DonutAI, of course!"),
            ("What is DonutAI?", "DonutAI (me) is an AI bot developed by Gautham Nair."),
            ("What is DonutOS?", "DonutOS is an OS developed by Gautham Nair from scratch."),
            ("What is DonutLLM?", "DonutLLM is a fine-tuned Google PaLM 2 LLM developed by Gautham Nair."),
            ("What is DonutDB?", "DonutDB is a database developed by Gautham Nair."),
            ("What is GIUC?", "GIUC is a utility collection developed by Gautham Nair.")
        ]
        if self.reply_mode == "False":
            try:
                response = chat.send_message(msg, generation_config={'temperature' : 0.5})
                if "```" in response.text:
                    parts = response.text.split("```")
                    full_message = "<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>"
                    is_code = False
                    for part in parts:
                        if is_code:
                            lines = part.split("\n")
                            if len(lines) > 1:
                                language_name = '<strong>' + lines[0] + '</strong>'
                                code = '<pre><code>' + html.escape('\n'.join(lines[1:])) + '</code></pre>'
                                part = language_name + code
                            else:
                                part = '<pre><code>' + html.escape(part) + '</code></pre>'
                        else:
                            part = markdown.markdown(part)
                        full_message += "<p style='font-family: Segoe UI; text-align:left;color:white;'>"+part+"</p>"
                        is_code = not is_code
                        self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>"+full_message+"</p>", False)
                        self.append_to_chat_history("","Type")
                        self.reply_mode = True
                else:
                    response_text = markdown.markdown(response.text)
                    self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                    self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>"+response_text+"</p>", False)
                    self.append_to_chat_history("","Type")
                    self.reply_mode = True
            except Exception as e:
                print(e)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",  False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>Could not give response </p>", "Error")
                self.append_to_chat_history("","Type")
                self.message_entry.clear()
        else:
            try:
                response = chat.send_message(msg, generation_config={'temperature' : 0.5})
                if "```" in response.text:
                    parts = response.text.split("```")
                    full_message = "<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>"
                    is_code = False
                    for part in parts:
                        if is_code:
                            lines = part.split("\n")
                            if len(lines) > 1:
                                language_name = '<strong>' + lines[0] + '</strong>'
                                code = '<pre><code>' + html.escape('\n'.join(lines[1:])) + '</code></pre>'
                                part = language_name + code
                            else:
                                part = '<pre><code>' + html.escape(part) + '</code></pre>'
                        else:
                            part = markdown.markdown(part)
                        full_message += "<p style='font-family: Segoe UI; text-align:left;color:white;'>"+part+"</p>"
                        is_code = not is_code
                    self.append_to_chat_history(full_message, False)
                    self.append_to_chat_history("","Type")
                    self.reply_mode = True
                else:
                    response_text = response.text
                    response_text = markdown.markdown(response_text)
                    self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>", False)
                    self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>"+response_text+"</p>", False)
                    self.append_to_chat_history("","Type")
                    self.reply_mode = True
                self.msg1 = response
            except Exception as e:
                print(e)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>DonutAI : </p>",  False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:white;'>Could not give response </p>", "Error")
                self.append_to_chat_history("","Type")

app = QApplication(sys.argv)
window = ChatbotGUI()
window.show()
sys.exit(app.exec_())