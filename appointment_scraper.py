#!/usr/bin/env python3
"""
Colorado DMV Appointment Scraper
Scrapes appointment availability from Colorado DMV appointment scheduling system
and exports data to a spreadsheet.
"""

import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import re

class AppointmentScraper:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.appointments_data = []
        
    def setup_driver(self):
        """Initialize Chrome webdriver with options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver_manager to automatically handle chromedriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
        
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
                
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
    
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
    
    scraper = AppointmentScraper(url)
    
    try:
        scraper.scrape_all_appointments()
        scraper.export_to_spreadsheet('colorado_dmv_appointments.xlsx')
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("\nTip: Make sure Chrome/Chromium is installed and chromedriver is in your PATH")


if __name__ == "__main__":
    main()
