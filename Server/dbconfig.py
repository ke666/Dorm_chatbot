from flask import Flask, request, url_for, redirect, render_template
from flaskext.mysql import MySQL
import re,datetime

def dbconfig(app):
    mysql = MySQL()
    app.config["MYSQL_DATABASE_USER"]='root'
    app.config["MYSQL_DATABASE_PASSWORD"]='1710725'
    app.config["MYSQL_DATABASE_DB"]='thesis'
    app.config["MYSQL_DATABASE_HOST"]='localhost'
    mysql.init_app(app)
    return mysql
#==================================================================================
def subconfig(subjectid,app,condition,course,mssv):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    flag = 0
    if len(subjectid)>6:
        subid = re.findall(r"[\w']+", subjectid)
        for i in subid:
            check = curr.execute("CALL CTDT(%s,%s)",(course,i))
            if check == 1:
                subid = i
                flag = 1
                break
        if flag == 0:  
            return "Môn học này không thuộc CTDT khóa của bạn bạn nhé !"
    else:
        subid = subjectid
    
    if condition == 'credict':
        check = curr.execute("SELECT name, id, credict FROM subject WHERE id = %s",subid)
        if check == 1:
            record = curr.fetchall()
            for i in record:
                return 'Môn ' + i[0] + ' ( ' + i[1] + ' ) có ' + i[2] + ' tín chỉ bạn nhé !'
    elif condition == 'can_register':
        check = curr.execute("CALL CanDKMH(%s,%s)",(mssv, subid))
        record = curr.fetchall()
        if check == 0:
            return 'Bạn không thể đăng ký môn học này bạn nhé !'
        else:
            return 'Bạn đủ điều kiện đăng ký môn học này bạn nhé !'
    else:
        check = curr.execute("CALL getSubRequest(%s,%s)",(subid,condition))
        response = ''
        subject = ''
        if check > 0:
            record = curr.fetchall()
            for i in record:
                if i[4]=='-':
                    if condition == 'HT':
                        response = 'Môn ' + str(i[1]) + ' không có môn học trước bạn nhé !'
                    elif condition == 'SH':
                        response = 'Môn ' + str(i[1]) + ' không có môn song hành bạn nhé !'
                    else:
                        response = 'Môn ' + str(i[1]) + ' không có môn tiên quyết bạn nhé !'
                    return response
                else:
                    subject = subject + str(i[4]) + ' ( '
                    if (i[3]!='------'):
                        subject = subject + str(i[2]) + ' hoặc ' + str(i[3]) + ' ); '
                    else:
                        subject = subject + str(i[2]) + ' );'
            subject = subject[:-1]
            if condition == 'HT':
                response = 'Môn ' + str(i[1]) + ' có môn học trước là ' + subject + ' bạn nhé !'
            elif condition == 'SH':
                response = 'Môn ' + str(i[1]) + ' có môn song hành là ' + subject + ' bạn nhé !'
            else:
                response = 'Môn ' + str(i[1]) + ' có môn tiên quyết là ' + subject + ' bạn nhé !'
            return response
    
    return 'Hệ thống không tìm thấy dữ liệu phù hợp ! Bạn vui lòng thử lại nhé !'

#==============================================================================================
def avstand(year,course,app):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    if year == 'CAVLV':
        check = curr.execute("CALL getEngStand(%s,3, NULL)",course)
        record = curr.fetchall()
        if check >= 1:
            for row in record:
                toeic_from = row[4]
            return 'Chuẩn anh văn nhận luận văn khóa ' + str(course) + ' là toeic ' + str(toeic_from)
    elif year == 'CAVTN':
        check = curr.execute("CALL getEngStand(%s,3, NULL)",course)
        record = curr.fetchall()
        if check >= 1:
            for row in record:
                toeic_from = row[4]
                speak_write = row[6]
            return 'Chuẩn anh văn tốt nghiệp khóa ' + str(course) + ' là toeic ' + str(toeic_from) + ' và toeic nói-viết ' + str(speak_write)
    else:
        if year == 'CAV1':
            y = 1
        elif year == 'CAV2':
            y = 2
        else:
            y = 3
        check = curr.execute("CALL getEngStand(%s,%s,NULL)",(course,y))
        record = curr.fetchall()
        if check >= 1:
            for row in record:
                toeic_from = row[4]
                sub_eng = row[5]
            return 'Chuẩn anh văn sau năm ' + str(y) + ' khóa  ' + str(course) + ' là toeic từ ' + str(toeic_from) + ' trở lên hoặc đạt môn ' + str(sub_eng)
    return 'Hiện tại hệ thống không tìm được chuẩn theo yêu cầu của bạn !'

#====================================================================================================
def toeicchange(msg,app):
    score = re.findall(r'\d+', msg)
    score_data = None
    result = ''
    if len(score)>1:
        return 'Dữ liệu điểm bạn cung cấp không đúng, vui lòng thử lại nhé !'
    else:
        score = int(score[0])
        if score >=0 and score <=990:
            mysql = dbconfig(app)
            connect = mysql.connect()
            curr = connect.cursor()
            check = curr.execute("SELECT * FROM toeic_score")
            record = curr.fetchall()
            for row in record:
                if score == row[1]:
                    score_data = [row[2],row[3],row[4],row[5]]
                    break
                elif score > row[1]:
                    score_data = [row[2],row[3],row[4],row[5]]
                else:
                    break
            if score_data == None:
                return 'Bạn không thể chuyển điểm cho cả 4 môn anh văn bạn nhé !'
            else:
                if score_data[0] != None:
                    result = result + 'Anh văn 1: ' + str(score_data[0]) 
                if score_data[1] != None:
                    result = result + '; Anh văn 2: ' + str(score_data[1]) 
                if score_data[2] != None:
                    result = result + '; Anh văn 3: ' + str(score_data[2]) 
                if score_data[3] != None:
                    result = result + '; Anh văn 4: ' + str(score_data[3])
                return result
        else:
            return 'Dữ liệu điểm bạn cung cấp không đúng, vui lòng thử lại nhé !'

#====================================================================================================
def teachinfo(teacher,app):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    check = curr.execute("SELECT * FROM infoteacher WHERE id = %s", teacher)
    record = curr.fetchall()
    result_room = ''
    result_time = ''
    if (check==0):
        return 'Thông tin giảng viên không có trong hệ thống bạn nhé !'
    else:
        for row in record:
            name = row[1]
            room = row[2]
            build = row[3]
            mail = row[4]
            date = row[5] 
            timef = row[6]
            timet = row[7]
            state = row[9]
        result_mail = 'Địa chỉ email của giảng viên '+name+' là '+ mail
        if state == 0:
            result_time = '. Tuần này thầy không tiếp sinh viên bạn nhé !'
        else:
            if room != None:
                result_room = '. Tuần này thầy sẽ tiếp sinh viên tại phòng '+ str(room) + str(build)
            if date != None and timef != None and timet != None:
                result_time = '. Bạn có thể gặp thầy vào thứ ' + str(date) + ' từ ' + str(timef) + ' đến ' + str(timet)
    return result_mail + result_room + result_time
#==============================================================================
def svstand(sv,app):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    if sv == 'CSV1':
        k = 1
    elif sv == 'CSV2':
        k = 2
    elif sv == 'CSV3':
        k = 3
    elif sv == 'CSV4':
        k = 4
    elif sv == 'CSV5':
        k = 5
    check = curr.execute("SELECT * FROM stu_csv WHERE years = %s", k)
    if check > 0:
        record = curr.fetchall()
        for i in record:
            return 'Chuẩn sinh viên năm ' + str(k) + ' từ ' + str(i[1]) + ' tín chỉ đến ' + str(i[2]) + ' tín chỉ bạn nhé !' 
    else :
        return 'Hiện tại hệ thống không tìm được chuẩn theo yêu cầu của bạn !'
#/////////////////////////////////////////////////////////////////////////////////////////
def gethistory(question,answer,mssv,app, time_process):
    mysql = dbconfig(app)
    connect = mysql.connect()
    curr = connect.cursor()
    time = datetime.datetime.now()
    time.strftime('%y-%m-%d %HH:%MM:%SS')
    curr.execute("INSERT INTO `user_history` VALUES (%s,%s,%s,%s,%s)",(mssv,time,question,answer, time_process))
    connect.commit()