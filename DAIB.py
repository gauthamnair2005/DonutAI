from tkinter import *
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import requests
import wolframalpha
import subprocess
import pyjokes
import time
import google.generativeai
from langchain.embeddings import GooglePalmEmbeddings
from langchain.llms import GooglePalm
from bs4 import BeautifulSoup
from PyInquirer import Separator, prompt
import markdown
import threading

# GUI
root = Tk()
root.title("DonutAI")

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Roboto 14"
FONT_BOLD = "Roboto 13 bold"

model_id="models/chat-bison-001"
llm=GooglePalm(google_api_key="AIzaSyCQ0Ro5YqoawhDDK0yiiceAd0ljWrwa5pw")
llm.temperature=0.7

engine = pyttsx3.init()
engine.setProperty('rate',150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(audio):                   
    engine.say(audio)
    engine.runAndWait()


def send():
	send = "You : " + e.get()
	txt.insert(END, "\n" + send)

	user = e.get().lower()

	if (user == "hello"):
		txt.insert(END, "\n" + "DonutAI : Hi there, how can I help?" + "\n")
		res_str = "Hi there, how can I help?"
		t = threading.Thread(target=speak, args=(res_str,))
		t.start()

	elif (user == "hi" or user == "hii" or user == "hiiii"):
		txt.insert(END, "\n" + "DonutAI : Hi there, what can I do for you?" + "\n")
		res_str = "Hi there, how can I help?"
		t = threading.Thread(target=speak, args=(res_str,))
		t.start()
	elif (user == "how are you"):
		txt.insert(END, "\n" + "DonutAI : I'm fine! and you" + "\n")
		res_str = "I'm fine! and you?"
		t = threading.Thread(target=speak, args=(res_str,))
		t.start()
	elif (user == "fine" or user == "i am good" or user == "i am doing good"):
		txt.insert(END, "\n" + "DonutAI : Great! how can I help you?" + "\n")
		res_str = "Great! how can I help you?"
		t = threading.Thread(target=speak, args=(res_str,))
		t.start()
	elif (user == "thanks" or user == "thank you" or user == "now its my time"):
		txt.insert(END, "\n" + "DonutAI : My pleasure !" + "\n")
		res_str = "My pleasure !"
		t = threading.Thread(target=speak, args=(res_str,))
		t.start()
	elif (user == "tell me a joke" or user == "tell me something funny" or user == "crack a funny line"):
		My_joke = pyjokes.get_joke(language="en", category="neutral")
		res_str = ''.join(map(str, My_joke))    
		txt.insert(END, "\n" + "DonutAI : " + res_str + "\n")
		t = threading.Thread(target=speak, args=(res_str,))
		t.start()
	elif (user == "" or user == " "):
		pass
	elif (user == "goodbye" or user == "see you later" or user == "see yaa"):
		txt.insert(END, "\n" + "DonutAI : Have a nice day!" + "\n")
		root.quit()

	else:
		try:
			prompt = [user]
			llm_results = llm._generate(prompt)
			res = llm_results.generations
			res_str = ''.join(map(str, res[0][0].text))
			txt.insert(END,"\n")
			txt.insert(END,"\n" + "Generating Answers..!")
			txt.insert(END, "\n")
			txt.insert(END, "\n" + "DonutAI : " + res_str)
			txt.insert(END, "\n")
			t = threading.Thread(target=speak, args=(res_str,))
			t.start()
		except:
			txt.insert(END,"\n" + "An unexpected Error Occurred.!")
	e.delete(0, END)

lable1 = Label(root, bg=BG_COLOR, fg=TEXT_COLOR, text="🍩 DonutAI PREVIEW", font=FONT_BOLD, pady=12, width=60, height=1).grid(
    row=0)
txt = Text(root, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=60)
txt.grid(row=1, column=0, columnspan=2)
scrollbar = Scrollbar(txt)
scrollbar.place(relheight=1, relx=0.974)

e = Entry(root, bg="#2C3E50", fg=TEXT_COLOR, font=FONT, width=55)
e.grid(row=2, column=0)

send = Button(root, text="Send", font=FONT_BOLD, bg=BG_GRAY,
			command=send).grid(row=2, column=1)

root.mainloop()
