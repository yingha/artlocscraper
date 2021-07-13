import argparse
import pandas as pd
from artlocscraper.utils import make_url, get_content, extract_artist_urls, get_artist_content, extract_museum_list
from geopy.geocoders import Nominatim

parser = argparse.ArgumentParser(description='scrape museum list of the artist based on art style from artcyclopedia.com and output a csv file in ./data/')
parser.add_argument('subject', help='art stlye to scrape, eg. "cubism"')
parser.add_argument('dir', help='where to store the html files')
parser.add_argument("-v", "--verbosity", help="increase output verbosity", action="store_true")
args = parser.parse_args()

if args.verbosity:
    print(f'scraping html page from artcyclopedia.com for {args.subject}...')

artist_html = get_content(args.subject,args.dir)

if args.verbosity:
    print(f'extract artist urls from {args.subject} html...')

artist_urls = extract_artist_urls(artist_html)

if args.verbosity:
    print('get artist content and return a list of htmls...')

artist_htmls = get_artist_content(artist_urls,args.dir)

if args.verbosity:
    print('extract museum list from each artist and return a list of museumcs...')

museum_list = extract_museum_list(artist_htmls, args.subject)

if args.verbosity:
    print(f'save {args.subject} museum list as csv file')

df = pd.DataFrame(museum_list,columns=['artist','style','museum_name','museum_location','museum_link']) 

# Get the lat and lon of museums
lats = []
lons = []

for name in df['museum_name']:
    loc = Nominatim(user_agent="my_map").geocode(f'{name}')
    try:
        df_loc = pd.DataFrame(loc.raw)
        df_loc.drop([1,2,3], inplace=True)
        lat = float(df_loc['lat'][0])
        lon = float(df_loc['lon'][0])
    except AttributeError:
        print('can not find it on map')
        lat = 0.0
        lon = 0.0      
    lats.append(lat)
    lons.append(lon)

df.insert(3, "lat", lats, True)
df.insert(4, "lon", lons, True)

# delete duplicates
df = df.drop_duplicates(subset=['artist','museum_name'], keep="first")

df.to_csv(f'./data/{args.subject}_museum_list.csv')

print('done')

