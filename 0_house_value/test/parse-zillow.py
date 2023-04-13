from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path

# Folder path for your chrome web browser driver
PATH  = ''

# Passes your path to a chrome driver
service_object = Service(binary_path)
driver = webdriver.Chrome(ChromeDriverManager().install())
#driver = webdriver.Chrome(service=service_object)

# Zillows website link for rental properties being listed{string interpolation} for page #'s
request_url = "https://www.zillow.com/arlington-tx/rentals/{}_p"

name = []
details = []
address = []

# Iterating through a range (in reference to the page #'s) and grabbing name,details,address.
for page in range(1,6):
    
    # Formats the zillow's website link with the page num
    base_url = request_url.format(page)

    driver.get(base_url)


    wait = driver.implicitly_wait(60)
    
    # Grabs the all the search result element in a page 
    main = driver.find_element("search-page-list-container")
    
    # Grabs all the info about a listing
    card_info = main.find_elements_by_class_name('list-card-info')
    
    # Iterates through all every listing on the page & appends it all to a list.
    for listing in card_info:
        name.append(listing.find_element_by_class_name('list-card-footer').text)
        address.append(listing.find_element_by_class_name('list-card-addr').text)
        details.append(listing.find_element_by_class_name('list-card-heading').text)
    
        wait

# Quits your session.
#driver.quit()
#
#zillow_data = {}
#
#zillow_data['Name'],zillow_data['Details'],zillow_data['Address'] = name,details,address
#
#print(zillow_data)
#
