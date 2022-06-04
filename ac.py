#!env python

import argparse
import pandas
import requests
from bs4 import BeautifulSoup
import sys

SELECTOR_PAPER_ENTRY = "p.d-sm-flex.align-items-stretch"


def GetHtml(url: str) -> str:
    """
    Download HTML from 'url'

    Parameters:
    -----------
    url : str
        URL of the site to extract papers

    Returns:
    --------
    str : HTML string of the URL
    int : HTTP status code when an error occured
    """
    res = requests.get(url)
    if res.status_code != 200:
        return res.status_code
    return res.text


def ExtractPapers(html: str) -> pandas.DataFrame:
    """
    Extract paper info from HTML text

    Parameters:
    -----------
    html : str
        HTML text to extract papers

    Returns:
    --------
    DataFrame : pandas.DataFrame for all the papers
    """

    series_title = []
    series_authors = []
    series_abstract = []
    series_pdf = []
    series_bib = []
    series_sw = []
    series_code = []
    soup = BeautifulSoup(html, "html.parser")
    for paper in soup.select(SELECTOR_PAPER_ENTRY):
        # Analyze the header with pdf, bib, abs, etc.
        spans = paper.select("span")
        pdf = bib = abs = sw = code = ""
        for mark in spans[0].select("a"):
            txt = mark.get_text(strip=True)
            href = mark["href"]
            if txt == "pdf":
                pdf = href
            elif txt == "bib":
                bib = href
            elif txt == "abs":
                abs = href
            elif mark.select_one("i") is not None:
                sw = href
            elif mark.select_one("svg") is not None:
                code = href
            else:
                sys.stderr.write("ERROR: " + txt + "\n")
                sys.exit(1)
        # Get Abstract text
        if abs != "":
            abs = soup.select_one("div" + abs).get_text(strip=True)
        # Get Title and authors
        title = authors = ""
        links = spans[1].select("a")
        if len(links) > 1:
            title = links[0].get_text(strip=True)
            for author in links[1:]:
                authors += author.get_text(strip=True) + ";"
            authors = authors.rstrip(";")
        series_title.append(title)
        series_authors.append(authors)
        series_abstract.append(abs)
        series_pdf.append(pdf)
        series_bib.append(bib)
        series_sw.append(sw)
        series_code.append(code)
    df = pandas.DataFrame(
        {
            "title": series_title,
            "authors": series_authors,
            "abstract": series_abstract,
            "pdf": series_pdf,
            "bib": series_bib,
            "sw": series_sw,
            "code": series_code,
        },
        index=range(1, len(series_title) + 1),
    )
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
Extract papsers.csv from ACL Anthology page

Example:
  ac.py https://aclanthology.org/events/acl-2022/#2022-acl-long
  ac.py -s page.html https://aclanthology.org/events/acl-2022/#2022-acl-long
"""
    )
    parser.add_argument("url_or_path", help="URL or file of the ACL page to be extracted")
    parser.add_argument("-s", "--save", help="Save the html data", type=str)
    parser.add_argument("-f", "--file-path", help="Extract from a file", action="store_true")
    args = parser.parse_args()
    if args.file_path is True:
        with open(args.url_or_path, "rt") as f:
            html = f.read()
    else:
        html = GetHtml(args.url_or_path)
        if type(html) != str:
            sys.stderr.write("ERROR: cannot get HTML: status=%d\n" % (html))
            sys.exit(1)
        if type(args.save) == str and args.save != "":
            with open(args.save, "wt") as f:
                f.write(html)
    df = ExtractPapers(html)
    df.to_csv(sys.stdout)
