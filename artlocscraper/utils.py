import requests
import time
import re
import os
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'User-Agent': user_agent}

def make_url(subject):
    '''
    takes artist (e.g. 'Eric-Claopton') and returns lyrics.com url for that artist
    '''
    if re.findall('\w+\_\w+', subject):
        return f'http://www.artcyclopedia.com/artists/{subject}.html'
    else:
        return f'http://www.artcyclopedia.com/history/{subject}.html'

def get_content(subject,dir):
    '''
    check if html file already exist in ./data/html/ (read it in)
    if not scrape it from lyrics.com
    subject can be art style name (Cubism) or artist name (e.g. Pablo_Picasso)
    '''
    filename = subject.replace('/','')
    filename = subject +'.html'
    if filename in os.listdir(dir):
        #print(filename)
        #print('file is already there')
        file = dir+filename
        html = open(file).read()
        return html
    else:
        #print(filename)
        #print('file is not there, so get the url first and get the centent (save the html in ./data/html/)')
        url = make_url(subject)
        response = requests.get(url,headers=headers)
        time.sleep(0.1) # only needed if it's from the internet
        assert response.status_code == 200
        open(dir+f'{filename}', mode='w').write(response.text)
        return response.text

def extract_artist_urls(html):
    '''
    extracts lyric urls from the artist html
    dupliates will be removed by imput artist e.g. 'Eric-Clapton'
    return a list of lyric urls
    '''
    artist_urls = re.findall('/\w+\_\w+', html)
    return artist_urls

def get_artist_content(artist_urls,dir):
    '''
    gets all artist contents (html) from artist_urls
    '''
    artist_htmls = []
    #i=0
    for artist_url in artist_urls:
        #i=i+1
        #print(i,'artist_html')
        #print(artist_url)
        artist_html = get_content(artist_url,dir)
        artist_htmls.append(artist_html)
    return artist_htmls

def extract_museum_list(artist_htmls, style):
    '''
    extracts all museum from lyric htmls
    '''
    museum_list = []
    for artist_html in tqdm(artist_htmls, desc ='parse and extract museum info'):
        pattern = '</BLOCKQUOTE><A NAME=\"museums\">[\s\S]+</BLOCKQUOTE><A NAME=\"artmarket\">'
        museum_sum = re.findall(pattern, artist_html)
        if len(museum_sum)==0:
            continue
        museum_infos = re.findall('<A TARGET=.+<BR CLEAR=\"all\"><BR>',museum_sum[0])
        soup = BeautifulSoup(artist_html, 'html.parser')
        artist = soup.find('title').get_text().replace(' Online','')
        for i in range(0,len(museum_infos)):
            museum_split = museum_infos[i].replace('<BR>','||').replace('<A HREF=','||').replace('<BR','||').replace('<I','||').replace('&nbsp;','').split('||')[0].split('</A>')
            if len(museum_split)!=2:
                museum_split.append(' ')
            soup = BeautifulSoup(museum_split[0], 'html.parser')
            museum_name = soup.find_all(name='a')[0].get_text()
            museum_link = soup.find('a').get('href').replace('..','http://www.artcyclopedia.com')
            museum_location = museum_split[1].split('(')[0].split('-')[0][2:]
            #print(museum_location)
            museum = [artist,style,museum_name, museum_location,museum_link]
            museum_list.append(museum)
    return museum_list

if __name__ == '__main__':
    
    print('start scraping')

    print(make_url('Cubism'))
    #print(make_url('Expressionism'))
    #print(make_url('Impressionism'))
    #print(make_url('Pop'))

    cub_html = get_content('cubism','./data/html/')
    #exp_html = get_content('expressionism','./data/html/')
    #imp_html = get_content('impressionism','./data/html/')
    #pop_html = get_content('pop','./data/html/')

    cub_artist_urls = extract_artist_urls(cub_html)
    #exp_artist_urls = extract_artist_urls(exp_html)
    #imp_artist_urls = extract_artist_urls(imp_html)
    #pop_artist_urls = extract_artist_urls(pop_html)

    print('cub url number',len(cub_artist_urls))
    #print('exp',len(exp_artist_urls))
    #print('imp',len(imp_artist_urls))
    #print('pop',len(pop_artist_urls))
    
    cub_artist_htmls = get_artist_content(cub_artist_urls,'./data/html/cubism/')
    print('cub html number',len(cub_artist_htmls))
    museum_list = extract_museum_list(cub_artist_htmls, 'Cubism')
    print(len(museum_list))
