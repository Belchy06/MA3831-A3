import csv
import threading
import urllib

from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import os
import traceback

MAX_THREADS = 8
DATE_RANGE = 31
POST_PER_SUB_FIELD = 25


def check_has_numbers(input_string):
    return bool(re.search(r'\d', input_string))


def get_classification_urls(file):
    urls = []
    with open(file, 'r') as nav:
        soup = BeautifulSoup(nav, 'html.parser')
        # print(soup.prettify())
        els = soup.find_all('a')
        indent = False
        classification = ""
        subclassification = ""
        for el in els:
            label = el['aria-label'].lower()
            # Remove the categories for 'all jobs in {field}' or 'other'
            if label[0:3] == 'all' or label[0:5] == 'other':
                continue
            label = re.sub(r'[/&-,]', ' ', label)
            label = re.sub(r'[\']', '', label)
            label = re.sub(r'[ ]{2,}', ' ', label)
            label = re.sub(r'[ ]', '-', label.strip())
            if not check_has_numbers(label):
                # Is the field
                classification = 'jobs-in-' + label
                # print('\n')
                # print(classification)
            else:
                # is the sub-field
                label = re.sub(r'[0-9](.*)', '', label)
                subclassification = label[:-1]
                single_url = classification + '/' + subclassification
                urls.append([classification, subclassification])
                # print('\t' + single_url)
    return urls


def get_valid_urls(urls):
    valid_list = []
    for url in urls:
        single_page_url = "https://www.seek.com.au/" + url[0] + '/' + url[1]
        response = requests.get(single_page_url)
        if response.status_code == requests.codes.ok:
            print('Valid: ' + "https://www.seek.com.au/" + url[0] + '/' + url[1])
            valid_list.append([url[0], url[1]])
    return valid_list


def thread_function(index, data):
    with open(r'output{}.csv'.format(index), 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['FIELD', 'SUB-FIELD', 'TITLE', 'DESCRIPTION'])

    length = len(data)
    i = 0
    prev_sub_field = ""
    for url in data:
        print("Thread {}: Index {}/{}".format(index, i, length))
        i = i + 1

        if url[1] != prev_sub_field:
            sub_field_total = 0
            prev_sub_field = url[1]

        for page_num in range(1, 3):
            seek_url = ''.join([
                "https://www.seek.com.au/",
                url[0] + '/' + url[1],
                "?daterange=",
                str(DATE_RANGE),
                '&page=',
                str(page_num),
                "&sortmode=ListedDate"
            ])

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                request1 = urllib.request.Request(url=seek_url, headers=headers)
                response1 = urllib.request.urlopen(request1)
                temp_html = response1.read().decode()
                temp_html = BeautifulSoup(temp_html, "lxml")
                results = temp_html.find_all('article')

                for result in results:
                    if sub_field_total == POST_PER_SUB_FIELD:
                        continue
                    job_title = ''
                    single_page_url = ''
                    try:
                        single_page_url = "https://www.seek.com.au" + result.contents[0].div['href']
                        request2 = urllib.request.Request(url=single_page_url, headers=headers)
                        response2 = urllib.request.urlopen(request2)
                        single_temp_html = response2.read().decode()
                        single_temp_html = BeautifulSoup(single_temp_html, "lxml")

                        job_title = single_temp_html.title.string
                        desc_title = single_temp_html.find('h2', text='Job description')
                        if desc_title is None:
                            job_description = single_temp_html.find(attrs={"data-automation": "jobDescription"})
                        else:
                            desc_parent = desc_title.find_parent('div')
                            job_description = desc_parent.find_next_sibling("div")
                        desc_text = re.sub('\xa0', ' ',
                                           " ".join(item.strip() for item in job_description.find_all(text=True)))
                        desc_text = re.sub('[ ]{2,}', ' ', desc_text.strip())
                        fields = [url[0],  # Field
                                  url[1],  # Sub-field
                                  job_title,  # Job tite
                                  desc_text]  # Job description
                        with open(r'output{}.csv'.format(index), 'a', newline='', encoding='utf-8-sig') as file:
                            w = csv.writer(file, delimiter=',')
                            try:
                                w.writerow(fields)
                                sub_field_total = sub_field_total + 1
                            except Exception:
                                print("Thread {}, Index {}: MISSED WRITING TO FILE. URL: {}".format(index, i,
                                                                                                    single_page_url))
                                traceback.print_exc()
                    except Exception:
                        print('{} failed, URL: {}'.format(job_title, single_page_url))
                        traceback.print_exc()
            except Exception:
                print(url[0] + '/' + url[1] + ' failed')
                traceback.print_exc()


if __name__ == '__main__':
    classification_urls = get_classification_urls('nav.html')
    # valid_urls = get_valid_urls(classification_urls)
    valid_urls = classification_urls

    """
    MULTI-THREADING
    """
    # Split dataframe into equal amounts
    n = int(len(classification_urls) / MAX_THREADS) + 1
    list_urls = [classification_urls[i:i + n] for i in range(0, len(classification_urls), n)]
    # Instantiate threads
    threads = list()
    for idx in range(MAX_THREADS):
        print("Main: creating and starting thread {}".format(idx))
        x = threading.Thread(target=thread_function, args=(idx, list_urls[idx],))
        threads.append(x)
        x.start()

    for idx, thread in enumerate(threads):
        thread.join()
        print("Main: \tThread {} done".format(idx))

    """
    COMBINING TEMP FILES
    """
    # Combine files
    with open(r'job_data.csv', 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['FIELD', 'SUB-FIELD', 'TITLE', 'DESCRIPTION'])

    all_files = ['output{}.csv'.format(i) for i in range(MAX_THREADS)]
    combined_descriptions = pd.concat([pd.read_csv(f) for f in all_files])
    # export to csv
    combined_descriptions.to_csv("job_data.csv", index=False, encoding='utf-8-sig')
    # Remove temp files
    for file in all_files:
        os.remove(file)
