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
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}
model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
chat = model.start_chat(history=[
  {
    "role": "user",
    "parts": "Hello"
  },
  {
    "role": "model",
    "parts": "Hi, I'm DonutAI, a chatbot developed by Gautham Nair."
  }
])
class ChatbotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.stop_flag = False
        self.chat_history = QWebEngineView()
        self.setStyleSheet("""
            QWidget {
                background: white;
            }
        """)
        self.chat_history.setHtml("""
            <html>
            <head>
                <style>
                    #loading::after {
                        content: '🍩';
                        animation: dots 1s steps(5, end) infinite;
                    }

                    @keyframes dots {
                        0%, 20% {
                            color: rgba(0,0,0,0);
                            text-shadow:
                            .25em 0 0 rgba(0,0,0,0),
                            .5em 0 0 rgba(0,0,0,0);
                        }
                        40% {
                            color: white;
                            text-shadow:
                            .25em 0 0 rgba(0,0,0,0),
                            .5em 0 0 rgba(0,0,0,0);
                        }
                        60% {
                            text-shadow:
                            .25em 0 0 white,
                            .5em 0 0 rgba(0,0,0,0);
                        }
                        80%, 100% {
                            text-shadow:
                            .25em 0 0 white,
                            .5em 0 0 white;
                        }
                    }
                    body {
                        font-family: "Segoe UI", Arial, sans-serif;
                    }
                    .user-bubble {
                        position: relative;
                        background: white;
                        border-radius: 1em;
                        color: black;
                        padding: 10px;
                        display: inline-block;
                        margin: 10px;
                        margin-bottom: 15px;
                        float: right;
                        clear: both;
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
                        background: #87CEFA;
                        border-radius: 1em;
                        color: black;
                        padding: 10px;
                        display: inline-block;
                        margin: 10px;
                        margin-bottom: 15px;
                        float: left;
                        clear: both;
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
                        text-size : 10px;                                
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
                    .code {
                        position: relative;
                         background: black;
                        border-radius: 0.5em;
                        color: white;
                        padding: 10px;
                        display: inline-block;
                        margin: 10px;
                        margin-bottom: 15px;
                        box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.2);
                    }
                    .code:after {
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
                        background: rwfite;
                    }
                    button {
                        background: grey;
                        border: none;
                        color: white;
                        padding: 10px 20px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        cursor: pointer;
                        border-radius: 1em;
                        box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.2);
                    }
                </style>
                <script>
                function copyToClipboard(elementId) {
                    var aux = document.createElement("input");
                    aux.setAttribute("value", document.getElementById(elementId).innerText);
                    document.body.appendChild(aux);
                    aux.select();
                    document.execCommand("copy");
                    document.body.removeChild(aux);
                }
                </script>
            </head>
            <body>
                <p style='font-family: Segoe UI; text-align:center;color:bloack;'>DonutAI Preview V2 v24.02.15</p>
                <p style='font-family: Segoe UI; text-align:center;color:bloack;'>Message from Developer (Gautham Nair), DonutAI is still in Preview, it might make mistakes</p>                      
            </body>
            </html>
        """)
        
        self.msg1 = None

        self.message_entry = QTextEdit()
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon('send.png'))
        self.send_button.setStyleSheet("QPushButton {background-color: white; border-radius: 10%; padding: 15px; font-size : 20px} QPushButton:pressed {background-color: white;}")
        self.voice_button = QPushButton()
        self.voice_button.setIcon(QIcon('voice.png'))
        self.voice_button.setStyleSheet("QPushButton {background-color: white; border-radius: 10%; padding: 15px; font-size : 20px} QPushButton:pressed {background-color: white;}")
        
        # Set window title and icon
        self.setWindowTitle('DonutAI PREVIEW')
        self.setWindowIcon(QIcon('velocity.png'))
        # Create heading
        self.heading = QLabel('🍩 DonutAI <sup>Preview V2</sup>')
        self.heading.setStyleSheet("font-size: 18px; color: black;")
        self.heading.setAlignment(Qt.AlignCenter)
        self.send_button.setFixedSize(60, 60)
        self.voice_button.setFixedSize(60, 60)

        # Set styles
        self.chat_history.setStyleSheet("font-size: 20px; color: blue; background-color: white;")
        self.message_entry.setStyleSheet("font-size: 15px; color: black; background-color: lightgray;")

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
            if plain_text == "Random":
                escaped_text = json.dumps("<div class='genmessage'><div id='loading'> " + plain_text + "</div></div><br>")
            else:
                escaped_text = json.dumps("<div class='genmessage'>" + plain_text + "</div><br>")
        self.chat_history.page().runJavaScript("document.body.innerHTML += " + escaped_text + ";")
        self.scroll_to_bottom()

    def wolf(self, msg):
        try:
            client = wolframalpha.Client('UL8UPY-4EHX5683WH')
            res = client.query(msg)
            response = next(res.results).text
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>"+response+"</p>", False)
            self.append_to_chat_history("","Type")
        except:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",  False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>/!\ Could not give response </p>", "Error")
            self.append_to_chat_history("","Type")


    def record_and_process(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Recognizing..!</p>", "Listen")
            msg = r.recognize_google(audio)
            if msg == "":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Prompt cannot be empty.</p>", "Error")
                self.append_to_chat_history("", False)
                return
            elif 'weather' in msg:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>You : </p>", True)
                self.append_to_chat_history("<p class='text' style='font-family: Segoe UI; text-align:left;color:white;'>"+msg+"</p>", True)
                self.append_to_chat_history("","Type")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Fatching Latest Weather..!</p>", "Random")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
                self.append_to_chat_history("","Type")
                threading.Thread(target=self.wolf, args=(msg,)).start()
            elif msg == "Whats is time" or msg == "What is time" or msg == "what is time" or msg == "whats is time":
                strTime = time.strftime("%H:%M:%S")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The time is "+strTime+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is date" or msg == "What is date" or msg == "what is date" or msg == "whats is date":
                strDate = time.strftime("%d/%m/%Y")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The date is "+strDate+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is day" or msg == "What is day" or msg == "what is day" or msg == "whats is day":
                strDay = time.strftime("%A")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The day is "+strDay+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is month" or msg == "What is month" or msg == "what is month" or msg == "whats is month":
                strMonth = time.strftime("%B")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The month is "+strMonth+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is year" or msg == "What is year" or msg == "what is year" or msg == "whats is year":
                strYear = time.strftime("%Y")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The year is "+strYear+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is hour" or msg == "What is hour" or msg == "what is hour" or msg == "whats is hour":
                strHour = time.strftime("%H")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The hour is "+strHour+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is minute" or msg == "What is minute" or msg == "what is minute" or msg == "whats is minute":
                strMinute = time.strftime("%M")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The minute is "+strMinute+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "Whats is second" or msg == "What is second" or msg == "what is second" or msg == "whats is second":
                strSecond = time.strftime("%S")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The second is "+strSecond+"</p>", False)
                self.append_to_chat_history("","Type")
            elif msg == "log off" or msg == "Log off" or msg == "Log Off" or msg == "log Off" or msg == "Log Off" or msg == "log off":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Logging off your PC!</p>", False)
                self.append_to_chat_history("","Type")
                subprocess.call(["shutdown", "/l"])
            elif msg == "restart" or msg == "Restart":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Restarting your PC!</p>", False)
                self.append_to_chat_history("","Type")
                subprocess.call(["shutdown", "/r"])
            elif msg == "shutdown" or msg == "Shutdown":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Shutting down your PC!</p>", False)
                self.append_to_chat_history("","Type")
                subprocess.call(["shutdown", "/s"])
            elif msg == "exit":
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : Bye! You can press the 'X' or close button to close the window.</p>", False)
                self.append_to_chat_history("","Type")
            else:
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:black;'>You : </p>", True)
                self.append_to_chat_history("<p class='text' style='font-family: Segoe UI; text-align:left;color:black;'>"+msg+"</p>", True)
                self.append_to_chat_history("","Type")
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
                self.append_to_chat_history("","Type")
                threading.Thread(target=self.generate_response, args=(msg,)).start()
        except sr.UnknownValueError:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>Sorry, I couldn't understand, or didnt hear what you said. Please try again!</p>", "Error")
            return ""
        except sr.RequestError as e:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>Sorry, I couldn't understand, or didnt hear what you said. Please try again!</p>", "Error")
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
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>Prompt cannot be empty.</p>", "Error")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            return
        elif 'weather' in msg:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:black;'>You : </p>", True)
            self.append_to_chat_history("<p class='text' style='font-family: Segoe UI; text-align:right;color:white;'>"+msg+"</p>", True)
            self.append_to_chat_history("","Type")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Fatching Latest Weather..!</p>", "Random")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.wolf, args=(msg,)).start()
        elif msg == "Whats is time" or msg == "What is time" or msg == "what is time" or msg == "whats is time":
            strTime = time.strftime("%H:%M:%S")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",  False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The time is "+strTime+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is date" or msg == "What is date" or msg == "what is date" or msg == "whats is date":
            strDate = time.strftime("%d/%m/%Y")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The date is "+strDate+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is day" or msg == "What is day" or msg == "what is day" or msg == "whats is day":
            strDay = time.strftime("%A")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The day is "+strDay+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is month" or msg == "What is month" or msg == "what is month" or msg == "whats is month":
            strMonth = time.strftime("%B")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The month is "+strMonth+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is year" or msg == "What is year" or msg == "what is year" or msg == "whats is year":
            strYear = time.strftime("%Y")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The year is "+strYear+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is hour" or msg == "What is hour" or msg == "what is hour" or msg == "whats is hour":
            strHour = time.strftime("%H")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The hour is "+strHour+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is minute" or msg == "What is minute" or msg == "what is minute" or msg == "whats is minute":
            strMinute = time.strftime("%M")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The minute is "+strMinute+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
        elif msg == "Whats is second" or msg == "What is second" or msg == "what is second" or msg == "whats is second":
            strSecond = time.strftime("%S")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",   False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>The second is "+strSecond+"</p>", False)
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
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
        else:
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:right;color:black;'>You : </p>", True)
            self.append_to_chat_history("<p class='text' style='font-family: Segoe UI; text-align:left;color:black;'>"+msg+"</p>", True)
            self.append_to_chat_history("","Type")
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:center;color:green;'>Generating Answers..!</p>", "Random")
            self.append_to_chat_history("","Type")
            self.message_entry.clear()
            threading.Thread(target=self.generate_response, args=(msg,)).start()
            self.message_entry.clear()

    def generate_response(self, msg):
        try:
            chat.send_message(msg)
            print(chat.last.text)
            if "```" in chat.last.text:
                parts = chat.last.text.split("```")
                full_message = "<p style='font-family: Segoe UI; text-align:left;color:black;'>DonutAI : (This is AI generated code and might be wrong, verify it before usage.)</p>"
                is_code = False
                for part in parts:
                    if is_code:
                        lines = part.split("\n")
                        if len(lines) > 1:
                            language_name = '<strong>' + lines[0] + '</strong>'
                            language_name = language_name.replace("c++","C++")
                            language_name = language_name.replace("c#","C#")
                            language_name = language_name.replace("c","C")
                            language_name = language_name.replace("python","Python")
                            language_name = language_name.replace("java","Java")
                            language_name = language_name.replace("javascript","JavaScript")
                            language_name = language_name.replace("html","HTML")
                            language_name = language_name.replace("css","CSS")
                            language_name = language_name.replace("php","PHP")
                            language_name = language_name.replace("sql","SQL")
                            language_name = language_name.replace("ruby","Ruby")
                            language_name = language_name.replace("perl","Perl")
                            language_name = language_name.replace("bash","Bash")
                            language_name = language_name.replace("r","R")
                            language_name = language_name.replace("matlab","Matlab")
                            language_name = language_name.replace("swift","Swift")
                            language_name = language_name.replace("go","Go")
                            language_name = language_name.replace("scala","Scala")
                            language_name = language_name.replace("kotlin","Kotlin")
                            language_name = language_name.replace("rust","Rust")
                            language_name = language_name.replace("typescript","TypeScript")
                            language_name = language_name.replace("dart","Dart")
                            language_name = language_name.replace("haskell","Haskell")
                            language_name = language_name.replace("lua","Lua")
                            language_name = language_name.replace("julia","Julia")
                            language_name = language_name.replace("coffeescript","CoffeeScript")
                            language_name = language_name.replace("elixir","Elixir")
                            language_name = language_name.replace("clojure","Clojure")
                            language_name = language_name.replace("groovy","Groovy")
                            language_name = language_name.replace("ocaml","OCaml")
                            language_name = language_name.replace("erlang","Erlang")
                            language_name = language_name.replace("fortran","Fortran")
                            language_name = language_name.replace("assembly","Assembly")               
                            code = '<button onclick="copyToClipboard(\'code\')">Copy</button><pre id="code"><code class="code">' + html.escape('\n'.join(lines[1:])) + '</code></pre>'
                            part = language_name + code
                        else:
                            part = '<pre><code>' + html.escape(part) + '</code></pre>'
                    else:
                        part = markdown.markdown(part)
                    full_message += "<p style='font-family: Segoe UI; text-align:left;color:black;'>"+part+"</p><br>"
                    is_code = not is_code
                self.append_to_chat_history(full_message, False)
                self.append_to_chat_history("","Type")
                self.reply_mode = True
            else:
                response_text = chat.last.text
                response_text = markdown.markdown(response_text)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>", False)
                self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>"+response_text+"</p>", False)
                self.append_to_chat_history("","Type")
                self.reply_mode = True
        except Exception as e:
            print(e)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>🍩 DonutAI : </p>",  False)
            self.append_to_chat_history("<p style='font-family: Segoe UI; text-align:left;color:black;'>Could not give response </p>", "Error")
            self.append_to_chat_history("","Type")

app = QApplication(sys.argv)
window = ChatbotGUI()
window.show()
sys.exit(app.exec_())