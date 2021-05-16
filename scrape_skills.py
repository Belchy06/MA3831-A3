import csv
import threading
import urllib

from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import os
import traceback

PAGE_URL = "https://www.thebalancecareers.com/employment-skills-listed-by-job-2062389"

if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    request = urllib.request.Request(url=PAGE_URL, headers=headers)
    response = urllib.request.urlopen(request)
    temp_html = response.read().decode()
    temp_html = BeautifulSoup(temp_html, "lxml")
    uls = temp_html.find_all('ul')

    url_dict = {}
    for x in uls:
        for li in x.find_all('a', {'data-type': 'internalLink'}):
            if "skills-list" in li['href']:
                url_dict[li.text] = li['href']
    # skills-list
    skillList = []
    for key, val in url_dict.items():
        request = urllib.request.Request(url=val, headers=headers)
        response = urllib.request.urlopen(request)
        temp_html = response.read().decode()
        temp_html = BeautifulSoup(temp_html, "lxml")
        lis = temp_html.find_all('li', attrs={'class': None})
        lis_text = [x.text.lower() for x in lis]
        result_list = list(set(lis_text) | set(skillList))
        skillList = result_list
        print(val)
    print(*skillList, sep="\n")

    with open(r'skills.csv', 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['TEXT', 'TARGET'])
    for skill in skillList:
        with open(r'skills.csv', 'a', newline='', encoding='utf-8-sig') as file:
            w = csv.writer(file, delimiter=',')
            try:
                w.writerow([skill, '1'])
            except Exception:
                traceback.print_exc()
