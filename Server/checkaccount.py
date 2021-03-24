import dbconfig, flask
def check_login(username,password,curr):
    app = flask.Flask(__name__)
    check = curr.execute("CALL Login(%s, %s)", (username, password))
    if (check == 1):
        record = curr.fetchall()
        for i in record:
            state = i[0]
            if (state==1):
                name = i[2]
                mssv = i[1]
                course = i[3]
                clocked = i[4]
                if (clocked==1):
                    return False, -1, "Your account is blocked. Please contact to admin to get more infomation"
                else:
                    dbconfig.gethistory('LOGIN','OK',mssv,app,0)
                    return True, state, [name, mssv, course]
            elif (state==2):
                name = i[1]
                return True, state, name
    else:
        return False,-1, "The account isn't exist"
        
def check_register(data_form,curr,connect):
    #[password, passconf,email,name,username,mssv]
    password = data_form[0]
    passconf = data_form[1]
    email = data_form[2]
    name = data_form[3]
    username = data_form[4]
    mssv = data_form[5]
    error = []
    if password=='' or email=='' or name=='' or username=='' or mssv=='':
        error.append("Anything on form not be empty.")
        return False, error
    if passconf != password:
        error.append("Password confirm don't match.")
    if email.find('@') == -1:
        error.append("Email is wrong for missing '@' character.")
    if len(mssv)!=7:
        error.append("The ID student must be has 7 number digits.")
    if (len(error)==0):
        try:
            curr.execute("INSERT INTO `student`(`name`,`mssv`,`email`,`username`,`password`,`clocked`,`course`) VALUES (%s,%s,%s,%s,%s,0,'17')",
                            (name,mssv,email,username,password))
            connect.commit()
            return True, "The register is complete !"
        except:
            error.append("The email or student ID was exist !")
    return False, error





        