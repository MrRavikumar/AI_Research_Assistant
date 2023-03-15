from flask import Flask, render_template, redirect,request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore,auth
import requests
from bs4 import BeautifulSoup
import json
from flask_cors import CORS
 
app = Flask(__name__)
CORS(app)
cred = credentials.Certificate("airesearch.json")
firebase_admin.initialize_app(cred)

store = firestore.client()

@app.route('/',methods = ['GET','POST'])
def home():

    return render_template("index.html")

@app.route('/signup',methods = ['GET','POST'])
def signup():
    userid=""
    message=""
    details = {}
    skills = []

    if request.method == 'POST':
        username=request.form["username"]
        useremail=request.form["email"]
        userpassword=request.form["password"]
        userconfirmp=request.form["confirmpassword"]
        
        
        try:
            print("inside")
            user=auth.create_user(
            email=useremail,
            email_verified=False,
            password=userpassword)
            message="Succesfully created user"
            userid = user.uid
        
            dit = {}
            dit['username'] = username
            dit["email"] = useremail
            dit['password'] = userpassword
            
            
            if userpassword == userconfirmp:
                store.collection('UserCollection').add(dit)
                return redirect('/login')
            else:
                message = "Password Does not Match!"
                

            
            
        except:
            message="User already exists"

        print(message)
        return jsonify("message:",message)
    
    return render_template("Signup.html")

@app.route('/login',methods = ['GET','POST'])
def login():
    dit = {}
    message = ""
    print(f"method is {request.method}")
    if request.method == 'POST':
        useremail=request.form["email"]
        userpassword=request.form["password"]
        message=""
        uid=""
        try:
            user=auth.get_user_by_email(useremail)
            message="Woohooo, succesfully logged in"

            return redirect('/searchpaper')
        except:
            message="User authentication failed"
            return jsonify("message:",message)
        

    return render_template('Login.html')

@app.route('/searchpaper',methods = ['GET','POST'])
def search():
    return render_template("searchPaper.html")

@app.route('/scrape/<string:query>',methods = ['GET','POST'])
def scrapping(query):
    # query = "Face+Recognition+System+using+Machine+Learning"
    # req  = json.loads(request.form)
    # query = req["title"]
    actualQuery = ""
    for each in query:
        if each == " ":
            actualQuery+="+"
        else:
            actualQuery+=each
    res = list()
    for i in range(0, 100, 10):
        headers = {'User-Agent':'Mozilla/5.0'}
        url = f'https://scholar.google.com/scholar?start={i}&q={actualQuery}&hl=en&as_sdt=2007&as_ylo=2000&as_yhi=2023'
    
    # url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={query}&btnG="

    # response = requests.get(url, headers = headers)
        response = requests.get(url)
    #print("====================================================================================================================================")
        soup = BeautifulSoup(response.content, "html.parser")
    # print(soup.prettify())
        # print("====================================================================================================================================")
        results = soup.find_all("div", {"class": "gs_r gs_or gs_scl"})
        for result in results:
            try:
                title = result.find("h3", {"class": "gs_rt"}).get_text().strip()
            except:
                title = ""
            
            try:
                author = result.find("div", {"class": "gs_a"} ).get_text().strip()
                    
            except:
                author = ""
                
            try:
                summary = result.find("div", {"class": "gs_rs"}).get_text().strip()
            except:
                summary = ""
                
            try:
                publisher = result.find("div", {"class": "gs_pub"}).get_text().strip()
            except:
                publisher = ""
                    
            try:
                link = result.find("a")["href"]
            except:
                link = ""
                
            res.append([title, author, summary, link])

    #print("=============================================================================================================================================")
    print(len(res))
    #print("=============================================================================================================================================")
    # print()
    # print()
    # print()

    return jsonify("res",res)
    

if __name__ == '__main__':
    app.run(host = "127.0.0.1", port = "3000",debug=True)