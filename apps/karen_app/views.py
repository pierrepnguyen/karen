from django.shortcuts import render, HttpResponse, redirect
import speech_recognition as sr
from gtts import gTTS
from time import ctime
import time
from weather import Weather
import os
import re
import requests
import pafy
from bs4 import BeautifulSoup
import urllib.request
import webbrowser
import datetime
import youtube_dl
import wikipedia
from googlesearch import search

def index(request):
  return render(request, "karen_app/index.html")

def speak(phrase, request):
  print(phrase)
  tts = gTTS(text=phrase, lang='en')
  tts.save("audio.mp3")
  os.system("mpg321 audio.mp3")

def greeting(request):
  hour = int(datetime.datetime.now().hour)
  if hour>=0 and hour<12:
      speak("Good Morning!", request)
  elif hour>=12 and hour<18:
    speak("Good Afternoon!", request)   
  else:
    speak("Good Evening!", request)  
  speak("I'm Karen. How may I help you?", request)

# def takeCommand():
#   # Record Audio
#   r = sr.Recognizer()
#   with sr.Microphone() as source:
#     print("Say something!")
#     audio = r.listen(source)

#   # Speech recognition using Google Speech Recognition
#   data = ""
#   try:
#     data = r.recognize_google(audio)
#     print("You said: " + data)
#   except sr.UnknownValueError:
#     print("Google Speech Recognition could not understand audio")
#   except sr.RequestError as e:
#     print("Could not request results from Google Speech Recognition service; {0}".format(e))

#   return data

def karen(request):
    command = request.POST['web_voice_phrase']
    PLAY_SONG_REGEX = re.compile(r'(play song)')
    WEATHER_REGEX_COMMAND = re.compile(r'(current weather)')
    WHOIS_REGEX = re.compile(r'(who is)')

    if 'search' in command:
      reg_ex = re.search(r'(?<=\bsearch\s)(.*)', command)
      print(reg_ex)
      if reg_ex:
        domain = reg_ex.group(1)
        new = 2
        tabUrl = "https://google.com/?#q="
        term = domain
        webbrowser.open(tabUrl+term, new = new, autoraise=True)
        speak("i opened your results in a new page! your welcome!", request)
        print('Done!')
        return redirect("/")
      else:
        pass
        return redirect("/")

    elif "hey" in command:
      speak("hey", request)
      return redirect("/")
    
    elif "hello" in command:
      speak("Hello!", request)
      return redirect("/")

    elif "I love you" in command:
      speak("I love you too", request)
      return redirect("/")

    elif "how are you" in command:
      speak("i'm doing fine, thanks for asking", request)
      return redirect("/")

    elif 'goodbye' in command:
      speak('It was a pleasure assisting you!', request)
      return redirect("/")

    elif 'stop' in command:
      request.session['style'] = "display:none;"
      if 'url' in request.session:
        del request.session['url']
      speak("stopping song", request)

    # test: "open website yahoo.com"
    elif 'open' in command:
      reg_ex = re.search('open (.+)', command)
      if reg_ex:
        domain = reg_ex.group(1)
        url = 'https://www.' + domain
        webbrowser.open(url)
        print('Done!')
        return redirect("/")
      else:
        pass
        return redirect("/")

    elif not hasattr(command, 'status_code'):

      if PLAY_SONG_REGEX.search(command.lower()):
        SONG_REGEX = re.compile(r'(?<=\bsong\s)(.*)')            
        song = ""
        if SONG_REGEX.search(command.lower()):
          song_regex_result = SONG_REGEX.search(command.lower())
          song = song_regex_result.group(0)
        textToSearch = song
        query = urllib.parse.quote(textToSearch)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
          video = 'https://www.youtube.com' + vid['href']
          break
        url = video
        video = pafy.new(url)
        best = video.getbest()
        playurl = best.url
        request.session['url'] = playurl
        request.session['style'] = "display:none;"
        speak("Playing song", request)
        return redirect("/")

      # test: "current weather in los angeles"
      if WEATHER_REGEX_COMMAND.search(command.lower()):
        WEATHER_CITY_REGEX = re.compile(r'(?<=\bweather in\s)(.*)')
        city = "los angeles"
        if WEATHER_CITY_REGEX.search(command.lower()):
          weather_regex_result = WEATHER_CITY_REGEX.search(command.lower())
          city = weather_regex_result.group(0)
          try:
            obs = owm.weather_at_place(city)
            # obs = owm.weather_at_id(2643741)
            w = obs.get_weather()
            temp = w.get_temperature('fahrenheit')
            status = w.get_status()
            weatherimage = w.get_weather_icon_url()
            request.session["weatherimage"] = weatherimage
            # print(request.session["weatherimage"])
            Phrase.objects.create(content=weatherimage)
            request.session["command_weather"] = "current weather in " + city + " is " + str(
              status) + " with a temerature of " + str(temp["temp"]) + " degrees"
            print(temp)
            speak("current weather in " + city + " is " + str(status) +
              " with a temperature of " + str(temp["temp"]) + " degrees", request)
            return redirect("/")                    
          except:
            speak("I could not find your " + city, request)
            return redirect("/")

      # test: "who is aubrey graham"
      if WHOIS_REGEX.match(command.lower()):
        PERSON_REGEX = re.compile(r'(?<=\bwho is\s)(.*)')
        name = "bob ross"
        if PERSON_REGEX.search(command.lower()):
          regex_person_result = PERSON_REGEX.search(command.lower())
          name = regex_person_result.group(0)
          try:
            speak(wikipedia.summary(name, sentences=1), request)
            return redirect("/")
          except:
            speak("No information on " + name, request)
            return redirect("/")

# initialization
# time.sleep(1)
# if __name__ == "__main__":
#   greeting()
#   while True:
#     data = takeCommand()
#     voice(data)