from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

file_path = 'C:\\Users\\DELL\\Desktop\\updated_skuld_data.json'

# Load data from JSON
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Setup Selenium options
chrome_options = Options()
# Comment out the line below for debugging
chrome_options.add_argument("--headless")

service = Service(executable_path="C:\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    for word in data:
        if word[1] == "":  # Process only words without definitions
            url = "https://www.oxfordlearnersdictionaries.com/definition/english/"
            try:
                driver.get(url)
                print(f"Processing: {word[0]} at {url}")
            except Exception as e:
                print(f"Couldn't connect to {url}: {e}")
                continue

            # Search for the word
            try:
                search_bar = driver.find_element(By.XPATH, 
                    "//div[@class='mainsearch']/form[@class='selector_english']/div[@class='searchfield']/input[@class='searchfield_input']"
                )
                search_bar.clear()
                search_bar.send_keys(word[0])
                search_bar.send_keys(Keys.RETURN)

                # Wait for results to load
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='oald']"))
                )
                print(f"Search successful for: {word[0]}")
            except Exception as e:
                print(f"Search bar interaction failed for {word[0]}: {e}")
                continue

            # Extract result
            try:
                result = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='oald']/div[@class='entry']/div[@class='top-container']/div[@class='top-g']/div[@class='webtop']/span[@class='pos']")
                    )
                )
                word[1] = result.text
                print(f"Found: {word[0]} -> {result.text}")
            except Exception as e:
                print(f"Error finding result for {word[0]}: {e}")
                word[1] = ""

finally:
    driver.quit()

# Save the updated data to a file
output_file_path = 'C:\\Users\\DELL\\Desktop\\upgrade_skuld.json'
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Scraping complete. Results saved.")
