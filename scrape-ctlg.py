import requests
from bs4 import BeautifulSoup
import lxml
import pprint
import json
import re
from fake_useragent import UserAgent
import random
from time import sleep
from itertools import islice
import json



# Limits how fast a function decorated by this is called
def rate_limit(function):
    def wrapper(*args, **kwargs):
        pause_time = 6 + random.randint(-2, 2)
        print('Pausing for ' + str(pause_time) + 's')
        sleep(pause_time)
        return function(*args, **kwargs)
    return wrapper

@rate_limit
def request_soup(url):
    r  = requests.get(url, headers = {'User-Agent': UserAgent().chrome})
    return BeautifulSoup(r.text, 'lxml')


def ctlg_terms_url():
    return 'https://horizon.mcgill.ca/pban1/bwckctlg.p_disp_dyn_ctlg'

def ctlg_subjects_url(term_code):
    return ("https://horizon.mcgill.ca/pban1/bwckctlg.p_disp_cat_term_date"
            "?call_proc_in=bwckctlg.p_disp_dyn_ctlg"
            "&search_mode_in="
            "&cat_term_in=" + term_code)

def ctlg_courses_url(term_code, subj_code):
    return ("https://horizon.mcgill.ca/pban1/bwckctlg.p_display_courses"
            "?term_in=" + term_code +
            "&call_proc_in=bwckctlg.p_disp_dyn_ctlg"
            "&sel_subj=dummy"
            "&sel_levl=dummy"
            "&sel_schd=dummy"
            "&sel_coll=dummy"
            "&sel_divs=dummy"
            "&sel_dept=dummy"
            "&sel_attr=dummy"
            "&search_mode_in=" 
            "&sel_subj=" + subj_code +
            "&sel_crse_strt="
            "&sel_crse_end="
            "&sel_title="
            "&sel_levl=%25"
            "&sel_schd=%25"
            "&sel_divs=%25"
            "&sel_dept=%25"
            "&sel_from_cred="
            "&sel_to_cred="
            "&sel_attr=%25")


def rand_lim_subset(lst, size):
    if (size > 0):
        random.shuffle(lst)
        lst = list(islice(lst, 0, size));
    return lst

# Scrape the terms from the catalog
def scrape_ctlg_terms(include_suppl=False, recurse=0, limit=0):
    print('Scraping ctlg for terms.')
    return_data = {}
    soup = request_soup(ctlg_terms_url())

    term_options_elems = soup.find(id='term_input_id').find_all('option')
    term_options_elems = [x for x in term_options_elems if (x['value'] != '' and x['value'] != 'None' and (include_suppl or 'Supplement' not in x.text))]
    term_options_elems = rand_lim_subset(term_options_elems, limit)
    for elem in term_options_elems:
        term_code = elem['value']
        return_data[term_code] = {
            'desc': clean_term_desc(elem.text)
        }
        if (recurse > 0):
            return_data[term_code]['subjects'] = scrape_ctlg_subjects(term_code, recurse=recurse-1, limit=limit)
    return return_data
        
def clean_term_desc(term_desc):
    clean = term_desc.strip('\n');
    return clean


# Scrape the subjects for a given term from the catalog
def scrape_ctlg_subjects(term_code, recurse=0, limit=0):
    print('--Scraping ctlg for subjects from term ' + str(term_code))
    return_data = {}
    soup = request_soup(ctlg_subjects_url(term_code))

    subj_obtions_elems = soup.find(id='subj_id').find_all('option')
    subj_obtions_elems = rand_lim_subset(subj_obtions_elems, limit)
    for elem in subj_obtions_elems:
        subj_code = elem['value']
        return_data[subj_code] = { 
            'desc': clean_subj_desc(elem.text), 
        }
        if (recurse > 0):
            return_data[subj_code]['courses'] = scrape_ctlg_courses(term_code, subj_code, recurse=recurse-1, limit=limit)
    return return_data
    
def clean_subj_desc(subj_desc):
    clean = subj_desc.strip('\n');
    clean = clean.split('-')[1]
    clean = clean.strip(' ')
    return clean


# Scrape the courses for a given term and subject from the catalog
def scrape_ctlg_courses(term_code, subj_code, recurse=0, limit=False):
    print('----Scraping ctlg for courses from term ' + str(term_code) + ' and subj ' + str(subj_code))
    return_data = {}
    soup = soup = request_soup(ctlg_courses_url(term_code, subj_code))
    
    course_title_elems = soup.find_all('td', class_='nttitle')
    course_title_elems = rand_lim_subset(course_title_elems, limit)
    for elem in course_title_elems :
        title_string = elem.contents[0].text
        course_code = title_string.split(' - ')[0]
        print('------Scraping ctlg for data from term ' + str(term_code) + ' and subj ' + str(subj_code) + ' and course ' + str(course_code))

        full_content = elem.parent.next_sibling.next_sibling.td.text
        print(full_content);
        
        return_data[course_code] = {
            'code_subj': course_code.split(' ')[0],
            'code_numb': course_code.split(' ')[1],
            'name': title_string.split(' - ')[1],
            'content': parse_ctlg_course_content(full_content)
        }
    return return_data


def parse_ctlg_course_content(full_content) :
    full_content_regex = r"\n(.*)\n?\n{2}(.*)\n?\n(.+)\n{3}(.+)\n{3}(.+)\n{2}(.+)\n{3}"
    match = re.fullmatch(full_content_regex, full_content, re.DOTALL)

    ctlg_content = {
        # 'full_content': full_content,
        'description': match.group(1).rstrip(),
        'notes': parse_ctlg_course_notes(match.group(2)),
        'credits': parse_ctlg_course_credits(match.group(3)),
        'schd_types': parse_ctlg_course_schd_types(match.group(4)),
        'faculty': match.group(5).strip(),
        'department': match.group(6)
    }
    return ctlg_content

def parse_ctlg_course_credits(credits_string) :
    return float(credits_string.strip().split(' Credit hours')[0])

def parse_ctlg_course_notes(notes_string) :
    ctlg_notes = {
        'all': [],
        'prereq': [],
        'coreq': [],
        'restrict': []
    }
    split_notes = notes_string.split('\n')
    for note in split_notes :
        if note != '' :
            ctlg_notes['all'].append(note)
            for label in ['Prereq', 'Coreq', 'Restrict']:
                if label in note:
                    ctlg_notes[label.lower()].append(note)
    return ctlg_notes

def parse_ctlg_course_schd_types(schd_types_string) :
    ctlg_schd_types = []
    split_schd_types = schd_types_string.split('Schedule Types: ')[1].split('\n\n')[0].split(', ')
    for schd_type in split_schd_types :
        if schd_type != '' :
            ctlg_schd_types.append(schd_type.strip())
    return ctlg_schd_types


# ctlg_terms = scrape_ctlg_terms(recurse=0, limit=0)
# pprint.pprint(ctlg_terms)

# ctlg_subjects = scrape_ctlg_subjects('201709', recurse=0, limit=0)
# pprint.pprint(ctlg_subjects)

ctlg_courses = scrape_ctlg_courses('201709', 'BIOL')
pprint.pprint((ctlg_courses))

with open('data.json', 'w') as fp:
    json.dump(ctlg_courses, fp, sort_keys=True, indent=4)



