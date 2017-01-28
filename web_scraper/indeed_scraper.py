from bs4 import BeautifulSoup # For HTML parsing
import urllib2 # Website connections
import re # Regular expressions
from time import sleep # To prevent overwhelming the server between connections
import pandas as pd # For converting results to a dataframe and bar chart plots


def text_cleaner(website):

    try:
        site = urllib2.urlopen(website).read() # Connect to the job posting
    except: 
        return   # Need this in case the website isn't there anymore or some other weird connection problem 
    
    soup_obj = BeautifulSoup(site,"lxml") # Get the html from the site
    
    for script in soup_obj(["script", "style"]):
        script.extract() # Remove these two elements from the BS4 object
    
    text = soup_obj.get_text() # Get the text from this   
    lines = (line.strip() for line in text.splitlines()) # break into lines
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each
    
    def chunk_space(chunk):
        chunk_out = chunk + ' ' # Need to fix spacing issue
        return chunk_out  
        
    text = ''.join(chunk_space(chunk) for chunk in chunks if chunk).encode('utf-8') # Get rid of all blank lines and ends of line
    # Now clean out all of the unicode junk (this line works great!!!)
        
    try:
        text = text.decode('unicode_escape').encode('ascii', 'ignore') # Need this as some websites aren't formatted
    except:                                                            # in a way that this works, can occasionally throw
        return                                                         # an exception
        
    text = re.sub("[^a-zA-Z.+3#]"," ", text)  # Now get rid of any terms that aren't words (include 3 for d3.js)
    return text


final_job = 'data+scientist' # searching for data scientist exact fit("data scientist" on Indeed search)
base_url = 'http://www.indeed.com'
start_url = 'http://www.indeed.com/jobs?q='+ final_job + '&l='

# determine the number pages
soup = BeautifulSoup(urllib2.urlopen(start_url),"lxml") # Get the html from the first page
num_jobs_area = soup.find(id = 'searchCount').string.encode('utf-8') # Now extract the total number of jobs found
job_numbers = re.findall('\d+', num_jobs_area) # Extract the total jobs found from the search result
    
if len(job_numbers) > 3: # Have a total number of jobs greater than 1000
    total_num_jobs = (int(job_numbers[2])*1000) + int(job_numbers[3])
else:
    total_num_jobs = int(job_numbers[2]) 
    
num_pages = total_num_jobs/10

df = pd.DataFrame()
    
for page in range(1,5): # Loop through all of our search result pages
    print 'Getting page', page
    start_num = (page-1)*10 # Assign the multiplier of 10 to view the pages we want
    url = start_url + '&start=' + str(start_num)
    page_obj = BeautifulSoup(urllib2.urlopen(url),"lxml") 
    
    targetElements1= page_obj.findAll('div', attrs={'class' : ' row result'})
    targetElements2= page_obj.findAll('div', attrs={'class' : 'lastRow row result'})
    targetElements = targetElements1 + targetElements2

    targetElements3= page_obj.findAll('div', attrs={'class' : 'row result'})
    targetElements4= page_obj.findAll('div', attrs={'class' : 'row sjlast result'})
    targetElementsSponsored = targetElements3 + targetElements4   
        
    for elem in targetElements:
        comp_name = elem.find('span', attrs={'itemprop':'name'}).getText().strip()
        job_title = elem.find('a', attrs={'class':'turnstileLink'}).attrs['title']
        home_url = "http://www.indeed.com"
        job_link = "%s%s" % (home_url,elem.find('a').get('href'))
        job_addr = elem.find('span', attrs={'itemprop':'addressLocality'}).getText()
        job_posted = elem.find('span', attrs={'class': 'date'}).getText()
        
        df = df.append({'comp_name': comp_name, 'job_title': job_title, 
                        'job_description': text_cleaner(job_link), 'job_posted': job_posted,
                         'job_location': job_addr
                       }, ignore_index=True)
    
    for elem in targetElementsSponsored:
        comp_name = elem.find('span', attrs={'class':'company'}).getText().strip()
        job_title = elem.find('a', attrs={'class':'jobtitle turnstileLink'}).attrs['title']
        home_url = "http://www.indeed.com"
        job_link = "%s%s" % (home_url,elem.find('a').get('href'))
        job_addr = elem.find('span', attrs={'class':'location'}).getText()

        df = df.append({'comp_name': comp_name, 'job_title': job_title, 
                        'job_description': text_cleaner(job_link), 'job_posted': 'Sponsored',
                         'job_location': job_addr
                       }, ignore_index=True)    


df.to_csv('job.csv',encoding='utf-8')
