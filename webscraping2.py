import urllib2
from bs4 import BeautifulSoup
import string
import pandas as pd

wiki = "https://en.wikipedia.org/wiki/List_of_state_and_union_territory_capitals_in_India"

page = urllib2.urlopen(wiki)
soup = BeautifulSoup(page)

print soup.prettify()

soup.h1
soup.title
soup.append

links = soup.find_all("a")
link2 = [link.get("href") for link in links]
for link in link2:
    print link

all_tables = soup.find_all("table")
for table in all_tables:
    print table
right_table = soup.find('table', class_ = 'wikitable sortable plainrowheaders') 

A = []
B = []
C = []
D = []
E = []
F = []
G = []

for row in right_table.findAll('tr'):
    cells = row.findAll('td')
    states = row.findAll('th')
    if len(cells) == 6:
        A.append(cells[0].find(text = True))
        B.append(states[0].find(text=True))
        C.append(cells[1].find(text = True))
        D.append(cells[2].find(text = True))
        E.append(cells[3].find(text = True))
        F.append(cells[4].find(text = True))
        G.append(cells[5].find(text = True))

df = pd.DataFrame({'Number': A, 'State/UT': B, 'Admin_capital': C, 'Legislative_Capital': D,
    'Judiciary_Capital': E, 'Year_Capital': F, 'Former_capital': G})

df

lets = [let for let in string.uppercase[:7]]
print lets
for let in lets:
    let = []

############## to deal with  404 Errors #############
try:
    print urllib2.urlopen(url).read()
except urllib2.HTTPError, e:
    print e.code
    print e.msg
    print e.headers
    x = e.fp.read()
print x