#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 14:11:08 2020

@author: Andy Gao
"""

from lxml import html
import requests
# courses lists
T1_offered = []
T2_offered = []
T3_offered = []
not_offered = []

def constr_url(year = "2020", school = "COMP", campus = "KENS"):
    url = f"http://timetable.unsw.edu.au/{year}/{school}{campus}.html"
    return url

def get_xml_tree(url):
    print("Sending http request...")
    page = requests.get(url)
    page.raise_for_status()
    print(f"Got response with status code: {page.status_code}")
    tree = html.fromstring(page.content)
    return tree

# kinda hard coded here
def find_course_table_from_tree(tree):
    # find the tables depending on their class name
    elements = tree.xpath("//td[@class='formBody']")
    # 6th element contains the table of courses lists
    table_1 = elements[5].xpath("//tr[@class='rowHighlight']")
    table_2 = elements[5].xpath("//tr[@class='rowLowlight']")
    return table_1, table_2

def extract_courses(year="2020", table = None):
    for row in table:
        row_elements = row.xpath("td")
        if len(row_elements) == 3:
            course_code = row_elements[0].xpath('a')[0].text
            course_title = row_elements[1].xpath('a')[0].text
            course_credits = row_elements[2].text
    
            timetable_url = requests.get(f"http://timetable.unsw.edu.au/{year}/" + course_code + ".html")
    
            subtree = html.fromstring(timetable_url.content)
    
            e = subtree.xpath('.//*[contains(text(),"offering information for the selected course was not found")]')
            if (len(e) > 0):
                not_offered.append([course_code, course_title])
            else:
                e = subtree.xpath('.//*[contains(text(),"TERM THREE")]')
                if (len(e) > 0):
                    T3_offered.append([course_code, course_title])
                e = subtree.xpath('.//*[contains(text(),"TERM TWO")]')
                if (len(e) > 0):
                    T2_offered.append([course_code, course_title])
                e = subtree.xpath('.//*[contains(text(),"TERM ONE")]')
                if (len(e) > 0):
                    T1_offered.append([course_code, course_title])
        else:
            print(f"Invlaid table format")
            
def build_course_lists(year="2020" , tree = None):
    if tree is None:
        print("NULL xml path")
        return False
    
    tables = find_course_table_from_tree(tree)
    for t in tables:
        extract_courses(year, t)
    
    print("Extracting courses done")
    return True


def out_put(fname, year):
    with open(fname, 'w') as f:
        f.write("# CSE Electives\n\n")        
        f.write(f"\n### Offered {year}T1:\n")
        # format https://www.handbook.unsw.edu.au/postgraduate/courses/2020/comp9021/
        for i in T1_offered:
            f.write('[{0}](http://timetable.unsw.edu.au/{2}/{3}.html) [{1}](https://www.handbook.unsw.edu.au/postgraduate/courses/{2}/{0})\n'.format(i[0].lower(), i[1], year, i[0].upper()))
        
        f.write(f"\n### Offered {year}T2:\n")
        for i in T2_offered:
            f.write('[{0}](http://timetable.unsw.edu.au/{2}/{3}.html) [{1}](https://www.handbook.unsw.edu.au/postgraduate/courses/{2}/{0})\n'.format(i[0].lower(), i[1], year, i[0].upper()))
        
        f.write(f"\n### Offered {year}T3:\n")
        for i in T3_offered:
            f.write('[{0}](http://timetable.unsw.edu.au/{2}/{3}.html) [{1}](https://www.handbook.unsw.edu.au/postgraduate/courses/{2}/{0})\n'.format(i[0].lower(), i[1], year, i[0].upper()))
        
        f.write("\n### Not running :(\n")
        for i in not_offered:
            f.write('[{0}](http://timetable.unsw.edu.au/{2}/{3}.html) [{1}](https://www.handbook.unsw.edu.au/postgraduate/courses/{2}/{0})\n'.format(i[0].lower(), i[1], year, i[0].upper()))
    
    
if __name__ == "__main__":
    import sys
    import os
    
    if (len(sys.argv) < 4):
        print("Usage: ./courses.py <year> <school> <campus>")
        print("NOTE: currently only supports 'KENS' as the arg for campus")
        sys.exit(1)
        
    year   = sys.argv[1]
    school = sys.argv[2]
    # not use for that moment, since we are all in KENS
    campus = sys.argv[3]
    
    url = constr_url(year, school, campus)
    tree = get_xml_tree(url)
    
    print("Extracting course lists...")
    build_course_lists(year, tree)
    
    fname = f"{year}-" + f"{school}{campus}-" + "courses.md"
    print(f"Output to {os.getcwd()}\{fname}")
    out_put(fname, year)
    
    print("Bye :)")
    
    
    
    
    