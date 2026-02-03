"""
Google Search Console - Full Audit Exporter
Automates browser to export:
1. Top Linking Sites (Links report) → Top Links folder
2. Page Indexing/Coverage report → Pages folder (ZIP)
"""

import asyncio
import os
import re
import json
import datetime
from pathlib import Path
from urllib.parse import quote, unquote
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
BASE_DIR = Path(__file__).parent
USER_DATA_DIR = BASE_DIR / "browser_session"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"

# Google account index (u/0, u/1, u/2, etc.) - change if using different account
ACCOUNT_INDEX = "2"

# Base URLs with account index
GSC_BASE_URL = f"https://search.google.com/u/{ACCOUNT_INDEX}/search-console"
GSC_WELCOME_URL = f"{GSC_BASE_URL}/welcome"
GSC_INDEX_URL = f"{GSC_BASE_URL}/index"  # Page Indexing
GSC_LINKS_URL = f"{GSC_BASE_URL}/links/drilldown"  # Top Links


def load_credentials():
    """Load credentials from JSON file (gitignored)."""
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return None


def extract_domain(property_url):
    """Extract clean domain name from property URL."""
    domain = property_url.replace('https://', '').replace('http://', '')
    domain = domain.replace('sc-domain:', '')
    domain = domain.rstrip('/')
    return domain


async def wait_for_download(page, click_action, timeout=30000):
    """Helper to handle download after a click action."""
    try:
        async with page.expect_download(timeout=timeout) as download_info:
            await click_action()
        return await download_info.value
    except Exception as e:
        print(f"    Download error: {e}")
        return None


async def export_links_report(page, property_url, output_path, date_str):
    """
    Export Top Linking Sites from the Links report.
    """
    domain = extract_domain(property_url)

    # Build the correct URL format: sc-domain:domain.com
    resource_id = f"sc-domain:{domain}"
    encoded_resource = quote(resource_id, safe='')

    # Use the correct links drilldown URL with all required params
    links_url = f"{GSC_LINKS_URL}?resource_id={encoded_resource}&type=DOMAIN&target=&domain="

    try:
        await page.goto(links_url)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)

        # Find and click the Export button
        export_clicked = False

        # Try to find export button by looking for the icon/button in the toolbar
        # GSC uses material icons, the export is usually a download arrow
        export_selectors = [
            'span.izuYW',  # GSC export button class
            '[aria-label*="xport"]',
            '[aria-label*="ownload"]',
            'button[aria-label*="xport"]',
            'button[aria-label*="ownload"]',
            '[data-tooltip*="xport"]',
            'button:has-text("Export")',
            '.Lj2aab button',
            'button.VfPpkd-LgbsSe',
        ]

        for selector in export_selectors:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    export_clicked = True
                    await page.wait_for_timeout(500)
                    break
            except:
                continue

        if not export_clicked:
            # Try finding by icon - look for download/export icons
            buttons = page.locator('button')
            count = await buttons.count()
            for i in range(count):
                btn = buttons.nth(i)
                try:
                    # Check for aria-label or inner content suggesting export
                    aria = await btn.get_attribute('aria-label') or ''
                    if 'export' in aria.lower() or 'download' in aria.lower():
                        await btn.click()
                        export_clicked = True
                        await page.wait_for_timeout(500)
                        break
                except:
                    continue

        if not export_clicked:
            print(f"    Could not find export button for Links")
            return False

        # Handle the dropdown menu - look for CSV option
        download = None
        csv_selectors = [
            'text="Download CSV"',
            'text="CSV"',
            '[role="menuitem"]:has-text("CSV")',
            'a:has-text("CSV")',
            '.VfPpkd-StrnGf-rymPhb-ibnC6b:has-text("CSV")',  # Material menu item
        ]

        for selector in csv_selectors:
            try:
                csv_opt = page.locator(selector).first
                if await csv_opt.is_visible(timeout=1000):
                    download = await wait_for_download(page, lambda: csv_opt.click())
                    break
            except:
                continue

        if download:
            filename = f"{domain}-Top linking sites-{date_str}.csv"
            save_path = output_path / "Top Links" / filename
            await download.save_as(save_path)
            print(f"    [Links] Saved: {filename}")
            return True
        else:
            print(f"    [Links] Could not complete download")
            return False

    except Exception as e:
        print(f"    [Links] Error: {e}")
        return False


async def export_indexing_report(page, property_url, output_path, date_str):
    """
    Export Page Indexing (Coverage) report as ZIP.
    """
    domain = extract_domain(property_url)

    # Build the correct URL format: sc-domain:domain.com
    resource_id = f"sc-domain:{domain}"
    encoded_resource = quote(resource_id, safe='')

    # Use the correct page indexing URL
    indexing_url = f"{GSC_INDEX_URL}?resource_id={encoded_resource}"

    try:
        await page.goto(indexing_url)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)

        # Find and click the Export button
        export_clicked = False

        export_selectors = [
            'span.izuYW',  # GSC export button class
            '[aria-label*="xport"]',
            '[aria-label*="ownload"]',
            'button[aria-label*="xport"]',
            'button[aria-label*="ownload"]',
            '[data-tooltip*="xport"]',
            'button:has-text("Export")',
            '.Lj2aab button',
            'button.VfPpkd-LgbsSe',
        ]

        for selector in export_selectors:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    export_clicked = True
                    await page.wait_for_timeout(500)
                    break
            except:
                continue

        if not export_clicked:
            buttons = page.locator('button')
            count = await buttons.count()
            for i in range(count):
                btn = buttons.nth(i)
                try:
                    aria = await btn.get_attribute('aria-label') or ''
                    if 'export' in aria.lower() or 'download' in aria.lower():
                        await btn.click()
                        export_clicked = True
                        await page.wait_for_timeout(500)
                        break
                except:
                    continue

        if not export_clicked:
            print(f"    Could not find export button for Indexing")
            return False

        # Wait for menu to appear after clicking export
        await page.wait_for_timeout(1000)

        # The indexing export shows a dropdown menu - need to click "Download CSV"
        download = None

        # Use same selectors that work for Links export
        csv_selectors = [
            'text="Download CSV"',
            'text="CSV"',
            '[role="menuitem"]:has-text("CSV")',
            '[role="menuitem"]:has-text("Download")',
            'a:has-text("CSV")',
            '.VfPpkd-StrnGf-rymPhb-ibnC6b:has-text("CSV")',
        ]

        for selector in csv_selectors:
            try:
                csv_opt = page.locator(selector).first
                if await csv_opt.is_visible(timeout=1000):
                    download = await wait_for_download(page, lambda c=csv_opt: c.click(), timeout=15000)
                    if download:
                        break
            except:
                continue

        if download:
            # The file might be a zip or csv - check the suggested filename
            suggested = download.suggested_filename
            if suggested.endswith('.zip'):
                filename = f"{domain}-Coverage-{date_str}.zip"
            else:
                filename = f"{domain}-Coverage-{date_str}.csv"

            save_path = output_path / "Pages" / filename
            await download.save_as(save_path)
            print(f"    [Indexing] Saved: {filename}")
            return True
        else:
            print(f"    [Indexing] Could not complete download")
            return False

    except Exception as e:
        print(f"    [Indexing] Error: {e}")
        return False


async def discover_properties(page):
    """
    Discover all properties from the GSC homepage.
    Returns a list of property URLs.
    """
    properties = []

    try:
        # Navigate to the Search Console welcome/homepage which lists all properties
        await page.goto(GSC_WELCOME_URL)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)

        # Find all property links on the page
        # GSC homepage shows property cards with links containing resource_id
        property_links = page.locator('a[href*="resource_id="]')
        count = await property_links.count()

        print(f"  Found {count} property links on homepage...")

        for i in range(count):
            try:
                href = await property_links.nth(i).get_attribute('href')
                if href and 'resource_id=' in href:
                    # Extract the resource_id (URL-encoded property URL)
                    start = href.find('resource_id=') + len('resource_id=')
                    end = href.find('&', start) if '&' in href[start:] else len(href)
                    resource_id = href[start:end]
                    # Decode the URL
                    from urllib.parse import unquote
                    property_url = unquote(resource_id)
                    if property_url and property_url not in properties:
                        properties.append(property_url)
            except Exception as e:
                continue

        # If we didn't find properties via links, try the property selector dropdown
        if not properties:
            print("  Trying property selector dropdown...")
            # Look for the property selector and click it
            selector = page.locator('[data-property-selector], .ScResourceSelector').first
            if await selector.is_visible(timeout=2000):
                await selector.click()
                await page.wait_for_timeout(1000)

                # Get items from dropdown
                items = page.locator('[role="menuitem"], [role="option"]')
                item_count = await items.count()

                for i in range(item_count):
                    try:
                        text = await items.nth(i).inner_text()
                        if text and ('http' in text.lower() or '.com' in text or '.org' in text or '.net' in text):
                            # Clean up the text to get the URL
                            prop = text.strip().split('\n')[0].strip()
                            if prop and prop not in properties:
                                properties.append(prop)
                    except:
                        continue

                await page.keyboard.press('Escape')

    except Exception as e:
        print(f"  Error discovering properties: {e}")

    return properties


def filter_properties(properties, excluded_domains):
    """Filter out excluded domains from the properties list."""
    filtered = []
    for prop in properties:
        # Check if any excluded domain is in this property URL
        is_excluded = any(excl.lower() in prop.lower() for excl in excluded_domains)
        if not is_excluded:
            filtered.append(prop)
    return filtered


async def run_full_audit(properties=None, output_folder_name=None, headless=False,
                         export_links=True, export_indexing=True):
    """
    Run full audit export for all properties.

    Args:
        properties: List of property URLs (optional - uses fallback list if not provided)
        output_folder_name: Custom folder name (default: auto-generated)
        headless: Run without browser window (default: True)
        export_links: Export Top Linking Sites
        export_indexing: Export Page Indexing/Coverage
    """
    if output_folder_name is None:
        month_name = datetime.date.today().strftime('%B %Y')
        output_folder_name = f'GSC Audit {month_name}'

    output_path = BASE_DIR / output_folder_name
    date_str = datetime.date.today().strftime('%Y-%m-%d')

    # Create folder structure
    (output_path / "Top Links").mkdir(parents=True, exist_ok=True)
    (output_path / "Pages").mkdir(parents=True, exist_ok=True)
    (output_path / "Reports").mkdir(parents=True, exist_ok=True)

    print(f"Output folder: {output_path}")
    print("-" * 60)

    USER_DATA_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        # Launch with settings to avoid bot detection
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=headless,
            accept_downloads=True,
            viewport={'width': 1280, 'height': 900},
            # Anti-bot detection settings
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ],
            ignore_default_args=['--enable-automation'],
            chromium_sandbox=False,
        )

        page = await browser.new_page()

        # Remove webdriver property to avoid detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Navigate to GSC and handle login
        print("Navigating to Google Search Console...")
        await page.goto(GSC_WELCOME_URL)
        await page.wait_for_load_state('networkidle')

        if 'accounts.google.com' in page.url or 'signin' in page.url.lower():
            print("\nLogin required. Attempting automated login...")

            # Load credentials
            creds = load_credentials()
            if creds:
                try:
                    # Wait for email input
                    email_input = page.locator('input[type="email"]')
                    await email_input.wait_for(timeout=10000)
                    await email_input.fill(creds['email'])
                    print(f"  Entered email: {creds['email']}")

                    # Click Next
                    await page.locator('#identifierNext, button:has-text("Next")').click()
                    await page.wait_for_timeout(3000)

                    # Wait for password input
                    password_input = page.locator('input[type="password"]')
                    await password_input.wait_for(timeout=10000)
                    await password_input.fill(creds['password'])
                    print("  Entered password")

                    # Click Next/Sign in
                    await page.locator('#passwordNext, button:has-text("Next"), button:has-text("Sign in")').click()
                    await page.wait_for_timeout(5000)

                    print("  Login submitted, waiting for redirect...")

                except Exception as e:
                    print(f"  Automated login failed: {e}")
                    print("  Please complete login manually in the browser.")
                    if not headless:
                        input("  Press Enter after you've logged in...")
            else:
                print("  No credentials file found. Please login manually.")
                if not headless:
                    input("  Press Enter after you've logged in...")

            # Wait for redirect and navigation
            await page.wait_for_timeout(5000)

            # Navigate to Search Console welcome page if not already there
            if 'search.google.com' not in page.url or 'search-console' not in page.url:
                await page.goto(GSC_WELCOME_URL)
                await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)

            # Check if login succeeded
            if 'accounts.google.com' in page.url:
                print("\n  WARNING: Still on login page. Google may have blocked automated login.")
                print("  Try running with --no-headless to complete login manually.")
                if headless:
                    await browser.close()
                    return {'error': 'Login blocked by Google'}

        # Use provided properties or fallback list (skip auto-discovery - it doesn't work reliably)
        if properties is None:
            properties = filter_properties(PROPERTIES, EXCLUDED_DOMAINS)
            print(f"\nUsing property list: {len(properties)} properties (after exclusions)")

        print(f"\nProperties to process: {len(properties)}")
        print(f"Exports: Links={export_links}, Indexing={export_indexing}")
        print("-" * 60)

        # Track results
        results = {
            'links_success': 0,
            'links_failed': [],
            'indexing_success': 0,
            'indexing_failed': []
        }

        for i, prop in enumerate(properties, 1):
            domain = extract_domain(prop)
            print(f"\n[{i}/{len(properties)}] {domain}")

            if export_links:
                success = await export_links_report(page, prop, output_path, date_str)
                if success:
                    results['links_success'] += 1
                else:
                    results['links_failed'].append(domain)

            if export_indexing:
                success = await export_indexing_report(page, prop, output_path, date_str)
                if success:
                    results['indexing_success'] += 1
                else:
                    results['indexing_failed'].append(domain)

            # Small delay between properties
            await page.wait_for_timeout(1500)

        await browser.close()

        # Print summary
        print("\n" + "=" * 60)
        print("AUDIT EXPORT COMPLETE")
        print("=" * 60)

        if export_links:
            print(f"\nTop Links: {results['links_success']}/{len(properties)} successful")
            if results['links_failed']:
                print(f"  Failed: {', '.join(results['links_failed'][:5])}" +
                      ("..." if len(results['links_failed']) > 5 else ""))

        if export_indexing:
            print(f"\nPage Indexing: {results['indexing_success']}/{len(properties)} successful")
            if results['indexing_failed']:
                print(f"  Failed: {', '.join(results['indexing_failed'][:5])}" +
                      ("..." if len(results['indexing_failed']) > 5 else ""))

        print(f"\nOutput: {output_path}")

        return results


# Properties to EXCLUDE from processing
EXCLUDED_DOMAINS = [
    "vs3.net",
    "personalwebsites.org",
    "personalwebsites.net",
    "drymyhands.com",
    "friendshiprecession.com",
    "jondeutser.com",
    "laurendeutser.com",
    "blakedeutser.com",
]

# All properties (excluding the ones above)
PROPERTIES = [
    "https://adambuice.com/",
    "https://adamlgerber.com/",
    "https://adamrozan.com/",
    "https://aidenfishbein.com/",
    "https://alexlieberman.com/",
    "https://andrewkanderson.com/",
    "https://andriayu.com/",
    "https://andysommer.com/",
    "https://aniawysocka.com/",
    "https://annepalermo.com/",
    "https://austinrief.com/",
    "https://aymanalabdullah.com/",
    "https://barbruhis.com/",
    "https://benjaminpeacehoffman.com/",
    "https://braelinnfrank.com/",
    "https://brianleenash.com/",
    "https://burns.gg/",
    "https://carolinabaffigo.com/",
    "https://catediaz.com/",
    "https://cathrynlavery.com/",
    "https://cherylannconnects.com/",
    "https://chrisgittings.com/",
    "https://chrispetkas.com/",
    "https://chrissparling.net/",
    "https://collinwmartin.com/",
    "https://courtneyjohnsonnews.com/",
    "https://danlerman.com/",
    "https://davidlkirkpatrick.com/",
    "https://davidshapiro.co/",
    "https://dustinhyle.com/",
    "https://edwindorsey.com/",
    "https://ericmelchor.com/",
    "https://geneseidman.com/",
    "https://gregcook.me/",
    "https://hannahmelody.com/",
    "https://itschadrubin.com/",
    "https://itslaurengoldstein.com/",
    "https://jacobvoncannon.com/",
    "https://jasonyoong.com/",
    "https://jennykaehms.com/",
    "https://johnarrow.com/",
    "https://johnwbrandes.com/",
    "https://jonathanwegener.com/",
    "https://jordanferney.com/",
    "https://kaycierobinsonsendero.com/",
    "https://malonedetecting.com/",
    "https://mattgronberg.com/",
    "https://meghanraftery.com/",
    "https://michaeldelamaza.com/",
    "https://michaelgalpert.com/",
    "https://mikesmith.me/",
    "https://monicalim.co/",
    "https://nickchristensen.co/",
    "https://nikhulewsky.com/",
    "https://noahberkson.com/",
    "https://peterknox.com/",
    "https://pieceofpai.com/",
    "https://pradeepnalluri.com/",
    "https://randallettinger.com/",
    "https://randlarsen.com/",
    "https://realbenalbert.com/",
    "https://rickyschay.com/",
    "https://rondarbouze.com/",
    "https://ryanbed.org/",
    "https://sameerkirtane.com/",
    "https://saulz.com/",
    "https://shaggyeells.com/",
    "https://shanefarmer.com/",
    "https://shlomoschreibman.net/",
    "https://skylarromines.com/",
    "https://sorenarnsbo.com/",
    "https://taylorjacobson.org/",
    "https://theadamrobinson.com/",
    "https://thearisohn.com/",
    "https://thebenhirsch.com/",
    "https://thenicolerojas.com/",
    "https://tjlarkin.com/",
    "https://trevormccandless.com/",
    "https://zain-jaffer.com/",
    "https://zubilashafiq.com/",
]


def get_active_properties():
    """Return properties list excluding the excluded domains."""
    return [p for p in PROPERTIES if not any(excl in p for excl in EXCLUDED_DOMAINS)]


def get_previous_month_folder():
    """Find the previous month's audit folder."""
    today = datetime.date.today()
    # Get previous month
    if today.month == 1:
        prev_month = 12
        prev_year = today.year - 1
    else:
        prev_month = today.month - 1
        prev_year = today.year

    prev_month_name = datetime.date(prev_year, prev_month, 1).strftime('%B %Y')
    prev_folder = BASE_DIR / f'GSC Audit {prev_month_name}'

    if prev_folder.exists():
        return prev_folder
    return None


def read_csv_files(folder_path, subfolder):
    """Read all CSV files from a subfolder and return combined content."""
    csv_folder = folder_path / subfolder
    if not csv_folder.exists():
        return ""

    content = []
    for csv_file in sorted(csv_folder.glob('*.csv')):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                content.append(f"=== {csv_file.name} ===\n{file_content}\n")
        except Exception as e:
            print(f"  Warning: Could not read {csv_file.name}: {e}")

    return "\n".join(content)


def get_anthropic_client():
    """Get Anthropic client, checking for API key in credentials or environment."""
    try:
        import anthropic
    except ImportError:
        print("  Anthropic SDK not installed. Run: pip install anthropic")
        return None

    # Check credentials file for API key
    api_key = None
    if CREDENTIALS_FILE.exists():
        creds = load_credentials()
        if creds and 'anthropic_api_key' in creds:
            api_key = creds['anthropic_api_key']

    # Fall back to environment variable
    if not api_key:
        api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        print("  No Anthropic API key found.")
        print("  Add 'anthropic_api_key' to credentials.json or set ANTHROPIC_API_KEY environment variable.")
        return None

    return anthropic.Anthropic(api_key=api_key)


def run_claude_analysis(output_path, export_links=True, export_indexing=True):
    """
    Run Claude to analyze the exported data and generate reports.
    """
    reports_folder = output_path / "Reports"
    reports_folder.mkdir(exist_ok=True)

    # Get Anthropic client
    client = get_anthropic_client()
    if not client:
        print("  Skipping analysis (no API client available).")
        return

    # Get previous month's folder for comparison
    prev_folder = get_previous_month_folder()
    prev_report_content = ""
    if prev_folder:
        prev_report_file = prev_folder / "Reports" / "TopLinks_Analysis_Report.md"
        if prev_report_file.exists():
            with open(prev_report_file, 'r', encoding='utf-8') as f:
                prev_report_content = f.read()
            print(f"  Found previous report: {prev_report_file.name}")

    current_month = datetime.date.today().strftime('%B %Y')
    date_str = datetime.date.today().strftime('%Y-%m-%d')

    # Generate Top Links Analysis Report
    if export_links:
        print("\nGenerating Top Links Analysis Report...")

        # Read all Top Links CSVs
        top_links_data = read_csv_files(output_path, "Top Links")

        if top_links_data:
            prompt = f"""Analyze the following Google Search Console Top Linking Sites data for {current_month}.

## Current Month Data ({current_month}):
{top_links_data[:50000]}

## Previous Month Report (for comparison):
{prev_report_content[:20000] if prev_report_content else "No previous report available."}

Generate a comprehensive analysis report in Markdown format similar to the previous report structure. Include:
1. Overview Statistics (total domains, unique linking sites, etc.)
2. Top 10 Most Common Linking Sites
3. Month-over-month trend analysis (improvements, stable, decreases)
4. Domains with most/fewest linking sites
5. Link quality categories (high-authority, quality business, profile/directory)
6. New domains and domains no longer in network
7. Summary of changes
8. Recommendations

Format the report professionally with tables, headers, and clear sections."""

            try:
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                if message.content:
                    report_content = message.content[0].text
                    report_file = reports_folder / "TopLinks_Analysis_Report.md"
                    with open(report_file, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                    print(f"  Saved: {report_file.name}")
                else:
                    print("  No response from Claude")

            except Exception as e:
                print(f"  Claude analysis error: {e}")

    # Generate Indexing Analysis Report
    if export_indexing:
        print("\nGenerating Indexing Analysis Report...")

        # For indexing, we need to read ZIP files - for now just note what was exported
        pages_folder = output_path / "Pages"
        if pages_folder.exists():
            zip_files = list(pages_folder.glob('*.zip'))
            csv_files = list(pages_folder.glob('*.csv'))

            indexing_summary = f"Exported {len(zip_files)} ZIP files and {len(csv_files)} CSV files.\n\n"
            indexing_summary += "Files exported:\n"
            for f in sorted(zip_files + csv_files)[:50]:
                indexing_summary += f"- {f.name}\n"

            # Get previous indexing report if exists
            prev_indexing_report = ""
            if prev_folder:
                prev_idx_file = prev_folder / "Reports" / "Indexing_Analysis_Report.md"
                if prev_idx_file.exists():
                    with open(prev_idx_file, 'r', encoding='utf-8') as f:
                        prev_indexing_report = f.read()

            prompt = f"""Analyze the following Google Search Console Page Indexing data export for {current_month}.

## Current Month Export Summary:
{indexing_summary}

## Previous Month Report (for comparison):
{prev_indexing_report[:10000] if prev_indexing_report else "No previous indexing report available."}

Generate an Indexing Analysis Report in Markdown format. Include:
1. Overview of exported data
2. Summary of indexing status across all properties
3. Month-over-month comparison (if previous data available)
4. Properties that may need attention
5. Recommendations for improving indexing

Note: The actual ZIP files contain detailed indexing data that would need to be extracted for full analysis."""

            try:
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                if message.content:
                    report_content = message.content[0].text
                    report_file = reports_folder / "Indexing_Analysis_Report.md"
                    with open(report_file, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                    print(f"  Saved: {report_file.name}")
                else:
                    print("  No response from Claude")

            except Exception as e:
                print(f"  Claude analysis error: {e}")

    print(f"\nReports saved to: {reports_folder}")


def push_to_github(output_path):
    """
    Commit and push the audit data to GitHub.
    """
    import subprocess

    print("\n" + "=" * 60)
    print("PUSHING TO GITHUB")
    print("=" * 60)

    try:
        # Get current month for commit message
        current_month = datetime.date.today().strftime('%B %Y')

        # Stage the audit folder
        folder_name = output_path.name
        subprocess.run(['git', 'add', folder_name], cwd=str(BASE_DIR), check=True)
        subprocess.run(['git', 'add', 'CHANGELOG.md'], cwd=str(BASE_DIR), check=False)  # If exists

        # Create commit
        commit_msg = f"""Add {current_month} GSC Audit data

- Top Links exports
- Page Indexing exports
- Analysis reports

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"""

        result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("  Committed changes")

            # Push to remote
            push_result = subprocess.run(
                ['git', 'push'],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True
            )

            if push_result.returncode == 0:
                print("  Pushed to GitHub successfully!")
            else:
                print(f"  Push failed: {push_result.stderr[:200]}")
        else:
            if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                print("  No new changes to commit")
            else:
                print(f"  Commit failed: {result.stderr[:200]}")

    except subprocess.CalledProcessError as e:
        print(f"  Git error: {e}")
    except FileNotFoundError:
        print("  Git not found in PATH")
    except Exception as e:
        print(f"  Error: {e}")


def get_audit_folders():
    """Get list of existing audit folders."""
    folders = []
    for item in BASE_DIR.iterdir():
        if item.is_dir() and item.name.startswith('GSC Audit'):
            folders.append(item)
    return sorted(folders, reverse=True)  # Most recent first


def display_menu():
    """Display the main menu and get user choice."""
    print("\n" + "=" * 60)
    print("   GSC AUDIT TOOL - MAIN MENU")
    print("=" * 60)
    print("\n  1. Full Audit (Export + Analysis + Push to GitHub)")
    print("  2. Export Only (Top Links + Indexing)")
    print("  3. Export Top Links Only")
    print("  4. Export Indexing Only")
    print("  5. Run Analysis Only (on existing data)")
    print("  6. Push to GitHub Only")
    print("  0. Exit")
    print("\n" + "-" * 60)

    while True:
        try:
            choice = input("Enter your choice (0-6): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6']:
                return choice
            print("Invalid choice. Please enter 0-6.")
        except KeyboardInterrupt:
            return '0'


def select_folder_menu():
    """Display folder selection menu."""
    folders = get_audit_folders()

    print("\n" + "-" * 60)
    print("SELECT AUDIT FOLDER")
    print("-" * 60)

    # Option for current month
    current_month = datetime.date.today().strftime('%B %Y')
    current_folder_name = f'GSC Audit {current_month}'
    print(f"\n  1. Current month ({current_folder_name})")

    # List existing folders
    if folders:
        print("\n  Existing folders:")
        for i, folder in enumerate(folders, 2):
            print(f"  {i}. {folder.name}")

    print(f"\n  0. Cancel")
    print("-" * 60)

    while True:
        try:
            choice = input("Enter your choice: ").strip()
            if choice == '0':
                return None
            if choice == '1':
                return BASE_DIR / current_folder_name
            idx = int(choice) - 2
            if 0 <= idx < len(folders):
                return folders[idx]
            print("Invalid choice.")
        except (ValueError, KeyboardInterrupt):
            return None


def select_analysis_type_menu():
    """Select which analysis to run."""
    print("\n" + "-" * 60)
    print("SELECT ANALYSIS TYPE")
    print("-" * 60)
    print("\n  1. Both (Top Links + Indexing)")
    print("  2. Top Links Only")
    print("  3. Indexing Only")
    print("  0. Cancel")
    print("-" * 60)

    while True:
        try:
            choice = input("Enter your choice (0-3): ").strip()
            if choice == '0':
                return None, None
            if choice == '1':
                return True, True
            if choice == '2':
                return True, False
            if choice == '3':
                return False, True
            print("Invalid choice.")
        except KeyboardInterrupt:
            return None, None


def run_interactive():
    """Run the tool with interactive menu."""

    while True:
        choice = display_menu()

        if choice == '0':
            print("\nGoodbye!")
            break

        elif choice == '1':
            # Full Audit
            print("\n" + "=" * 60)
            print("FULL AUDIT MODE")
            print("=" * 60)

            month_name = datetime.date.today().strftime('%B %Y')
            output_folder_name = f'GSC Audit {month_name}'
            output_path = BASE_DIR / output_folder_name

            print(f"Output folder: {output_folder_name}")
            print(f"Excluded domains: {', '.join(EXCLUDED_DOMAINS)}")

            # Run export
            results = asyncio.run(run_full_audit(
                properties=None,
                output_folder_name=output_folder_name,
                headless=True,
                export_links=True,
                export_indexing=True
            ))

            # Run analysis
            if results and (not isinstance(results, dict) or 'error' not in results):
                run_claude_analysis(output_path, export_links=True, export_indexing=True)

            # Push to GitHub
            push_to_github(output_path)

            print("\n" + "=" * 60)
            print("FULL AUDIT COMPLETE!")
            print("=" * 60)

        elif choice == '2':
            # Export Only (both)
            month_name = datetime.date.today().strftime('%B %Y')
            output_folder_name = f'GSC Audit {month_name}'

            print(f"\nExporting to: {output_folder_name}")

            asyncio.run(run_full_audit(
                properties=None,
                output_folder_name=output_folder_name,
                headless=True,
                export_links=True,
                export_indexing=True
            ))

        elif choice == '3':
            # Export Top Links Only
            month_name = datetime.date.today().strftime('%B %Y')
            output_folder_name = f'GSC Audit {month_name}'

            print(f"\nExporting Top Links to: {output_folder_name}")

            asyncio.run(run_full_audit(
                properties=None,
                output_folder_name=output_folder_name,
                headless=True,
                export_links=True,
                export_indexing=False
            ))

        elif choice == '4':
            # Export Indexing Only
            month_name = datetime.date.today().strftime('%B %Y')
            output_folder_name = f'GSC Audit {month_name}'

            print(f"\nExporting Indexing to: {output_folder_name}")

            asyncio.run(run_full_audit(
                properties=None,
                output_folder_name=output_folder_name,
                headless=True,
                export_links=False,
                export_indexing=True
            ))

        elif choice == '5':
            # Analysis Only
            folder = select_folder_menu()
            if folder is None:
                continue

            if not folder.exists():
                print(f"\nFolder does not exist: {folder}")
                print("Please run an export first.")
                continue

            # Check if folder has data
            top_links_folder = folder / "Top Links"
            pages_folder = folder / "Pages"

            has_links = top_links_folder.exists() and any(top_links_folder.glob('*.csv'))
            has_indexing = pages_folder.exists() and (any(pages_folder.glob('*.zip')) or any(pages_folder.glob('*.csv')))

            if not has_links and not has_indexing:
                print(f"\nNo data found in {folder.name}")
                print("Please run an export first.")
                continue

            # Select analysis type
            analyze_links, analyze_indexing = select_analysis_type_menu()
            if analyze_links is None:
                continue

            # Validate selection
            if analyze_links and not has_links:
                print("\nNo Top Links data found. Skipping Top Links analysis.")
                analyze_links = False
            if analyze_indexing and not has_indexing:
                print("\nNo Indexing data found. Skipping Indexing analysis.")
                analyze_indexing = False

            if not analyze_links and not analyze_indexing:
                print("\nNothing to analyze.")
                continue

            print(f"\nRunning analysis on: {folder.name}")
            run_claude_analysis(folder, export_links=analyze_links, export_indexing=analyze_indexing)

            # Ask if user wants to push
            push_choice = input("\nPush to GitHub? (y/n): ").strip().lower()
            if push_choice == 'y':
                push_to_github(folder)

        elif choice == '6':
            # Push to GitHub Only
            folder = select_folder_menu()
            if folder is None:
                continue

            if not folder.exists():
                print(f"\nFolder does not exist: {folder}")
                continue

            push_to_github(folder)

        input("\nPress Enter to continue...")


if __name__ == '__main__':
    import sys

    # Check for --menu or no arguments to run interactive mode
    if len(sys.argv) == 1 or '--menu' in sys.argv:
        run_interactive()
    else:
        # Legacy CLI mode for backwards compatibility
        import argparse

        parser = argparse.ArgumentParser(description='GSC Full Audit Export')
        parser.add_argument('--folder', '-f', help='Output folder name')
        parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode (default)')
        parser.add_argument('--no-headless', action='store_true', help='Run with visible browser window')
        parser.add_argument('--links-only', action='store_true', help='Only export Links report')
        parser.add_argument('--indexing-only', action='store_true', help='Only export Indexing report')
        parser.add_argument('--no-analysis', action='store_true', help='Skip Claude analysis')
        parser.add_argument('--no-push', action='store_true', help='Skip pushing to GitHub')
        parser.add_argument('--menu', action='store_true', help='Run interactive menu')

        args = parser.parse_args()

        export_links = not args.indexing_only
        export_indexing = not args.links_only
        headless = not args.no_headless

        print(f"Excluded domains: {', '.join(EXCLUDED_DOMAINS)}")
        print(f"Headless mode: {headless}")

        # Determine output folder
        if args.folder:
            output_folder_name = args.folder
        else:
            month_name = datetime.date.today().strftime('%B %Y')
            output_folder_name = f'GSC Audit {month_name}'

        output_path = BASE_DIR / output_folder_name

        # Run the export
        results = asyncio.run(run_full_audit(
            properties=None,
            output_folder_name=output_folder_name,
            headless=headless,
            export_links=export_links,
            export_indexing=export_indexing
        ))

        # Run Claude analysis if not skipped
        if not args.no_analysis and results and (not isinstance(results, dict) or 'error' not in results):
            run_claude_analysis(output_path, export_links=export_links, export_indexing=export_indexing)

        # Push to GitHub if not skipped
        if not args.no_push:
            push_to_github(output_path)

        print("\n" + "=" * 60)
        print("ALL DONE!")
        print("=" * 60)
