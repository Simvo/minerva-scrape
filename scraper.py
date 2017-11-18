import requests
from bs4 import BeautifulSoup
import lxml
import pprint
import json

r  = requests.get("https://horizon.mcgill.ca/pban1/bwckgens.p_proc_term_date?p_calling_proc=bwckschd.p_disp_dyn_sched&search_mode_in=&p_term=201709")
soup = BeautifulSoup(r.text, 'lxml')

# for link in soup.find_all('a'):
#     print(link)
    
# for c in soup.find(id='subj_id').children:
#     print(c)

# subj_obtions = [elem['value'] for elem in subj_obtions_elems]

data = {}

def scrape_subjects():
    subj_obtions_elems = soup.find(id='subj_id').find_all('option')
    for elem in subj_obtions_elems:
        subj_code = elem['value']
        data[subj_code] = { 
            'desc': clean_subj_desc(elem.text), 
            'courses': {} 
        }
        
def clean_subj_desc(subj_desc):
    clean = subj_desc.strip('\n');
    clean = clean.split('-')[1]
    clean = clean.strip(' ')
    return clean
 
scrape_subjects()
pprint.pprint(data)

