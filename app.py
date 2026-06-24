from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from concurrent.futures import ThreadPoolExecutor
import os
import threading

app = Flask(__name__)
CORS(app)

# Global tracker for load management
active_requests = 0
MAX_CONCURRENT = 40 

SOURCES = {
    "GitHub": "https://github.com/search?q=",
    "GitLab": "https://gitlab.com/search?search=",
    "Codeberg": "https://codeberg.org/explore/repos?q=",
    "SourceHut": "https://sr.ht/projects?search=",
    "Gitea": "https://gitea.com/explore/repos?q=",
    "Bitbucket": "https://bitbucket.org/repo/all?name=",
    "Launchpad": "https://launchpad.net/+search?field.text=",
    "SourceForge": "https://sourceforge.net/directory/?q=",
    "F-Droid": "https://search.f-droid.org/?q=",
    "Flathub": "https://flathub.org/apps/search?q=",
    "Snapcraft": "https://snapcraft.io/search?q=",
    "DebianPackages": "https://packages.debian.org/search?keywords=",
    "ArchPackages": "https://archlinux.org/packages/?q=",
    "FedoraPackages": "https://packages.fedoraproject.org/search?query=",
    "GentooPackages": "https://packages.gentoo.org/packages/search?q=",
    "NixOS": "https://search.nixos.org/packages?query=",
    "KernelOrg": "https://www.kernel.org/search/?q=",
    "AppleOpenSource": "https://opensource.apple.com/projects/?q=",
    "WebKit": "https://webkit.org/?s=",
    "SwiftOrg": "https://www.swift.org/search/?q=",
    "SwiftPackages": "https://swiftpackageindex.com/search?query=",
    "AOSP": "https://source.android.com/search?q=",
    "AndroidDev": "https://developer.android.com/s/results?q=",
    "ArchWiki": "https://wiki.archlinux.org/index.php?search=",
    "StackOverflow": "https://stackoverflow.com/search?q=",
    "MDN": "https://developer.mozilla.org/en-US/search?q=",
    "PythonDocs": "https://docs.python.org/3/search.html?q=",
    "RustDocs": "https://docs.rs/releases/search?query=",
    "DevTo": "https://dev.to/search?q=",
    "Wikipedia": "https://en.wikipedia.org/w/index.php?search=",
    "Archive": "https://archive.org/search?query=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
    "Brave": "https://search.brave.com/search?q=",
    "Proton": "https://proton.me/search?q=",
    "NewPipe": "https://newpipe.net/search?q=",
    "LibreTube": "https://yewtu.be/search?q=",
    "DataGovIndia": "https://data.gov.in/catalog?query=",
    "IndiaGov": "https://www.india.gov.in/search/site?keys=",
    "USAGov": "https://www.usa.gov/search?q=",
    "EUOpenData": "https://data.europa.eu/en/datasets?query=",
    "UNData": "http://data.un.org/Data.aspx?q=",
    "WorldBank": "https://data.worldbank.org/indicator?q=",
    "NASAOpenData": "https://data.nasa.gov/browse?q=",
    "ProPublica": "https://www.propublica.org/search?q=",
    "TheIntercept": "https://theintercept.com/search/?s=",
    "DemocracyNow": "https://www.democracynow.org/search?query=",
    "WikiNews": "https://en.wikinews.org/wiki/Special:Search?search=",
    "ArchiveNews": "https://archive.org/details/tv?q=",
    "ProjectGutenberg": "https://www.gutenberg.org/ebooks/search/?query=",
    "OpenLibrary": "https://openlibrary.org/search?q=",
    "InternetArchive": "https://archive.org/search?query=",
    "DOAJ": "https://doaj.org/search/articles?ref=homepage&source=1&q=",
    "SciHub": "https://sci-hub.se/",
    "Peertube": "https://sepiasearch.org/search?search=",
    "RadioBrowser": "https://www.radio-browser.info/search?name="
}

def fetch_from_source(source_info, query):
    name, base_url = source_info
    url = f"{base_url}{query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        requests.get(url, headers=headers, timeout=5)
        return {"source": name, "status": "Success", "link": url}
    except Exception as e:
        return {"source": name, "status": "Failed"}

@app.route('/health')
def health():
    global active_requests
    return jsonify({"status": "BUSY" if active_requests >= MAX_CONCURRENT else "FREE"})

@app.route('/search')
def search():
    global active_requests
    if active_requests >= MAX_CONCURRENT:
        return jsonify({"error": "Server Busy"}), 503
        
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query required"}), 400
        
    active_requests += 1
    try:
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(lambda s: fetch_from_source(s, query), SOURCES.items()))
        return jsonify({"results": results})
    finally:
        active_requests -= 1

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
