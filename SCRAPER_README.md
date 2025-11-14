# Colorado DMV Appointment Scraper

This script scrapes appointment availability from the Colorado DMV appointment scheduling system and exports the data to a spreadsheet.

## Features

- Scrapes all office locations from the appointment page
- Checks appointment availability for each location
- Extracts earliest available appointment dates and times
- Captures distance information when available
- Exports data to both Excel (.xlsx) and CSV formats
- Sorts results to show available appointments first

## Requirements

- Python 3.8 or higher
- Chrome or Chromium browser installed
- ChromeDriver (will be handled automatically with webdriver-manager)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. If you don't have Chrome installed, install it:
   - macOS: Download from https://www.google.com/chrome/
   - Or use Homebrew: `brew install --cask google-chrome`

## Usage

Run the scraper:
```bash
python appointment_scraper.py
```

The script will:
1. Load the appointment scheduling page
2. Extract all office locations
3. Check appointment availability for each office
4. Export results to `colorado_dmv_appointments.xlsx` and `colorado_dmv_appointments.csv`

## Output

The generated spreadsheet includes the following columns:
- **office_name**: Name of the DMV office
- **address**: Full address of the office
- **earliest_date**: The earliest available appointment date
- **earliest_time**: The earliest available appointment time
- **distance**: Distance from your location (if available)
- **status**: Availability status (Available, No availability, etc.)
- **total_slots_found**: Number of appointment slots found

## Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver issues, install it manually:
```bash
brew install chromedriver
```

### Selenium Import Errors
Make sure all dependencies are installed:
```bash
pip install --upgrade selenium pandas openpyxl webdriver-manager
```

### Website Changes
If the script stops working, the website structure may have changed. You may need to update the CSS selectors in the script.

## Notes

- The script runs in headless mode (no browser window)
- It includes delays to be respectful to the server
- Results are sorted to show available appointments first
- Both Excel and CSV formats are generated for compatibility

## Customization

You can modify the script to:
- Change the output filename (line 323)
- Adjust wait times (various `time.sleep()` calls)
- Remove headless mode to see the browser (line 24)
- Modify which data fields are captured

## Legal & Ethical Considerations

- This script is for personal use only
- Be respectful of the website's resources
- Don't run the script too frequently
- Check the website's Terms of Service before use
