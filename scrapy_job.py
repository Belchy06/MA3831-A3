'''
Sample script to scrape job info from SEEK website for non citizens
And generates the results in an html file
please installing the following packages first
pip install bs4 lxml
'''

import urllib.request, re, traceback
from bs4 import BeautifulSoup
import search_setting


def writeWarning(keyword, job_title, job_description, single_page_url, jobListingDate):
	f.write('<tr style="width: 5%"><th scope="row"><font color="red">X</font></th>')
	f.write('<td style="width: 25%"><font color="red">' + job_title + '</font></td>')
	f.write('<td style="width: 65%"><a target="_blank" href="' + single_page_url + '">' + job_description.find(
		string=re.compile(keyword, re.IGNORECASE)) + '</a></td>')
	f.write('<td style="width: 5%">' + jobListingDate + '</td></tr>')
	print(job_description.find(string=re.compile(keyword, re.IGNORECASE)))


def mainHtml(url, total_num, citizen_num):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
	request1 = urllib.request.Request(url=url, headers=headers)
	response1 = urllib.request.urlopen(request1)
	temp_html = response1.read().decode()
	temp_html = BeautifulSoup(temp_html, "lxml")
	results = temp_html.find_all('article')
	jobListingDate = temp_html.find_all(attrs={"data-automation": "jobListingDate"})

	for x in results:
		y = 0
		single_page_url = "https://www.seek.com.au" + x.contents[0].div['href']
		request2 = urllib.request.Request(url=single_page_url, headers=headers)
		response2 = urllib.request.urlopen(request2)
		single_temp_html = response2.read().decode()
		single_temp_html = BeautifulSoup(single_temp_html, "lxml")

		job_title = single_temp_html.title.string
		#
		desc_title = single_temp_html.find('h2', text='Job description')
		if desc_title is None:
			job_description = single_temp_html.find(attrs={"data-automation": "jobDescription"})
		else:
			desc_parent = desc_title.find_parent('div')
			job_description = desc_parent.find_next_sibling("div")
		desc_text = re.sub('\xa0', ' ', job_description.text)
		print(re.sub('[ ]{2, }', ' ', desc_text.strip()))
		total_num = total_num + 1

		# If the page contains words 'citizen', 'nv1', 'nv2' and 'clearance', go to error write functoin
		if job_description.find(string=re.compile('nv1', re.IGNORECASE)) != None:
			writeWarning('nv1', job_title, job_description, single_page_url, jobListingDate[y].text)
			citizen_num = citizen_num + 1
		elif job_description.find(string=re.compile('nv2', re.IGNORECASE)) != None:
			writeWarning('nv2', job_title, job_description, single_page_url, jobListingDate[y].text)
			citizen_num = citizen_num + 1
		else:
			f.write('<tr style="width: 5%"><th scope="row">' + str(total_num) + '</th>')
			f.write(
				'<td style="width: 25%"><a target="_blank" href="' + single_page_url + '">' + re.sub('- SEEK', '', job_title) + '</a></td>')
			f.write('<td style="width: 65%">' + str(re.sub('[ ]{2, }', ' ', desc_text.strip())) + '</td>')
			f.write('<td style="width: 5%">' + jobListingDate[y].text + '</td></tr>')
			print(single_page_url)
		y = y + 1
	return total_num, citizen_num


f = open(__file__[:-3] + '.html', 'w')
# header of html with Bootstrap 4
f.write('''
<html lang="en">
	<head>
		<meta charset="utf-8">
		<title>Job Searching results</title>
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
	</head>
	<body>
	<table class="table table-striped">
		<thead>
			<tr>
				<th scope="col" style="width: 5%">#</th>
				<th scope="col" style="width: 25%">Job Title</th>
				<th scope="col" style="width: 65%">URL</th>
				<th scope="col" style="width: 5%">Last Update</th>
			</tr>
		</thead>
		<tbody>
''')

total_num = 0
citizen_num = 0

for x in range(1, 3):
	# Search for full-time IT job in Canberra which published within 14 days
	url = ''.join(
		["https://www.seek.com.au/",
		 search_setting.CONFIG['Classification'],
		 # '/',
		 # search_setting.CONFIG['Where'],
		 "?daterange=",
		 str(search_setting.CONFIG['Daterange']),
		 '&page=',
		 str(x),
		 "&salaryrange=0-100000&salarytype=annual&sortmode=ListedDate"
		 ])
	total_num, citizen_num = mainHtml(url, total_num, citizen_num)

f.write('<tr><th scope="row"> </th><td>Total number: ' + str(total_num) + '</td><td>' + '' + '</td></tr>')
f.write('</tbody></table></body></html>')
f.close()
