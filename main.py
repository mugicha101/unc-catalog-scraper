import re
import mechanicalsoup
import time
import json
import os
import sys
import time

def restart_line():
    sys.stdout.write('\r')
    sys.stdout.flush()

class Course:
    def __init__(self, id, name, min_credits, max_credits, desc, coreqs, prereqs):
        self.time = time.time()
        self.id = id
        self.name = name
        self.min_credits = min_credits
        self.max_credits = max_credits
        self.desc = desc
        self.coreqs = coreqs
        self.prereqs = prereqs

    def update_file(self):
        dir = re.search(r"^[A-Z]*\s", self.id).group()[0:-1]
        fn = re.search(r"[0-9]*[A-Z]?$", self.id).group()
        os.makedirs(os.path.dirname(f'course-data/{dir}/'), exist_ok=True)
        with open(f'course-data/{dir}/{fn}', "w") as file:
            file.write(json.dumps({
                "time": self.time,
                "id": self.id,
                "name": self.name,
                "min_credits": self.min_credits,
                "max_credits": self.max_credits,
                "desc": self.desc,
                "coreqs": self.coreqs,
                "prereqs": self.prereqs
            }))


    def __str__(self):
        return f"id: {self.id}\nname: {self.name}\ncredits: {self.min_credits}-{self.max_credits}\ndesc: {self.desc}"


def update_course_data():
    print("Finding links")
    browser = mechanicalsoup.StatefulBrowser()
    catalog_url = "https://catalog.unc.edu/"
    browser.open(catalog_url + "courses/")
    links = set()
    for li in browser.get_current_page().find_all("a", {"href": re.compile(r"/courses/[a-z]{3,4}/")}):
        links.add(re.search(r'".*?"', str(li)).group()[2:-1])
    links = list(links)
    links.sort(key=str)
    courses = []
    i = 0
    for li in links:
        browser.open(catalog_url + li)
        i += 1
        restart_line()
        print(f'{i}/{len(links)} course categories updated', end="", flush=True)
        for raw_text in re.findall(r'<p class="courseblocktitle".*?\n<p class="courseblockdesc".*?\n.*?\n</p>', str(browser.get_current_page())):
            lines = re.sub(r"<.*?>|", "", re.sub(r'<p class="courseblockdesc".*?>', '\n', raw_text.replace("\n", ""))).split('\n')
            id = re.search(r'\A.*?\.', lines[0]).group()[:-1]
            lines[0] = lines[0][len(id)+3:]
            segs = lines[0].split('.  ')
            name = segs[0]
            credits = re.search(r"[0-9](-[0-9])?", segs[-1]).group()
            segs = lines[1].split(".")
            if segs[-1] == "":
                segs.pop()
            special_segs = []
            while re.fullmatch(r" ?(Grading status|Requisites|Repeat rules):.*?", segs[-1]):
                special_segs.append(re.sub("\A ?", "", segs.pop()))
            prereqs = []
            for ss in special_segs:

            courses.append(Course(id, name, int(credits[0]), int(credits[-1]), re.sub(r'  *', ' ', ".".join(segs) + ".")))
            courses[-1].update_file()
    print("\nCourse data updated")

class ReqGroup:
    def __init__(self, type, courses):
        self.type = type
        self.courses = courses


def construct_prereq_path(course):
    pass

def yes_no(question="") -> bool:
    response = response = input(f'{question}? (Y/N): ')
    while response != "N" and response != "Y":
        print("invalid response")
        response = input(f'{question} (Y/N): ')
    return response == "Y"

def main():
    if yes_no("Update course data?"):
        update_course_data()


if __name__ == "__main__":
    main()