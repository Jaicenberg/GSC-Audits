"""
Google Search Console - Full Audit Exporter
Automates browser to export:
1. Top Linking Sites (Links report) → Top Links folder
2. Page Indexing/Coverage report → Pages folder (ZIP)
"""

import asyncio
import os
import re
import datetime
from pathlib import Path
from urllib.parse import quote, unquote
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
BASE_DIR = Path(__file__).parent
USER_DATA_DIR = BASE_DIR / "browser_session"


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
    encoded_property = quote(property_url, safe='')
    links_url = f"https://search.google.com/search-console/links?resource_id={encoded_property}"
    domain = extract_domain(property_url)

    try:
        await page.goto(links_url)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)

        # Find and click the Export button
        export_clicked = False

        # Try to find export button by looking for the icon/button in the toolbar
        # GSC uses material icons, the export is usually a download arrow
        export_selectors = [
            'button[aria-label*="xport"]',
            'button[aria-label*="ownload"]',
            '[data-tooltip*="xport"]',
            'button:has-text("Export")',
            # GSC specific - look for the toolbar button
            '.Lj2aab button',  # Common GSC button container
            'button.VfPpkd-LgbsSe',  # Material button class
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
    encoded_property = quote(property_url, safe='')
    # The indexing report URL
    indexing_url = f"https://search.google.com/search-console/index?resource_id={encoded_property}"
    domain = extract_domain(property_url)

    try:
        await page.goto(indexing_url)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)

        # Find and click the Export button
        export_clicked = False

        export_selectors = [
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

        # The indexing export might directly download or show options
        # Try to catch the download
        download = None

        # First check if there's a menu with options
        menu_selectors = [
            'text="Download"',
            '[role="menuitem"]',
            '.VfPpkd-StrnGf-rymPhb-ibnC6b',
        ]

        for selector in menu_selectors:
            try:
                opt = page.locator(selector).first
                if await opt.is_visible(timeout=1000):
                    download = await wait_for_download(page, lambda: opt.click())
                    if download:
                        break
            except:
                continue

        # If no menu appeared, the export might have started directly
        if not download:
            try:
                # Wait a bit for any automatic download
                async with page.expect_download(timeout=5000) as download_info:
                    pass  # Download may have already started
                download = await download_info.value
            except:
                pass

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
        # Navigate to the Search Console homepage which lists all properties
        await page.goto('https://search.google.com/search-console')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)

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
                         export_links=True, export_indexing=True, auto_discover=True):
    """
    Run full audit export for all properties.

    Args:
        properties: List of property URLs (optional - will auto-discover if not provided)
        output_folder_name: Custom folder name (default: auto-generated)
        headless: Run without browser window (not recommended for first run)
        export_links: Export Top Linking Sites
        export_indexing: Export Page Indexing/Coverage
        auto_discover: Auto-discover properties from GSC (default: True)
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
        await page.goto('https://search.google.com/search-console')
        await page.wait_for_load_state('networkidle')

        if 'accounts.google.com' in page.url or 'signin' in page.url.lower():
            print("\n" + "=" * 60)
            print("LOGIN REQUIRED")
            print("=" * 60)
            print("Complete the login in the browser window:")
            print("  1. Enter your email: ash@nickgray.net")
            print("  2. Enter your password")
            print("  3. Complete any 2FA/CAPTCHA if prompted")
            print("  4. Wait until you see the Search Console dashboard")
            print("\nTake your time - the browser will wait.")
            print("=" * 60)
            input("\nPress Enter here AFTER you see the Search Console dashboard...")

            # Give extra time for any redirects
            await page.wait_for_timeout(2000)

            # Navigate to Search Console if not already there
            if 'search.google.com/search-console' not in page.url:
                await page.goto('https://search.google.com/search-console')
                await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)

        # Auto-discover properties if not provided
        if properties is None or auto_discover:
            print("\nDiscovering properties from your GSC account...")
            discovered = await discover_properties(page)

            if discovered:
                # Filter out excluded domains
                properties = filter_properties(discovered, EXCLUDED_DOMAINS)
                print(f"  Discovered: {len(discovered)} properties")
                print(f"  After exclusions: {len(properties)} properties")
            else:
                print("  Could not auto-discover properties.")
                if properties is None:
                    print("  Using fallback property list...")
                    properties = filter_properties(PROPERTIES, EXCLUDED_DOMAINS)

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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='GSC Full Audit Export')
    parser.add_argument('--folder', '-f', help='Output folder name')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--links-only', action='store_true', help='Only export Links report')
    parser.add_argument('--indexing-only', action='store_true', help='Only export Indexing report')
    parser.add_argument('--use-fallback-list', action='store_true',
                        help='Use the hardcoded fallback property list instead of auto-discovery')

    args = parser.parse_args()

    export_links = not args.indexing_only
    export_indexing = not args.links_only

    print(f"Excluded domains: {', '.join(EXCLUDED_DOMAINS)}")

    if args.use_fallback_list:
        # Use the hardcoded list
        active_properties = get_active_properties()
        print(f"Using fallback list: {len(active_properties)} properties\n")
        asyncio.run(run_full_audit(
            properties=active_properties,
            output_folder_name=args.folder,
            headless=args.headless,
            export_links=export_links,
            export_indexing=export_indexing,
            auto_discover=False
        ))
    else:
        # Auto-discover from GSC
        print("Will auto-discover all properties from your GSC account.\n")
        asyncio.run(run_full_audit(
            properties=None,
            output_folder_name=args.folder,
            headless=args.headless,
            export_links=export_links,
            export_indexing=export_indexing,
            auto_discover=True
        ))
