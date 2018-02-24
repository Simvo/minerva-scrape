import requests
from bs4 import BeautifulSoup
import lxml
import pprint
import json


def scrape_term_codes():
    return_data = {}
    #term_codes = []    #if a list is needed
    r  = requests.get("https://horizon.mcgill.ca/pban1/bwckschd.p_disp_dyn_sched")
    soup = BeautifulSoup(r.text, 'lxml')
    term_options_elems = soup.find(id='term_input_id').find_all('option')
    
    for elem in term_options_elems:
        if(elem['value'] != ''):
            term_code = elem['value']
            #term_codes.append(term_code) #if a list is needed
            return_data[term_code] = {
                'desc': clean_term_desc(elem.text)
            }
    return return_data
        
def clean_term_desc(term_desc):
    clean = term_desc.strip('\n');
    return clean


def scrape_subjects(term_code):
    return_data = {}
    r  = requests.get("https://horizon.mcgill.ca/pban1/bwckgens.p_proc_term_date?p_calling_proc=bwckschd.p_disp_dyn_sched&search_mode_in=&p_term=" + term_code)
    soup = BeautifulSoup(r.text, 'lxml')

    subj_obtions_elems = soup.find(id='subj_id').find_all('option')
    for elem in subj_obtions_elems:
        subj_code = elem['value']
        return_data[subj_code] = { 
            'desc': clean_subj_desc(elem.text), 
        }
    return return_data
        
def clean_subj_desc(subj_desc):
    clean = subj_desc.strip('\n');
    clean = clean.split('-')[1]
    clean = clean.strip(' ')
    return clean
 

def scrape_crns(term_code, subj_code):
    return_data = []
    r  = requests.get("https://horizon.mcgill.ca/pban1/bwckschd.p_get_crse_unsec?display_mode_in=LIST&search_mode_in=&term_in=" + term_code + "&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj=" + subj_code + "&sel_crse=&sel_title=&sel_schd=%25&sel_from_cred=&sel_to_cred=&sel_levl=%25&sel_ptrm=%25&sel_instr=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a")
    soup = BeautifulSoup(r.text, 'lxml')
    
    datadisplaytable = soup.find(class_='datadisplaytable')
    crn_links = datadisplaytable.find_all('a')
    for crn_link in crn_links :
        return_data.append(crn_link.text)
    return return_data


# pprint.pprint(scrape_term_codes())
# pprint.pprint(scrape_subjects("201709"))
pprint.pprint(scrape_crns("201701", "COMP"))
