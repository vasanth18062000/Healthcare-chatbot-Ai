from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
import pickle
import nltk 
import numpy as np
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import speech_recognition as sr
import pyttsx3

intents = json.loads(open('intents2.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('labels.pkl','rb'))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    print(return_list)
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res



#Creating GUI with tkinter
import tkinter
from tkinter import *
import tkinter as tk


def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
        global res

        res = chatbot_response(msg)
        ChatLog.insert(END, "Bot: " + res + '\n\n')

        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)


#convert text to audio
def aud():
        text_speech= pyttsx3.init()
        answer= res
        text_speech.say(answer)
        text_speech.runAndWait()

# Initialize the function for converting audio to text
def convert_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        msg = recognizer.recognize_google(audio)
        #text_area.insert(tk.END, 'You: ' + message + '\n')
    except:
        EntryBox.insert(tk.END, "Sorry, I didn't catch that. Could you please try again?\n")

    if msg != '':
        EntryBox.config(state=NORMAL)
        EntryBox.insert(END, msg + '\n\n')    
base = Tk()
base.title("🧑‍⚕️BSV Bot😷")#by default
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

#Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)

ChatLog.config(state=DISABLED)

#Binding scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

#Create Button to send message
audioButton = Button(font=("Verdana",12,'bold'), text="mic🎙️", width="9", height=5,
                    bd=0, bg="#32de97", activebackground="blue",fg='#ffffff',
                    command= convert_audio )
SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="9", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
                    command= send )

convert_button = Button(text="🔈🔉🔊", command=aud)
convert_button.grid(row=1, column=0, columnspan=2)
#Create the box to enter message
EntryBox = Text(base, bd=0, bg="white",width="36", height="50", font="Arial")#type pandra place
#EntryBox.bind("<Return>", send)


#Place all components on the screen;you can change its heightand width
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=375, width=370)
EntryBox.place(x=120, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=45)
audioButton.place(x=6, y=450, height=45)
convert_button.place(x=6,y=340,height=30)
base.mainloop()