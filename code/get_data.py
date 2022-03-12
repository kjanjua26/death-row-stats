"""
    We scrap data from Texas Department of Criminal Justice's website mainly.
        https://www.tdcj.texas.gov/death_row/dr_executed_offenders.html
    We also scrap data from some other websites such as:
        1. https://www.ranker.com/list/last-words-before-execution/notable-quotables
"""
import requests, re
from bs4 import BeautifulSoup
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


class DeathRowData:
    def __init__(self):
        self.base_texas_url = "https://www.tdcj.texas.gov/death_row/dr_executed_offenders.html"
        self.header = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
        self.last_statement_texas_url = "https://www.tdcj.texas.gov/death_row/dr_info/"
        self.data = open("data.csv", "w")
        self.data.write("LastName" + "," + "FirstName" + "," + "Age" + "," + "DateExecution" + "," + "Race" + "," + "County" + "," + "LastStatement" + "\n")

    def remove_non_ascii(self, text):
        return text.encode('ascii', errors='ignore')

    def read_a_page(self, link):
        page = requests.get(link, headers=self.header, verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def texas_website(self):
        soup = self.read_a_page(self.base_texas_url)
        inmates = soup.find_all('table', attrs={'class':'tdcj_table indent'})
        for ix, data in enumerate(inmates[0].find_all('tr')):
            inmate_data = ""
            for col in data.find_all('td'):
                inmate_data += f" {col.text}"
            inmate_data = inmate_data.split(' ')[6:]
            inmate_data = [x for x in inmate_data if x != '']
            if inmate_data:
                if inmate_data[0] == "Statement":
                    del inmate_data[0]
                first_name_last_name = inmate_data[0].lower() + inmate_data[1].lower() + "last.html"
                last_url = self.last_statement_texas_url + first_name_last_name
                soup_last = self.read_a_page(last_url)
                last_statements = soup_last.find_all('div', attrs={'id':'content_right'})
                try:
                    for last_statement in last_statements[0].find_all('p')[-1]:
                        if len(last_statement) > 1:
                            last_name, first_name, _, age, date_of_exec, race, county = inmate_data
                            last_statement = last_statement.replace(',', '').lstrip().rstrip()
                            last_statement = re.sub(r'[^\x00-\x7F]+',' ', last_statement)
                            self.data.write(last_name.replace(',', '') + ",")
                            self.data.write(first_name.replace(',', '') + ",")
                            self.data.write(age.replace(',', '') + ",")
                            self.data.write(date_of_exec.replace(',', '') + ",")
                            self.data.write(race.replace(',', '') + ",")
                            self.data.write(county.replace(',', '') + ",")
                            self.data.write(last_statement)
                            self.data.write("\n")
                            
                            print(inmate_data, last_statement)
                except:
                    pass
        self.data.close()
            
dr = DeathRowData()
dr.texas_website()
