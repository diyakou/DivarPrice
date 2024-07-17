import locale
import time
import re
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_posted_date(posted_text):
    if 'دیروز' in posted_text:
        return 1
    elif 'امروز' in posted_text:
        return 2  
    elif 'ساعت' in posted_text:
        return 3 
    elif 'روز پیش ۳' in posted_text:
        return 4  
    elif 'پریروز' in posted_text:
        return 5 
    else:
        return None 

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

app = Flask(__name__)
CORS(app)

def create_driver():
    return webdriver.Chrome(options=chrome_options)

@app.route('/edit/<lost_color>/<car_assident>' , methods=['POST'])
def car_options(lost_color, car_assident):
    try:
        with open('Lost_Price.json') as file:
            prices_lost = json.load(file)
        
        prices_lost["Color_Lost"] = lost_color
        prices_lost["Car_assident"] = car_assident

        with open('Lost_Price.json', 'w') as file:
            json.dump(prices_lost, file, indent=4)
        
        time.sleep(3)

        with open('Lost_Price.json', 'r') as file:
            prices_l = json.load(file)
        
        locale.setlocale(locale.LC_ALL, 'fa-IR.UTF-8')
        color_l = locale.atof(prices_l['Color_Lost'])
        assident_l = locale.atof(prices_l['Car_assident'])

        Final_price = color_l + assident_l
        prices_l["Final_price"] = int(Final_price)

        with open('Lost_Price.json', 'w') as file:
            json.dump(prices_l, file, indent=4)
        
        time.sleep(5)
        
        result = {"message": "Your operation was successful."}
        return jsonify(result)
    except Exception as e:
        print("Error in writing or reading data JSON file:", e)
        return jsonify({"message": "Error in processing data"}), 500

@app.route('/<city>/<name_product>/<model>', methods=['POST'])
def car(city, name_product , model):
    driver = create_driver()
    try:
        driver.get(f"https://divar.ir/s/{city}")

        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".kt-nav-text-field__input"))
        )
        search_input.send_keys(f'{name_product} مدل {model}')
        search_input.send_keys(Keys.RETURN)
        print(name_product)
        start_time = time.time()
        all_ads = []

        while (time.time() - start_time) < 30:
            driver.execute_script("window.scrollBy(0, 200);")


            time.sleep(0.5)

            ads = driver.find_elements(By.CSS_SELECTOR, ".post-list__widget-col-a3fe3 article.kt-post-card ")
            for ad in ads:
                ad_data = {}
                try:
                    description_elements = ad.find_elements(By.CSS_SELECTOR, ".kt-post-card__description")
                    title = ad.find_element(By.CSS_SELECTOR, ".kt-post-card__title").text

                    ad_data['title'] = ad.find_element(By.CSS_SELECTOR, ".kt-post-card__title").text

                    if name_product not  in title:
                        continue

                    ad_data['description'] = ad.find_element(By.CSS_SELECTOR, ".kt-post-card__description").text
                    if len(description_elements) >= 2:
                        # Extract price from the second description element
                        ad_data['price'] = description_elements[1].text
                    else:
                        continue
                    try:
                        img = ad.find_element(By.CSS_SELECTOR, ".kt-post-card-thumbnail img")
                        ad_data['img'] = img.get_attribute('src')
                    except:
                        ad_data['img'] = 'Null'
                    ad_data['link'] = ad.get_attribute('href')
                    posted_element = ad.find_element(By.CSS_SELECTOR, ".kt-post-card__bottom-description")
                    ad_data['posted'] = parse_posted_date(posted_element.text)
                    if ad_data['posted'] is not None and ad_data['posted'] <= 5:
                        ad_data['original_posted'] = posted_element.text
                        all_ads.append(ad_data)
                except Exception as e:
                    print(f"Error in extracting ad data: {e}")

        locale.setlocale(locale.LC_ALL, 'fa-IR.UTF-8')

        all_prices = [int(re.search(r'(\d[\d,]*)', ad['price']).group(1).replace(',', '')) for ad in all_ads if re.search(r'(\d[\d,]*)', ad['price'])]
        
        average_price = sum(all_prices) / len(all_prices) if all_prices else 0
        average_price_iranian = locale.currency(average_price, grouping=True)

        av_price = f"میانگین قیمت تمام آگهی‌ها: {average_price_iranian}"
        
        with open('Lost_Price.json', 'r') as file:
            final_price_min = json.load(file)

        real_val = average_price - final_price_min['Final_price']
        realsval = locale.format_string("%.2f", real_val, grouping=True)
        x = f"ارزش واقعی محصول شما : {realsval} ريال "

        return jsonify(final_res=av_price, fin=x, js_d=all_ads)
    except Exception as e:
        print(f"Error in scrapping data: {e}")
        return jsonify({"message": "Scrapper stopped, launching again in 4 seconds..."}), 500
    finally:
        driver.quit()

@app.route('/<city>/<name_melk>/<metrazh>/<region>', methods=['POST'])
def melk(city, name_melk, metrazh, region):
    driver = create_driver()
    try:
        driver.get(f"https://divar.ir/s/{city}")

        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".kt-nav-text-field__input"))
        )
        search_input.send_keys(f"{name_melk} {metrazh} {region}")
        search_input.send_keys(Keys.RETURN)

        start_time = time.time()
        all_ads = []

        while len(all_ads) < 20 and (time.time() - start_time) < 30:
            driver.execute_script("window.scrollBy(0, 200);")
            time.sleep(0.5)
            ads = driver.find_elements(By.CSS_SELECTOR, ".post-list__widget-col-c1444 article.kt-post-card")
            for ad in ads:
                ad_data = {}
                try:
                    ad_data['title'] = ad.find_element(By.CSS_SELECTOR, ".kt-post-card .kt-post-card__title").text
                    ad_data['price'] = ad.find_element(By.CSS_SELECTOR, ".kt-post-card .kt-post-card__description").text
                    try:
                        img = ad.find_element(By.CSS_SELECTOR, ".kt-post-card .kt-post-card-thumbnail img")
                        ad_data['img'] = img.get_attribute('src')
                    except:
                        ad_data['img'] = 'Null'
                    ad_data['link'] = ad.get_attribute('href')
                    all_ads.append(ad_data)
                except Exception as e:
                    print(f"Error in extracting ad data: {e}")

        locale.setlocale(locale.LC_ALL, 'fa_IR')

        all_prices = [int(re.search(r'(\d[\d,]*)', ad['price']).group(1).replace(',', '')) for ad in all_ads if re.search(r'(\d[\d,]*)', ad['price'])]
        
        average_price = sum(all_prices) / len(all_prices) if all_prices else 0
        average_price_iranian = locale.currency(average_price, grouping=True)

        av_price = f"میانگین قیمت تمام آگهی‌ها: {average_price_iranian}"
        
        with open('Lost_Price.json', 'r') as file:
            final_price_min = json.load(file)

        real_val = average_price - final_price_min['Final_price']
        realsval = locale.format_string("%.2f", real_val, grouping=True)
        x = f"ارزش واقعی محصول شما : {realsval} ريال "

        return jsonify(final_res=av_price, fin=x, js_d=all_ads)
    except Exception as e:
        print(f"Error in scrapping data: {e}")
        return jsonify({"message": "Scrapper stopped, launching again in 4 seconds..."}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run()
