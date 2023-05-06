import requests
import http
from bs4 import BeautifulSoup
import re
import time

"""
todo:
•	Accept command line parameters for products to download
•	Accept command line parameters for folder to download pdf document to
•	Identify name of file to download from server response
•	Figure out why requests library takes so long to get pdf file compared to browser-based download of same target
    (tried session, tried headers, tried stream & chunked-writes, trying sleep between tx)
"""

def get_splunkdoc_products():

    print('Getting list of splunk products.')

    url = "https://docs.splunk.com/Documentation/Splunk"
    #page = requests.get(url)
    page = s.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    elements = soup.select('#product-select')
    pattern = 'value=\"([^\"]+)\">(.*)\</option>'

    elements_dict = {}

    for element in elements[0].contents:
        element = str(element)
        match = re.match(pattern, element, re.IGNORECASE)
        if match := re.search(pattern, element, re.IGNORECASE):

            key = match.group(1)

            value = match.group(2)
            value = value.replace('<sup>', '')
            value = value.replace('</sup>', '')

            elements_dict[key] = value

    return elements_dict



        # list versions of documentation
        # versions = soup.select('#version-select')
        # for version in versions[0].contents:
        # print(version)

def get_splunkdoc_versions(product):

    url = "https://docs.splunk.com/Documentation/" + product
    #page = requests.get(url)
    page = s.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    elements = soup.select('#version-select')
    pattern = 'value=\"([^\"]+)\">(.*)\</option>'

    elements_dict = {}

    for element in elements[0].contents:
        element = str(element)
        match = re.match(pattern, element, re.IGNORECASE)
        if match := re.search(pattern, element, re.IGNORECASE):

            key = match.group(1)

            value = match.group(2)
            value = value.replace('<sup>', '')
            value = value.replace('</sup>', '')
            # value = value.replace(' (latest release)', '')

            # print('key: {}'.format(key))
            # print('value: {}'.format(value))

            elements_dict[key] = value

    return elements_dict

download_path = 'C:\Apps\splunkdocs'
my_products = ['Splunk', 'Forwarder', 'ES', 'Phantom', 'DBX']

# create session object for re-use
sleep_seconds = 1
s = requests.Session()
http.client.HTTPConnection.debuglevel = 0

for product in my_products:

    print('working on product: {}'.format(product))

    versions = (get_splunkdoc_versions(product))

    for version in versions:
        if 'latest release' in versions[version]:

            print('-found latest release version: {}'.format(version))

            # get page for specified product and version as soup
            url = 'https://docs.splunk.com/Documentation/' + product + '/' + version
            page = s.get(url)
            time.sleep(sleep_seconds)
            soup = BeautifulSoup(page.content, "html.parser")

            # process links listing documentation for product and version
            for i in soup.find_all(href=re.compile('^/Documentation/' + product + '/' + version + '/')):

                # get page associated with the document
                page = s.get('https://docs.splunk.com' + (i.attrs['href']))
                time.sleep(sleep_seconds)
                soup = BeautifulSoup(page.content, "html.parser")

                # get the links on document page associated with product pdfbook action
                for j in soup.find_all(href=re.compile('&action=pdfbook.*&product')):
                    href = j.attrs['href']

                    # process link instance for full manual (the one(s) that are not topic specific)
                    if '&topic' not in href:

                        # construct the download url
                        pdf_download_url = 'https://docs.splunk.com' + href

                        # construct the download filename
                        file_name = product + '-' + version + '-' + (href.split(":"))[2] + '.pdf'

                        # do the download!
                        file_fullname = download_path + '\\' + file_name
                        print('-downloading {} document to {}'.format((href.split(":"))[2], file_fullname))
                        response = s.get(pdf_download_url, stream=True)

                        with open(file_fullname, "wb") as file:
                            for chunk in response.iter_content(chunk_size=16*1024):
                                file.write(chunk)
