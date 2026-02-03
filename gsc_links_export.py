"""
Google Search Console - Links Report Exporter
Automates browser to export Top Linking Sites for all properties
"""

import asyncio
import os
import shutil
import datetime
from pathlib import Path
from urllib.parse import quote
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
BASE_DIR = Path(__file__).parent
USER_DATA_DIR = BASE_DIR / "browser_session"
DOWNLOAD_DIR = BASE_DIR / "downloads_temp"


async def get_all_properties(page):
    """
    Get list of all Search Console properties from the property selector.
    """
    properties = []

    # Click the property selector dropdown
    try:
        # Wait for the page to be fully loaded
        await page.wait_for_load_state('networkidle')

        # The property selector is usually in the top-left area
        # Look for the dropdown button that shows current property
        selector_button = page.locator('[data-resource-selector]').first
        if not await selector_button.is_visible():
            # Try alternative selector
            selector_button = page.locator('.ScResourceSelector').first

        if not await selector_button.is_visible():
            # Another alternative - look for the property name area
            selector_button = page.locator('[role="button"]').filter(has_text=".com").first

        await selector_button.click()
        await page.wait_for_timeout(1000)

        # Get all property items from the dropdown
        property_items = page.locator('[role="menuitem"], [role="option"], .ScResourceSelectorItem')
        count = await property_items.count()

        for i in range(count):
            item = property_items.nth(i)
            text = await item.inner_text()
            # Extract the URL/domain from the text
            if text and ('http' in text.lower() or '.' in text):
                properties.append(text.strip())

        # Close dropdown by pressing Escape
        await page.keyboard.press('Escape')

    except Exception as e:
        print(f"Error getting properties from dropdown: {e}")
        print("Will try to get properties from the Search Console API list instead...")

    return properties


async def get_properties_from_homepage(page):
    """
    Alternative: Get properties from the Search Console homepage property list.
    """
    properties = []

    try:
        await page.goto('https://search.google.com/search-console')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)

        # Look for property cards/links on the homepage
        property_links = page.locator('a[href*="resource_id="]')
        count = await property_links.count()

        for i in range(count):
            href = await property_links.nth(i).get_attribute('href')
            if href and 'resource_id=' in href:
                # Extract the resource_id (URL-encoded property URL)
                start = href.find('resource_id=') + len('resource_id=')
                end = href.find('&', start) if '&' in href[start:] else len(href)
                resource_id = href[start:end]
                # Decode the URL
                from urllib.parse import unquote
                property_url = unquote(resource_id)
                if property_url not in properties:
                    properties.append(property_url)

    except Exception as e:
        print(f"Error getting properties from homepage: {e}")

    return properties


async def export_links_for_property(page, property_url, output_folder, date_str):
    """
    Navigate to a property's Links report and export the Top Linking Sites CSV.
    """
    # URL-encode the property URL for the GSC URL
    encoded_property = quote(property_url, safe='')

    # Construct the Links report URL
    links_url = f"https://search.google.com/search-console/links?resource_id={encoded_property}"

    try:
        print(f"  Navigating to Links report...")
        await page.goto(links_url)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)

        # Check if we're on the right page
        if 'links' not in page.url.lower():
            print(f"  Warning: May not be on Links page. Current URL: {page.url}")
            return False

        # Look for the Export button
        # GSC typically has an export button with a download icon or "EXPORT" text
        export_button = None

        # Try various selectors for the export button
        selectors_to_try = [
            'button:has-text("Export")',
            '[aria-label="Export"]',
            '[aria-label="Download"]',
            'button:has-text("Download")',
            '[data-tooltip="Export"]',
            '.export-button',
            'button[jsname]'  # GSC often uses jsname attributes
        ]

        for selector in selectors_to_try:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    export_button = btn
                    break
            except:
                continue

        if not export_button:
            # Try looking for any button with download/export icon
            all_buttons = page.locator('button')
            count = await all_buttons.count()
            for i in range(count):
                btn = all_buttons.nth(i)
                try:
                    aria = await btn.get_attribute('aria-label') or ''
                    text = await btn.inner_text() or ''
                    if 'export' in aria.lower() or 'export' in text.lower() or 'download' in aria.lower():
                        export_button = btn
                        break
                except:
                    continue

        if export_button:
            print(f"  Found export button, clicking...")

            # Set up download handling
            async with page.expect_download(timeout=30000) as download_info:
                await export_button.click()

                # Sometimes there's a dropdown menu after clicking export
                await page.wait_for_timeout(500)

                # Look for "Download CSV" or similar option in dropdown
                csv_option = page.locator('text=CSV').first
                if await csv_option.is_visible(timeout=2000):
                    await csv_option.click()
                else:
                    # Try other patterns
                    csv_patterns = ['text="Download CSV"', 'text="Export CSV"', '[role="menuitem"]:has-text("CSV")']
                    for pattern in csv_patterns:
                        try:
                            opt = page.locator(pattern).first
                            if await opt.is_visible(timeout=500):
                                await opt.click()
                                break
                        except:
                            continue

            download = await download_info.value

            # Extract domain name for filename
            domain = property_url.replace('https://', '').replace('http://', '')
            domain = domain.replace('sc-domain:', '').rstrip('/')

            # Create filename matching their format
            filename = f"{domain}-Top linking sites-{date_str}.csv"
            save_path = output_folder / filename

            await download.save_as(save_path)
            print(f"  Saved: {filename}")
            return True

        else:
            print(f"  Could not find export button")
            return False

    except PlaywrightTimeout as e:
        print(f"  Timeout error: {e}")
        return False
    except Exception as e:
        print(f"  Error exporting: {e}")
        return False


async def run_export(output_folder_name=None, headless=False):
    """
    Main export function.

    Args:
        output_folder_name: Custom output folder (default: auto-generated)
        headless: Run browser in headless mode (default: False for first run to allow login)
    """
    # Setup output folder
    if output_folder_name is None:
        month_name = datetime.date.today().strftime('%B %Y')
        output_folder_name = f'GSC Audit {month_name}'

    output_path = BASE_DIR / output_folder_name / 'Top Links'
    output_path.mkdir(parents=True, exist_ok=True)

    date_str = datetime.date.today().strftime('%Y-%m-%d')

    print(f"Output folder: {output_path}")
    print("-" * 50)

    # Create browser session directory
    USER_DATA_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        # Launch browser with persistent context (saves login)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=headless,
            accept_downloads=True,
            viewport={'width': 1280, 'height': 800}
        )

        page = await browser.new_page()

        # Navigate to Search Console
        print("Navigating to Google Search Console...")
        await page.goto('https://search.google.com/search-console')
        await page.wait_for_load_state('networkidle')

        # Check if we need to log in
        if 'accounts.google.com' in page.url or 'signin' in page.url.lower():
            print("\n" + "="*50)
            print("LOGIN REQUIRED")
            print("="*50)
            print("Please log in to your Google account in the browser window.")
            print("After logging in, press Enter here to continue...")
            print("="*50 + "\n")

            # Wait for user to log in
            input("Press Enter after you've logged in...")

            # Navigate to Search Console again after login
            await page.goto('https://search.google.com/search-console')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)

        # Get list of properties
        print("\nGetting list of properties...")
        properties = await get_properties_from_homepage(page)

        if not properties:
            print("Could not automatically detect properties.")
            print("Trying alternative method...")
            properties = await get_all_properties(page)

        if not properties:
            print("\nCould not detect properties automatically.")
            print("Please enter property URLs manually (one per line, empty line to finish):")
            while True:
                prop = input("> ").strip()
                if not prop:
                    break
                properties.append(prop)

        print(f"\nFound {len(properties)} properties")

        # Export links for each property
        successful = 0
        failed = []

        for i, prop in enumerate(properties, 1):
            print(f"\n[{i}/{len(properties)}] {prop}")

            success = await export_links_for_property(page, prop, output_path, date_str)

            if success:
                successful += 1
            else:
                failed.append(prop)

            # Small delay between properties to avoid rate limiting
            await page.wait_for_timeout(1000)

        # Close browser
        await browser.close()

        # Summary
        print("\n" + "="*50)
        print("EXPORT COMPLETE")
        print("="*50)
        print(f"Successful: {successful}/{len(properties)}")
        print(f"Output: {output_path}")

        if failed:
            print(f"\nFailed exports ({len(failed)}):")
            for f in failed:
                print(f"  - {f}")

        return successful, failed


async def run_with_property_list(properties, output_folder_name=None, headless=False):
    """
    Run export for a specific list of properties.
    Use this if automatic detection doesn't work.
    """
    if output_folder_name is None:
        month_name = datetime.date.today().strftime('%B %Y')
        output_folder_name = f'GSC Audit {month_name}'

    output_path = BASE_DIR / output_folder_name / 'Top Links'
    output_path.mkdir(parents=True, exist_ok=True)

    date_str = datetime.date.today().strftime('%Y-%m-%d')

    print(f"Output folder: {output_path}")
    print(f"Properties to export: {len(properties)}")
    print("-" * 50)

    USER_DATA_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=headless,
            accept_downloads=True,
            viewport={'width': 1280, 'height': 800}
        )

        page = await browser.new_page()

        # Navigate to Search Console and handle login
        await page.goto('https://search.google.com/search-console')
        await page.wait_for_load_state('networkidle')

        if 'accounts.google.com' in page.url or 'signin' in page.url.lower():
            print("\nPlease log in to your Google account in the browser window.")
            print("Press Enter after you've logged in...")
            input()
            await page.goto('https://search.google.com/search-console')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)

        successful = 0
        failed = []

        for i, prop in enumerate(properties, 1):
            print(f"\n[{i}/{len(properties)}] {prop}")
            success = await export_links_for_property(page, prop, output_path, date_str)

            if success:
                successful += 1
            else:
                failed.append(prop)

            await page.wait_for_timeout(1000)

        await browser.close()

        print(f"\n{'='*50}")
        print(f"Successful: {successful}/{len(properties)}")
        print(f"Output: {output_path}")

        return successful, failed


# List of all 80 properties (extracted from January audit)
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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Export GSC Links Reports')
    parser.add_argument('--folder', '-f', help='Output folder name')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (not recommended for first run)')
    parser.add_argument('--auto-detect', action='store_true', help='Auto-detect properties instead of using built-in list')

    args = parser.parse_args()

    if args.auto_detect:
        asyncio.run(run_export(
            output_folder_name=args.folder,
            headless=args.headless
        ))
    else:
        asyncio.run(run_with_property_list(
            PROPERTIES,
            output_folder_name=args.folder,
            headless=args.headless
        ))
