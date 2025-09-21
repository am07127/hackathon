import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import csv
import urllib.parse

load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")  # e.g. "https://your-domain.atlassian.net/wiki"
USERNAME = os.getenv("CONFLUENCE_USERNAME")
API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

KEYWORD = "knoccs"  # change keyword as needed
SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", None)  # optional: restrict to a space

if not all([CONFLUENCE_URL, USERNAME, API_TOKEN]):
    raise RuntimeError("Missing one of CONFLUENCE_URL, USERNAME, API_TOKEN")

auth = HTTPBasicAuth(USERNAME, API_TOKEN)
headers = {
    "Accept": "application/json"
}

def search_keyword(keyword, space_key=None, limit=25, cursor=None):
    """
    Search pages via CQL for keyword in title or text.
    Returns a JSON response with results, maybe cursor for next.
    """
    # Build CQL
    cql_parts = ['type = page', f'(title ~ "{keyword}" OR text ~ "{keyword}")']
    if space_key:
        cql_parts.append(f'space = "{space_key}"')
    cql_query = " AND ".join(cql_parts)

    params = {
        "cql": cql_query,
        "limit": limit,
        "expand": "version,metadata.labels,space",
    }
    if cursor:
        params["cursor"] = cursor

    url = f"{CONFLUENCE_URL.rstrip('/')}/wiki/rest/api/content/search"
    resp = requests.get(url, headers=headers, auth=auth, params=params)
    resp.raise_for_status()
    return resp.json()

def fetch_content_body(page_id):
    """
    Optional: fetch the body storage (or another representation) for the page
    """
    url = f"{CONFLUENCE_URL.rstrip('/')}/wiki/rest/api/content/{page_id}"
    params = {
        "expand": "body.storage,version,metadata.labels,space"
    }
    resp = requests.get(url, headers=headers, auth=auth, params=params)
    resp.raise_for_status()
    return resp.json()

def export_keyword_results(keyword, space_key=None, output_csv="knoccs_confluence.csv"):
    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "page_id",
            "title",
            "space_key",
            "version_number",
            "labels",
            "excerpt",  # truncated text/body
        ])
        # Pagination
        cursor = None
        while True:
            search_results = search_keyword(keyword, space_key=space_key, limit=25, cursor=cursor)
            results = search_results.get("results", [])
            if not results:
                break

            for item in results:
                page_id = item.get("id")
                title = item.get("title")
                space = item.get("space", {}).get("key") if item.get("space") else ""
                version_num = item.get("version", {}).get("number", "")
                labels = []
                # metadata.labels may be in item, or fetch via expand
                md = item.get("metadata", {}).get("labels", {}).get("results", [])
                if md:
                    labels = [lbl.get("name") for lbl in md]

                # try to get an excerpt / body snippet
                # either from a summary field or fetch full content
                excerpt = ""
                # if item has a body excerpt already
                # often there's no body in search results, so fetch full content
                content = fetch_content_body(page_id)
                body_storage = content.get("body", {}).get("storage", {}).get("value", "")
                if body_storage:
                    # truncate to first 500 chars
                    excerpt = body_storage.replace("\n", " ").strip()[:500]

                writer.writerow([
                    page_id,
                    title,
                    space,
                    version_num,
                    ";".join(labels),
                    excerpt
                ])

            # check for next page in search
            # in cloud API the search with CQL returns a `cursor` or next link
            next_cursor = search_results.get("cursor", None)
            if not next_cursor:
                # older API may use _links.next
                # or break if no more
                break
            cursor = next_cursor

    print(f"Keyword export done, data stored in {output_csv}")

if __name__ == "__main__":
    export_keyword_results(KEYWORD, space_key=SPACE_KEY)
