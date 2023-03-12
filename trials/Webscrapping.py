import requests
from bs4 import BeautifulSoup

query = "Face+Recognition+System+using+Machine+Learning"
res = list()
for i in range(0, 100, 10):
  headers = {'User-Agent':'Mozilla/5.0'}
  url = f'https://scholar.google.com/scholar?start={i}&q={query}&hl=en&as_sdt=2007&as_ylo=2000&as_yhi=2023'
  print(url)
  # url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={query}&btnG="

  # response = requests.get(url, headers = headers)
  response = requests.get(url)
  #print("====================================================================================================================================")
  soup = BeautifulSoup(response.content, "html.parser")
  # print(soup.prettify())
  print("====================================================================================================================================")
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
print()
print()
print()
for i in range(len(res)):
    print(res[i])
    print("=============================================================================================================================================")