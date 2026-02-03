"""
Google Search Console Monthly Audit Tool
Automates export of Top Links, Performance Data, and Indexing Status
"""

import os
import json
import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd

# Configuration
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CLIENT_SECRET_FILE = 'Service Account Key/client_secret_247867919393-a2l0cc43ub41c4n03vovc69m4a0bpcnh.apps.googleusercontent.com.json'
TOKEN_FILE = 'Service Account Key/token.json'

# Base directory
BASE_DIR = Path(__file__).parent


def get_credentials():
    """Get or refresh OAuth credentials."""
    creds = None
    token_path = BASE_DIR / TOKEN_FILE
    client_secret_path = BASE_DIR / CLIENT_SECRET_FILE

    # Load existing token if available
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            print("Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("Credentials saved for future runs.")

    return creds


def get_all_properties(service):
    """Get list of all Search Console properties."""
    sites = service.sites().list().execute()
    properties = []

    for site in sites.get('siteEntry', []):
        site_url = site['siteUrl']
        permission = site['permissionLevel']
        properties.append({
            'url': site_url,
            'permission': permission
        })

    print(f"Found {len(properties)} properties")
    return properties


def extract_domain_name(site_url):
    """Extract clean domain name from site URL."""
    # Remove protocol and trailing slashes
    domain = site_url.replace('https://', '').replace('http://', '')
    domain = domain.replace('sc-domain:', '')  # Handle domain properties
    domain = domain.rstrip('/')
    return domain


def get_top_linking_sites(service, site_url):
    """Get top external linking sites for a property."""
    try:
        # External links - sites linking to this property
        response = service.searchanalytics().query(
            siteUrl=site_url,
            body={
                'startDate': '2020-01-01',
                'endDate': datetime.date.today().isoformat(),
                'dimensions': ['page'],
                'type': 'web',
                'rowLimit': 1000
            }
        ).execute()

        # The links API is separate - use the links endpoint
        links = service.links().list(siteUrl=site_url).execute()

        # Process external links
        external_links = []
        for link in links.get('externalLinks', []):
            external_links.append({
                'Site': link.get('targetUrl', ''),
                'Linking pages': link.get('linkCount', 0),
                'Target pages': link.get('targetCount', 1)
            })

        return external_links
    except Exception as e:
        print(f"  Error getting links for {site_url}: {e}")
        return []


def get_top_linking_sites_v2(service, site_url):
    """Get top external linking sites using the correct API endpoint."""
    try:
        # Get external links (sites linking TO this property)
        external_response = service.urlcrawlerrorssamples()  # This doesn't exist

        # Actually, we need to use a different approach
        # The Search Console API has limited link data access
        # Let's try the searchanalytics approach for what's available

        return []
    except Exception as e:
        print(f"  Error: {e}")
        return []


def get_links_data(service, site_url):
    """
    Get linking data for a property.
    Note: The full links report requires using the Search Console web interface export
    or the newer API endpoints.
    """
    links_data = {
        'external_sites': [],
        'external_pages': [],
        'internal_links': []
    }

    try:
        # Try to get links data - this uses internal API structure
        # External linking sites
        request_body = {
            "startDate": "2020-01-01",
            "endDate": datetime.date.today().isoformat(),
        }

        # The links data is available through a different method
        # Using the sites().get() to check property info first
        site_info = service.sites().get(siteUrl=site_url).execute()

        return links_data
    except Exception as e:
        print(f"  Links API error for {site_url}: {e}")
        return links_data


def get_performance_data(service, site_url, days=28):
    """Get performance data (clicks, impressions, CTR, position)."""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)

    try:
        response = service.searchanalytics().query(
            siteUrl=site_url,
            body={
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'dimensions': ['query'],
                'type': 'web',
                'rowLimit': 1000
            }
        ).execute()

        rows = []
        for row in response.get('rows', []):
            rows.append({
                'Query': row['keys'][0],
                'Clicks': row.get('clicks', 0),
                'Impressions': row.get('impressions', 0),
                'CTR': round(row.get('ctr', 0) * 100, 2),
                'Position': round(row.get('position', 0), 1)
            })

        return rows
    except Exception as e:
        print(f"  Error getting performance for {site_url}: {e}")
        return []


def get_performance_by_page(service, site_url, days=28):
    """Get performance data grouped by page."""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)

    try:
        response = service.searchanalytics().query(
            siteUrl=site_url,
            body={
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'dimensions': ['page'],
                'type': 'web',
                'rowLimit': 1000
            }
        ).execute()

        rows = []
        for row in response.get('rows', []):
            rows.append({
                'Page': row['keys'][0],
                'Clicks': row.get('clicks', 0),
                'Impressions': row.get('impressions', 0),
                'CTR': round(row.get('ctr', 0) * 100, 2),
                'Position': round(row.get('position', 0), 1)
            })

        return rows
    except Exception as e:
        print(f"  Error getting page performance for {site_url}: {e}")
        return []


def inspect_url(service, site_url, page_url):
    """Inspect a single URL for indexing status."""
    try:
        response = service.urlInspection().index().inspect(
            body={
                'inspectionUrl': page_url,
                'siteUrl': site_url
            }
        ).execute()

        result = response.get('inspectionResult', {})
        index_status = result.get('indexStatusResult', {})

        return {
            'URL': page_url,
            'Coverage State': index_status.get('coverageState', 'Unknown'),
            'Indexing State': index_status.get('indexingState', 'Unknown'),
            'Last Crawl Time': index_status.get('lastCrawlTime', ''),
            'Page Fetch State': index_status.get('pageFetchState', ''),
            'Robots Txt State': index_status.get('robotsTxtState', ''),
        }
    except Exception as e:
        return {
            'URL': page_url,
            'Coverage State': f'Error: {str(e)[:50]}',
            'Indexing State': '',
            'Last Crawl Time': '',
            'Page Fetch State': '',
            'Robots Txt State': '',
        }


def run_audit(output_folder=None, include_performance=True, include_indexing=False, sample_urls_per_site=5):
    """
    Run the full GSC audit for all properties.

    Args:
        output_folder: Custom output folder name (default: auto-generated based on month)
        include_performance: Include performance data export
        include_indexing: Include URL inspection (slower, uses quota)
        sample_urls_per_site: Number of URLs to inspect per site for indexing status
    """
    # Setup output folder
    if output_folder is None:
        month_name = datetime.date.today().strftime('%B %Y')
        output_folder = f'GSC Audit {month_name}'

    output_path = BASE_DIR / output_folder
    top_links_path = output_path / 'Top Links'
    performance_path = output_path / 'Performance'
    indexing_path = output_path / 'Indexing'

    # Create directories
    output_path.mkdir(exist_ok=True)
    top_links_path.mkdir(exist_ok=True)
    if include_performance:
        performance_path.mkdir(exist_ok=True)
    if include_indexing:
        indexing_path.mkdir(exist_ok=True)

    print(f"Output folder: {output_path}")
    print("-" * 50)

    # Authenticate
    creds = get_credentials()
    service = build('searchconsole', 'v1', credentials=creds)

    # Get all properties
    properties = get_all_properties(service)

    date_str = datetime.date.today().strftime('%Y-%m-%d')

    # Summary data for consolidated report
    summary_data = []

    for i, prop in enumerate(properties, 1):
        site_url = prop['url']
        domain = extract_domain_name(site_url)

        print(f"\n[{i}/{len(properties)}] Processing: {domain}")

        # Get performance data first (to identify top pages for indexing check)
        perf_data = []
        if include_performance or include_indexing:
            perf_data = get_performance_by_page(service, site_url)

            if include_performance and perf_data:
                perf_df = pd.DataFrame(perf_data)
                perf_file = performance_path / f"{domain}-Performance-{date_str}.csv"
                perf_df.to_csv(perf_file, index=False)
                print(f"  Saved performance data ({len(perf_data)} pages)")

        # Get query performance
        if include_performance:
            query_data = get_performance_data(service, site_url)
            if query_data:
                query_df = pd.DataFrame(query_data)
                query_file = performance_path / f"{domain}-Queries-{date_str}.csv"
                query_df.to_csv(query_file, index=False)
                print(f"  Saved query data ({len(query_data)} queries)")

        # URL Inspection (sample top pages)
        if include_indexing and perf_data:
            top_pages = [p['Page'] for p in perf_data[:sample_urls_per_site]]
            indexing_results = []

            for page_url in top_pages:
                result = inspect_url(service, site_url, page_url)
                indexing_results.append(result)

            if indexing_results:
                idx_df = pd.DataFrame(indexing_results)
                idx_file = indexing_path / f"{domain}-Indexing-{date_str}.csv"
                idx_df.to_csv(idx_file, index=False)
                print(f"  Saved indexing data ({len(indexing_results)} URLs)")

        # Calculate summary stats
        total_clicks = sum(p.get('Clicks', 0) for p in perf_data) if perf_data else 0
        total_impressions = sum(p.get('Impressions', 0) for p in perf_data) if perf_data else 0

        summary_data.append({
            'Property': domain,
            'URL': site_url,
            'Permission': prop['permission'],
            'Pages with Data': len(perf_data) if perf_data else 0,
            'Total Clicks (28d)': total_clicks,
            'Total Impressions (28d)': total_impressions,
        })

    # Save summary report
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_file = output_path / f"Audit_Summary-{date_str}.csv"
        summary_df.to_csv(summary_file, index=False)
        print(f"\n{'='*50}")
        print(f"Summary saved: {summary_file}")

    print(f"\nAudit complete! {len(properties)} properties processed.")
    print(f"Output: {output_path}")


def get_external_links_report(service, site_url):
    """
    Attempt to get external links using available API methods.
    Note: Full links report may require manual export from GSC UI.
    """
    # The Search Console API v1 doesn't expose the full Links report
    # that's available in the web UI. This is a known limitation.
    #
    # Options:
    # 1. Use searchanalytics to get pages with traffic (indirect indicator)
    # 2. Use URL inspection API for specific URLs
    # 3. Manual export from UI for the links report
    #
    # The links() method existed in older API versions but is not in v1

    return None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Google Search Console Monthly Audit')
    parser.add_argument('--folder', '-f', help='Output folder name (default: auto-generated)')
    parser.add_argument('--no-performance', action='store_true', help='Skip performance data')
    parser.add_argument('--indexing', action='store_true', help='Include URL inspection (slower)')
    parser.add_argument('--sample-urls', type=int, default=5, help='URLs to inspect per site')

    args = parser.parse_args()

    run_audit(
        output_folder=args.folder,
        include_performance=not args.no_performance,
        include_indexing=args.indexing,
        sample_urls_per_site=args.sample_urls
    )
