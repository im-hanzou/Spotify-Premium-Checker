import requests
import json
import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

os.system('cls' if os.name == 'nt' else 'clear')
print("Made by ExeDesK#0628\nChrome 112 or later is required.")

with open("config.json", "r") as f:
    config = json.load(f)

with open("lang.json", "r") as f:
    messages = json.load(f)[config["language"]]

discord_id = config["discord_id"]
webhook_url = config["webhook_url"]

if platform.system() == "Windows":
    driver_path = "./chromedriver/chromedriver.exe"
    print(messages["windows_platform"])
else:
    driver_path = "/chromedriver/chromedriver"
    print(messages["linux_platform"])

options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")

non_premium_users = []

with open("logins.txt", "r") as f:
    for line in f:
        username, password = line.strip().split(":")

        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://accounts.spotify.com/login?continue=https%3A%2F%2Fspotify.com%2Faccount%2Foverview")

        wait = WebDriverWait(driver, 10)

        username_field = driver.find_element(By.ID, "login-username")
        username_field.send_keys(username)

        password_field = driver.find_element(By.ID, "login-password")
        password_field.send_keys(password)

        login_button = driver.find_element(By.ID, "login-button")
        login_button.click()

        wait.until(EC.presence_of_element_located((By.ID, "your-plan")))

        if "Spotify Free" in driver.find_element(By.XPATH, "//body").text:
            non_premium_users.append(username)
            print(messages["user_not_premium"].format(username=username))
        else:
            print(messages["user_is_premium"].format(username=username))

        driver.delete_all_cookies()

        driver.quit()

user_list = "\n".join(non_premium_users)

if user_list:
    headers = {"Content-Type": "application/json"}
    payload = {
        "content": f"<@{discord_id}>\n```{user_list}```"
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 204:
        print(messages["discord_notification_success"])
    else:
        print(messages["discord_notification_error"])
