# sticker-designs

## Colorado DMV Appointment Scraper

This repository contains a web scraping script to help find available DMV appointments in Colorado.

### Quick Start

1. **Verify your setup:**
   ```bash
   python verify_setup.py
   ```

2. **Try the demo (no internet required):**
   ```bash
   python appointment_scraper.py --test
   ```

3. **Run the actual scraper:**
   ```bash
   python appointment_scraper.py
   ```

### Documentation

For detailed instructions, troubleshooting, and usage examples, see [SCRAPER_README.md](SCRAPER_README.md).

### What it does

- Finds earliest available DMV appointments across all Colorado locations
- Exports results to Excel and CSV files
- Shows appointment dates, times, addresses, and distances
- Includes test mode for demonstration

### Need Help?

1. Run `python verify_setup.py` to check your setup
2. Try test mode: `python appointment_scraper.py --test`
3. Read the full documentation: [SCRAPER_README.md](SCRAPER_README.md)
