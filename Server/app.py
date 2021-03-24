from flask import Flask, request, url_for, redirect, render_template, request, abort, send_from_directory
from flaskext.mysql import MySQL
import time, chatprocess, dbconfig, voicebot, os, json, base64, checkaccount, notification, datetime

app = Flask(__name__)
mysql = dbconfig.dbconfig(app)
connect = mysql.connect()
curr = connect.cursor()
#==============================================================================================
@app.route('/')
def login():
    return render_template('login.html')



@app.route('/bot', methods=['POST'])
def logcheck():
    username = request.form['username']
    password = request.form['password']
    state, check, messenger = checkaccount.check_login(username,password,curr)
    if (state == True and check == 1):
        return render_template('home.html',name=messenger[0],mssv=messenger[1],course=messenger[2])
    elif (state == True and check == 2):
        return render_template('gv.html',name=messenger)
    else:
        return render_template('login.html', fail = messenger)


@app.route('/logcheckapp', methods=['POST'])
def logcheckapp():
    connect = mysql.connect()
    curr = connect.cursor()
    username = request.form['username']
    password = request.form['password']
    state, check, messenger = checkaccount.check_login(username,password,curr)
    if (state == True and check == 1):
        return json.dumps({"state":"true", "name":messenger[0],"mssv":messenger[1],"course":messenger[2]})
    elif (state == True and check == 2):
        return json.dumps({"state":"true", "name":messenger[0]})
    else:
        return json.dumps({"state":"false", "error": messenger})

#=========================================================================================


#=========================================================================================
@app.route('/getbot')
def get_bot_response():
    userText = request.args.get('msg')
    course = request.args.get('course')
    mssv = request.args.get('mssv')
    answer, type_num =  chatprocess.chatbot_response(userText,course,mssv)
    data = {'answer': answer, 'type':type_num}
    return json.dumps(data, ensure_ascii=False)

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@app.route("/voicebot")
def get_record():
    course = request.args.get('course')
    mssv = request.args.get('mssv')
    voicebot.voicebot(course,mssv)
    id_file = dir_last_updated('./static')
    return id_file


@app.route('/uploadface', methods=['POST'])
def upload_files():
    upload_file = request.form['image']
    img = base64.b64decode(upload_file)
    with open('./imagedownload/FaceImage.jpg', 'wb') as f:
        f.write(img)
    return "Image is loaded !"

#=============================================================================================
@app.route('/getscore', methods=['GET'])
def getscore():
    mssv = request.args.get('mssv')
    check = curr.execute("CALL getTBM(%s)", mssv)
    record = curr.fetchall()
    if (check>0):
        for row in record:
            state = row[0]
        state = eval(state)
        check = curr.execute("SELECT tbtl, credict, toeic, csv FROM student WHERE mssv = %s", mssv)
        record = curr.fetchall()
        if check>0:
            for row in record:
                data =  "{'TBTL': " + str(row[0]) + ", 'credit': " + str(row[1]) + "}"
        data = eval(data)
        state.append(data)
        return json.dumps(state, ensure_ascii=False)
    else:
        return "Fail to connect !"
#=============================================================================================
@app.route('/closesql')
def closesql():
    curr.close()
    connect.close()


@app.route('/return-files/<path:path>')
def get_files(path):
    DOWNLOAD_DIRECTORY = "./tailieu"
    try:
        return send_from_directory(DOWNLOAD_DIRECTORY, path, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/getpdt')
def getpdt():
    app = Flask(__name__)
    code = request.args.get('code')
    return notification.get_pdt(app,code)

@app.route('/getbomon')
def getbomon():
    return notification.get_bomon()

@app.route('/getbieumau')
def getbieumau():
    return notification.get_bieumau_pdt()

@app.route('/getquyche')
def getquyche():
    return notification.get_quyche()

@app.route('/getdcmh')
def getdcmh():
    check = curr.execute("CALL getSubject()")
    record = curr.fetchall()
    if (check>0):
        for row in record:
            data = row[0]
        data = eval(data)
        return json.dumps({"data":data}, ensure_ascii=False)
    else:
        return json.dumps({"data":"Fail to connect !"}, ensure_ascii=False)

@app.route('/getmail')
def getemail():
    check = curr.execute("SELECT JSON_ARRAYAGG(JSON_OBJECT('id',T.ID,'name', T.name)) FROM (SELECT ID, name FROM thesis.infoteacher) AS T;")
    record = curr.fetchall()
    if (check>0):
        for row in record:
            data = row[0]
        data = eval(data)
        return json.dumps({"data":data}, ensure_ascii=False)
    else:
        return json.dumps({"data":"Fail to connect !"}, ensure_ascii=False)




@app.route('/sendmail', methods=["POST"])
def sendmail():
    fromid = request.form['fromid']
    toid = request.form['toid']
    content = request.form['contentmail']
    subject = request.form['subject']
    time = datetime.datetime.now()
    time.strftime('%y-%m-%d %HH:%MM:%SS')
    curr.execute("CALL addEmail(%s,%s,%s,%s,%s);",(time,fromid,toid,subject,content))
    connect.commit()
    return 'Tin nhắn đã được gửi thành công !'

@app.route('/showmail')
def showmail():
    mssv = request.args.get('mssv')
    curr.execute("CALL getEmailContent(%s)",mssv)
    record = curr.fetchall()
    for i in record:
        data = i[0]
    data = eval(data)
    return json.dumps({"data":data},ensure_ascii=False)

if __name__ == '__main__':
    app.run(host='172.20.10.12', port=8000, debug=True)
    
    #app.run(host='localhost', port=8000, debug=True)
    #app.run(host='192.168.100.10', port=8000, debug=True)
