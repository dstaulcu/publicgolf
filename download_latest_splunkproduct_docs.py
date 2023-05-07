import requests
import http
from bs4 import BeautifulSoup
import re

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
user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68'}

s = requests.Session()
s.headers.update(user_agent)

# toggle value from 0 to 1 to enable http request debugging
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
            soup = BeautifulSoup(page.content, "html.parser")

            # process links listing documentation for product and version
            for i in soup.find_all(href=re.compile('^/Documentation/' + product + '/' + version + '/')):

                # get page associated with the document
                page = s.get('https://docs.splunk.com' + (i.attrs['href']))
                soup = BeautifulSoup(page.content, "html.parser")

                # get the links on document page associated pdfbook (effectively excluding topic)
                for j in soup.find_all(href=re.compile('title=Documentation:.*&action=pdfbook&[^\&]+&product=')):

                    # construct the download url
                    href = j.attrs['href']
                    pdf_download_url = 'https://docs.splunk.com' + href

                    # construct the download filename
                    document = (href.split(":"))[2]
                    file_name = product + '-' + version + '-' + document + '.pdf'

                    # do the download!
                    response = s.get(pdf_download_url, stream=True)

                    # extract filename from server request headers
                    file_name = response.headers.get("Content-Disposition").split("filename=")[1]
                    file_name = file_name.replace('"', '')

                    # construct the file_path
                    file_path = download_path + '\\' + file_name
                    print('-downloading {} document to {}'.format(document, file_path))
                    print('-download url: {}'.format(pdf_download_url))

                    # download stremed results
                    with open(file_path, "wb") as file:
                        for chunk in response.iter_content(chunk_size=1024*8):
                            file.write(chunk)
