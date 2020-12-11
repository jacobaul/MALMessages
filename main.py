from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import datetime
import time
import math


import pprint

chrome_options = Options()
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

username = "unamehere"
password = 'pwordhere'

def get_full_message_text(url):
    driver.get(url)
    message = driver.find_element_by_class_name('dialog-text')
    return message.text

def parse_mal_date(date_string):
    if("seconds" in date_string):
        return datetime.datetime.now() - datetime.timedelta(seconds=int(date_string.split()[0]))
    if("minutes" in date_string):
        return datetime.datetime.now() - datetime.timedelta(minutes=int(date_string.split()[0]))
    if("hours" in date_string):
        return datetime.datetime.now() - datetime.timedelta(hours=int(date_string.split()[0]))
    if("Yesterday" in date_string):
        dt = datetime.datetime.today() - datetime.timedelta(days=1)
        tm = datetime.datetime.strptime(date_string[11:], '%I:%M %p').time()
        return  dt.combine(dt,tm)
    else:
        try:
            return datetime.datetime.strptime(date_string, '%b %d, %I:%M %p').replace(year=datetime.datetime.today().year)
        except:
            try:
                return datetime.datetime.strptime(date_string, '%b %d, %Y %I:%M %p')
            except:
                return datetime.datetime.now()

def get_messages(url, is_received, n = 20):

    driver.get(url)
    
    try:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "message"))
        )
    except:
        return []
    messages_elements = driver.find_elements_by_class_name('message')


    messages = []
    for message in messages_elements:
        subject_line = message.find_element_by_class_name('mym_subject')
        user = message.find_element_by_class_name('mym_user').text
        date = message.find_element_by_class_name('mym_date').text
        subject = subject_line.find_element_by_class_name('subject-link')
        subject_text = subject.text
        url = subject.get_attribute("href")
        text_preview = subject.find_element_by_class_name('text').text
        unread = "unread" in message.get_attribute("class")
        subject_text = subject_text[:-len(text_preview)-3]
        truncated = text_preview.endswith("...")
        full_text = text_preview

        messages.append({"user":user,
                        "subject":subject_text,
                        "preview":text_preview,
                        "full_text":full_text,
                        "unread":unread,
                        "url":url,
                        "date":date,
                        "is_received":is_received})
        if(len(messages) > n):
            break
    for message in messages:
        if(message["preview"].endswith("...")):
            message["full_text"] = get_full_message_text(message["url"])
        message["date"] = parse_mal_date(message["date"])

    return messages


def login():

    driver.get('https://myanimelist.net/login.php')

    if("Login" in driver.title):

        id_box = driver.find_element_by_name('user_name')

        id_box.send_keys(username)

        password_box = driver.find_element_by_name('password')

        password_box.send_keys(password)

        login_button = driver.find_element_by_class_name("btn-form-submit")

        driver.execute_script("arguments[0].click();", login_button)
        #login_button.click()

def get_n_received_messages(n):
    n_messages = []
    for i in range(math.ceil(n/20)):
        messages = get_messages("https://myanimelist.net/mymessages.php?show="+str(20*i), True)
        if(messages == []):
            break
        n_messages += messages
    return n_messages[:n]

def get_n_sent_messages(n):
    n_messages = []
    for i in range(math.ceil(n/20)):
        messages = get_messages("https://myanimelist.net/mymessages.php?go=sent&show="+str(20*i), False)
        if(messages == []):
            break
        n_messages += messages
    return n_messages[:n]

def get_n_received_from_user(n, user, start_page = 0):
    
    count = 0
    pages = start_page
    user_messages = []
    while(count < n):
        messages = get_messages("https://myanimelist.net/mymessages.php?show="+str(20*pages), True)
        if (messages == []):
            break
        for message in messages:
            if(message["user"] == user):
                user_messages.append(message)
                count += 1
        pages += 1

    return user_messages[:n]

def get_n_sent_to_user(n, user, start_page = 0):
    
    count = 0
    pages = start_page
    user_messages = []
    while(count < n):
        messages = get_messages("https://myanimelist.net/mymessages.php?go=sent&show="+str(20*pages), False)
        if (messages == []):
            break
        for message in messages:
            if(message["user"] == user):
                user_messages.append(message)
                count += 1
        pages += 1

    return user_messages[:n]

def get_n_combined_user(n, user):
    sent = get_n_sent_to_user(n, user)
    received = get_n_received_from_user(n, user)

    combined = sent+received

    sorted_combined = sorted(combined, key=lambda k: k['date'], reverse=True)

    return sorted_combined[:n]

def send_message(message, user):
    driver.get('https://myanimelist.net/mymessages.php?go=send&toname='+user)
    driver.find_element_by_name("subject").send_keys("Messenger for MAL message")
    driver.find_element_by_name("message").send_keys(message)
    buttons = driver.find_elements_by_class_name("btn-recaptcha-submit")
    for button in buttons:
        if("Send Message" in button.get_attribute("value")):
            button.click()

def get_new_sent_since(date):
    all_messages = []
    new_messages = True
    pages = 0
    while(new_messages):
        messages = get_messages("https://myanimelist.net/mymessages.php?go=sent&show="+str(20*pages), False)
        if(messages == []):
            break
        all_messages += messages
        for message in messages:
            if(message["date"] < date):
                new_messages = False
        pages +=1

    filtered_all = [message for message in all_messages if message["date"] > date]

    sorted_all = sorted(filtered_all, key=lambda k: k['date'], reverse=True)

    return sorted_all



def get_new_received_since(date):
    all_messages = []
    new_messages = True
    pages = 0
    while(new_messages):
        messages = get_messages("https://myanimelist.net/mymessages.php?&show="+str(20*pages), True)
        if(messages == []):
            break
        all_messages += messages
        for message in messages:
            if(message["date"] < date):
                new_Messages = False
        pages +=1
     
    filtered_all = [message for message in all_messages if message["date"] > date]

    sorted_all = sorted(filtered_all, key=lambda k: k['date'], reverse=True)

    return sorted_all


def get_new_since(date):

    sent = get_new_sent_since(date)
    received = get_new_received_since(date)

    all_messages = sent+received

    filtered_all = [message for message in all_messages if message["date"] > date]

    sorted_all = sorted(filtered_all, key=lambda k: k['date'], reverse=True)

    return sorted_all




login()
time.sleep(1)
one_month = datetime.datetime.now() - datetime.timedelta(days=30)
messages = get_new_since(one_month)
#driver.close()

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(messages)



