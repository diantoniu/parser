from bs4 import BeautifulSoup
import requests, os, urllib
import json


class Parser:
    url = 'https://nuft.edu.ua/'
    urlUniv = 'https://nuft.edu.ua/pro-universitet/navchalni-pidrozdily/instytuty-fakultety/'
    urlTeach = '?active=vykladackyi-sklad-ktcipv'
    degree = {0: 'викладач', 1: 'старший викладач', 2: 'доцент', 3: 'професор', 4: 'асистент'}
    result = []
    imgFolder = 'teachers/img/'

    def __init__(self):
        if not os.path.exists(self.imgFolder):
            os.makedirs(self.imgFolder)

    def parseHtml(self, url):
        page = requests.get(url)
        return BeautifulSoup(page.text, 'html.parser')

    def parseNuft(self):
        self.parseFaculties()
        with open('nuft.json', 'w') as outfile:
            json.dump(self.result, outfile, ensure_ascii=False)

    def parseFaculties(self):
        soup = self.parseHtml(self.urlUniv)
        for faculty in soup.find_all('div', {'class': 'content-fak'}):
            self.parseDepartments(faculty)

    def parseDepartments(self, htmlFaculty):
        divDepartments = htmlFaculty.find('div', {'class': 'content-fak-min'})
        for dep in divDepartments.find_all('li'):
            urlDep = dep.find(href=True)['href']
            urlTeachers = self.url + urlDep + self.urlTeach
            self.parseTeachers(self.parseHtml(urlTeachers))

    def parseTeachers(self, htmlTeachers):
        teachers = htmlTeachers.find('ul', {'class': 'people-list'})
        for teacher in teachers.find_all('li'):
            self.parseTeacher(teacher)

    def parseTeacher(self, htmlTeacher):
        # name
        name = htmlTeacher.find('p', {'class': 'name'}).text.split(' ')
        last_name = name[0]
        first_name = name[1]
        middle_name = name[2]

        # img
        img = ''
        try:
            imgUrl = urllib.parse.quote(self.url + htmlTeacher.find('img')['src'], safe=':/')
            img = self.imgFolder + imgUrl.split('/')[-1]
            urllib.request.urlretrieve(imgUrl, img)
        except:
            pass

        # degree
        position = htmlTeacher.find('p', {'class': 'position'}).text
        degree = self.getDegree(position)

        # result
        teachRes = {'last_name': last_name, 'first_name': first_name, 'middle_name': middle_name, 'img': img,
                    'degree': degree}

        # apppend to res array
        self.result.append(teachRes)

    def getDegree(self, position):
        degree = 5
        position = position.lower()
        for i in range(0, 5):
            if self.degree.get(i) in position:
                degree = i
        return degree


# parse data to nuft.json
parser = Parser()
parser.parseNuft()

# load json data
# with open('nuft.json') as f:
#     data = json.load(f)
#     print(data)
