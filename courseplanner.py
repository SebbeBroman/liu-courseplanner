from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import os

class Course:
    def __init__(self, name, c_id, hp, block, level, link, termin="",period=""):
        self.name = name
        self.id = c_id
        self.hp = hp
        self.block = block
        self.level = level
        self.link = link
        self.termin = termin
        self.period = period

    def __str__(self):
        r = " Namn: "+ self.name + \
            " Kurskod: "+ self.id + \
            " HP: "+ self.hp + \
            " Block: "+ self.block + \
            " Nivå: "+ self.level + \
            " Länk: "+ self.link
        
        if self.period != "":
            r = "Period " + str(self.period) + " " + r

        if self.termin != "":
            r = self.termin + " " + r

        return r

    def __eq__(self, other):
        if not isinstance(other, Course):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.id == other.id and self.block == other.block  and self.termin == other.termin and self.period == other.period

class Calendar:
    def __init__(self, terminer=9, perioder=2, block=4):
        self.calendar = [[[ [] for k in range(block)] for j in range(perioder)] for i in range(terminer)]

    def plan_course(self, course):
        blocks = course.block.split("/")
        if blocks == ["-"]:
            for i in range(4):
                occasion = self.calendar[int(course.termin[7]) - 1][course.period - 1][i]
                if not (course in occasion):
                    occasion.append(course)
        else:
            for block in blocks:
                    occasion = self.calendar[int(course.termin[7]) - 1][course.period - 1][int(block) -1]
                    if not (course in occasion):
                        occasion.append(course)

    def remove_course(self, course):
        blocks = course.block.split("/")
        if blocks == ["-"]:
            for i in range(4):
                occasion = self.calendar[int(course.termin[7]) - 1][course.period - 1][i]
                if course in occasion:
                    occasion.remove(course)
        else:
            for block in blocks:
                occasion = self.calendar[int(course.termin[7]) - 1][course.period - 1][int(block) -1]
                if course in occasion:
                    occasion.remove(course)

    def total_hp(self):
        hp = 0
        long_courses = []
        for i in range(6,9):
            for j in range(2):
                for k in range(4):
                    if self.calendar[i][j][k] != []:
                        for c in self.calendar[i][j][k]:
                            if c.hp.endswith("*"):
                                if not (c.id in long_courses):
                                    long_courses.append(c.id)
                                    hp += int(c.hp[:-1])
                            else:
                                hp += int(c.hp)
        return hp
                            
    

    def __str__(self):
        buffer = ""
        for i in range(6,9):
            buffer += "Termin " + str(i + 1) + "\n"
            for j in range(2):
                buffer += "\tPeriod " + str(j + 1) + "\n"
                for k in range(4):
                    buffer += "\t\tBlock " + str(k + 1) + "\n"
                    if self.calendar[i][j][k] != []:
                        for c in self.calendar[i][j][k]:
                            buffer += "\t\t\t" + c.name + " " + c.id + " HP: " + c.hp + " " + c.termin +"\n"
        return buffer
        

def get_courses(soup, course_lookup):
    for article in soup('article'):
        try:
            termin = article.contents[1].contents[1].contents[0]
            main = BeautifulSoup(article.prettify(), "html.parser")
            for period in main(class_='period'):
                p_t = int(period.th.contents[0][-9])
                body = BeautifulSoup(period.prettify(), "html.parser")
                for course in body(class_='main-row'):
                    c = Course(
                        course.contents[3].contents[1].string.strip(),
                        course['data-course-code'],
                        course.contents[5].string.strip(),
                        course.contents[9].string.strip(),
                        course.contents[7].string.strip(),
                        course.contents[3].contents[1]['href'],
                        termin, p_t)
                    if c.id in course_lookup:
                        if not (c in course_lookup[c.id]):
                            course_lookup[c.id].append(c)
                    else:
                        course_lookup[c.id] = [c]
        except IndexError:
            pass

def save_courses(mycourses):
    if len(mycourses) > 0:
        f = open("mycourses.json", "w")
        for c in mycourses:
            s = json.dumps(c.__dict__)
            f.write(s)
            f.write("\n")
        f.close()
        print("Skrev ner valda kurser i kurser.txt")


def read_json_courses(mycourses):
    calendar = Calendar()
    try:
        f = open("mycourses.json")
    except FileNotFoundError:
        return calendar # First time, no courses written.
        
    for line in f:
        try:
            t = json.loads(line)
            c = Course(t['name'], t['id'], t['hp'], t['block'], t['level'], t['link'], t['termin'],t['period'])
            calendar.plan_course(c)
            mycourses.append(c)
        except:
            print("Something went wrong reading line "+ line)
    return calendar

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def remove_courses(calendar, mycourses, course_lookup):
    while True:
        clear_terminal()
        print(calendar)
        print("HP valda: " + str(calendar.total_hp()))
        print("Skriv kurskod för att ta bort kurser, svara q när du är klar")
        c_id = input("Kurskod? ").upper()
        if(c_id == "Q"):
            break
        if c_id in course_lookup:
            print("Kursen går ")
            for c in course_lookup[c_id]:
                print(c)
                y = input("Vill du ta bort detta tillfälle? y/n ").lower()
                if y.startswith("y"):
                    mycourses.remove(c)
                    calendar.remove_course(c)
        else:
            print("Kunde inte hitta kursen")

def add_courses(calendar, mycourses, course_lookup):
    while True:
        clear_terminal()
        print(calendar)
        print("HP valda: " + str(calendar.total_hp()))
        print("Skriv kurskod för att lägga till kurser, svara q när du är klar")
        c_id = input("Kurskod? ").upper()
        if(c_id == "Q"):
            break
        if c_id in course_lookup:
            print("Kursen går ")
            for c in course_lookup[c_id]:
                print(c)
                y = input("Vill du läsa kursen detta tillfälle? y/n ").lower()
                if y.startswith("y"):
                    mycourses.append(c)
                    calendar.plan_course(c)
        else:
            print("Kunde inte hitta kursen")

def yes_no(message):
    answer = input(message + " [y/n]")
    if(answer.upper().startswith("Y")):
        return True
    return False

def get_webdata():
    html = ""
    if yes_no("Uppdatera tillgängliga kurser via internet?"):
        f = open("courses.html", "w")
        url = "https://liu.se/studieinfo/program/6cddd/3695"
        page = urlopen(url)
        html = page.read().decode("utf-8")
        f.write(html)
    else:
        try:
            f = open("courses.html")
            html = f.read()
        except FileNotFoundError:
            print("Du behöver hämta kurser från internet")
            return ""
    f.close()
    return html

def main():
    html = ""
    while html == "":
        html = get_webdata()
    soup = BeautifulSoup(html, "html.parser")
    mycourses = []
    course_lookup = {}
    
    get_courses(soup, course_lookup)

    calendar = read_json_courses(mycourses)

    add_courses(calendar, mycourses, course_lookup)
    remove_courses(calendar, mycourses, course_lookup)
    clear_terminal()
    print(calendar)
    print("HP valda: " + str(calendar.total_hp()))
    f = open("kurser.txt", "w")
    f.write(str(calendar))
    f.close()
    save_courses(mycourses)

if __name__ == "__main__":
    main()
