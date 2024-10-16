import os
import psycopg2
from bs4 import BeautifulSoup

# Directory containing the HTML files
directory = 'data'  # Replace with the path to your HTML files directory

# PostgreSQL database connection parameters
DB_HOST = 'your_db_host'
DB_NAME = 'your_db_name'
DB_USER = 'your_db_user'
DB_PASSWORD = 'your_db_password'

# Function to parse an HTML file
def parse_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'lxml')
        
    # Extract addresses
    addresses = []
    for p in soup.find_all('p'):
        if p.find('svg', class_='svg-icon svg-location'):
            address = p.get_text(strip=True)  # Extract and strip text from <p>
            addresses.append(address)
    
    # Extract date and time
    date_time = 'NA'
    date_time_element = soup.find('div', class_='step-info-date')
    if date_time_element:
        date_time = date_time_element.find('h6').text.strip()

    # Extract data for each vehicle grid item
    vehicles = []
    for vehicle_item in soup.find_all('div', class_='vehicle-grid-item'):
        # Get vehicle type
        vehicle_type = vehicle_item.find('h2', class_='vehicle-grid-item-heading').text.strip()

        # Get vehicle model (from description)
        model_description_container = vehicle_item.find('div', id=lambda x: x and x.startswith('vehicleDescription'))
        if model_description_container:
            vehicle_model = model_description_container.find('p').text.strip()
        else:
            vehicle_model = 'NA'  # Not Available

        # Get price
        price_container = vehicle_item.find('div', class_='vehicle-grid-item-price-numb')
        price = price_container.get_text().strip() if price_container else 'NA'
        
        # Get number of passengers & luggage
        pass_container = vehicle_item.find_all('span', class_='input-group-addon')
        pass_no = pass_container[1].text.strip() if len(pass_container) > 1 else 'NA'
        lag_no = pass_container[3].text.strip() if len(pass_container) > 3 else 'NA'

        # Initialize vehicle data dictionary
        vehicle_data = {
            'Vehicle_Type': vehicle_type,
            'Vehicle_Model': vehicle_model,
            'Price': price,
            'Passenger_No': pass_no,
            'Luggage_No': lag_no,
            'Date_Time': date_time,
        }

        # Check if there are addresses and assign them
        if len(addresses) > 0:
            vehicle_data['Pick_Up_Location'] = addresses[0]
        if len(addresses) > 1:
            vehicle_data['Drop_Off_Location'] = addresses[1]

        # Extract rate details from the table
        rate_details = {}
        rate_table = vehicle_item.find('table', class_='table table-striped table-sm')
        if rate_table:
            for row in rate_table.find_all('tr', class_='child'):
                cells = row.find_all('th') + row.find_all('td')
                if len(cells) == 2:
                    rate_details[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
        
        # Add rate details to the vehicle data
        vehicle_data.update(rate_details)

        vehicles.append(vehicle_data)

    return vehicles

# Function to store data in PostgreSQL
def store_data_in_db(data):
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()

        # Create table if it doesn't exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS vehicle_data (
            Vehicle_Type VARCHAR(255),
            Vehicle_Model VARCHAR(255),
            Price VARCHAR(50),
            Passenger_No VARCHAR(50),
            Luggage_No VARCHAR(50),
            Date_Time VARCHAR(50),
            Pick_Up_Location VARCHAR(255),
            Drop_Off_Location VARCHAR(255),
            Flat_Rate VARCHAR(50),
            Std_Grat VARCHAR(50),
            GA_State_Taxes VARCHAR(50)
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()

        # Insert data into the table
        for vehicle in data:
            insert_query = '''
            INSERT INTO vehicle_data (
                Vehicle_Type, Vehicle_Model, Price, Passenger_No, Luggage_No,
                Date_Time, Pick_Up_Location, Drop_Off_Location, Flat_Rate, Std_Grat, GA_State_Taxes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            '''
            cursor.execute(insert_query, (
                vehicle.get('Vehicle_Type', 'NA'), vehicle.get('Vehicle_Model', 'NA'), vehicle.get('Price', 'NA'),
                vehicle.get('Passenger_No', 'NA'), vehicle.get('Luggage_No', 'NA'), vehicle.get('Date_Time', 'NA'),
                vehicle.get('Pick_Up_Location', 'NA'), vehicle.get('Drop_Off_Location', 'NA'),
                vehicle.get('Flat Rate', 'NA'), vehicle.get('Std Grat(20.00%)', 'NA'), vehicle.get('GA State Taxes(7.00%)', 'NA')
            ))
        connection.commit()

    except Exception as error:
        print(f"Error while connecting to PostgreSQL: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Iterate over all files in the directory and store data in PostgreSQL
for filename in os.listdir(directory):
    if filename.endswith('.html'):  # Process only HTML files
        file_path = os.path.join(directory, filename)
        vehicles_data = parse_html_file(file_path)
        store_data_in_db(vehicles_data)
