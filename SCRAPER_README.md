# Colorado DMV Appointment Scraper

This script scrapes appointment availability from the Colorado DMV appointment scheduling system and exports the data to a spreadsheet.

## Features

- Scrapes all office locations from the appointment page
- Checks appointment availability for each location
- Extracts earliest available appointment dates and times
- Captures distance information when available
- Exports data to both Excel (.xlsx) and CSV formats
- Sorts results to show available appointments first
- **Test mode** for demonstration without accessing the actual website

## Requirements

- Python 3.8 or higher
- Chrome or Chromium browser installed
- Internet connection (for actual scraping)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- selenium (web automation)
- pandas (data processing)
- openpyxl (Excel file generation)
- webdriver-manager (automatic ChromeDriver management)
- requests (for connectivity checks)

### 2. Verify Chrome Installation

Make sure Chrome or Chromium is installed on your system:

**Check if Chrome is installed:**
```bash
# On Linux/Mac
which google-chrome chromium chromium-browser

# On Windows (Command Prompt)
where chrome
```

**Install Chrome if needed:**
- **Ubuntu/Debian:** `sudo apt-get install chromium-browser`
- **macOS:** `brew install --cask google-chrome`
- **Windows:** Download from https://www.google.com/chrome/

### 3. Run the Script

**Test mode (no internet required):**
```bash
python appointment_scraper.py --test
```

**Actual scraping:**
```bash
python appointment_scraper.py
```

## Usage Examples

### Basic Usage (Live Scraping)
```bash
python appointment_scraper.py
```

### Test/Demo Mode (No Internet Required)
```bash
python appointment_scraper.py --test
# or
python appointment_scraper.py --demo
```

The script will:
1. Check if the website is accessible (skipped in test mode)
2. Initialize Chrome browser in headless mode
3. Extract all office locations (or use sample data in test mode)
4. Check appointment availability for each office
5. Export results to:
   - `colorado_dmv_appointments.xlsx` (Excel format)
   - `colorado_dmv_appointments.csv` (CSV format)

## Output

The generated spreadsheet includes the following columns:
- **office_name**: Name of the DMV office
- **address**: Full address of the office
- **earliest_date**: The earliest available appointment date
- **earliest_time**: The earliest available appointment time
- **distance**: Distance from your location (if available)
- **status**: Availability status (Available, No availability, etc.)
- **total_slots_found**: Number of appointment slots found

Results are automatically sorted to show available appointments first.

## Advanced Usage

### Running Without Headless Mode (See the Browser)

Edit line 45 in `appointment_scraper.py` and remove or comment out the headless option:
```python
# options.add_argument('--headless=new')  # Comment this out
```

### Changing Output Filename

Edit line 296 to customize the output filename:
```python
scraper.export_to_spreadsheet('my_custom_filename.xlsx')
```

### Adjusting Wait Times

Modify `time.sleep()` calls throughout the script to adjust delays between operations:
- Line 44: Initial page load wait
- Line 100: Wait after clicking office
- Line 117: Wait for appointment data to load
- Line 204: Wait between offices

## Testing Your Setup

**Step 1:** Test with sample data (no internet needed)
```bash
python appointment_scraper.py --test
```
This should create Excel and CSV files with sample data.

**Step 2:** If test mode works, try actual scraping
```bash
python appointment_scraper.py
```

If you see "Website is not accessible", check your internet connection and verify the website URL.

## Troubleshooting

### Common Issues and Solutions

#### 1. "Could not resolve host" or "Website is not accessible"

**Symptoms:** Error message about not being able to connect to the website.

**Solutions:**
- Check your internet connection
- Verify the website URL is still valid by opening it in a browser
- The website might be temporarily down - try again later
- Your network might have firewall restrictions
- Try running in **test mode** to verify the script itself works:
  ```bash
  python appointment_scraper.py --test
  ```

#### 2. "ChromeDriver" or "Chrome" errors

**Symptoms:** Errors mentioning ChromeDriver, Chrome version mismatch, or browser not found.

**Solutions:**
1. Make sure Chrome/Chromium is installed:
   ```bash
   # Check installation
   which google-chrome chromium
   
   # Install if needed (Ubuntu/Debian)
   sudo apt-get install chromium-browser
   ```

2. Update webdriver-manager:
   ```bash
   pip install --upgrade selenium webdriver-manager
   ```

3. If issues persist, manually install ChromeDriver:
   ```bash
   # macOS
   brew install chromedriver
   
   # Linux - download from https://chromedriver.chromium.org/
   ```

#### 3. "No module named 'selenium'" or import errors

**Symptoms:** Python can't find required packages.

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

#### 4. Script hangs or takes too long

**Symptoms:** Script seems to freeze or doesn't complete.

**Solutions:**
- Press `Ctrl+C` to stop the script safely
- The website might be slow - this is normal, give it time
- Check if the website is accessible in your browser first
- Run in test mode to verify the script logic works

#### 5. No data in output files or "No appointments available"

**Symptoms:** Script completes but no meaningful data is collected.

**Possible causes:**
- The website structure may have changed
- All offices genuinely have no appointments
- The scraping selectors need updating

**Solutions:**
- Verify the website works in a regular browser
- Check if the website layout has changed
- Open an issue if the script needs updating for website changes

## Notes

- The script runs in headless mode by default (no visible browser window)
- It includes delays to be respectful to the server
- Results are sorted to show available appointments first
- Both Excel and CSV formats are generated for compatibility
- ChromeDriver is automatically managed by webdriver-manager (no manual installation needed)
- The script includes connectivity checks before attempting to scrape

## Customization

You can modify the script to:
- Change the output filename (line 296)
- Adjust wait times (various `time.sleep()` calls)
- Remove headless mode to see the browser (line 45)
- Modify which data fields are captured
- Add additional office information or filters

## Legal & Ethical Considerations

- This script is for **personal use only**
- Be respectful of the website's resources
- Don't run the script too frequently (recommended: no more than once per hour)
- Check the website's Terms of Service before use
- The script includes rate limiting to avoid overwhelming the server

## Getting Help

If you encounter issues:

1. **First, try test mode:** `python appointment_scraper.py --test`
2. **Check the troubleshooting section above**
3. **Verify your setup:**
   - Python 3.8+ installed: `python --version`
   - Dependencies installed: `pip list | grep selenium`
   - Chrome installed: `which google-chrome`
4. **Read error messages carefully** - they often indicate exactly what's wrong
5. **Check internet connection** if you see connectivity errors

## What This Script Does NOT Do

- It does NOT automatically book appointments (it only finds them)
- It does NOT bypass CAPTCHAs or authentication
- It does NOT guarantee appointments will be available
- It does NOT modify or interact with the website beyond viewing public data
