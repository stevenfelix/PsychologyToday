 
//*[@id="profHdr"]/div/div[1]/h2/span[1]/button/span
//*[@id="profHdr"]
## method 2
//*[@id="profile-content"]/div/div[1]/div[2]/div

#soup = BeautifulSoup(page)
#type(str(soup.contents[1])) # string
#soupStr = str(soup.contents[1])

# requests
page = requests.get(ur)
page.status_code

type(page)
type(page.content) # string = good for xlml
type(page.text) # lxml doesn't like this bcuz returns unicode

## wikipedia example

url = "https://en.wikipedia.org/wiki/List_of_state_and_union_territory_capitals_in_India"
page = requests.get(url)
tree = html.fromstring(page.content)
heading = tree.xpath('//*[@id="firstHeading"]/text()')
heading

h1s = tree.xpath('//h1/text()')
h1s
