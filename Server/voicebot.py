import speech_recognition
from gtts import gTTS
import os, string
import playsound,chatprocess
from datetime import date,datetime
import pyaudio
import wave

def record():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 512
    RECORD_SECONDS = 6
    WAVE_OUTPUT_FILENAME = "./static/question.wav"
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True, frames_per_buffer=CHUNK)
    print ("recording started")
    Recordframes = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        Recordframes.append(data)
    print ("recording stopped")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(Recordframes))
    waveFile.close()

def botprocess(course,mssv):
	robot_ear = speech_recognition.Recognizer()
	robot_brain = ""
	filename = "./static/question.wav"
	with speech_recognition.AudioFile(filename) as source:
		print("Robot: I'm listening")
		audio_data = robot_ear.record(source)
		you = robot_ear.recognize_google(audio_data,language='vi-VN').lower()
		print("you: " + you)
	if you != "":
		robot_brain, _ = chatprocess.chatbot_response(you,course,mssv)
	else:
		robot_brain = "Tôi không nghe được bạn nói gì ! Hãy thử lại nhé !"
	
	print("Robot: " + robot_brain)

	tts=gTTS(text=robot_brain,lang='vi',slow=False)
	tts.save("./static/answer.mp3")

def voicebot(course,mssv):
	record()
	botprocess(course,mssv)
	