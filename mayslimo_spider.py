#!/usr/bin/env python
"""
Author : stan <stan@localhost>
Date   : 2024-06-25
Purpose: Booking Spider
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import os
from bs4 import BeautifulSoup
import time
import argparse

service = Service(executable_path='./chromedriver.exe')
driver = webdriver.Chrome(service=service)
# use to change the webdriver wait times
wait = WebDriverWait(driver, 30)

# adjust this based on connection speed


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Booking Spider',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-u',
                        '--url',
                        metavar='url',
                        default="https://www.mayslimo.com/online-booking/",
                        help='URL of website')

    parser.add_argument('-s',
                        '--service_type',
                        help='Service type as an integer',
                        metavar='int',
                        choices=[x for x in range(0, 4)],
                        type=int,
                        default=1)

    parser.add_argument('-d',
                        '--date',
                        help='Date as a string in the form mm/dd/yyyy',
                        metavar='date text',
                        type=str,
                        default='06/30/2024')

    parser.add_argument('-t',
                        '--time',
                        help='Time as a string in the form hh:mm AM/PM',
                        metavar='time text',
                        type=str,
                        default="10:30 AM")

    parser.add_argument('-pl',
                        '--pickup_location_str',
                        help='Pick-up location as a string',
                        metavar='pickup location text',
                        type=str,
                        default='ATL Airport')

    parser.add_argument('-dl',
                        '--dropoff_location_str',
                        help='Drop-off location as a string',
                        metavar='dropoff location text',
                        type=str,
                        default='Sandy Springs')

    parser.add_argument('-si',
                        '--stop_location',
                        help='Stop location as a string',
                        metavar='Stop location text',
                        type=str,
                        default='BMW')

    parser.add_argument('-stop',
                        '--add_stop',
                        help='Boolean flag to add stop',
                        action='store_true')

    parser.add_argument('-pn',
                        '--pass_num',
                        help='Number of passengers',
                        metavar='int',
                        type=int,
                        default=1)

    parser.add_argument('-nh',
                        '--hr_num',
                        help='Number of hours',
                        metavar='int',
                        type=int)

    parser.add_argument('-lc',
                        '--luggage_num',
                        help='Count of luggage',
                        metavar='int',
                        type=int,
                        default=1)

    parser.add_argument('-rl',
                        '--bool_rtn_loc',
                        help='Boolean flag to add stop',
                        action='store_true')

    return parser.parse_args()


def switch_to_frame():
    """Switches to iframe for booking service"""
    wait.until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, 'iFrameResizer0')))


def select_service(service_type):
    """Selects service type"""
    wait.until(EC.presence_of_element_located((By.ID, 'ServiceTypeId')))
    dropdown_element = driver.find_element(By.ID, 'ServiceTypeId')
    select = Select(dropdown_element)
    select.select_by_index(service_type)


def select_date(date_text):
    """Select the appropriate date"""
    wait.until(EC.presence_of_element_located((By.ID, 'PickUpDate')))
    date_input = driver.find_element(By.ID, 'PickUpDate')
    date_input.click()
    date_input.clear()
    driver.execute_script(f"arguments[0].value = '{date_text}';", date_input)


def select_time(select_time):
    """Selects time for ride"""
    time_input = driver.find_element(By.ID, 'PickUpTime')
    time_input.clear()
    driver.execute_script(f"arguments[0].value = '{select_time}';", time_input)


def pickUp_location(pickup_location_str):
    """Pickup location address"""
    pickup_location_input = driver.find_element(By.ID, 'PickupLocation')
    pickup_location_input.clear()
    pickup_location_input.send_keys(pickup_location_str)
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH,
             "//div[@id='PickupLocationSuggestionDiv']/ul//li[position()=2]"
             ))).click()


def drop_off_location(dropoff_location_str):
    """Drop off location"""
    dropoff_location_input = driver.find_element(By.ID, 'DropoffLocation')
    dropoff_location_input.clear()
    dropoff_location_input.send_keys(dropoff_location_str)
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH,
             "//div[@id='DropoffLocationSuggestionDiv']/ul//li[position()=2]"
             ))).click()


def add_stop(stop_location):
    """Checks to see whether we need stops"""
    add_stop_link = driver.find_element(By.ID, 'addNewStopLink')
    add_stop_link.click()
    stop_input = driver.find_element(By.ID, 'Stops_1_')
    stop_input.clear()
    stop_input.send_keys(stop_location)
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH,
                "//div[@id='Stops_1_SuggestionDiv']/ul//li[position()=1]"
                ))).click()


def no_passengers(pass_num):
    """Passenger number"""
    passenger_input = driver.find_element(By.ID, 'PassengerNumber')
    passenger_input.clear()
    driver.execute_script(f"arguments[0].value = '{pass_num}';",
                          passenger_input)


def no_hours(hr_num):
    """Estimated duration of trip"""
    no_hours = driver.find_element(By.ID, 'HoursNumber')
    no_hours.clear()
    driver.execute_script(f"arguments[0].value = '{hr_num}';", no_hours)


def luggage_count(luggage_num):
    """Estimated number of luggage"""
    luggage_input = driver.find_element(By.ID, 'LuggageCount')
    luggage_input.clear()
    driver.execute_script(f"arguments[0].value = '{luggage_num}';",
                          luggage_input)


def return_at_diff_location():
    """Clicks the return to different location checkbox"""
    checkbox = driver.find_element(By.ID, 'showDropoffLocation')
    ActionChains(driver).move_to_element(checkbox).perform()
    checkbox.click()


def select_vehicle():
    """Clicks the select vehicle button"""
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[@id='showRatesBtn']"))).click()


def click_rate_details_buttons():
    """Click the rate details button for each vehicle item."""
    try:
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "vehicle-grid-item-price")))
        
        vehicle_items = driver.find_elements(By.CLASS_NAME,
                                                     "vehicle-grid-item-price")
        for vehicle_item in vehicle_items:
            try:
                button = vehicle_item.find_elements(By.CLASS_NAME,
                                                     "vehicle-decription-btn")[1]
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                button.click()
               
            except Exception as e:
                print(f"Could not click the button for a vehicle item: {e}")
    except Exception as e:
        print(
            f"An error occurred while trying to click rate details buttons: {e}"
        )


def save_page_source(filename):
    """Save the current page source to a file in the data folder."""
    if not os.path.exists('data'):
        os.makedirs('data')
    with open(os.path.join('data', filename), 'w', encoding='utf-8') as file:
        file.write(driver.page_source)


def click_next_until_disabled():
    """Click the next page button"""
    pages = driver.find_elements(By.CSS_SELECTOR, 'li.page a')
    num_pages = len(pages)

    for page_num in range(num_pages):
        try:
            pages = driver.find_elements(By.CSS_SELECTOR, 'li.page a')
            time.sleep(10)
            save_page_source(f'page_{page_num}.html')
            click_rate_details_buttons()
            page_button = wait.until(
                EC.element_to_be_clickable(pages[page_num]))
            page_button.click()
            print(f"Clicked page {page_num + 1}")

        except (NoSuchElementException, ElementClickInterceptedException,
                StaleElementReferenceException) as e:
            print("No longer clickable or not found:", e)
            break
        except Exception as e:
            print("An unexpected error occurred:", e)
            break


# --------------------------------------------------
def main():
    args = get_args()
    url_str = args.url
    service_type = args.service_type
    date_str = args.date
    time_str = args.time
    pickup_location_str = args.pickup_location_str
    dropoff_location_str = args.dropoff_location_str
    bool_stop = args.add_stop
    pass_num = args.pass_num
    hr_num = args.hr_num
    luggage_num = args.luggage_num
    bool_rtn_loc = args.bool_rtn_loc
    stop_location = args.stop_location

    try:
        driver.maximize_window()
        driver.get(url_str)
        time.sleep(10)
        switch_to_frame()

        select_service(service_type)
        select_date(date_str)
        select_time(time_str)
        if bool_stop:
            add_stop(stop_location)
        pickUp_location(pickup_location_str)
        drop_off_location(dropoff_location_str)
        no_passengers(pass_num)
        luggage_count(luggage_num)

        if service_type == 3:
            if bool_rtn_loc:
                return_at_diff_location()
            no_hours(hr_num)

        select_vehicle()
        click_next_until_disabled()

    except Exception as ex:
        print(ex)

    finally:
        time.sleep(5)
        driver.close()
        driver.quit()


# --------------------------------------------------
if __name__ == '__main__':
    main()
