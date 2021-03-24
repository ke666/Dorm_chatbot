import speech_recognition
from gtts import gTTS
import os, string
import playsound,chatprocess
import socket
import time, voicebot

host = ''
port = 5560

def setupServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created.")
    try:
        s.bind((host, port))
    except socket.error as msg:
        print(msg)
    print("Socket bind comlete.")
    return s

def setupConnection():
    try:
        s.listen(1)
    except:
        return -1
    conn, address = s.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))
    return conn



def sendToClient(conn):
    f = open('./static/answer.mp3','rb')
    l = f.read(1024)
    while (l):
       conn.send(l)
       l = f.read(1024)
    conn.send(str.encode("#"))
    f.close()
     
    print('Done sending')

def recvFrClient(conn):
    with open('./static/question.wav', 'wb') as f:
        while True:
            data = conn.recv(1024)
            try:
                abs = data[-1].to_bytes(2, 'big').decode('utf-8')
                # print(abs)
                if "7" in abs:
                    return "17"
                    break
                if "9" in abs:
                    return "19"
                    break       
            except:
                #print("khong decode")
                pass
   
            f.write(data)

        f.close()
        
    print('Successfully get the file from client')

def voiceProcess(course):
    voicebot.botprocess(course,1000000)

if __name__=='__main__':
    s = setupServer()
    while(True):
        conn = setupConnection()
        recvValue= recvFrClient(conn)
        if recvValue == "17":
            try:
                voiceProcess(17)
                sendToClient(conn)
            except:
                f = open('./static/error.mp3','rb')
                l = f.read(1024)
                while (l):
                    conn.send(l)
                    l = f.read(1024)
                    conn.send(str.encode("#"))
                    f.close()
                print('Done sending')


        if recvValue == "19":
            try:
                voiceProcess(19)
                sendToClient(conn)
            except:
                f = open('./static/error.mp3','rb')
                l = f.read(1024)
                while (l):
                    conn.send(l)
                    l = f.read(1024)
                    conn.send(str.encode("#"))
                    f.close()
                print('Done sending')
        print("======================================================================")
        