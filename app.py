from flask import Flask, render_template, redirect,request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore,auth
import requests
from bs4 import BeautifulSoup
import json
from flask_cors import CORS
import numpy as np
import PyPDF2
import re
import requests
import base64
import urllib.request
from PyPDF2 import PdfReader
from PIL import Image
import tensorflow_hub as hub
import io
import openai
from tqdm.auto import tqdm
from sklearn.neighbors import NearestNeighbors
 
app = Flask(__name__)
CORS(app)
cred = credentials.Certificate("airesearch.json")
firebase_admin.initialize_app(cred)
store = firestore.client()
# app.jinja_env.auto_reload = True
# app.config['TEMPLATES_AUTO_RELOAD'] = True
a = list()
class SemanticSearch:
    
    def __init__(self):
        self.use = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')
        print("module  loaded https://tfhub.dev/google/universal-sentence-encoder/4")
        self.fitted = False
    
    
    def fit(self, data, batch=1000, n_neighbors=4):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)
        self.fitted = True
    
    def get_text_embedding(self, texts, batch=1000):
        embeddings = []
        for i in tqdm(range(0, len(texts), batch)):
            text_batch = texts[i:(i+batch)]
            emb_batch = self.use(text_batch)
            embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings

def preprocess(text):
    '''
    preprocess chunks
    1. Replace new line character with whitespace.
    2. Replace redundant whitespace with a single whitespace
    '''
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text

def text_to_chunks(texts, word_length=50, start_page=1):
    '''
    convert list of texts to smaller chunks of length `word_length`
    '''
    text_toks = [t.split(' ') for t in texts]
    page_nums = []
    chunks = []
    
    for idx, words in enumerate(text_toks):
        for i in range(0, len(words), word_length):
            chunk = words[i:i+word_length]
            if (i+word_length) > len(words) and (len(chunk) < word_length) and (
                len(text_toks) != (idx+1)):
                text_toks[idx+1] = chunk + text_toks[idx+1]
                continue
            chunk = ' '.join(chunk).strip()
            chunk = f'[{idx+start_page}]' + ' ' + '"' + chunk + '"'
            chunks.append(chunk)
    return chunks

def assign_a(text_list):
    global a
    a = text_list



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

@app.route('/scrape/<string:option>/<string:initQuery>/<string:searchfactor>',methods = ['GET','POST'])
def scrapping(option, initQuery, searchfactor):
    url = ""
    res = list()
    query = ""
    for i in initQuery:
        if i == " " or i == "  ":
            query += "+"
        else:
            query += i

    search_base = {
    "All fields": "all",
    "Author": "author",
    "Title":"title",
    "Journal Reference":"journal_ref",
    "Abstract":"abstract"
    }
    
    domain = {
        "Physics": "physics",
        "Mathematics":"math",
        "Computer Science":"cs",
        "Quantitative Biology":"q-bio",
        "Quantitative Finance":"q-fin",
        "Statistics":"stat",
        "Electrical Engineering and Systems Science":"eess",
        "Economics":"econ"
    }

    url = f"https://arxiv.org/search/{domain[option]}?query={query}&searchtype={search_base[searchfactor]}&abstracts=show&order=-announced_date_first&size=50&start=0"
    

    if query != "":
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        results = soup.find_all("li", {"class": "arxiv-result"})
        for result in results:
            try:
                title = result.find("p", {"class": "title is-5 mathjax"}).get_text().strip()
            except:
                title = ""  
            try:
                init_author = result.find("p", {"class": "authors"} ).text.strip()
                author = " ".join(init_author.split())
                author = author.replace("Authors: ", "")      
            except:
                author = ""  
            try:
                summary = result.find("span", {"class": "abstract-short has-text-grey-dark mathjax"}).text.strip()
            except:
                summary = ""     
            try:
                pre_link = result.find("p", {"class": "list-title is-inline-block"})
                link = pre_link.span.a['href']
            except:
                link = ""
            res.append([title, author, summary, link])
            

    return jsonify("res",res)


@app.route('/getknowledge/<string:link>/<string:title>',methods = ['GET','POST'])
def getknowledge(link, title):
    print("start")
    openai.api_key = "openai_api_key"
    nlink = ""
    for i in link:
        if i == '_':
            nlink += '/'
        else:
            nlink += i
    page_text = ""
    pdf_summary_text = ""
    images = []
    res = []
    print(title)
    print(nlink)
    url = "https://api.meaningcloud.com/summarization-1.0"
    pdf_file = io.BytesIO(urllib.request.urlopen(nlink).read())
    reader = PyPDF2.PdfReader(pdf_file)
        
    print("Start Summarization")
    for page_num in range(len(reader.pages)):
        page_summary = ""
        page_text = reader.pages[page_num].extract_text()

        payload={
            'key': 'cff43ebd530952e1a6336c4e3fe67219',
            'txt': page_text,
            'sentences': 10
        }
        response = requests.post(url, data=payload)
        a = response.json() 
            
        if 'summary' in a:
            page_summary = a['summary']
            pdf_summary_text += page_summary + "\n \n \n \n"
        else:
            pass
    # for page_num in range(len(reader.pages)):
    #     page_text = reader.pages[page_num].extract_text().lower()
    #     response = openai.Completion.create(
    #         engine = "text-davinci-003",
    #         prompt = page_text,
    #         max_tokens=512,
    #         n = 1,
    #         stop=None,
    #         temperature=0.7,
    # )
    #     page_summary = response["choices"][0]["text"]
    #     pdf_summary_text+=page_summary + "\n"

    print("End Summarization")

    print("Start Image Extraction")

    
    for page in reader.pages:
        for image in page.images:
            image_data = base64.b64encode(image.data).decode('utf-8')
            image_format = Image.open(io.BytesIO(image.data)).format.lower()
            image_src = f"data:image/{image_format};base64,{image_data}"
            image_alt = f"PDF Image {len(images)+1}"
            images.append({"src": image_src, "alt": image_alt})
        
    res.append(title)
    res.append(pdf_summary_text)
    res.append(images)
    images = []

    print("End Image Extraction")
    
    print("Returning")
    # return jsonify(res)
    return render_template('Display_Card.html', data = res)
    
@app.route('/chatbot', methods=['GET', 'POST'])
def upload_file():
    filename = ""
    if request.method == 'POST':
        file = request.files['files']
        if file:
            filename = file.filename
            text_list = []
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                text = preprocess(text)
                text_list.append(text)
            
            assign_a(text_list)
            # return render_template('chatbot.html', filename = filename)
    return render_template('chatbot.html',  filename = filename)

@app.route('/actualchatbot', methods=['GET','POST'])
def chatbot():
    openai.api_key = "openai_api_key"
    recommender = SemanticSearch()
    
    chunks = text_to_chunks(a)
    recommender.fit(chunks)
    # Get the incoming message from the request
    question = request.json['message']
    print(question)
    # topn_chunks = recommender(question)
        # Embed the query using the same Universal Sentence Encoder as the chunks
    query_emb = recommender.use([question])[0]
    
    # Perform a nearest neighbor search to find the most similar chunks to the query
    nn_dist, nn_idx = recommender.nn.kneighbors([query_emb])
    topn_chunks = [chunks[i] for i in nn_idx[0]]
    prompt = ""
    prompt += 'search results:\n\n'
    for c in topn_chunks:
            prompt += c + '\n\n'
        
    prompt += "Instructions: Compose a comprehensive reply to the query using the search results given."\
              "Cite each reference using [number] notation (every result has this number at the beginning)."\
              "Citation should be done at the end of each sentence. If the search results mention multiple subjects"\
              "with the same name, create separate answers for each. Only include information found in the results and"\
              "don't add any additional information. Make sure the answer is correct and don't output false content."\
              "If the text does not relate to the query, simply state 'Found Nothing'. Don't write 'Answer:'"\
              "Directly start the answer.\n"
    
    prompt += f"Query: {question}\n\n"

    responsez = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = prompt,
        max_tokens=512,
        n = 1,
        stop=None,
        temperature=0.7,
    )

    response = responsez.choices[0]['text']
    # Return the response as JSON
    return jsonify({'message': response})

if __name__ == '__main__':
    app.run(host = "127.0.0.1", port = "3000",debug=True)