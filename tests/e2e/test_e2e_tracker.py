import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import unittest

class TestProductCostTrackerE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.get('http://127.0.0.1:5000/form')

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_hunt_form_track_product(self):
        driver = self.driver
        driver.get('http://127.0.0.1:5000/form')
        url_input = driver.find_element(By.ID, 'product_url')
        price_input = driver.find_element(By.ID, 'target_price')
        alias_select = driver.find_element(By.ID, 'chatid_pick')
        url_input.send_keys('https://www.myntra.com/watches/tommy+hilfiger/tommy-hilfiger-women-pink-analogue-watch-th1781973/9846981/buy')
        price_input.send_keys('5000')
        for option in alias_select.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip().lower() == 'kalyan':
                option.click()
        submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type=submit]'))
        )
        # Hide sticky/fixed overlays before clicking
        driver.execute_script('''
            var nodes = document.querySelectorAll('*');
            for (var i = 0; i < nodes.length; i++) {
                var s = window.getComputedStyle(nodes[i]);
                if (s.position === 'fixed' || s.position === 'sticky') {
                    nodes[i].style.display = 'none';
                }
            }
        ''')
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", submit_btn)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert'))
        )
        alerts = driver.find_elements(By.CLASS_NAME, 'alert')
        self.assertTrue(any('track' in a.text.lower() or 'notification' in a.text.lower() for a in alerts))

    def test_schedule_and_edit_delete(self):
        driver = self.driver
        driver.get('http://127.0.0.1:5000/form')
        url_input = driver.find_element(By.ID, 'product_url')
        price_input = driver.find_element(By.ID, 'target_price')
        alias_select = driver.find_element(By.ID, 'chatid_pick')
        url_input.send_keys('https://www.myntra.com/watches/tommy+hilfiger/tommy-hilfiger-women-pink-analogue-watch-th1781973/9846981/buy')
        price_input.send_keys('5000')
        for option in alias_select.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip().lower() == 'kalyan':
                option.click()
        schedule_chk = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'schedule_tracking'))
        )
        driver.execute_script('''
            var nodes = document.querySelectorAll('*');
            for (var i = 0; i < nodes.length; i++) {
                var s = window.getComputedStyle(nodes[i]);
                if (s.position === 'fixed' || s.position === 'sticky') {
                    nodes[i].style.display = 'none';
                }
            }
        ''')
        driver.execute_script("arguments[0].scrollIntoView(true);", schedule_chk)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", schedule_chk)
        submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type=submit]'))
        )
        driver.execute_script('''
            var nodes = document.querySelectorAll('*');
            for (var i = 0; i < nodes.length; i++) {
                var s = window.getComputedStyle(nodes[i]);
                if (s.position === 'fixed' || s.position === 'sticky') {
                    nodes[i].style.display = 'none';
                }
            }
        ''')
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", submit_btn)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Being Hunted'))
        )
        driver.get('http://127.0.0.1:5000/tracking')
        table = driver.find_element(By.CLASS_NAME, 'venator-table')
        self.assertIn('kalyan', table.text.lower())
        # Edit
        edit_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Edit')]")
        edit_btn.click()
        alias_input = driver.find_element(By.NAME, 'edit_chat_aliases')
        alias_input.clear()
        alias_input.send_keys('uma')
        save_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Save')]")
        save_btn.click()
        time.sleep(1)
        table = driver.find_element(By.CLASS_NAME, 'venator-table')
        self.assertIn('uma', table.text.lower())
        # Delete
        delete_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Delete')]")
        delete_btn.click()
        driver.switch_to.alert.accept() if hasattr(driver, 'switch_to') and hasattr(driver.switch_to, 'alert') else None
        time.sleep(1)
        table = driver.find_element(By.CLASS_NAME, 'venator-table')
        self.assertNotIn('uma', table.text.lower())

if __name__ == '__main__':
    unittest.main()
