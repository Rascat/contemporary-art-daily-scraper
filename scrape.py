from bs4 import BeautifulSoup
import requests
import re
import os.path
import time

def create_dir(dirname):
    try:
        os.mkdir(dirname)
    except OSError:
        print (f'Creation of the directory {dirname} failed')
        return
    else:
        print (f'Successfully created the directory {dirname}')


def save_urls(urls, path):
    dirname = os.path.dirname(path)

    if not os.path.isdir(dirname):
        create_dir(dirname)
    
    with open(path, 'w') as f:
        f.write('\n'.join(urls))
        f.write('\n')


def scrape_article_urls(url, page_limit=30):
    savefile = f'{url[-4:]}.txt'
    savefile_path = f'./urls/{savefile}'
    
    if os.path.isfile(savefile_path):
        with open(savefile_path, 'r') as f:
            urls = f.read().splitlines()

            print(f'savefile containing {len(urls)} found')
            return urls

    print(f'scraping article links from {url}')
    cad_link_pattern = r'https:\/\/contemporaryartdaily\.com\/\d{4}\/\d{2}\/(\w|-)+\/$'
    valid_cad_link = re.compile(cad_link_pattern)

    html_pages = []
    for page in range(1, page_limit + 1):
        html_page = requests.get(f'{url}/page/{page}/?pgg={page}')
        html_pages.append(html_page.text)

    anchors = []
    for html in html_pages:
        soup = BeautifulSoup(html, 'lxml')
        anchors.extend(soup.find_all('a'))

    links = list(filter(lambda x: 'href' in x.attrs, anchors))
    cad_links = list(filter(lambda x: valid_cad_link.match(x['href']), links))
    cad_urls = [x['href'] for x in cad_links]
    unique_cad_urls = list(set(cad_urls))

    print(f'found {len(unique_cad_urls)} article urls')
    save_urls(unique_cad_urls, savefile_path)
    return unique_cad_urls


def scrape_page_text(url):
    print(f'scraping {url}')

    page = requests.get(url)
    html = page.text
    soup = BeautifulSoup(html, 'lxml')
    ps = soup.find_all('p')
    text_list = [ x for x in list(map(lambda x: x.string, ps)) if x is not None ]
    return '\n'.join(text_list)


def main():
    unix_epoch = int(time.time())
    path = f'./texte-{unix_epoch}.txt'
    base_url = 'https://contemporaryartdaily.com'
    archive_urls = [ f'{base_url}/{year}' for year in range(2008, 2022) ]

    print(f'archive urls: {archive_urls}')

    article_urls = []
    for url in archive_urls:
        new_urls = scrape_article_urls(url, 100)
        article_urls.extend(new_urls)

    for url in article_urls:
        text = scrape_page_text(url)
        with open(path, 'a') as f:
            f.write(f'### {url} ###\n\n')
            f.write(text)
            f.write('\n\n\n')


if __name__ == '__main__':
    main()