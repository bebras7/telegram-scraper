import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_user_info():
    info = {}
    with open("user_info.txt") as f:
        lines = f.readlines()
        f.close()
    for line in lines:
        item = line.replace("\n", "").split(":")
        if item[0] == "":
            continue
        k, v = item
        info[k] = v
    return info


def get_members():
    df = pd.read_csv("members.csv")
    df = df[df.username.notnull()]
    return df.username


def get_auhtorized(driver, mobile: str):
    driver.get("https://web.telegram.org/z/")
    driver.maximize_window()
    login_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#auth-qr-form > div > button"))
    )
    login_btn.click()
    time.sleep(3)
    number_i = driver.find_element(By.CSS_SELECTOR, "#sign-in-phone-number")
    number_i.clear()
    number_i.send_keys(mobile)
    time.sleep(2)
    next_btn = driver.find_element(By.CSS_SELECTOR, "#auth-phone-number-form > div > form > button.has-ripple")
    next_btn.click()
    time.sleep(3)
    code = input("Please input code from telegram:")
    code_i = driver.find_element(By.CSS_SELECTOR, "#sign-in-code")
    code_i.send_keys(code)
    time.sleep(5)


def get_group(driver, group: str):
    actions = ActionChains(driver)
    grp = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{group}')]"))
    )
    actions.move_to_element(grp).click().perform()
    time.sleep(2)
    again_grp = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.XPATH, f"//*[contains(text(), '{group}')]"))
    )
    actions.move_to_element(again_grp[1]).click().perform()


def add_members(driver, members):
    actions = ActionChains(driver)
    skip_add_btn = False
    for member in members:
        try:
            time.sleep(2)
            print(skip_add_btn)
            if not skip_add_btn:
                add_grp_btn = WebDriverWait(driver, 5, ignored_exceptions=StaleElementReferenceException).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "button.FloatingActionButton i"))
                )
                actions.move_to_element(add_grp_btn).click().perform()
            driver.implicitly_wait(5)
            add_user_input = driver.find_element(By.CSS_SELECTOR, "#new-members-picker-search")
            add_user_input.clear()
            time.sleep(2)
            add_user_input.send_keys(member)
            time.sleep(2)
            found = driver.find_element(By.CSS_SELECTOR, "div.picker-list div.ListItem")
            checkbox = found.find_element(By.CSS_SELECTOR, "label.Checkbox > input")
            actions.move_to_element(checkbox).click().perform()
            add_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button.FloatingActionButton i"))
            )
            time.sleep(2)
            actions.move_to_element(add_btn).click().perform()
            print(member, " Added")
            skip_add_btn = False
        except NoSuchElementException:
            add_user_input.clear()
            skip_add_btn = True
            print(f"{member} Member not found")


if '__main__' == __name__:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(service=Service("./chromedriver"), options=options)
    info = get_user_info()
    get_auhtorized(driver, mobile=info["phone"])
    get_group(driver, group=info["group"])
    members = get_members()
    add_members(driver, members)
