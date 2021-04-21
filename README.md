# MA3831 Assignment 3 - Career Finder
This assignment required the use of a web scraper and the implementation of several Natural Language Processing techniques

## How it works
The file ```nav.html``` contains the classification selector from Seek.com.au.
```get_job_postings.py``` breaks down the classification selector to identify each field and sub-field.
The URLs are constructed based on the fields and sub-fields indentified.

For each of the URLs, the scraper grabs a maximum of the 25 most recent job postings for that sub-field.
The postings title and description are stored alongside the field and sub-field in the ```job_data.csv``` file.

