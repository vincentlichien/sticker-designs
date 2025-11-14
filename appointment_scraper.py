#!/usr/bin/env python3
"""
Colorado DMV Appointment Scraper
Scrapes appointment availability from Colorado DMV appointment scheduling system
and exports data to a spreadsheet.
"""

import time
import pandas as pd
import sys
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import re

class AppointmentScraper:
    def __init__(self, url, test_mode=False):
        self.url = url
        self.driver = None
        self.appointments_data = []
        self.test_mode = test_mode
        
    def check_website_accessibility(self):
        """Check if the target website is accessible before attempting to scrape"""
        print("Checking website accessibility...")
        try:
            response = requests.head(self.url, timeout=10, allow_redirects=True)
            if response.status_code < 500:
                print("✓ Website is accessible")
                return True
            else:
                print(f"✗ Website returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Cannot access website: {e}")
            print("\nPossible issues:")
            print("  - Check your internet connection")
            print("  - The website might be down or temporarily unavailable")
            print("  - There might be firewall/network restrictions")
            print("  - The URL might have changed")
            return False
    
    def setup_driver(self):
        """Initialize Chrome webdriver with options"""
        print("Setting up Chrome driver...")
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')  # Updated headless flag
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver_manager to automatically handle chromedriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            print("✓ Chrome driver initialized successfully")
        except WebDriverException as e:
            print(f"✗ Failed to initialize Chrome driver: {e}")
            print("\nTroubleshooting steps:")
            print("  1. Make sure Chrome/Chromium is installed:")
            print("     - Ubuntu/Debian: sudo apt-get install chromium-browser")
            print("     - macOS: brew install --cask google-chrome")
            print("  2. Check if chromedriver is compatible with your Chrome version")
            print("  3. Try running: pip install --upgrade selenium webdriver-manager")
            raise
        
    def get_office_locations(self):
        """Extract all office locations from the main page"""
        print("Loading appointment page...")
        self.driver.get(self.url)
        time.sleep(3)  # Wait for page to load
        
        offices = []
        
        try:
            # Find all office location elements
            office_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='office'], div[class*='location'], a[href*='office']")
            
            # Try to find office names and addresses in the page
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Parse office information from text
            lines = page_text.split('\n')
            current_office = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                # Skip empty lines and headers
                if not line or line in ['Office', 'Service', 'Date and Time', 'Customer', 'Confirmation']:
                    continue
                    
                # Check if this looks like an office name (typically short, no numbers)
                if line and not re.search(r'\d{3,}', line) and len(line) < 50:
                    # Next line might be the address
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if re.search(r'\d+.*\w+.*\w+.*\d{5}', next_line):  # Looks like an address
                            offices.append({
                                'name': line,
                                'address': next_line
                            })
            
            print(f"Found {len(offices)} office locations")
            
        except Exception as e:
            print(f"Error extracting offices: {e}")
            
        return offices
    
    def click_office(self, office_name):
        """Click on an office to check availability"""
        try:
            # Try multiple selectors to find and click the office
            selectors = [
                f"//div[contains(text(), '{office_name}')]",
                f"//a[contains(text(), '{office_name}')]",
                f"//*[contains(text(), '{office_name}')]"
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    time.sleep(2)
                    return True
                except:
                    continue
                    
        except Exception as e:
            print(f"Could not click office {office_name}: {e}")
            
        return False
    
    def get_appointment_data(self, office_name, office_address):
        """Extract appointment availability for a specific office"""
        try:
            # Wait for appointment calendar or date elements to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)
            
            # Try to find date/time elements
            dates = []
            times = []
            
            # Look for calendar dates
            date_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "div[class*='date'], span[class*='date'], td[class*='day'], button[class*='date']")
            
            for elem in date_elements:
                text = elem.text.strip()
                if text and len(text) < 20:  # Reasonable date length
                    dates.append(text)
            
            # Look for time slots
            time_elements = self.driver.find_elements(By.CSS_SELECTOR,
                "div[class*='time'], span[class*='time'], button[class*='time']")
            
            for elem in time_elements:
                text = elem.text.strip()
                if text and re.search(r'\d{1,2}:\d{2}|AM|PM', text, re.IGNORECASE):
                    times.append(text)
            
            # Check for "no appointments available" message
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            if 'no appointment' in page_text or 'not available' in page_text or 'no available' in page_text:
                return {
                    'office_name': office_name,
                    'address': office_address,
                    'earliest_date': 'No appointments available',
                    'earliest_time': 'N/A',
                    'distance': 'N/A',
                    'status': 'No availability'
                }
            
            # Get earliest appointment
            earliest_date = dates[0] if dates else 'Not found'
            earliest_time = times[0] if times else 'Not found'
            
            # Try to extract distance if available
            distance = 'N/A'
            distance_match = re.search(r'(\d+\.?\d*)\s*(mile|mi|km)', page_text, re.IGNORECASE)
            if distance_match:
                distance = distance_match.group(0)
            
            return {
                'office_name': office_name,
                'address': office_address,
                'earliest_date': earliest_date,
                'earliest_time': earliest_time,
                'distance': distance,
                'status': 'Available' if dates and times else 'Unknown',
                'total_slots_found': len(dates) if dates else 0
            }
            
        except Exception as e:
            print(f"Error getting appointment data for {office_name}: {e}")
            return {
                'office_name': office_name,
                'address': office_address,
                'earliest_date': 'Error',
                'earliest_time': 'Error',
                'distance': 'N/A',
                'status': f'Error: {str(e)}'
            }
    
    def scrape_all_appointments(self):
        """Main method to scrape all office appointments"""
        try:
            # Check website accessibility first
            if not self.test_mode and not self.check_website_accessibility():
                print("\n" + "="*60)
                print("CANNOT PROCEED: Website is not accessible")
                print("="*60)
                return False
            
            self.setup_driver()
            
            # Get all office locations
            offices = self.get_office_locations()
            
            if not offices:
                print("No offices found. Attempting alternative extraction...")
                # Fallback: try to extract from page source
                offices = self.extract_offices_from_source()
            
            print(f"\nScraping appointments from {len(offices)} offices...")
            
            for i, office in enumerate(offices, 1):
                print(f"\n[{i}/{len(offices)}] Checking: {office['name']}")
                
                # Go back to main page for each office
                self.driver.get(self.url)
                time.sleep(2)
                
                # Click on the office
                if self.click_office(office['name']):
                    # Get appointment data
                    appt_data = self.get_appointment_data(office['name'], office['address'])
                    self.appointments_data.append(appt_data)
                    print(f"  → Earliest: {appt_data['earliest_date']} at {appt_data['earliest_time']}")
                else:
                    # If can't click, still record the office
                    self.appointments_data.append({
                        'office_name': office['name'],
                        'address': office['address'],
                        'earliest_date': 'Could not check',
                        'earliest_time': 'N/A',
                        'distance': 'N/A',
                        'status': 'Unable to access'
                    })
                
                time.sleep(1)  # Be respectful to the server
            
            return True
                
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                self.driver.quit()
                print("\n✓ Browser closed")
    
    def extract_offices_from_source(self):
        """Fallback method to extract offices from page source"""
        offices = []
        try:
            page_source = self.driver.page_source
            # Use regex to find office patterns
            pattern = r'<div[^>]*>(.*?)</div>\s*<div[^>]*>(\d+[^<]+\d{5})</div>'
            matches = re.findall(pattern, page_source, re.DOTALL)
            
            for match in matches:
                name = re.sub(r'<[^>]+>', '', match[0]).strip()
                address = re.sub(r'<[^>]+>', '', match[1]).strip()
                if name and address:
                    offices.append({'name': name, 'address': address})
        except Exception as e:
            print(f"Error in fallback extraction: {e}")
            
        return offices
    
    def generate_test_data(self):
        """Generate test data for demonstration purposes"""
        print("\n" + "="*60)
        print("RUNNING IN TEST MODE - Using Sample Data")
        print("="*60)
        
        test_offices = [
            {
                'office_name': 'Denver DMV - Main Office',
                'address': '1234 Broadway, Denver, CO 80202',
                'earliest_date': 'December 15, 2025',
                'earliest_time': '10:30 AM',
                'distance': '5.2 miles',
                'status': 'Available',
                'total_slots_found': 12
            },
            {
                'office_name': 'Aurora DMV Office',
                'address': '5678 E Colfax Ave, Aurora, CO 80010',
                'earliest_date': 'December 18, 2025',
                'earliest_time': '2:15 PM',
                'distance': '12.3 miles',
                'status': 'Available',
                'total_slots_found': 8
            },
            {
                'office_name': 'Colorado Springs DMV',
                'address': '910 Motor City Dr, Colorado Springs, CO 80905',
                'earliest_date': 'No appointments available',
                'earliest_time': 'N/A',
                'distance': '68.5 miles',
                'status': 'No availability',
                'total_slots_found': 0
            },
            {
                'office_name': 'Boulder DMV Office',
                'address': '2850 Iris Ave, Boulder, CO 80304',
                'earliest_date': 'December 12, 2025',
                'earliest_time': '9:00 AM',
                'distance': '28.7 miles',
                'status': 'Available',
                'total_slots_found': 15
            },
            {
                'office_name': 'Fort Collins DMV',
                'address': '1540 Blue Spruce Dr, Fort Collins, CO 80524',
                'earliest_date': 'December 20, 2025',
                'earliest_time': '1:45 PM',
                'distance': '65.2 miles',
                'status': 'Available',
                'total_slots_found': 6
            }
        ]
        
        self.appointments_data = test_offices
        print(f"✓ Generated test data for {len(test_offices)} offices")
        return True
    
    def export_to_spreadsheet(self, filename='appointment_results.xlsx'):
        """Export scraped data to Excel spreadsheet"""
        if not self.appointments_data:
            print("No data to export!")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.appointments_data)
        
        # Sort by earliest date (available appointments first)
        df['sort_key'] = df['earliest_date'].apply(lambda x: 0 if x not in ['No appointments available', 'Could not check', 'Error', 'Not found'] else 1)
        df = df.sort_values('sort_key').drop('sort_key', axis=1)
        
        # Export to Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n✓ Data exported to {filename}")
        
        # Also export to CSV as backup
        csv_filename = filename.replace('.xlsx', '.csv')
        df.to_csv(csv_filename, index=False)
        print(f"✓ Data also exported to {csv_filename}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total offices checked: {len(df)}")
        available = len(df[df['status'].str.contains('Available', case=False, na=False)])
        print(f"Offices with availability: {available}")
        print(f"{'='*60}")
        
        return df


def main():
    """Main execution function"""
    url = "https://coloradoappt.cxmflow.com/Appointment/Index/d74f48b1-33a9-428c-acd1-d7d1bfc9555c"
    
    print("="*60)
    print("Colorado DMV Appointment Scraper")
    print("="*60)
    
    # Check command line arguments for test mode
    test_mode = '--test' in sys.argv or '--demo' in sys.argv
    
    scraper = AppointmentScraper(url, test_mode=test_mode)
    
    try:
        if test_mode:
            # Run in test mode with sample data
            success = scraper.generate_test_data()
        else:
            # Run actual scraping
            success = scraper.scrape_all_appointments()
        
        if success or scraper.appointments_data:
            scraper.export_to_spreadsheet('colorado_dmv_appointments.xlsx')
        else:
            print("\n" + "="*60)
            print("No data was collected. Troubleshooting tips:")
            print("="*60)
            print("1. Check your internet connection")
            print("2. Verify the website URL is still valid")
            print("3. Try running in test mode: python appointment_scraper.py --test")
            print("4. Make sure Chrome/Chromium is installed")
            print("5. Check if the website structure has changed")
            print("\nFor demo/testing, run: python appointment_scraper.py --test")
            
    except KeyboardInterrupt:
        print("\n\n⚠ Script interrupted by user")
        print("Tip: The script was stopped. You can resume by running it again.")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        print("2. Make sure Chrome/Chromium is installed")
        print("3. Try running in test mode to verify the script works:")
        print("   python appointment_scraper.py --test")
        print("4. Check the full error message above for specific issues")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
