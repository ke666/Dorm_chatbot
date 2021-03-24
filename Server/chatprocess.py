import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle, os
import numpy as np
from tensorflow.keras.models import load_model
import json, dbconfig, statistics
import random
from flask import Flask
from flaskext.mysql import MySQL
import matplotlib.pyplot as plt
import datetime, timeit


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower() )for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))



def predict_class(sentence, model, jsname):
    words = pickle.load(open('./words/'+jsname+'.pkl','rb'))
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    if (jsname=='switch'):
        classes = pickle.load(open('./classes/'+jsname+'.pkl','rb'))
        retest = [[i,r] for i,r in enumerate(res)]
        retest.sort(key=lambda x: x[1], reverse=True)
        res_pvar = 0
        max_pvar = max(res)
        for r in res:
            res_pvar = res_pvar + (r-max_pvar)*(r-max_pvar)
        # x=[]
        # y=[]
        # for r in retest:
        #     y.append(classes[r[0]])
        #     x.append(r[1])
        # plt.plot(x,y,'go-')
        # plt.xlabel('Probability')
        # plt.ylabel('Subject')
        # plt.show()
        # print(res_pvar/len(res))
        return res_pvar/len(res), retest[0]
    else:
        classes = pickle.load(open('./classes/'+jsname+'.pkl','rb'))
        res_pvar = 0
        max_pvar = max(res)
        for r in res:
            res_pvar = res_pvar + (r-max_pvar)*(r-max_pvar)
        return res_pvar/len(res), res, classes
    
  
    
    

def takeelelist(lists, num):
    results = []
    count = 0
    for i in lists:
        results.append(i)
        count = count + 1
        if count == num:
            break
    return results


def getResponse(ints,jsnum,course,msg, mssv):
    app = Flask(__name__)
    if ints == None:
        return 'Hệ thống không tìm thấy dữ liệu phù hợp ! Bạn vui lòng thử lại nhé !'
    if jsnum == 4:
        for i in ints:
            if (i['intent']=='HT' or i['intent']=='SH' or i['intent']=='TQ' or i['intent']=='credict' or i['intent']=='can_register'):
                condition = i['intent']
                ints.remove(i)
                for j in ints:
                    if (j['intent']!='HT' and j['intent']!='SH' and j['intent']!='TQ' and j['intent']!='credict' and j['intent']!='can_register'):
                        subjectid = j['intent']
                        if (float(j['probability'])<0.0001):
                            return 'Hệ thống không tìm thấy dữ liệu phù hợp ! Bạn vui lòng thử lại nhé !'
                        if subjectid == 'EE3333':
                            return '''Đồ án tốt nghiệp có môn học trước là các môn cơ sở ngành.Ngoài ra, để đăng ký môn này, bạn được nợ tối đa 16 tín chỉ tính theo số tín chỉ tích 
                            lũy ngành của khóa/ngành khi học đúng tiến độ. Khi tính số tín chỉ tích lũy ngành, các 
                            môn đã đăng ký học trong học kỳ chính kế trước được xem như đạt (không tính môn dự thính).'''
                        elif subjectid == 'EE4333 EE4337':
                            return dbconfig.subconfig(subjectid,app,condition,course,mssv) + '''
                                Ngoài ra, để đăng ký môn này, bạn được nợ tối đa 7 tín chỉ tính theo số tín chỉ tích 
                                lũy ngành của khóa-ngành khi học đúng tiến độ. Khi tính số tín chỉ tích lũy ngành, 
                                các môn đã đăng ký học trong học kỳ chính kế trước được xem như đạt (không tính môn dự thính) 
                                và cần phải thỏa điều kiện anh văn, ngày công tác xã hội để đăng ký môn này.'''
                        else:
                            return dbconfig.subconfig(subjectid,app,condition,course,mssv)
    elif jsnum == 3:
        for i in ints:
            if (i['intent']=='CAV1' or i['intent']=='CAV2' or i['intent']=='CAV3' or i['intent']=='CAVLV' or i['intent']=='CAVTN'):
                course = ''
                year = i['intent']
                ints.remove(i)
                for j in ints:
                    if (j['intent'] == '17' or j['intent'] == '18' or j['intent'] == '19'): 
                        course = j['intent']
                        return dbconfig.avstand(year,course,app)
            elif (i['intent']=='CSV1' or i['intent']=='CSV2' or i['intent']=='CSV3' or i['intent']=='CSV4' or i['intent']=='CSV5' ):
                sv = i['intent']
                return dbconfig.svstand(sv,app)
            elif (i['intent']=='TOEIC'):
                return dbconfig.toeicchange(msg,app)

    elif jsnum == 0:
        for i in ints:
            teacher = ints[0]['intent']
            app = Flask(__name__)
            return dbconfig.teachinfo(teacher,app)
    elif jsnum == 2:
        for i in ints:
            if (i['intent']=='greeting'):
                return '''Chào bạn ! Mình là Chatbot hỗ trợ tư vấn học tập sinh viên ! Mình có thể giúp gì cho bạn ?'''
            elif (i['intent']=='goodbye'):
                return '''Tạm biệt bạn ! Nếu có gì thắc mắc, bạn cứ tìm đến Chatbot nhé !'''
            elif (i['intent']=='thanks'):
                return '''Chúng tôi luôn sẵn sàng giải đáp thắc mắc cho cậu !'''
    
    elif jsnum ==1:
        return ints[0]['intent']
    else:
        return 'Hiện tại Bot chưa hiểu yêu cầu của bạn ! Bạn vui lòng thử lại nhé !'
   


def chatbot_response(msg, course, mssv):
    start = timeit.default_timer()
    app = Flask(__name__)
    arr = os.listdir('./json file')
    arr_file_name = []
    for i in arr:
        arr_file_name.append(os.path.splitext(i)[0])
    model = load_model('./model h5/'+ 'switch' +'.h5')
    pvar, [js_num, js_prob] = predict_class(msg,model,'switch')
    print(pvar,"**********")
    if (pvar>0.5):
        jsname = arr_file_name[js_num]
        model = load_model('./model h5/'+ jsname +'.h5')
        pvar, res, classes =  predict_class(msg, model, jsname)
        print(jsname,pvar,js_prob)
        if (pvar>0.25):
            retest = [[i,r] for i,r in enumerate(res)]
            retest.sort(key=lambda x: x[1], reverse=True)
            for r in retest:
                print("intent: "+classes[r[0]]+" "+str(r[1]))
            ints = []
            for r in retest:
                ints.append({"intent": classes[r[0]], "probability": str(r[1])})
            answer = getResponse(ints,js_num,course,msg,mssv)
        else:
            answer = getResponse(None,None,course,msg,mssv)
    else:
        answer =  getResponse(None,None,course,msg,mssv)
    stop = timeit.default_timer()
    dbconfig.gethistory(msg,answer,mssv,app, stop-start)
    return answer, js_num