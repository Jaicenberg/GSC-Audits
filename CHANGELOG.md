# GSC Audit Tool - Changelog

## [1.2.0] - 2026-02-03

### Added
- Interactive menu system (runs by default when no arguments provided)
- Menu options:
  - Full Audit (Export + Analysis + Push)
  - Export Only (Top Links + Indexing)
  - Export Top Links Only
  - Export Indexing Only
  - Analysis Only (select existing folder + analysis type)
  - Push to GitHub Only
- Folder selection menu showing all existing audit folders
- Analysis type selection (both, Top Links only, Indexing only)

### Changed
- Default mode is now interactive menu
- CLI arguments still work for automation/scripting

## [1.1.0] - 2026-02-03

### Added
- Automated Claude analysis after export completion
- Generates two reports per audit:
  - `TopLinks_Analysis_Report.md` - Analysis of backlinks with month-over-month comparison
  - `Indexing_Analysis_Report.md` - Analysis of page indexing status
- Reports saved to `Reports/` folder in each month's audit directory
- Comparison with previous month's data when available

### Fixed
- Export button detection using `.izuYW` class selector
- "Download CSV" menu item selection for both Links and Indexing exports
- Removed unreliable auto-discovery, now uses property list directly
- Correct URL patterns with `/u/2/` account index and `sc-domain:` prefix

### Changed
- Headless mode enabled by default
- Automated login with credentials file (gitignored)
- Streamlined startup - no more waiting for property discovery

## [1.0.0] - 2026-02-03

### Initial Release
- Browser automation for GSC exports using Playwright
- Export Top Linking Sites (CSV) for all properties
- Export Page Indexing/Coverage (ZIP) for all properties
- Support for ~80 properties with exclusion list
- Persistent browser session (login saved)
- Anti-bot detection measures for Google login

### Configuration
- Properties to exclude: vs3.net, personalwebsites.org, personalwebsites.net, drymyhands.com, friendshiprecession.com, jondeutser.com, laurendeutser.com, blakedeutser.com
- Google account index: `/u/2/`
