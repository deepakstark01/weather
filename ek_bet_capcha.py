import os
# import db_operations as db
from datetime import date, datetime
from selenium.webdriver.chrome.options import Options
import json
import cv2
from pyzbar.pyzbar import decode
import pandas as pd
import re
import time
import pytz
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium_stealth import stealth
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from fuzzywuzzy import fuzz
start_time = time.time()
from PIL import Image
import requests
# server, mysql = db.create_db_engine()
# from clear_data import clear_browsing_data

# custom sort function to sort tags based on the matched percentage with a string

upi_ids_found = []
continue_payment_recursive_count = 0
global limit_btns
def captcha():
    url = "https://brandsafetydashboard.mfilterit.net/aws_text_detection"

    payload = {}
    files=[('filename',('captcha.png',open(r'C:\ekbet\screenshot.png','rb'),'image/png'))]
    headers = {'Cookie': 'session=5817b763-1c9c-42c8-8038-85d2242f00ea'}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    code=response.text
    data_dict = json.loads(code)
    value = data_dict['data']
    print(response.text)
    return  value

def sort_tags(arr_of_tags=[], match_string=''):
    # print(fuzz.token_set_ratio("login","Login"))
    sorted_tags = []
    try:
        for tag in arr_of_tags:
            # sorted_tags.append({tag: fuzz.token_set_ratio(tag.text, match_string)})
            sorted_tags.append({
                "tag": tag,
                "match_pct": fuzz.token_set_ratio(tag.text, match_string)
                # "match_pct": fuzz.partial_ratio(tag.text, match_string)
            })

    except:
        pass

    print("len(arr_of_tags): ", len(arr_of_tags))
    print("len(sorted_tags): ", len(sorted_tags))
    # print(sorted(sorted_tags, key=lambda x: x['match_pct'],reverse=True))
    sorted_tags = sorted(
        sorted_tags, key=lambda x: x['match_pct'], reverse=True)
    final_arr = []
    for tag in sorted_tags:
        final_arr.append(tag['tag'])

    # print(final_arr)
    return final_arr


def is_match(tag, r, matched_entity, check_attrs=True):
    if check_attrs:
        attr = tag.attrs
        k = attr.keys()
        # if tag.name == "img":
        #     print("tag: ",tag.name)
        #     print("tag attributes: ",k)
        v = attr.values()
        items = list(k)
        items.extend(list(v))
        # items = [item for sublist in items for item in sublist]
        temp_items = []
        for item in items:
            if type(item) == list:
                for inner_item in item:
                    temp_items.append(inner_item)
            else:
                temp_items.append(str(item))
        items = temp_items
        for item in items:
            try:
                if r.search(item):
                    # print("debug print: (is_match fu) ", item)
                    matched_entity[tag] = str(item)
                    return True
            except:
                print("exception due to this item : ", item)
    # print("debug print: tag text= ", tag.text.strip()[:50])
    if r.search(tag.text.strip()[:50]):
        matched_entity[tag] = str(tag.text.strip()[:50])
        return True
    return False


def load_website(driver, url):
    # driver.maximize_window()
    driver.get(url)
    print("site loaded")
    


def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
    components.reverse()
    # print("debug print xpath components: ", '/%s' % '/'.join(components))
    return '/%s' % '/'.join(components)


def login(driver, userid, password, rules, prev_search, password_tags):
    time.sleep(3)
    driver.save_screenshot("full_screenshot.png")

    # Define the coordinates for the region you want to capture
    x1 = 1073  # X-coordinate of the top-left corner
    y1 = 470  # Y-coordinate of the top-left corner
    x2 = 1210  # X-coordinate of the bottom-right corner
    y2 = 519   # Y-coordinate of the bottom-right corner

    # Crop the full screenshot to the specified region
    im = Image.open("full_screenshot.png")
    region = im.crop((x1, y1, x2, y2))
    region.save("screenshot.png")
    print("debug -: lenof pass ", len(password_tags))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    userid_tags = soup.find_all(lambda tag: tag.name == 'input')
    print("the userid tag is -:",len(userid_tags))
    temp_userid_tags = []
    for tag in userid_tags:
        try:
            if tag.attrs['type'] in ['email', 'tel', 'text'] or ("placeholder" in tag.attrs and re.compile(rules['userid']).findall(tag.attrs['placeholder'])):
                temp_userid_tags.append(tag)
            elif tag.attrs['id'] in ['email', 'tel', 'text'] or ("placeholder" in tag.attrs and re.compile(rules['userid']).findall(tag.attrs['placeholder'])):
                temp_userid_tags.append(tag)
        except:
            if ("placeholder" in tag.attrs and re.compile(rules['userid']).findall(tag.attrs['placeholder'])):
                temp_userid_tags.append(tag)

    userid_tags = temp_userid_tags
    # if len(userid_tags) == 0:
    #     print("inside if statement")
    #     userid_tags = soup.find_all(
    #         lambda tag: tag.name == 'input' and (tag.name == 'input' or 'type' in tag.attrs and tag.attrs['type'] in ['text']))

    # print("before sorting: ", userid_tags[0])
    userid_tags.sort(key=lambda tag: len(xpath_soup(tag)))
    # print("after sorting: ", userid_tags[0])
    print("number of userid tags", len(userid_tags))

    exit = False
    for tag in userid_tags:
        print(f"len of xpath of {tag}: ", len(xpath_soup(tag)))
        # if tag.attrs['type'] != "password":
        if tag not in password_tags:
            for e in driver.find_elements(By.XPATH, xpath_soup(tag)):
                u_x = e.location['x']  # uid_loc_x
                u_y = e.location['y']  # uid_loc_y
                p_x = password_tag_loc['x']
                p_y = password_tag_loc['y']
                print("u_x : ", u_x)
                print("u_y : ", u_y)
                print("p_x : ", p_x)
                print("p_y : ", p_y)
                limit = 300
                try:
                    print('class of userid_tag : ', tag.attrs['class'])
                except:
                    try:
                        print('id of userid_tag : ', tag.attrs['id'])
                    except:
                        pass

                if e.is_displayed():
                    if (p_x-limit <= u_x <= p_x+limit) and (p_y-limit <= u_y <= p_y+limit):
                        # if (u_x <= p_x) or (p_y >= u_y):
                        prev_search[tag] = True
                        userid_tag = e
                        userid_tag_actual = tag  # e
                        exit = True
                        break
        if exit:
            break
    try:
        print(f"userid tag: {userid_tag_actual.attrs['class']}")
    except:
        pass
    try:
        clear = ActionChains(driver)
        try:
            clear.click(userid_tag).key_down(Keys.CONTROL).send_keys(
                "A").key_up(Keys.CONTROL).perform()
        except:
            print("not clear the  userid field ")
        # userid_tag.clear()
        userid_tag.send_keys(userid)
        # time.sleep(2)
        print(f"entered userid: {userid}", "in", userid_tag_actual)
    except Exception as e:
        print(e)
        try:
            driver.execute_script(f"arguments[0].value='{userid}';", userid_tag)
            print("send userid 🥳🥳")
        except:
            print("no data send ")

    # password_tags = soup.find_all(
    #     lambda tag: tag.name == 'input' and 'type' in tag.attrs and tag.attrs['type'] == password)
    print("debug print: no of password tags: ", len(password_tags))
    for tag in password_tags:
        # for e in driver.find_elements(By.XPATH, xpath_soup(tag)):
        e = driver.find_element(By.XPATH, xpath_soup(tag))
        if True:
            # if e.is_displayed():
            prev_search[tag] = True
            password_tag = e
            # break
            try:
                clear = ActionChains(driver)
                clear.click(password_tag).key_down(Keys.CONTROL).send_keys(
                    "A").key_up(Keys.CONTROL).perform()
                password_tag.send_keys(password)
                password_tag.send_keys(Keys.ENTER)
                # time.sleep(2)
                print(f"entered password: {password}")
                print("pressed enter key")

            except Exception as e:
                print(e)
                
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    verification_code = soup.find_all(lambda tag: is_match(tag, re.compile(rules["verification_code"]), {}) and tag.name in ['input'])
    print("len of code -:",verification_code )
    verification_code=sort_tags(verification_code, "Code")
    for tag in verification_code:
        element=driver.find_element(By.XPATH,xpath_soup(tag))
        V_code=captcha()
        # V_code="captcha()"
        
        try:
            clear = ActionChains(driver)
            clear.click(element).key_down(Keys.CONTROL).send_keys("A").key_up(Keys.CONTROL).perform()
            element.send_keys(V_code)

            # element.send_keys(Keys.ENTER)
            # time.sleep(2)
            print(f"entered code: {V_code}")

            print("pressed enter key")
        except Exception as e:
            print(e)
    # r = re.compile(rules["login"])
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # login_btns = soup.find_all(lambda tag: r.findall(
    #     str(tag)) and tag.name in ['input', 'button'])
    matched_signin_btns = {}

    signin_btns = soup.find_all(lambda tag: is_match(tag, re.compile(
        rules["login"]), matched_signin_btns, check_attrs=True))
    print("no of signin button before close btn filter: ", len(signin_btns))
    # trying to remove "close login btns" from list of login btns
    close_btns = soup.find_all(lambda tag: is_match(
        tag, re.compile(rules["popup"]), {}) and tag.name in ['button', 'svg', 'img', 'span','i'])
    # signin_btns = [btn for btn in signin_btns if btn not in close_btns and btn.name in ['input','span','button']]
    temp_signin_btns = []
    for btn in signin_btns:
        if btn not in close_btns and btn.name in ['input', 'button', 'span', 'div']:
            if btn.name == 'div':
                try:
                    if driver.find_element(By.XPATH, xpath_soup(btn)).is_displayed() and len(btn.text) < 50:
                        temp_signin_btns.append(btn)
                    else:
                        continue
                except:
                    pass
            if btn.name != 'input':
                temp_signin_btns.append(btn)
            try:
                if btn.name == 'input' and btn.attrs['type'] == 'submit':
                    temp_signin_btns.append(btn)
            except:
                pass
    signin_btns = temp_signin_btns

    signin_btns.sort(key=lambda tag: len(xpath_soup(tag)))
    # signin_btns =sort_tags(signin_btns, "login")
    
    
    print(" the btn are -:", signin_btns[:5])
    print("no of signin button after close btn filter: ", len(signin_btns))
    exit = False
    print("debug print: len of prev_Search", len(prev_search))
    # print(prev_search)

    for btn in signin_btns:
        if btn not in prev_search:
            try:
                e = driver.find_element(By.XPATH, xpath_soup(btn))
            except:
                continue
            if e.is_displayed():
                # sb = signin_btn
                # p = password_field
                btn_loc = e.location
                sb_x = btn_loc['x']
                sb_y = btn_loc['y']
                p_x = password_tag_loc['x']
                p_y = password_tag_loc['y']
                print("sb_x: ", sb_x)
                print("sb_y: ", sb_y)
                print("p_x: ", p_x)
                print("p_y: ", p_y)
                if ((p_x < sb_x <= p_x+300) and (p_y-10 <= sb_y <= p_y+10)) or ((p_x-50 <= sb_x <= p_x+300) and (p_y < sb_y <= p_y+500)):
                    print("found the btn")
                    # e.click()
                    ac = ActionChains(driver)
                    ac.move_to_element(e).move_by_offset(
                        1, 1).click().perform()
                    time.sleep(1)
                    try:
                        driver.execute_script("arguments[0].click();", e)
                        print("clicked through js  😎😎😎")
                    except:
                        print(" the login  is not clicked ")
                    print("clicked")
                    # exit = True
                    try:
                        if password_tag.is_displayed():
                            continue
                    except:
                        break
    if password_inside_iframe:
        driver.switch_to.default_content()

# function to finding amount buttons -tanuj


def amount_button(driver):
    print("*********Searching for the amount buttons *********")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    zeros_tags = soup.find_all(lambda tag: is_match(
        tag, re.compile(rules['zero_buttons']), {}, check_attrs=False) and tag.name in ['button', 'p', 'span', 'div'])
    print("length of 1000 buttons -:", len(zeros_tags))
    temp_btns = []
    for btn in zeros_tags:
        # children of amount btns should be less than 2
        if len(btn.find_all()) < 2:
            temp_btns.append(btn)   

    # zeros_tags = temp_btns
    zeros_tags = sort_tags(temp_btns, '000')
    clicked = False
    for tag in zeros_tags:
        el = driver.find_element(By.XPATH, xpath_soup(tag))
        # clicked = False
        if "200" in tag.text or "100" in tag.text:
            try:
                el.click()
                print("clicked on 1000 button")
                clicked = True
                break
            except:
                # print("unable to click on amt_btn")
                try:
                    ac = ActionChains(driver)
                    ac.move_to_element(el).click().perform()
                    print("clicked on 1000 button")
                    clicked = True
                    break
                except:
                    print("1000 btn not clicked")
                
        else:
            # print(btn.text)
            pass
    if clicked:
        submit_amt(driver, el)
    return clicked

#----------------------------------------------------------------------------------------------------------------------------------------------------
def find_login(prev_search, rules, matched_login_entity):
    global password_tag_loc
    global password_inside_iframe
    password_inside_iframe = False
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    login_elements = soup.find_all(lambda tag: is_match(
        tag, re.compile(rules["login"]), matched_login_entity, check_attrs=True))
    print("number of login elements: ", len(login_elements))
    temp_login_elements = []
    for tag in login_elements:
        try:
            if tag.name in ['button', 'input', 'a', 'span','p']:
                temp_login_elements.append(tag)
            else:
                # print("this element is not displayed: ",tag)
                pass
        except:
            print("error while filtering in: ", tag)

    login_elements = temp_login_elements

    print("number of login elements after filter: ", len(login_elements))
    login_elements = sort_tags(login_elements, "login signin")

    start_url = driver.current_url

    for tag in login_elements:
        try:
            print("trying to create login element using its xpath")
            el_1 = driver.find_element(by=By.XPATH, value=xpath_soup(tag))
            el_1.click()
        except Exception as e:
            print("error in making login element from tag: ", e)
            # continue
            try:
                print("trying to create login element using its class")
                login_btn_class = tag.attrs['class']
                el = driver.find_element(By.CLASS_NAME, login_btn_class)
                el.click()
            except:
                print("error in making login element from tag anyhow! ")
                pass

        clicked_login_flag = False
        
        if tag not in prev_search and  el_1:
            try:
                print("worked till here")
                time.sleep(2)
                try:
                    print(
                        "debug print: trying to click on login button, class of that btn is : ", tag.attrs['class'])
                except:
                    pass
                try:
                    prev_search[tag] = True
                    print('login btn: ', tag)
                    el_1.click()
                    print("debug print: clicked on login button by xpath")
                    clicked_login_flag = True
                except Exception as e:
                    print(e)
                    print(
                        "unable to click by xpath method, now trying to click by class name")
                    # prev_search[tag] = True
                    try:
                        # driver.find_element(By.CLASS_NAME, " ".join(el.attrs['class'])).click()
                        driver.find_element_by_class_name(
                            " ".join(tag.attrs['class'])).click()
                        clicked_login_flag = True
                    except Exception as e:
                        print(e)
                        try:
                            driver.execute_script("arguments[0].click();", el_1)
                            print("clicked through js 😎😎😎")
                            clicked_login_flag = True
                        except:
                            try:
                                ac = ActionChains(driver)
                                ac.move_to_element(el_1).move_by_offset(
                                    1, 1).click().perform()
                            except:
                                print("not clicked through js")
                            print("unable to click login btn anyhow!")

                try:
                    print("class of login btn is: ", tag.attrs['class'])
                    print("xpath of element is: ", xpath_soup(tag))
                except:
                    pass

                if not clicked_login_flag:
                    continue

                # check if it redirects to a new page if yes then go to that page and check for password field if found then continue else close that tab and retry with other found login btns
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    print("switched to the other window")
                time.sleep(7)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
                # funciton to find password tags(both input tags with type=password and input tags with type=text)

                def find_password_tags(driver):
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    password_tags = soup.find_all(lambda tag: is_match(
                        tag, re.compile(rules["password"]), {}, check_attrs=True) and tag.name in ['input'] and 'type' in tag.attrs)
                    print("length password tags -:", len(password_tags))
                    print("password tags are -:",password_tags)
                    # sorting logic by tanuj
                    password_tags.sort(key=lambda e: len(xpath_soup(e)))

                    # password_tags = soup.find_all(
                    #     lambda tag: tag.name == input and type in tag)
                    temp_password_tags = []
                    for tag in password_tags:
                        print('in for loop ----->',tag)
                        if tag.attrs['type'] == "password":
                            temp_password_tags.append(tag)
                            print('in if loop ----->',tag)
                        try:
                            if tag.attrs['type'] == "text" and re.compile(rules['password']).search(tag.attrs['placeholder']):
                                temp_password_tags.append(tag)
                        except:
                            pass
                    password_tags = temp_password_tags
                    return password_tags

                password_tags = find_password_tags(driver)
                
                # if unable to find password field then try to find it inside iframes
                if len(password_tags) == 0:
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    print("finding password field inside iframe tags")
                    print("no of iframes: ", len(iframes))
                    for iframe in iframes:
                        try:
                            driver.switch_to.frame(iframe)
                        except:
                            print("unable to switch to iframe tag")
                        time.sleep(3)
                        password_tags = find_password_tags(driver)
                        if len(password_tags) > 0:
                            password_inside_iframe = True
                            break
                        else:
                            driver.switch_to.default_content()

                no_of_password_fields = len(password_tags)
                print("debug print: no of password fields=",
                      no_of_password_fields)
                if no_of_password_fields > 0:
                    for tag in password_tags:
                        el = driver.find_element(By.XPATH, xpath_soup(tag))
                        
                        # if el.is_displayed():
                        if True:
                            password_tag_loc = el.location
                            print("first loop is running")
                            return True, password_tags
                            
                # didnt found the password field in the redirected page switching back to the first window
                no_of_tabs = len(driver.window_handles)
                print("no of opened tabs", no_of_tabs)
                if no_of_tabs > 1:
                    for tab in range(no_of_tabs-1, 0, -1):
                        print(tab)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[tab-1])

                elif find_login(prev_search, rules, matched_login_entity):
                    return True, password_tags
                else:
                    driver.get(start_url)
                break
            except Exception as e:
                print("the type of exception variabe e is: ", type(e))
                print("exception: ", e)
                time.sleep(5)
                pass
    driver.get(start_url)
    return False, []

# #----------------------------------------------------------------------------------------------------------------------------------------
def close_pu(driver, matched_login_entity):
    # driver.refresh()
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    popups = soup.find_all(lambda tag: is_match(
        tag, re.compile(rules["popup"]), {}) and tag.name in ['button', 'svg', 'img', 'span', 'i', 'a', 'div'])
    # popups.sort(key=lambda e: len(matched_login_entity[e]))
    print("no of popup buttons: ", len(popups))
    # code to filter elements on the basis of their visibility
    temp_popups = []
    for tag in popups:
        try:
            if tag.name == 'div':
                if driver.find_element(By.XPATH, xpath_soup(tag)).is_displayed() and len(tag.text) < 50:
                    temp_popups.append(tag)
                else:
                    continue
            # elif driver.find_element(By.XPATH, xpath_soup(tag)).is_displayed():
            else:
                temp_popups.append(tag)
        except Exception as e:
            print(e)
            continue

    popups = temp_popups
    print("no of popup buttons after filter: ", len(popups))

    popups = sort_tags(popups, "close")
    print(popups)
    for pu in popups:
        try:
            popup_class = pu.attrs['class'][0]
        except:
            popup_class = "UnKnownClass"
        print(f'popup button -----> {pu.text.strip()}')
        # print("DP: ", len(driver.find_element(By.XPATH, xpath_soup(pu))))

        try:
            el = driver.find_element(By.XPATH, xpath_soup(pu))
            driver.execute_script("arguments[0].click();",el )
            
        except:
            print(" the popup is not clicked ")
           
#----------------------------------------------------------------------------------------------------------------------------------------------------
# function to submit the amount after clicking amt btn or entering amt in the field
def submit_amt(driver, amount_field):
    # this function find submit btns below the amt_input_field/amt_btn and click on it
    # amount_field : is either amt_btn or amt_input_field
    try:
        amount_field_loc = amount_field.location
    except:
        amount_field_loc = {"x":0,"y":0}
    
    # trying to click on the submit button after entering amount in the field
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    submit_btns = soup.find_all(
        lambda tag: is_match(tag, re.compile(rules['submit']), {}) and tag.name in ['button', 'input', 'a', 'div','span'])
    print("no. of submit buttons before filter: ",
          len(submit_btns))
    temp_submit_btns = []
    for btn in submit_btns:
        if btn.name == 'input':
            try:
                if btn.name == 'input' and btn.attrs['type'] in ['submit', 'button']:
                    temp_submit_btns.append(btn)
            except:
                pass
        elif btn.name == 'div' and len(btn.text) < 8:
            if len(btn.find_all()) < 2:
                temp_submit_btns.append(btn)
        else:
            temp_submit_btns.append(btn)
    # submit_btns = temp_submit_btns

    # submit_btns = sorted(temp_submit_btns, key=lambda x: len(x.text))
    submit_btns = sort_tags(submit_btns, "deposit submit")
    print("submit btn 1st: ", submit_btns[0])
    print("no. of submit buttons after filter: ",
          len(submit_btns))
    submitted = False
    for btn in submit_btns:
        if btn not in prev_search:
            # print("submit btn: ", btn.text.strip())
            try:
                e = driver.find_element(
                    By.XPATH, xpath_soup(btn))
            except:
                continue
            if e.is_displayed():
                print(f'submit btn: {btn.text.strip()[:50]} ({btn.name})')
                # sb = submit_btn
                # a = amount_field
                btn_loc = e.location
                sb_x = btn_loc['x']
                sb_y = btn_loc['y']
                a_x = amount_field_loc['x']
                a_y = amount_field_loc['y']
                print("sb_x: ", sb_x)
                print("sb_y: ", sb_y)
                print("a_x: ", a_x)
                print("a_y: ", a_y)
                # if ((a_x<sb_x <= a_x+300) and (a_y-10 <= sb_y <= a_y+10 )) or ((a_x-50 <= sb_x <= a_x+300) and (sb_y<=a_y+300)):
                # <= a_y+300)):
                if ((a_x-500 <= sb_x <= a_x+1000) and (a_y+20 < sb_y)):
                    print("found the submit btn")
                    # e.click()
                    ac = ActionChains(driver)
                    ac.move_to_element(e).move_by_offset(
                        1, 1).click().perform()
                    time.sleep(1)
                    print("clicked submit btn: ", btn.text.strip())
                    submitted = True
                    break
    return submitted
# function to find amount tags

#----------------------------------------------------------------------------------------------------------------------------------------
def find_amount_tags(driver):
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    amount_tags = soup.find_all(lambda tag: tag.name == 'input' and is_match(
        tag, re.compile(rules['amount']), {},check_attrs=True))
    temp_amount_tags = []
    
    for tag in amount_tags:
        try:
            if tag.attrs['type'] in ['text', 'tel', 'number']:
                temp_amount_tags.append(tag)
        except:
            pass
    amount_tags = temp_amount_tags
    amount_tags = sort_tags(amount_tags, "amount")
    
    if len(amount_tags)==0:
        amount_tags = soup.find_all(lambda tag: tag.name == 'input', {})
        temp_amount_tags = []
        for tag in amount_tags:
            try:
                if tag.attrs['type'] in ['text', 'tel', 'number']:
                    temp_amount_tags.append(tag)
            except:
                pass
        amount_tags = temp_amount_tags
        # amount_tags = sort_tags(amount_tags, "amount")
    
    return amount_tags

#------------------------------------------------------------------------------------------------------------------------------------------------------
#  function to enter amount and then press submit btn
def deposit_amount(driver, amount_tags):
    exit = False
    time.sleep(5)
    print("length of amount tags: ", len(amount_tags), amount_tags)
    amt_btn_clicked = amount_button(driver)
    # if not amt_btn_clicked:
    for tag in amount_tags:
        if tag not in prev_search:
            for e in driver.find_elements(By.XPATH, xpath_soup(tag)):
                # if e.is_displayed():
                if True:
                    prev_search[tag] = True
                    print("amount tag is visible")
                    amount_field = e
                    try:
                        amount_field_loc = amount_field.location
                        ac = ActionChains(driver)
                        # print("problem in clicking on the amount field")
                        try:
                            print("id of the amount tag: ", tag.attrs['id'])
                        except:
                            pass
                        # checking if amt btn is clicked, if so dont enter amt manually
                        # if not amt_btn_clicked:
                        if True:
                            try:  
                                ac.click(amount_field).key_down(Keys.CONTROL).send_keys(
                                    "A").key_up(Keys.CONTROL).perform()
                            except:
                                print("amount field is not cleared ")
                            print("cleared amount field")
                            # amount_field.clear()
                            amount_field.send_keys('1000')
                            print("entered amount in amount field")
                        else:
                            print(
                                "already clicked on amt btn so not entering amt manually")
                        # amount_field.send_keys(Keys.ENTER)
                        print("pressed enter key")
                        submitted = submit_amt(driver, amount_field)
                        if len(driver.window_handles) > 1 or submitted:
                            exit = True
                            break

                    except Exception as e:
                        try:
                            driver.execute_script("arguments[0].click();", amount_field)
                        except:
                            print(" the amount field is not clicked ")
                            print(amount_field)
                            
                        try:
                            driver.execute_script("arguments[0].value='1000';", amount_field)
                            print("send 1000 to amount field 🥳🥳")
                        except:
                            print("no data send ")
                        print(e)
                        pass

            if exit:
                break
# find_payment_gateway
#-------------------------------------------------------------------------------------------------------------------------------------------------------

# def find_upi_btns(driver, prev_search, in_frames=False):
#     if not in_frames:
#         # first check for upi buttons outside the iframe tags
#         print("looking for upi buttons outside iframe tags")
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         upi_buttons = soup.find_all(lambda tag: is_match(
#             tag, re.compile(rules["upi"]), matched_login_entity))
#         upi_buttons.sort(key=lambda e: len(matched_login_entity[e]))
#         upi_buttons=sort_tags(upi_buttons,"upi")
        
#         return upi_buttons
#     else:
#         iframes = driver.find_elements(By.TAG_NAME, "iframe")
#         print("no of iframes: ", len(iframes))
#         # then check for upi buttons inside iframe tagsmatched
#         print("looking for upi buttons inside iframe tags")
#         for iframe in iframes:
#             try:
#                 driver.switch_to.frame(iframe)
#             except:
#                 print("unable to switch to iframe tag")
#             soup = BeautifulSoup(driver.page_source, 'html.parser')
#             # with open('./temp.html', 'w') as f:
#             #     f.write(str(soup))
#             # upi_buttons = soup.find_all(lambda tag: is_match(
#             #     tag, re.compile(rules["upi"]), matched_login_entity))
#             # upi_buttons.sort(key=lambda e: len(matched_login_entity[e]))
#             upi_buttons = soup.find_all(lambda tag: re.compile('upi').findall(
#                 str(tag)) and tag.name in ['a', 'svg', 'img', 'span', 'p', 'div', 'figure'])
#             # upi_buttons.sort(key=lambda e: len(xpath_soup(e)))
#             #commit 1
#             upi_buttons.sort(key=lambda e: len(xpath_soup(e)))
#             # start_url = driver.current_url
#             if len(upi_buttons) > 0:
#                 return upi_buttons
#             else:
#                 driver.switch_to.default_content()
#         return []


#---------------------------------------------------------------------------------------------------------------------------------------------------

# def continue_payment(driver):
#     time.sleep(10)
#     no_of_tabs = len(driver.window_handles)
#     print("no of opened tabs", no_of_tabs)
#     if no_of_tabs > 1:
#         driver.switch_to.window(driver.window_handles[-1])
#     print(driver.title)
#     # small function to clear field before entering something
#     def clear_field(el):
#         try:
#             print("trying clear the field")
#             ac = ActionChains(driver)
#             ac.click(el).key_down(Keys.CONTROL).send_keys(
#                 "A").key_up(Keys.CONTROL).perform()
#             print("cleared the field")
#         except:
#             print("unable to clear the field")

#     print("------------contiue_payment start------------")
#     print("on page: ",driver.title)
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     input_tags = soup.find_all(lambda tag: is_match(tag, re.compile(rules['pla']), {
#     }) and tag.name == 'input')  # and tag.attrs['type']  in ['tel','text','Email','input'])
#     temp_input_tags = []
#     for tag in input_tags:
#         try:
#             if tag.attrs['type'] in ['tel', 'text', 'email', 'number', 'input','checkbox']:
#                 temp_input_tags.append(tag)
#         except:
#             # when input tag doesnot have type attribute then by default type is text
#             temp_input_tags.append(tag)
#     input_tags = temp_input_tags
#     print(f"no of input tags: {len(input_tags)}")
#     continue_btns = soup.find_all(lambda tag: is_match(
#         tag, re.compile(rules['continue']), {}) and tag.name in ['button', 'a', 'span'])

#     print(f"number of continue btns before filter: {len(continue_btns)}")
#     temp_continue_btns = []
#     for btn in continue_btns:
#         if len(btn.find_all()) < 3:
#             temp_continue_btns.append(btn)
#     continue_btns = temp_continue_btns
#     print(f"number of continue btns after filter: {len(continue_btns)}")

#     for field in input_tags:
#         if field not in prev_search:
#             try:
#                 el = driver.find_element(By.XPATH, xpath_soup(field))
#             except:
#                 # if unable to convert that field into element then skipping that field
#                 continue

#             try:
#                 # name
#                 # if re.compile(rules['form_regex']['name']).findall(str(tag)[:50]):
#                 if re.compile(rules['form_regex']['name']).findall(field.attrs['placeholder']):
#                 # if is_match(tag, re.compile(rules['form_regex']['name']),{}):
#                     # el.click()
#                     clear_field(el)
#                     el.send_keys(rules['form_data']['name'])
#                     el.send_keys(Keys.ENTER)
#                     print(f"entered name: {rules['form_data']['name']}")
#                 # phone_no
#                 # elif re.compile(rules['form_regex']['phone']).findall(str(tag)[:50]):
#                 elif is_match(tag, re.compile(rules['form_regex']['phone']),{}):
#                     # el.click()
#                     clear_field(el)
#                     el.send_keys(rules['form_data']['phone'])
#                     el.send_keys(Keys.ENTER)
#                     print(f"entered phone_no: {rules['form_data']['phone']}")
#                 # email
#                 # elif re.compile(rules['form_regex']['email']).findall(str(tag)[:50]):
#                 elif is_match(tag, re.compile(rules['form_regex']['email']),{}):
#                     # el.click()
#                     clear_field(el)
#                     el.send_keys(rules['form_data']['email'])
#                     el.send_keys(Keys.ENTER)
#                     print(f"entered email: {rules['form_data']['email']}")
#                 # upi
#                 # elif re.compile(rules['form_regex']['upi']).findall(str(tag)[:50]):
#                 elif is_match(tag, re.compile(rules['form_regex']['upi']),{}):
#                     # el.click()
#                     # clear_field(el)
#                     el.send_keys(rules['form_data']['upi'])
#                     # el.send_keys(Keys.ENTER)
#                     print(f"entered upi: {rules['form_data']['upi']}")
#                 # account_no
#                 # elif re.compile(rules['form_regex']['account']).findall(str(tag)[:50]):
#                 elif is_match(tag, re.compile(rules['form_regex']['account']),{}):
                
#                     # el.click()
#                     clear_field(el)
#                     el.send_keys(rules['form_data']['account'])
#                     el.send_keys(Keys.ENTER)
#                     print(
#                         f"entered account_no: {rules['form_data']['account']}")
#                     # post_code
#                 # elif re.compile(rules['form_regex']["post_code"]).findall(str(tag)[:50]):
#                 elif is_match(tag, re.compile(rules['form_regex']['post_code']),{}):
#                     # el.click()
#                     clear_field(el)
#                     el.send_keys(rules['form_data']["post_code"])
#                     el.send_keys(Keys.ENTER)
#                     print(
#                         f"entered post_code: {rules['form_data']['post_code']}")
#                     # city
#                 # elif re.compile(rules['form_regex']['city']).findall(str(tag)[:50]):
#                 elif is_match(tag, re.compile(rules['form_regex']['city']),{}):
#                     # el.click()
#                     clear_field(el)
#                     el.send_keys(rules['form_data']['city'])
#                     el.send_keys(Keys.ENTER)
#                     print(f"entered city: {rules['form_data']['city']}")
#                 # address
#                 # elif re.compile(rules['form_regex']['address']).findall(str(tag)[:50]):
#                 elif is_match(tag, re.compile(rules['form_regex']['address']),{}):
#                     # el.click()
#                     clear_field(el)
#                     el.send_keys(rules['form_data']['address'])
#                     el.send_keys(Keys.ENTER)
#                     print(f"entered address: {rules['form_data']['address']}")
#                 # checkbox
#                 elif field.attrs['type'] == 'checkbox':
#                     el.click()
#                     el.send_keys(Keys.SPACE)
#                     print("checked the checkbox")
#                 elif field.attrs['placeholder'] == '':
#                     raise Exception
#                 else:
#                     clear_field(el)
#                     el.send_keys("damo1000")
#                     el.send_keys(Keys.ENTER)
#                     print("entered demo123")

#             except:
#                 # when the field does not have any placeholder then just enter "demo123"
#                 # el.click()
#                 try:
#                     clear_field(el)
#                     el.send_keys("damo1000")
#                     # el.send_keys(Keys.ENTER)
#                     print("entered demo123")
#                 except Exception as e:
#                     print(e)
#                     try:
#                         driver.execute_script("arguments[0].click();", el)
#                     except:
#                         print("*****")
#     len_continue_btns = len(continue_btns)
#     Qr_code = soup.find_all(lambda tag: is_match(tag, re.compile(rules['scan_qr']), {}, check_attrs=True))
#     continue_btns.sort(key=lambda tag: len(xpath_soup(tag)))
#     if len_continue_btns < 30 and len(Qr_code)<1:
#         for no,btn in enumerate(continue_btns):
#             print(f'----------continue btn: {no}/{len_continue_btns}----------')
#             try:
#                 el = driver.find_element(By.XPATH, xpath_soup(btn))
#             except:
#                 # if unable to convert that btn into element then skipping that btn
#                 print("skiping")
#                 continue
#             try:
#                 el.click()
#                 print(f"clicked on continue btn: {btn.text.strip()}")
#             except:
#                 print("error while clicking continue btn")
#                 pass
#                 # try:
#                 #     ac = ActionChains(driver)
#                 #     ac.move_to_element(el).click().perform()
#                 # except:
#                 #     print("cant click continue btn")
#     else:
#         print("len of continue btns is too much hence skipping all.")

#     time.sleep(5)
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     continue_btns = soup.find_all(lambda tag: is_match(
#         tag, re.compile(rules['continue']), {},check_attrs=False) and tag.name in ['button', 'a','img','span'])
#     print(f"number of continue btns before filter: {len(continue_btns)}")
#     # temp_continue_btns = []
#     # continue_btns=sort_tags(continue_btns,'pay')
#     continue_btns.sort(key=lambda tag: len(xpath_soup(tag)))
#     # for btn in continue_btns:
#     #     if len(btn.find_all()) < 3 and len(btn.text.strip()) < 10:
#     #         temp_continue_btns.append(btn)
#     # continue_btns = temp_continue_btns
#     print(f"number of continue btns after filter: {len(continue_btns)}")
#     time.sleep(5)
#     # Qr_code = soup.find_all(lambda tag: is_match(
#     #     tag, re.compile(rules['scan_qr']), {}) and tag.name in ['h1', 'div', 'small'])
#     Qr_code = soup.find_all(lambda tag: is_match(tag, re.compile(rules['scan_qr']), {}),check_attrs=False)
#     for tag in Qr_code:
#         if is_match(tag, re.compile(rules['upi_id']), {},check_attrs=True):
#             upi_id = re.compile(rules['upi_id']).findall(str(tag))[0]
#             print(f'upi id is ------> {upi_id}')
#             try:
#                 if upi_id not in upi_ids_found:
#                     upi_ids_found.append(upi_id)
#             except:
#                 print("upi variale nhi mila ")
                
#         else:
#             try:
#                 if re.compile("Click here for qR code").search(tag.text):
#                     tag.cilck()
#             except:
#                 print(f'upi or qr btn ------> {tag.text.strip()}')
                
#             # print(f'upi or qr btn ------> {tag.text.strip()}')
            


#     stop_key=1
#     # again cliking the continue btns
#     print(f"length of QR-: {len(Qr_code)}")
#     if len(Qr_code) > 0 and stop_key==2:
#         return
#     len_continue_btns = len(continue_btns)
#     continue_btns = sort_tags(continue_btns, "deposit confirm")
#     if len_continue_btns < 30:
            
#         for no,btn in enumerate(continue_btns):
#             if len(btn.text.strip()[:50])<2:
#                 continue
#             print(f'----------continue btn: {no}/{len_continue_btns}----------')
#             print(f'continue btn--->{btn.text.strip()[:50]}')
#             try:
#                 el = driver.find_element(By.XPATH, xpath_soup(btn))
#             except:
#                 # if unable to convert that btn into element then skipping that btn
#                 continue

#             try:
#                 el.click()
#                 print(f"clicked on continue btn: {btn.text.strip()}")
#                 stop_key=stop_key+1
#             except:
#                 try:
#                     driver.execute_script("arguments[0].click();", el)
#                     print("clicked through js 😎😎😎")
#                 except:
#                     print("not clicked through js")
#                 pass
#                 # try:
#                 #     ac = ActionChains(driver)
#                 #     # ac.move_to_element(el).click().perform()
#                 #     ac.click(el).perform()
#                 # except:
#                 #     print("cant click continue btn")
#     else:
#         print("len of continue btns is too much hence skipping all.")


#     for Qr in Qr_code:
#         print(Qr.text)
#         try:
#             el = driver.find_element(By.XPATH, xpath_soup(Qr))
#             ActionChains(driver).move_to_element(el).perform()
#             try:
#                 ac = ActionChains(driver)
#                 ac.move_to_element(el).perform()
#             except:
#                 print(" not at QR")
#         except:
#             # if unable to convert that btn into element then skipping that btn
#             try:
#                 ac = ActionChains(driver)
#                 ac.move_to_element(el).perform()
#             except:
#                 print("cant find QR")
#             continue
    
#     # tring to call this function recursively 
#     soup = BeautifulSoup(driver.page_source, 'html.parser')

#     qr_or_upi_id = soup.find_all(lambda tag: is_match(tag, re.compile(rules['scan_qr']), {}, check_attrs=False))
#     print(f'no or qr or upi elements before filter: {len(qr_or_upi_id)}')
#     # temp_qr_or_upi_id=[]
#     # for tag in qr_or_upi_id:
#     #     if len(tag.find_all()) < 2:
#     #         temp_qr_or_upi_id.append(tag)
#     # qr_or_upi_id = temp_qr_or_upi_id

#     # print(f'no or qr or upi elements after filter: {len(qr_or_upi_id)}')
#     global continue_payment_recursive_count
#     if len(qr_or_upi_id) < 2 and continue_payment_recursive_count < 4:
#         print(f'--------------------continue payment called recursively({continue_payment_recursive_count})--------------------')
#         continue_payment_recursive_count+=1
#         continue_payment(driver)
#     else:
#         print("exiting continue payment function")        
#===================================================================================================================================================

# def get_payment_page(prev_search, driver):
#     # flow
#     # 1. look for any payment option in the website
#     # 1.1 find deposit money option in the page
#     # soup = BeautifulSoup(driver.page_source, 'html.parser')
#     page_height = driver.execute_script(
#         "return window.innerHeight")
#     exit = False
#     print("no of rules for deposit_copy: ", len(rules['deposit_copy']))
#     soup = custom_wait(driver, re.compile(rules['deposit']))
#     if not soup:
#         soup = BeautifulSoup(driver.page_source, 'html.parser')

#     for rule_no in range(len(rules['deposit_copy'])):
#         print(f'============ rule no: {rule_no} / {len(rules["deposit_copy"])} ============')
#         print("using rule: ", rules['deposit_copy'][rule_no])
#         deposit_buttons = soup.find_all(lambda tag: is_match(
#             tag, re.compile(rules["deposit_copy"][rule_no]), {}, check_attrs=True))
#         # deposit_buttons.sort(key=lambda e: len(matched_login_entity[e]))
#         print("deposit buttons before filter:", len(deposit_buttons))
    
#         # code to filter elements on the basis of their visibility
#         temp_deposit_buttons = []
#         for tag in deposit_buttons:
#             try:
#                 # if driver.find_element(By.XPATH, xpath_soup(tag)).is_displayed():
#                 el = driver.find_element(By.XPATH, xpath_soup(tag))

#                 if el.location['y'] < page_height:
#                     # code to check whether the tag has 0 children
#                     btn_text = tag.text.strip()
#                     if len(tag.find_all()) < 3 and len(btn_text) < 20 and "\n" not in btn_text:
#                         temp_deposit_buttons.append(tag)
#             except:
#                 continue
#         deposit_buttons = temp_deposit_buttons

 
#         count=5
#         if len(deposit_buttons)<5 :
#             count=len(deposit_buttons)
            
#         deposit_buttons =sort_tags(deposit_buttons, 'deposit')
#         deposit_buttons = deposit_buttons[:5]
#         len_deposit_btns = len(deposit_buttons)
#         print("deposit buttons after filter:", len_deposit_btns)
        
#         for no,tag in enumerate(deposit_buttons):
#             print(f'----------- deposit btn: {no}/{len_deposit_btns}-----------')
#             print(f'deposit btn ----------->"{tag.text.strip()}"')
#             if tag not in prev_search:
#                 try:
#                     el = driver.find_element(
#                         by=By.XPATH, value=xpath_soup(tag))
#                 except:
#                     continue
#                 print(
#                     f"location of deposit btn: ({el.location['x']},{el.location['y']})")
#                 # if el.location['y'] < 200:
#                 if True:
#                     try:
#                         prev_search[tag] = True
#                         time.sleep(5)
#                         el.click()
#                         print(
#                             f"clicked on deposit button : {tag.text.strip()}")
#                         try:
#                             print("the id of deposit button : ",
#                                   tag.attrs['id'])
#                         except:
#                             print("the class of deposit button : ",
#                                   tag.attrs['class'])

#                         time.sleep(2)
                        
#                     except:
#                         try:
#                             try:
#                                 driver.execute_script("arguments[0].click();", el)
#                                 print(f'debug print: clicked on deposit btn "{tag.text.strip()}" using JS')
#                             except:
#                                 print(f'debug print: unable to click on deposit btn "{tag.text.strip()}" using JS')

#                         except:
#                             print(f'unable to click on deposit btn "{tag.text.strip()}" using move_by_offset')
#                             ac = ActionChains(driver)
#                             ac.move_to_element(el).move_by_offset(
#                                 2, 2).click().perform()
#                             print(f'debug print: clicked on deposit btn "{tag.text.strip()}" using move_by_offset')
                            
#                     # checking wheather we are at payments option page
#                     # button_of_ok = driver.find_element_by_class_name('el-button.depositDialog-btn.el-button--default')
#                     # button_of_ok.click()
#                     ok_button = driver.find_element(By.XPATH, "//span[text()='OK']")

#                     ok_button.click()
#                     try:
#     # Find the h6 element with the text 'INSTANT PAYMENT (D)'
#                         h6_element = driver.find_element(By.XPATH, "//h6[text()='INSTANT PAYMENT (D)']")

#     # Find the button element inside the h6 element
#                         button_element = h6_element.find_element(By.TAG_NAME, 'button')

#     # Click on the button
#                         button_element.click()

#                     except Exception as e:
#                         print(f"An error occurred: {str(e)}")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------             
# ==========================> deposit without bonus page handle 
                    
                    # soup = BeautifulSoup(driver.page_source, 'html.parser')
                    # bonus_options = soup.find_all(lambda tag: is_match(
                    #     tag, re.compile(rules['bonus']), {},check_attrs=False))
                    # #-------> sorting the tag on the basis of without text
                    # print("*********************** Bonus page Start ***********************")
                    # print("the length of bonus is-", len(bonus_options))
                    # bonus_options= sort_tags(bonus_options, 'bonus')     
                    # for bonus in bonus_options:
                    #     if re.compile(rules["bonus"]).search(bonus.text) and len(bonus.find_all())< 3 and len(bonus.text)< 32:
                    #         try:
                    #             bonus.click()
                    #             print("clicked the bonus button using direct click ")
                    #         except Exception as e:
                    #             print("error during clicking bonus",e)
                    #         try:
                    #             el = driver.find_element(
                    #             by=By.XPATH, value=xpath_soup(bonus))
                    #             el.click()
                    #             print("clicked the bonus button using Xpath click ")
                    #         except Exception as e:
                    #             print("error during clicking bonus By = Xpath",e)
                                    
# ==========================> end bonus page 
                    
                    # print("page_height: ", page_height)
                    # time.sleep(10)
                    # print("checking that are we on payment page or not")
                    # soup = BeautifulSoup(driver.page_source, 'html.parser')
                    # payments_options = soup.find_all(lambda tag: is_match(
                    #     tag, re.compile(rules['payment_page']), {},check_attrs=True))
                    # # filtering payment options
                    # temp_payment_options = []
                    # for pay_option in payments_options:
                    #     try:
                    #         el = driver.find_element(
                    #             by=By.XPATH, value=xpath_soup(tag))
                    #     except:
                    #         continue
                    #     if el.location['y'] < page_height:
                    #         if len(pay_option.text.strip()) < 40 and len(pay_option.find_all()) < 3 and len(pay_option.text.strip())>1:
                    #             temp_payment_options.append(pay_option)
                    # payments_options = temp_payment_options

                    # print("no of payment options: ", len(payments_options))

                    # # if no payments options found in default content then we will look for them in iframes
                    # if len(payments_options) ==0:
                    #     print("looking for payment options inside iframes")
                    #     iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    #     print("no of iframes: ", len(iframes))
                    #     for iframe in iframes:
                    #         try:
                    #             driver.switch_to.frame(iframe)
                    #         except:
                    #             print("unable to switch to iframe tag")
                    #             continue
                    #         soup = BeautifulSoup(
                    #             driver.page_source, 'html.parser')
                    #         payments_options = soup.find_all(lambda tag: is_match(
                    #             tag, re.compile(rules['payment_page']), {}))
                    #         # filtering payment options
                    #         print(len(payments_options))
                    #         temp_payment_options = []
                    #         for pay_option in payments_options:
                    #             try:
                    #                 el = driver.find_element(
                    #                     by=By.XPATH, value=xpath_soup(tag))
                    #             except:
                    #                 continue
                    #             if el.location['y'] < page_height:
                    #                 if len(pay_option.text.strip()) < 40 and len(pay_option.find_all()) < 3:
                    #                     temp_payment_options.append(pay_option)
                    #         payments_options = temp_payment_options

                    #         if len(payments_options) > 0:
                    #             print("found payments option inside iframe")
                    #             # driver.switch_to.default_content()
                    #             break
                    #         else:
                    #             driver.switch_to.default_content()

                    # visible_payment_optns_count = 0
                    # print("===========no of payments options: ",
                    #       len(payments_options))
                    # for pay_option in payments_options:
                    #     try:
                    #         print("pay option text: ", pay_option.text.strip())
                    #         el = driver.find_element(
                    #             By.XPATH, xpath_soup(pay_option))
                    #         print("el_y_coordinate:", el.location['y'])
                    #         if el.location['y'] < page_height:
                    #             visible_payment_optns_count += 1
                    #     except Exception as e:
                    #         print("temp error log: ", e)
                    #         pass

                    # print("visible_payment_optns_count: ",
                    #       visible_payment_optns_count)
                    # # print("percentage of visible elements: ", (visible_payment_optns_count/len(payments_options))*100)
                    # # if len(payments_options) > 0 and visible_payment_optns_count > 0.2 * len(payments_options):
                    # if len(payments_options) > 0 and visible_payment_optns_count > 3:
                    #     # we are at the payment page
                    #     exit = True
        #             #     break
        # if exit:
        #     print("we are on payment page!")
        #     try:
        #         driver.switch_to.default_content()
        #     except:
        #         pass
        #     break
        print("clicked------------------------------------------------------------------------------------------------------")
    # 2. find UPI option in payment in payment method
    # time.sleep(5)
    # exit = False
    # online_deposit(driver)
    # print("looking for upi buttons outside iframe tags")
    # first check for upi buttons outside the iframe tags
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    upi_buttons = soup.find_all(lambda tag: is_match(tag, re.compile(rules["upi"]), matched_login_entity))
    # upi_buttons.sort(key=lambda e: len(matched_login_entity[e]))
    l1 = []
    l2 = []
    for upi_btn in upi_buttons:
        if len(upi_btn.find_all()) < 2 and re.compile(rules["upi"]).search(upi_btn.text):
            # if len(upi_btn.find_all())==0 and re.compile(rules["upi"]).search(upi_btn.text):
            print("req: ", upi_btn.text)
            l1.append(upi_btn)
        else:
            l2.append(upi_btn)

    upi_buttons = l1+l2
    upi_buttons = sort_tags(upi_buttons, 'upipay D')

    # upi_buttons = soup.find_all(lambda tag: re.compile('upi').findall(
    #     str(tag)) and tag.name in ['a', 'svg', 'img', 'span', 'p'])
    # upi_buttons.sort(key=lambda e: len(xpath_soup(e)))
    # start_url = driver.current_url
    print("no of upi buttons: ", len(upi_buttons))
    for el in upi_buttons:
        # print(el)
        if el not in prev_search and len(el.text)<10:
            time.sleep(1)
            try:
                if driver.find_element(
                        by=By.XPATH, value=xpath_soup(el)):
                    # print(driver.find_element(
                    
                    #     by=By.XPATH, value=xpath_soup(el)).text)
                    el_1=driver.find_element(
                        by=By.XPATH, value=xpath_soup(el))
                    #  =====>  Debug
                    # driver.find_element(
                    #     by=By.XPATH, value=xpath_soup(el)).click()
                    driver.find_element(
                        by=By.XPATH, value=xpath_soup(el)).click()
                    time.sleep(2)
                    try:
                        driver.find_element(
                            by=By.XPATH, value=xpath_soup(el)).click()
                        print("clicked on upi option second time")
                    except:
                        print(" clicking second time to upi button")
                    print(f"debug print: clicked on UPI option ----> {el.text.strip()}")
                    try:
                        
                        print("class of upi btn:", el.attrs['class'])
                    except:
                        try:
                            print('id of upi btn: ', el.attrs['id'])
                        except:
                            pass
                    prev_search[el] = True
                    break
                else:
                    print('upi btn is not displayed')
                    try:
                        driver.execute_script("arguments[0].click();", el_1)
                        print("clicked through js 😎😎😎")
                    except:
                        print("not clicked through js")
            except Exception as e:
                print(e)
                print("debug print: unable to click on UPI option by xpath method")
                try:
                    driver.execute_script("arguments[0].click();", el_1)
                    print("clicked through js 😎😎😎")
                except:
                    print("not clicked through js")
                    # upi_buttons=0
                    
# =====================> start continue button  after clicking UPI option
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')   
    continue_buttons = soup.find_all(lambda tag: is_match(
                tag, re.compile(rules["continue"]), {}))
    print("----------------- continue button len -: ", len(continue_buttons))
    continue_buttons.sort(key=lambda tag:len(xpath_soup(tag)))
    #filtering the btns
    temp_continue_btns=[]
    for c_btns in continue_buttons:
        if len(c_btns.find_all())<4:
            temp_continue_btns.append(c_btns)
        else:
            pass
        
    continue_buttons==temp_continue_btns
    print("the len of continue btns after filter is -: ", len(continue_buttons))
    for btn in continue_buttons:
        if len(btn.text)<10:
            if re.compile(rules["continue1"]).search(btn.text):
                el=driver.find_element(By.XPATH, xpath_soup(btn))
                try:
                    print("----> click ",btn.text)
                    btn.click()
                except:
                    print("can't click by normal click ")
                    try:
                        print("----> click by Xpath ",btn.text)
                        el.click()
                    except:
                        print("can't click by xpath ")
        
    
# =====================> ending continue button

    # 2.1 enter some amount and go to the check out page
    time.sleep(5)

    amount_tags = find_amount_tags(driver)

    # deposit_amount(driver, amount_tags)

    if len(upi_buttons) == 0 or len(amount_tags) == 0:
        time.sleep(1)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print("no of iframes: ", len(iframes))
        # then check for upi buttons inside iframe tagsmatched
        print("looking for upi buttons inside iframe tags")
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
            except:
                print("unable to switch to iframe tag")
                continue
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # with open('./temp.html', 'w') as f:
            #     f.write(str(soup))
            upi_buttons = soup.find_all(lambda tag: is_match(
                tag, re.compile(rules["upi"]), {}) and tag.name in ['a', 'svg', 'img', 'span', 'p', 'div', 'figure', 'h1'])
            # upi_buttons.sort(key=lambda e: len(matched_login_entity[e]))
            # upi_buttons = soup.find_all(lambda tag: re.compile('upi').findall(
            #     str(tag)) and tag.name in ['a', 'svg', 'img', 'span', 'p', 'div', 'figure','h1'])
            print("no of upi buttons: ", len(upi_buttons))
            l1 = []
            l2 = []
            for upi_btn in upi_buttons:
                if len(upi_btn.find_all()) < 2 and re.compile(rules["upi"]).search(upi_btn.text):
                    # if len(upi_btn.find_all())==0 and re.compile(rules["upi"]).search(upi_btn.text):
                    print("req: ", upi_btn.text)
                    l1.append(upi_btn)
                else:
                    l2.append(upi_btn)

            upi_buttons = l1+l2
            upi_buttons = sort_tags(upi_buttons, 'upi Qr')

            # upi_buttons.sort(key=lambda e: len(xpath_soup(e)))
            # temp_upi_btns = []
            # for btn in upi_buttons:
            #     if len(btn.find_all()) < 2:
            #         temp_upi_btns.append(btn)
            # if len(temp_upi_btns) != 0:
            #     upi_buttons = temp_upi_btns
            print("no of upi buttons after filter: ", len(upi_buttons))
            # start_url = driver.current_url
            exit = False
            for el in upi_buttons:
                # print(el)
                if el not in prev_search:
                    try:
                        driver.find_element(
                            by=By.XPATH, value=xpath_soup(el)).click()
                        print(f"debug print: clicked on UPI option ----> {el.text.strip()}")
                        print("tag name: ", el.name)
                        try:
                            print("the id of upi btn: ", el.attrs['id'])
                        except:
                            try:
                                print("the class of upi btn: ",
                                      el.attrs['class'])
                            except:
                                pass
                        prev_search[el] = True
                        # if we can find ammount fields break the loop of UPI btns
                        time.sleep(2)
                        amount_tags = find_amount_tags(driver)
                        if len(amount_tags) > 0:
                            exit = True
                            break
                    except:
                        print(
                            "debug print: unable to click on UPI option by xpath method")
                        print("tag name: ", el.name)
                        try:
                            # print("id of element id: ", el.attrs['id'])
                            # driver.find_element(
                            #     By.ID, f"{el.attrs['id']}").click()
                            # print("debug print: clicked on UPI option by id method")
                            print(
                                "trying to click on UPI option using move_to_element")
                            ac = ActionChains(driver)
                            ac.move_to_element(el).click()
                        except:
                            print(
                                "debug print: unable to click on UPI option by id method")

        #     if exit:
        #         # continue_payment(driver)
        #         break
        #     else:
        #         print("switch to default content-:")
        #         # driver.switch_to.default_content()
        # # 2.1 enter some amount and go to the check out page
        # time.sleep(5)
        # deposit_amount(driver, amount_tags)
        # time.sleep(10)
        # continue_payment(driver)
    # else:
    #     deposit_amount(driver, amount_tags)
    #     time.sleep(10)
    #     continue_payment(driver)
    # # 3. take the screenshot of the receiver's UPI id

def online_deposit(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    online_deposit_buttons=soup.find_all(lambda tag: is_match(
        tag, re.compile(rules["online"]), {}) and tag.name in ["div"])
    print(online_deposit_buttons)
    flag=False
    online_deposit_buttons=sort_tags(online_deposit_buttons,"deposit")
    print("length of online -:", len(online_deposit_buttons))
    for tag in online_deposit_buttons:
        print(len(tag.text))
        if tag.name=="div" and len(tag.find_all())<2:
            if flag==True:
                print("last tag --------> ",tag)
                break
            else:
                try:
                    print("tag ------> ",tag)
                    el=driver.find_element(By.XPATH,xpath_soup(tag))
                    el.click()
                    flag=True
                except:
                    print("the online button is not clicked")
                    
                    try:
                        driver.execute_script("arguments[0].click();", el)
                        print("clicked through js 01")
                        # flag= True
                    except:
                        print("button not clicked")
                        
                    
def check_login(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    login_btns = soup.find_all(lambda tag: is_match(
        tag, re.compile(rules["check_login_status"]), {}))  # {} is matched_login_entity
    if len(login_btns) > 0:
        return "unable to login"
    else:
        return "logged in"


def agreeTnC(driver):
    print("inside agreeTnC")
    # trying to find agree checkbox
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    agreeCB = soup.find_all(lambda tag: tag.name == "input")
    temp_agreeCB = []
    for cb in agreeCB:
        try:
            if cb.attrs['type'] == 'checkbox':
                temp_agreeCB.append(cb)
        except:
            pass
    agreeCB = temp_agreeCB

    # trying to find accept btn
    matched_accept_btns = {}
    accept_btns = soup.find_all(lambda tag: tag.name in ['button', 'span'] and is_match(
        tag, re.compile(rules['accept']), matched_accept_btns, check_attrs=False))

    for cb in agreeCB:
        e = driver.find_element(By.XPATH, xpath_soup(cb))
        if e.is_displayed():
            e.send_keys(Keys.SPACE)
            print("checkbox checked")


def accept_cookies(driver):
    driver.refresh()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cookie_ele = soup.find_all(lambda tag: is_match(
        tag, re.compile(rules['cookies']), {}, check_attrs=False))
    temp_cookie_ele = []
    for tag in cookie_ele:
        if len(tag.find_all()) < 2:
            temp_cookie_ele.append(tag)
    cookie_ele = temp_cookie_ele

    cookie_acc_btn = soup.find_all(lambda tag: is_match(
        tag, re.compile(rules['cookies_accept']), {}, check_attrs=False))
    temp_cookie_acc_btn = []
    for tag in cookie_acc_btn:
        if len(tag.find_all()) < 2:
            temp_cookie_acc_btn.append(tag)
    cookie_acc_btn = temp_cookie_acc_btn

    for tag in cookie_ele:
        try:
            el = driver.find_element(By.XPATH, xpath_soup(tag))
            el.click()
        except:
            continue
        loc = el.location
        c_x = loc['x']
        c_y = loc['y']
        for acc_btn in cookie_acc_btn:
            try:
                el2 = driver.find_element(By.XPATH, xpath_soup(acc_btn))
            except:
                continue
            loc2 = el2.location
            acb_x = loc2['x']
            acb_y = loc2['y']
            if (acb_x > c_x) and (c_y+200 > acb_y > c_y-20):
                if el2.is_displayed():
                    try:
                        el2.click()
                        print("clicked on accept_cookies btn")
                        print("name: ", acc_btn.text)
                        # break
                    except:
                        print("unable to click on accept_cookies btn")
    
    print("cookie elements: ", len(cookie_ele))
    print("cookie accept btn: ", len(cookie_acc_btn))
    # exit()

# function to upload the required screen shot to s3 and generate finl output 
def final_output(ss_path,url):
    # check for QR code present in the image and extract upi id from that
    img_full_path = os.getcwd() + ss_path[1:]
    try:
        img =cv2.imread(img_full_path)
    except:
        print("unable to read the image")
    decoded_img = decode(img)

    if decoded_img:
        for barcode in decoded_img:
            myData = barcode.data.decode('utf-8')
            match = re.search(r'pa=([^&]+)', myData)
            if match:
                upi_id = match.group(1)
                print(f"upi id found throug QR scanner: {upi_id}")
                if upi_id not in upi_ids_found:
                    upi_ids_found.append(str(upi_id))
            else:
                print(myData)
                # if upi_id not in upi_ids_found:
                #     print(f"upi id found throug QR scanner: {upi_id}")
                #     upi_ids_found.append(str(upi_id))
    else:
        print("no QR code found")

    if len(upi_ids_found)>0:
        # upload that ss to S3 bucket
        BUCKET = 'mf-portal-store'
        CREDENTIALS = {'aws_access_key_id': "",
               'aws_secret_access_key': ""
               }
        # img_path = '/home/tushar/work/AutoLoginScrapper/sites_60_ss/www.lilibet.png'
        # s3_client = boto3.client('s3', **CREDENTIALS)
        IST = pytz.timezone('Asia/Kolkata')
        time = datetime.now(IST).strftime("%H_%M_%S")
        _date = datetime.now(IST).strftime("%Y-%m-%d")
        _datetime = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
        filename = f"{_date}/{time}_{ss_path[ss_path.find('/',2)+1:]}"
        print("========================================================")
        print("========================================================")
        print("========================================================")
        print(f"name of s3 bucket: {BUCKET}")
        print(f"actual path of img: {img_full_path}")
        print(f"folder and name of img on S3: {filename}")
        print(f"upi ids found: {', '.join(upi_ids_found)}")
        print("========================================================")
        print("========================================================")
        print("========================================================")

        try:
            # response = s3_client.upload_file(img_full_path, BUCKET, filename)
            public_img_url = f'https://d28155fq69xo8c.cloudfront.net/{filename}'
            output_df = pd.DataFrame({"url":[url],"upi_ids":[', '.join(upi_ids_found)],"public_img_url":[public_img_url], "datetime":[_datetime], "scan_date":[_date]})
            output_df.to_csv(f"./output.csv", index=False, header=False, mode='a')
            print("========================================================")
            print("========================================================")
            print("============file uploaded and record added to csv============")
            print("========================================================")
            print("========================================================")
            print(public_img_url)
        except Exception as e:
            print(e)

    else:
        print("no upi ids found")

        # create csv like
        # "website url", "upi_ids_found", "path of the ss uploaded to S3" 

def custom_wait(driver, regex_pattern):
    print("custom_wait fn called! waiting until the required elements are found.")
    required_items = []
    # max wait time approx 1 min:
    for wait_counter in range(10):
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        required_items = soup.find_all(
            lambda tag: is_match(tag, regex_pattern, {}))
        print("required elements: ", len(required_items))
        if len(required_items) != 0:
            print("found the required elements resuming the code")
            return soup
    print("required elements not found...stopping the execution")
    # driver.quit()
    return False


options = webdriver.ChromeOptions()
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')
options.add_argument("--disable-notifications")
# options.add_argument('--disable-overlay-scrollbar')
# options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument('--no-sandbox')
# options.set_preference('intl.accept_languages', 'en-GB')
options.add_argument('--window-size=2150,2000')
# options.add_argument('--hide-scrollbars')
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
# opt.profile = ffprofile
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['ignoreZoomSetting'] = False
driver = webdriver.Chrome(
    "chromedriver.exe", options=options)  # , desired_capabilities=capabilities)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                       "source": "Object.defineProperty(navigator, 'webdriver', {get: () => false})"})  # True==>Not genuine false==>genuine
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        run_on_insecure_origins=False,

        )


with open("rules.json", "r") as f:
    rules = json.loads(f.read())

prev_search = {}
matched_login_entity = {}


def main(driver, url, userid, password):
    upi_ids_found.clear()
    parsed = urlparse(url)
    baseURL = parsed.netloc
    baseURL = "http://"+baseURL
    print("base url : ", baseURL)
    load_website(driver, baseURL)
    
    time.sleep(5)
        
    found_login_btn, password_tags = find_login(
        prev_search, rules, matched_login_entity)
    if found_login_btn:
        print("debug 1 -: len of pass", len(password_tags))
        print("location of password field is: ", password_tag_loc)
        time.sleep(3)
        login(driver, userid, password, rules, prev_search, password_tags)
        no_of_tabs = len(driver.window_handles)
        time.sleep(5)
        accept_cookies(driver)
        # agreeTnC(driver)
        # trying to close popup after the login
        try:
            close_pu(driver, matched_login_entity)
            print('close_pu executed')
        except Exception as e:
            print('error in close_pu')
            print(e)
# if new window is opened by closing popup 
        no_of_tabs = len(driver.window_handles)
        print("no of opened tabs", no_of_tabs)
        if no_of_tabs > 1:
            for tab in range(no_of_tabs-1, 0, -1):
                print(tab)
                driver.close()
                driver.switch_to.window(driver.window_handles[tab-1])
                time.sleep(3)
        # get_payment_page(prev_search, driver)
        # checking if redirected to the payment page
        time.sleep(20)
        driver.switch_to.window(driver.window_handles[-1])
        print(driver.title)
        ss_path = f"./Headless/{url[8:url.find('.',12)]}.png"
        driver.save_screenshot(ss_path)
        final_output(ss_path,url)
        no_of_tabs = len(driver.window_handles)
        print("no of opened tabs", no_of_tabs)
        if no_of_tabs > 1:
            for tab in range(no_of_tabs-1, 0, -1):
                print(tab)
                driver.close()
                driver.switch_to.window(driver.window_handles[tab-1])        
        # driver.quit()
        return True
    else:
        # driver.save_screenshot(f"./screenshots/CFL_{url[8:url.find('.',12)]}.png")
        print("can't find login btn")
        # driver.quit()
        return False

main(driver, "https://ekbet1.com","sandy98081", "Pixel2022")
end_time = time.time()
print("execution time: ", int(end_time-start_time), ' sec')
