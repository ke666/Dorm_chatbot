import requests, json
from bs4 import BeautifulSoup
from flaskext.mysql import MySQL

def dbconfig(app, code):
    mysql = MySQL()
    app.config["MYSQL_DATABASE_USER"]='root'
    app.config["MYSQL_DATABASE_PASSWORD"]='1710725'
    app.config["MYSQL_DATABASE_DB"]='thesis'
    app.config["MYSQL_DATABASE_HOST"]='localhost'
    mysql.init_app(app)
    connect = mysql.connect()
    curr = connect.cursor()
    check = curr.execute("SELECT * FROM thesis.notification WHERE type = %s", code)
    record = curr.fetchall()
    url = []
    title = []
    if check > 0 :
        for i in record:
            if i[3] != None:

                url.append(i[3])
                title.append(i[2])
    return url, title


def get_pdt(app, code):
    url, title = dbconfig(app,code)
    data = []
    for i in url:
        r = requests.get(i)
        s = BeautifulSoup(r.content, "html.parser")
        d = str(s.select('div#content > p, table'))
        d = d[1:len(d)-2]
        data.append(str(d))
    jsonfile = {"data":data, "titles":title}
    return json.dumps(jsonfile,ensure_ascii=False)

def get_bomon():
    response = requests.get("http://dte.dee.hcmut.edu.vn/vi.html")
    soup = BeautifulSoup(response.content, "html.parser")
    titles = soup.find('a', attrs={"title": "Thông báo"}).parent
    titles = titles.select('h4.nspHeader > a')
    titles = titles[0:5]
    links = ['http://dte.dee.hcmut.edu.vn' + link.attrs["href"] for link in titles]
    data = []
    for i in links:
        html_data = []
        r = requests.get(i)
        s = BeautifulSoup(r.content, "html.parser")
        d = s.select('div.item-page > div')[1:]
        for j in d:
            html_data.append(str(j))
        data.append(html_data)

    title_links = [link.attrs["title"].upper() for link in titles]
    jsonfile = {"data":data, "titles":title_links}
    return json.dumps(jsonfile,ensure_ascii=False)

def get_bieumau_pdt():
    response = requests.get("http://www.aao.hcmut.edu.vn/index.php?route=catalog/chitietsv&path=91&tid=97")
    soup = BeautifulSoup(response.content, "html.parser")
    for a in soup.findAll('img'):
        a.attrs["src"] = "http://www.aao.hcmut.edu.vn/image/data/icon/pdf_download.png"
    
    d = str(soup.select('div#content > p, table'))
    d = d[1:len(d)-2]
    data = []
    data.append(str(d))
    jsonfile = {"data":data}
    return json.dumps(jsonfile,ensure_ascii=False)

def get_quyche():
    response = requests.get("http://www.aao.hcmut.edu.vn/index.php?route=catalog/chitietsv&path=90&tid=1658")
    soup = BeautifulSoup(response.content, "html.parser")
    for a in soup.findAll('img'):
        a.decompose()
    for a in soup.findAll('li'):
        a.attrs["class"] = "list-group-item list-group-item-action"

    for a in soup.findAll('h33'):
        a.attrs["class"] = "list-group-item list-group-item-action list-group-item-info question"
    for a in soup.findAll('div',class_="answer"):
        a.attrs["style"] = "display:none;"
    
    
    d = str(soup.select('ul#vtp_question_answer'))
    d = d[1:len(d)-2]
    
    data = []
    data.append(str(d))
    jsonfile = {"data":data}
    return json.dumps(jsonfile,ensure_ascii=False)
