from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import enum
import time
import re
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
import requests
import platform


#from apis import offnexmo
from apis import config
from apis import freesmsverifications
from apis import cloudsms
#from apis import nexmo
from util import kolor
from util.kolor import sprint
import proxifier
from apis.msg import MsgState



PLATFORM = platform.platform()
COUNTRIES = (
    "US", "GB", "CN"
)

WARNING_PREFIX_STYLE = kolor.StyleRule(bold=True, foreground="yellow")
WARNING_STYLE = kolor.StyleRule(
    prefix=kolor.Symbol.warning, prefix_style=WARNING_PREFIX_STYLE)

ERROR_PREFIX_STYLE = kolor.StyleRule(bold=True, foreground="red")
ERROR_STYLE = kolor.StyleRule(
    prefix=kolor.Symbol.error, prefix_style=ERROR_PREFIX_STYLE)

SUCCESS_PREFIX_STYLE = kolor.StyleRule(bold=True, foreground="green")
SUCCESS_STYLE = kolor.StyleRule(
    prefix=kolor.Symbol.check, prefix_style=SUCCESS_PREFIX_STYLE)

NOTE_PREFIX_STYLE = kolor.StyleRule(bold=True, foreground="blue")
NOTE_STYLE = kolor.StyleRule(
    prefix=kolor.Symbol.bullet, prefix_style=NOTE_PREFIX_STYLE)


class DriverError(Exception):
    EXEC_NOT_SET = "Path to Chrome Executable not set. Please set in config.py"

    def __init__(self, what):
        super().__init__(what)


class State(enum.Enum):
    LOADING = 0
    ENTERING_DETAILS = 1
    SUBMITTING = 2

# load_state = State.ENTERING_DETAILS
# load_state = State.LOADING


def init_driver():
    chrome = None
    sprint(NOTE_STYLE, "Initializing Chrome Driver with: --incognito, --start-maximized, --proxy-server")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2})

    if ("linux" in PLATFORM) or ("Linux" in PLATFORM) or ("Darwin" in PLATFORM) or ("darwin" in PLATFORM):
    #    options.add_argument("--kiosk")
        pass
    else:
        #options.add_argument("--start-maximized")
        pass
    #options.add_argument(
    #       '--proxy-server=%s' % proxifier.get_proxy())
    
    if config.path_to_chrome_driver:
        # ("/etc/alternatives/google-chrome")
        chrome = webdriver.Chrome(
        config.path_to_chrome_driver, chrome_options=options)
    else:
        chrome = webdriver.Chrome(chrome_options=options)
        
        return chrome
        #raise DriverError(DriverError.EXEC_NOT_SET)


def _valid_email(email: str):
    if re.search(r"[a-z0-9]+@[a-z0-9]+\.[a-z0-9]+", email, re.I):
        return True
    else:
        return False


def _valid_dob(dob: str):
    # dob in form mm/dd/yy
    match = re.match(r"^([0-9]{2})([0-9]{2})([0-9]{4})$", dob)
    if match:
        if int(match[1]) <= 12 and int(match[2]) <= 31 and int(match[3]) <= 2000:
            return True
    return False


def _valid_pw(password: str):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    return True


def load_page(driver):
    sprint(NOTE_STYLE, "Requesting Page...")
    # https://www.nike.com/cn/zh_cn/s/register
    sprint(NOTE_STYLE, "Connecting to:", " https://www.nike.com/launch")
    driver.get("https://www.nike.com/launch")
    sprint(NOTE_STYLE, "Waiting for Full Page load")
    driver.implicitly_wait(10)

"""
def register_cn(email, password, fname, lname, dob):
    # ensuring validity of parameters
    country = "CN"
    assert _valid_email(email), ERROR_STYLE.style(
        "Please enter a valid email; %s" % email)
    assert _valid_pw(
        password), ERROR_STYLE.style("Invalid password, Minimum of 8 characters 1 uppercase letter 1 lowercase letter 1 number ; %s" % password)

    NOTE_STYLE.print( "Details to be filled with: \n\tEmail: %s\n\tPassword: %s\n\tFirstName: %s\n\tLastName: %s\n\tDateOfBirth: %s\n\tCountry: %s" % (
        email, password, fname, lname, dob, country))

    print(" ")
    NOTE_STYLE.print("Launching Chrome...")
    driver = init_driver()
    SUCCESS_STYLE.print("Chrome Launched")
    #test = webdriver.Chrome()
    print("\n")
    NOTE_STYLE.print("Loading Page (trial 1/3)")
    load_page(driver)
    # WebDriverWait(driver, config.page_load_timeout).until(
    # EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label=\"Join or Log In\"]")))
    time.sleep(1)
    NOTE_STYLE.print("Checking if Page loaded")

    try:
        driver.find_element_by_css_selector(
            "#root > div > div > div > div > header > div > section > ul > li > button").click()
    except exceptions.NoSuchElementException as E:
        ERROR_STYLE.print("Page not loaded, Network Error")
        try:
            print("\n")
            WARNING_STYLE.print("Retrying Page Load (trial 2/3)")
            load_page(driver)
            
            driver.find_element_by_css_selector(
                ".join-log-in").click()
        except exceptions.NoSuchElementException as E:
            try:
                print("\n")
                WARNING_STYLE.print("Retrying Page Load (trial 3/3)")
                load_page(driver)
                driver.find_element_by_css_selector(
                    ".join-log-in").click()
            except exceptions.NoSuchElementException as E:
                driver.close()
                print("\n")
                ERROR_STYLE.print("Please check your internet connection\n")
                raise E

    SUCCESS_STYLE.print("Page Loaded, Signin/Signup button clicked")

    modal_box = None
    try:
        print("\n\n")
        NOTE_STYLE.print("Awaiting Signin Modal Box...")
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-container")))
        SUCCESS_STYLE.print("Signin/Signup Modal Box loaded")
        time.sleep(0.5)
        modal_box = driver.find_element_by_css_selector(".modal-container")
    except exceptions.NoSuchElementException as E:
        ERROR_STYLE.print("Signin/Signup Modal Box not loaded, Unknown error")
        raise E
    except exceptions.TimeoutException as E:
        ERROR_STYLE.print("Signin/Signup Modal Box not Responding, Unknown error")
        raise E

    print("\n\n")
    sprint(NOTE_STYLE, "Finding Signup button")
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".current-member-signin a")))
        time.sleep(0.5)
        modal_box.find_element_by_css_selector(
            ".current-member-signin a").click()
        sprint(SUCCESS_STYLE, "Signup Modal loaded")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Signup button")
        raise E
    except exceptions.TimeoutException as E:
        sprint(ERROR_STYLE, "Error locating Signup button")
        raise E

    print("\n\n")
    sprint(NOTE_STYLE, "Awaiting Registration Form Modal...")
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=\"email\"]")))
        #print("Entering Phone Number for Verification")
        sprint(SUCCESS_STYLE, "Registration Form Modal loaded")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Registration Form Modal")
        raise E
    except exceptions.TimeoutException as E:
        sprint(
            ERROR_STYLE, "Registration Form Modal not responding, Unknown Error Occurred")
        raise E

    sprint(SUCCESS_STYLE, "Registration Form Modal loaded")

    print("\n\n")
    sprint(NOTE_STYLE, "Selecting Country...")
    a = ActionChains(driver)
    a.move_by_offset(1, 1)
    a.perform()
    driver.find_element_by_css_selector("select[name=\"country\"]").click()
    time.sleep(0.25)
    driver.find_element_by_css_selector(
        "option[value=\"%s\"]" % country).click()
    sprint(SUCCESS_STYLE, "Country Selected: %s" % country)

    print("\n\n")
    sprint(NOTE_STYLE, "Awaiting Mobile Verification Modal...")

    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nike-unite-verifyMobileNumber")))

    except exceptions.NoSuchElementException as E:
        sprint(
            ERROR_STYLE, "Error occurred during Phone Number Modal search, Probably Network")
        raise E

    except exceptions.TimeoutException as E:
        sprint(
            ERROR_STYLE, "Phone Number Modal Not Responding, unknown Website error occured")
        raise E

    sprint(SUCCESS_STYLE, "Verification Modal Loaded")

    #  getting number phase
    print("\n\n")
    sprint(NOTE_STYLE, "Requesting Phone Number from GETSMSCODE...")
    phone_i_l = None
    try:
        phone_i_l, error = getsmscode.get_number()
        if not phone_i_l:
            sprint(ERROR_STYLE, "GETSMSCODE not responding:\n\t\t "+error)
            raise Exception("GETSMSCODE is not allocating Phone Number")
    except requests.ConnectionError:
        sprint(WARNING_STYLE, "Internet Connection Error. Retrying... ")
        try:
            phone_i_l, error = getsmscode.get_number()
        except requests.ConnectionError:
            sprint(WARNING_STYLE, "Internet Connection Error. Retrying... (trial 2)")
            try:
                phone_i_l, error = getsmscode.get_number()
            except requests.ConnectionError:
                sprint(WARNING_STYLE,
                       "Internet Connection Error. Retrying... (trial 3)")
                try:
                    phone_i_l, error = getsmscode.get_number()
                except requests.ConnectionError:
                    sprint(ERROR_STYLE, "Internet Connection Error")
                    raise Exception(
                        "Internet Connection Error. Please ensure you have internet access")

    sprint(SUCCESS_STYLE, "Gotten Phone Number from GETSMSCODE: +%s (%s)" % phone_i_l)

    # enter mobile number
    try:
        print("\n\n")
        sprint(NOTE_STYLE, "Entering Phone Number...")
        driver.find_element_by_css_selector(
            "input[data-componentname=\"phoneNumber\"]").send_keys(phone_i_l[1])
        # send verification code

    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error occurred during Locating Phone Number input box")
        raise E

    sprint(SUCCESS_STYLE, "Phone Number Entered")

    try:
        sprint(NOTE_STYLE, "Submitting Phone Number...")
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        time.sleep(0.24)
        driver.find_element_by_css_selector(".sendCodeButton").click()
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error Occurred Locating Phone Number button")
        raise E
    sprint(SUCCESS_STYLE, "Phone Number Submitted")

    # get sms from respective api
    trial = 1
    ver_code = None
    _rep_body = None

    time.sleep(4)

    print("\n\n")
    sprint(NOTE_STYLE, "Checking: %s for Verification Code..." % phone_i_l[0])
    while (not ver_code) and (trial <= config.read_message_trials):
        sprint(NOTE_STYLE, "Attempt %d of %d to check GETSMSCODE for Verification Code" %
               (trial, config.read_message_trials))
        try:
            ver_code, _rep_body = getsmscode.read_ver_code(phone_i_l[0])
        except requests.ConnectionError:
            sprint(ERROR_STYLE, "Unable to Connect to Internet, Retrying...")
        print("\t\t", _rep_body)
        time.sleep(config.read_message_delay)
        trial += 1

    if not ver_code:
        print("\n\n")
        sprint(ERROR_STYLE, "Unable to Get SMS\n\n")
        raise Exception("Please Try Resorting issues with GETSMSCODE")

    sprint(SUCCESS_STYLE, "Verification Code gotten")

    a = ActionChains(driver)
    a.move_by_offset(1, 1)
    a.perform()


    time.sleep(0.24)
    sprint(NOTE_STYLE, "Entering Verification code...")
    driver.find_element_by_css_selector(
        ".verifyCode input").send_keys(ver_code)
    
    a = ActionChains(driver)
    a.move_by_offset(1, 1)
    a.perform()
    a = ActionChains(driver)
    a.move_by_offset(1, 0)
    a.perform()
    
    time.sleep(0.5)
    sprint(NOTE_STYLE, "Submitting verification code...")
    
    a = ActionChains(driver)
    a.move_by_offset(1, 1)
    a.perform()
    
    driver.find_element_by_css_selector(".mobileJoinContinue input").click()

    try:
        print("\n\n")
        sprint(NOTE_STYLE, "Awaiting Registration Details Box...")
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-componentname=\"lastName\"]")))
        time.sleep(0.5)
        #print("Entering Phone Number for Verification")
        # print("")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Registration Form Modal")
        raise E
    except exceptions.TimeoutException as E:
        sprint(ERROR_STYLE, "Error locating Registration Form Modal")
        raise E

    sprint(SUCCESS_STYLE, "Registration Form Modal loaded")

    print("\n\n")
    sprint(NOTE_STYLE, "Filling registration details...")

    try:
        time.sleep(0.8)
        a = ActionChains(driver)

        elem = driver.find_element_by_css_selector(
            "input[type=\"password\"]")
        a.move_to_element(elem)
        a.perform()
        for l in password:
            elem.send_keys(l)
            time.sleep(0.2)
        
        a.move_by_offset(1, 1)
        a.perform()
        time.sleep(0.24
        )
        
        elem = driver.find_element_by_css_selector(
            "input[data-componentname=\"lastName\"]")
        elem.send_keys(fname[:-random.randint(1,3)])
        a = ActionChains(driver)
        a.move_to_element(elem)
        a.perform()
        time.sleep(1)

        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        time.sleep(0.24)

        driver.find_element_by_css_selector(
            "input[data-componentname=\"firstName\"]").send_keys(lname+"las")
        
        time.sleep(0.5)
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        time.sleep(0.24)

        driver.find_element_by_css_selector(
            "input[data-componentname=\"lastName\"]").clear()
        time.sleep(0.3)
        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        time.sleep(0.24)
        
        for l in fname:
            driver.find_element_by_css_selector(
                "input[data-componentname=\"lastName\"]").send_keys(l)
            time.sleep(0.2)

        
        time.sleep(0.8)
        
        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        time.sleep(0.24)


        driver.find_element_by_css_selector(
            "input[data-componentname=\"firstName\"]").clear()
        time.sleep(0.6)
        elem = driver.find_element_by_css_selector(
                "input[data-componentname=\"firstName\"]")
        for l in lname:
            elem.send_keys(l)
            time.sleep(0.5)
        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        time.sleep(0.24)
        a = ActionChains(driver)
        a.move_by_offset(1, 0)
        a.perform()
        time.sleep(0.24)
        a = ActionChains(driver)
        a.move_by_offset(0, 2)
        a.move_by_offset(0.1, 2.5)
        a.move_by_offset(4.5, 20)
        a.move_by_offset(3.8, 22)
        a.move_by_offset(1.2, 2.6)
        a.move_by_offset(10, 40)
        a.perform()
        time.sleep(1)
        
        c = driver.find_element_by_css_selector(
        "ul[data-componentname=\"shoppingGender\"]")
        a = ActionChains(driver)
        a.move_to_element(c)
        a.perform()
        time.sleep(1)
        avail_genders = driver.find_element_by_css_selector(
            "ul[data-componentname=\"shoppingGender\"]").find_elements_by_css_selector("li")
        random.choice(avail_genders).click()

    except exceptions.NoSuchElementException as E:
        sprint(
            ERROR_STYLE, "Error locating Input Boxes for Password,LastName and FirstName")
        raise E

    sprint(SUCCESS_STYLE, "Registration details filled")

    sprint(NOTE_STYLE, "Submitting Details")

    time.sleep(1)
    
    a = ActionChains(driver)
    a.move_by_offset(2, 3)
    a.perform()
    time.sleep(0.1)
    
    a = ActionChains(driver)
    a.move_by_offset(23, 1)
    a.perform()
    time.sleep(0.1)

    a = ActionChains(driver)
    a.move_by_offset(1, 0)
    a.perform()


    time.sleep(0.4)
    subm_b = driver.find_element_by_css_selector(
        ".nike-unite-submit-button input")
    a = ActionChains(driver)
    a.move_to_element_with_offset(subm_b,10,20)
    a.move_to_element(subm_b)
    a.perform()
    time.sleep(5)
    subm_b.click()




    sprint(SUCCESS_STYLE, "Submitted Registration details")

    try:
        print("\n\n")
        sprint(NOTE_STYLE, "Awaiting Email Verification Modal...")
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-componentname=\"emailAddress\"]")))
        #print("Entering Phone Number for Verification")
        # print("")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Email Verification Modal")
        raise E
    except exceptions.TimeoutException as E:
        sprint(ERROR_STYLE, "Error locating Email Verification Modal")
        raise E

    sprint(SUCCESS_STYLE, "Email Verification Modal Loaded")

    sprint(NOTE_STYLE, "Entering/Verifying email...")
    try:
        ActionChains(driver).move_by_offset(0, 1)
        time.sleep(0.2)
        ActionChains(driver).move_by_offset(1, 0)
        time.sleep(0.3)
        driver.find_element_by_css_selector(
            "input[data-componentname=\"emailAddress\"]").send_keys(email)
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Email Verification Modal")
        raise E

    ActionChains(driver).move_by_offset(1, 0)
    time.sleep(0.3)
    sprint(NOTE_STYLE, "Verifying Email...")
    driver.find_element_by_css_selector(".captureEmailSubmit input").click()
    sprint(NOTE_STYLE, "Submitting Email...")

    try:
        sprint(NOTE_STYLE, "Awaiting DOB Verification Box...")
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-componentname=\"dateOfBirthOptional\"]")))
        #print("Entering Phone Number for Verification")
        # print("")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating DOB Verification input box")
        raise E
    except exceptions.TimeoutException as E:
        sprint(ERROR_STYLE, "Error DOB Verification input box not responding")
        raise E

    try:
        sprint(NOTE_STYLE, "Verifying DOB...")
        sprint(NOTE_STYLE, "Entering DOB...")
        ActionChains(driver).move_by_offset(0, 1)
        time.sleep(0.2)
        ActionChains(driver).move_by_offset(1, 0)
        time.sleep(0.3)
        driver.find_element_by_css_selector(
            "input[data-componentname=\"dateOfBirthOptional\"]").send_keys(dob)
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating DOB Verification input box")
        raise E

    try:
        sprint(NOTE_STYLE, "Submitting DOB...")
        ActionChains(driver).move_by_offset(1, 0)
        time.sleep(0.3)

        driver.find_element_by_css_selector(
            ".mobileJoinDobEmailSubmit input").click()
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating DOB Verification input box")
        raise E

    sprint(SUCCESS_STYLE, "DOB Submitted")

    print("\n\n")
    try:
        sprint(NOTE_STYLE, "Awaiting Account Confirmation...")
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-qa=\"user-name\"]")))
        time.sleep(1)
        #print("Entering Phone Number for Verification")
        # print("")
    except exceptions.NoSuchElementException as E:
        sprint(NOTE_STYLE, "Error Verifying Account Confirmation")
        raise E
    except exceptions.TimeoutException as E:
        sprint(NOTE_STYLE, "Error Account Verification Modal not Responding")
        raise E

    sprint(NOTE_STYLE, "Logging Account Details...")
    sprint(SUCCESS_STYLE, "Account Registered, Verified and Logged")

    sprint(NOTE_STYLE, ("Blacklisting Phone number: +%s" %
                        phone_i_l[0]) + " on GETSMSCODE...")

    try:
        getsmscode.blacklist(phone_i_l[0])
    except:
        pass
    sprint(SUCCESS_STYLE, "Number Blacklisted")

    # done
    if __name__ == "__main__":
        #time.sleep(20000)
        pass
    driver.close()

"""


















# us,uk




def register_us(email, password, fname, lname, dob):
    country = "US"
    # ensuring validity of parameters
    assert _valid_email(email), ERROR_STYLE.style(
        "Please enter a valid email; %s" % email)
    assert _valid_pw(
        password), ERROR_STYLE.style("Invalid password, Minimum of 8 characters 1 uppercase letter 1 lowercase letter 1 number ; %s" % password)

    sprint(NOTE_STYLE, "Details to be filled with: \n\tEmail: %s\n\tPassword: %s\n\tFirstName: %s\n\tLastName: %s\n\tDateOfBirth: %s\n\tCountry: %s" % (
        email, password, fname, lname, dob, country))

    print(" ")
    sprint(NOTE_STYLE, "Launching Chrome...")
    driver = init_driver()
    sprint(SUCCESS_STYLE, "Chrome Launched")
    #test = webdriver.Chrome()
    print("\n")
    sprint(NOTE_STYLE, "Loading Page (trial 1/3)")
    load_page(driver)
    time.sleep(1)
    # WebDriverWait(driver, config.page_load_timeout).until(
    # EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label=\"Join or Log In\"]")))
    sprint(NOTE_STYLE, "Checking if Page loaded")

    try:
        driver.find_element_by_css_selector(
            "#root > div > div > div > div > header > div > section > ul > li > button").click()
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Page not loaded, Network Error")
        try:
            print("\n")
            sprint(WARNING_STYLE, "Retrying Page Load (trial 2/3)")
            load_page(driver)
            driver.find_element_by_css_selector(
                "#root > div > div > div > div > header > div > section > ul > li > button").click()
        except exceptions.NoSuchElementException as E:
            try:
                print("\n")
                sprint(WARNING_STYLE, "Retrying Page Load (trial 3/3)")
                load_page(driver)
                driver.find_element_by_css_selector(
                    "#root > div > div > div > div > header > div > section > ul > li > button").click()
            except exceptions.NoSuchElementException as E:
                driver.close()
                print("\n")
                sprint(ERROR_STYLE, "Please check your internet connection\n")
                raise E

    sprint(SUCCESS_STYLE, "Page Loaded, Signin/Signup button clicked")

    modal_box = None
    try:
        print("\n\n")
        sprint(NOTE_STYLE, "Awaiting Signin Modal Box...")
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-container")))
        sprint(SUCCESS_STYLE, "Signin/Signup Modal Box loaded")
        time.sleep(0.5)
        modal_box = driver.find_element_by_css_selector(".modal-container")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Signin/Signup Modal Box not loaded, Unknown error")
        raise E
    except exceptions.TimeoutException as E:
        sprint(ERROR_STYLE, "Signin/Signup Modal Box not Responding, Unknown error")
        raise E

    print("\n\n")
    sprint(NOTE_STYLE, "Finding Signup button")
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#nike-unite-loginForm > div:nth-child(9) > a")))
        time.sleep(0.5)
        modal_box.find_element_by_css_selector(
            "#nike-unite-loginForm > div:nth-child(9) > a").click()
        sprint(SUCCESS_STYLE, "Signup Modal loaded")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Signup button")
        raise E
    except exceptions.TimeoutException as E:
        sprint(ERROR_STYLE, "Error locating Signup button")
        raise E

    print("\n\n")
    sprint(NOTE_STYLE, "Awaiting Registration Form Modal...")
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=\"email\"]")))
        #print("Entering Phone Number for Verification")
        sprint(SUCCESS_STYLE, "Registration Form Modal loaded")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Registration Form Modal")
        raise E
    except exceptions.TimeoutException as E:
        sprint(
            ERROR_STYLE, "Registration Form Modal not responding, Unknown Error Occurred")
        raise E

    sprint(SUCCESS_STYLE, "Registration Form Modal loaded")

    print("\n\n")
    avail_genders = None
    try:
        sprint(NOTE_STYLE, "Filling Details...")
        ActionChains(driver).move_by_offset(1, 1)
        driver.find_element_by_css_selector("select[name=\"country\"]").click()
        time.sleep(0.3)
        driver.find_element_by_css_selector(
            "option[value=\"%s\"]" % country).click()
        
        for l in email:
            time.sleep(0.12)
            driver.find_element_by_css_selector(
                "input[type=\"email\"]").send_keys(l)

        driver.find_element_by_css_selector("input[type=\"email\"]").clear()
        
        for l in email:
            time.sleep(0.1)
            driver.find_element_by_css_selector(
                "input[type=\"email\"]").send_keys(l)
        
        for l in password:
            time.sleep(0.12)
            driver.find_element_by_css_selector(
                "input[type=\"password\"]").send_keys(l)
        
        
        time.sleep(0.12)
        driver.find_element_by_css_selector("input[type=\"date\"]").send_keys(dob)
        time.sleep(0.12)

        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        a = ActionChains(driver)
        a.move_by_offset(1, 0)
        a.perform()
        time.sleep(0.2)
        a = ActionChains(driver)
        a.move_to_element(driver.find_element_by_css_selector(
                "input[data-componentname=\"lastName\"]"))
        a.perform()
        for l in fname:
            time.sleep(0.15)
            driver.find_element_by_css_selector(
                "input[data-componentname=\"lastName\"]").send_keys(l)
        
        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        a = ActionChains(driver)
        a.move_by_offset(1, 0)
        a.perform()
        time.sleep(0.2)
        a = ActionChains(driver)
        a.move_to_element(driver.find_element_by_css_selector(
                "input[data-componentname=\"firstName\"]"))
        a.perform()

        for l in lname:
            time.sleep(0.11)
            driver.find_element_by_css_selector(
                "input[data-componentname=\"firstName\"]").send_keys(l)
        time.sleep(0.4)


        driver.find_element_by_css_selector("select[name=\"country\"]").click()
        driver.find_element_by_css_selector(
            "option[value=\"%s\"]" % country).click()
        ActionChains(driver).move_by_offset(1, 1)
        time.sleep(0.2)
        ActionChains(driver).move_by_offset(1, 1)
        time.sleep(1)
        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        a = ActionChains(driver)
        a.move_by_offset(1, 0)
        a.perform()
        time.sleep(0.2)
        a = ActionChains(driver)
        a.move_to_element(driver.find_element_by_css_selector(
        "ul[data-componentname=\"gender\"]").find_element_by_css_selector("li"))
        a.perform()

        avail_genders = driver.find_element_by_css_selector(
        "ul[data-componentname=\"gender\"]").find_elements_by_css_selector("li")
    
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Form Modal Irresponsive, Nike Error")
        raise E

    gender = random.choice(avail_genders)
    time.sleep(0.1)
    a = ActionChains(driver)
    a.move_to_element_with_offset(gender,1,5)
    a.move_to_element(gender)
    a.perform()
    time.sleep(0.1)
    gender.click()
    #avail_genders.click()
    ActionChains(driver).move_by_offset(1, 0)
    time.sleep(0.3)
    ActionChains(driver).move_by_offset(1, 1)
    time.sleep(0.24)
    ActionChains(driver).move_by_offset(0, 1)
    time.sleep(0.24)
    time.sleep(1)

    sprint(SUCCESS_STYLE, "All details filled, Submitting...")
    try:
        driver.find_element_by_css_selector(".nike-unite-submit-button").click()
        # mark email as used
        print("All Data Filled")
    except exceptions.NoSuchElementException as E:
        print("Submit Button Irresponsive")
        raise E



    sprint(NOTE_STYLE,"Awaiting Mobile Verification Modal...")

    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#nike-unite-mobile-verification-code-view")))
        time.sleep(0.5)
        
        print("Entering Phone Number for Verification")
    except exceptions.NoSuchElementException as E:
        print("Error occurred during Number Box search, Probably Network")
        raise E
    except exceptions.TimeoutException as E:
        print("couldn't locate Phone number modal, unknown error occured")
        raise E



    """
    # get number
    phone_i_l = None
    if country == "GB":
        nexmo.get_uk()
    else:
        # country us
        nexmo.get_us()
    """
    print("getting number...")
    error = None
    
    phone_number = cloudsms.get_number()

    #print("pvacodes: %s" % phone_number)
    print(error)
    if (phone_number == None):
        raise Exception("PVACODES gave an error response: \n\t\t\t%s" % error)

    #print("repeate ",error)
    
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=\"tel\"]")))
        time.sleep(0.5)
        for k in phone_number:
            time.sleep(0.2)
            driver.find_element_by_css_selector(
                "input[type=\"tel\"]").send_keys(k)
        ActionChains(driver).move_by_offset(0, 1)
        time.sleep(0.24)
        a = ActionChains(driver)
        a.move_to_element(driver.find_element_by_css_selector(
                "input[type=\"tel\"]"))
        a.perform()
        time.sleep(0.2)

        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        
        time.sleep(0.24)
        
        print("Submitting number")
        time.sleep(0.6)
        send_b = driver.find_element_by_css_selector(".sendCodeButton")
        
        a = ActionChains(driver)
        a.move_to_element_with_offset(send_b,1,5)
        a.perform()
        time.sleep(0.1)
        a = ActionChains(driver)
        a.move_by_offset(1,5)
        a.perform()
        time.sleep(0.1)
        a = ActionChains(driver)
        a.move_to_element(send_b)
        a.perform()
        
        time.sleep(1)
        
        send_b.click()
    
    except exceptions.NoSuchElementException as E:
        print("Error occurred during number verification")
        raise E
    except exceptions.TimeoutException as E:
        print("couldn't locate Phone number verification modal, unknown error occured")
        raise E
    
    
    
    vcode = None
    count = 0


    vcode = cloudsms.get_sms(phone_number)




    time.sleep(0.24)
    sprint(NOTE_STYLE, "Entering Verification code...")
    driver.find_element_by_css_selector(
        ".verifyCode input").send_keys(vcode)
    
    a = ActionChains(driver)
    a.move_by_offset(1, 1)
    a.perform()
    a = ActionChains(driver)
    a.move_by_offset(1, 0)
    a.perform()
    
    time.sleep(0.5)
    sprint(NOTE_STYLE, "Submitting verification code...")
    
    a = ActionChains(driver)
    a.move_by_offset(1, 1)
    a.perform()
    
    driver.find_element_by_css_selector("input[value=\"CONTINUE\"]").click()

    print("submitted")
    print("waiting to verify if account successfully generated")
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-qa=\"user-name\"]")))
        print("Verified")
        time.sleep(1)
    except exceptions.NoSuchElementException as E:
        print("Couldn't verify if account was created (Modal)")
        raise E
    except exceptions.TimeoutException as E:
        print("timeout for account new account profile")
        raise E

    if __name__ == "__main__":
        #time.sleep(11000)
        pass
    #try:
    #    driver.find_element_by_css_selector(".mobileNumber-div")
    #except exceptions.NoSuchElementException as E:
    #    print("Error occurred during number verification")
    #    raise E
    driver.close()
    """
    print("Submitting")
    time.sleep(10000)
    # driver.close()
    """

# print(_valid_dob("12991990"))
# print(_valid_pw("apedf5A434"))
# print(_valid_email("ryan@p"))
























# us,uk


def register_gb(email, password, fname, lname, dob):
    country = "GB"
    # ensuring validity of parameters
    assert _valid_email(email), ERROR_STYLE.style(
        "Please enter a valid email; %s" % email)
    assert _valid_pw(
        password), ERROR_STYLE.style("Invalid password, Minimum of 8 characters 1 uppercase letter 1 lowercase letter 1 number ; %s" % password)

    sprint(NOTE_STYLE, "Details to be filled with: \n\tEmail: %s\n\tPassword: %s\n\tFirstName: %s\n\tLastName: %s\n\tDateOfBirth: %s\n\tCountry: %s" % (
        email, password, fname, lname, dob, country))

    print(" ")
    sprint(NOTE_STYLE, "Launching Chrome...")
    driver = init_driver()
    sprint(SUCCESS_STYLE, "Chrome Launched")
    #test = webdriver.Chrome()
    print("\n")
    sprint(NOTE_STYLE, "Loading Page (trial 1/3)")
    load_page(driver)
    time.sleep(1)
    # WebDriverWait(driver, config.page_load_timeout).until(
    # EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label=\"Join or Log In\"]")))
    sprint(NOTE_STYLE, "Checking if Page loaded")

    try:
        driver.find_element_by_css_selector(
            "#root > div > div > div > div > header > div > section > ul > li > button").click()
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Page not loaded, Network Error")
        try:
            print("\n")
            sprint(WARNING_STYLE, "Retrying Page Load (trial 2/3)")
            load_page(driver)
            driver.find_element_by_css_selector(
                "#root > div > div > div > div > header > div > section > ul > li > button").click()
        except exceptions.NoSuchElementException as E:
            try:
                print("\n")
                sprint(WARNING_STYLE, "Retrying Page Load (trial 3/3)")
                load_page(driver)
                driver.find_element_by_css_selector(
                    "#root > div > div > div > div > header > div > section > ul > li > button").click()
            except exceptions.NoSuchElementException as E:
                driver.close()
                print("\n")
                sprint(ERROR_STYLE, "Please check your internet connection\n")
                raise E

    sprint(SUCCESS_STYLE, "Page Loaded, Signin/Signup button clicked")

    modal_box = None
    try:
        print("\n\n")
        sprint(NOTE_STYLE, "Awaiting Signin Modal Box...")
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-container")))
        sprint(SUCCESS_STYLE, "Signin/Signup Modal Box loaded")
        time.sleep(0.5)
        modal_box = driver.find_element_by_css_selector(".modal-container")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Signin/Signup Modal Box not loaded, Unknown error")
        raise E
    except exceptions.TimeoutException as E:
        sprint(ERROR_STYLE, "Signin/Signup Modal Box not Responding, Unknown error")
        raise E

    print("\n\n")
    sprint(NOTE_STYLE, "Finding Signup button")
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#nike-unite-loginForm > div:nth-child(9) > a")))
        time.sleep(0.5)
        modal_box.find_element_by_css_selector(
            "#nike-unite-loginForm > div:nth-child(9) > a").click()
        sprint(SUCCESS_STYLE, "Signup Modal loaded")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Signup button")
        raise E
    except exceptions.TimeoutException as E:
        sprint(ERROR_STYLE, "Error locating Signup button")
        raise E

    print("\n\n")
    sprint(NOTE_STYLE, "Awaiting Registration Form Modal...")
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=\"email\"]")))
        #print("Entering Phone Number for Verification")
        sprint(SUCCESS_STYLE, "Registration Form Modal loaded")
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Error locating Registration Form Modal")
        raise E
    except exceptions.TimeoutException as E:
        sprint(
            ERROR_STYLE, "Registration Form Modal not responding, Unknown Error Occurred")
        raise E

    sprint(SUCCESS_STYLE, "Registration Form Modal loaded")

    print("\n\n")
    avail_genders = None
    try:
        sprint(NOTE_STYLE, "Filling Details...")
        ActionChains(driver).move_by_offset(1, 1)
        driver.find_element_by_css_selector("select[name=\"country\"]").click()
        time.sleep(0.3)
        driver.find_element_by_css_selector(
            "option[value=\"%s\"]" % country).click()
        
        for l in email:
            time.sleep(0.12)
            driver.find_element_by_css_selector(
                "input[type=\"email\"]").send_keys(l)

        driver.find_element_by_css_selector("input[type=\"email\"]").clear()
        
        for l in email:
            time.sleep(0.1)
            driver.find_element_by_css_selector(
                "input[type=\"email\"]").send_keys(l)
        
        for l in password:
            time.sleep(0.12)
            driver.find_element_by_css_selector(
                "input[type=\"password\"]").send_keys(l)
        
        
        time.sleep(0.12)
        driver.find_element_by_css_selector("input[type=\"date\"]").send_keys(dob)
        time.sleep(0.12)

        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        a = ActionChains(driver)
        a.move_by_offset(1, 0)
        a.perform()
        time.sleep(0.2)
        a = ActionChains(driver)
        a.move_to_element(driver.find_element_by_css_selector(
                "input[data-componentname=\"lastName\"]"))
        a.perform()
        for l in fname:
            time.sleep(0.15)
            driver.find_element_by_css_selector(
                "input[data-componentname=\"lastName\"]").send_keys(l)
        
        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        a = ActionChains(driver)
        a.move_by_offset(1, 0)
        a.perform()
        time.sleep(0.2)
        a = ActionChains(driver)
        a.move_to_element(driver.find_element_by_css_selector(
                "input[data-componentname=\"firstName\"]"))
        a.perform()

        for l in lname:
            time.sleep(0.11)
            driver.find_element_by_css_selector(
                "input[data-componentname=\"firstName\"]").send_keys(l)
        time.sleep(0.4)


        driver.find_element_by_css_selector("select[name=\"country\"]").click()
        driver.find_element_by_css_selector(
            "option[value=\"%s\"]" % country).click()
        ActionChains(driver).move_by_offset(1, 1)
        time.sleep(0.2)
        ActionChains(driver).move_by_offset(1, 1)
        time.sleep(1)
        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        a = ActionChains(driver)
        a.move_by_offset(1, 0)
        a.perform()
        time.sleep(0.2)
        a = ActionChains(driver)
        a.move_to_element(driver.find_element_by_css_selector(
        "ul[data-componentname=\"gender\"]").find_element_by_css_selector("li"))
        a.perform()

        avail_genders = driver.find_element_by_css_selector(
        "ul[data-componentname=\"gender\"]").find_elements_by_css_selector("li")
    
    except exceptions.NoSuchElementException as E:
        sprint(ERROR_STYLE, "Form Modal Irresponsive, Nike Error")
        raise E

    gender = random.choice(avail_genders)
    time.sleep(0.1)
    a = ActionChains(driver)
    a.move_to_element_with_offset(gender,1,5)
    a.move_to_element(gender)
    a.perform()
    time.sleep(0.1)
    gender.click()
    #avail_genders.click()
    ActionChains(driver).move_by_offset(1, 0)
    time.sleep(0.3)
    ActionChains(driver).move_by_offset(1, 1)
    time.sleep(0.24)
    ActionChains(driver).move_by_offset(0, 1)
    time.sleep(0.24)
    time.sleep(1)

    sprint(SUCCESS_STYLE, "All details filled, Submitting...")
    try:
        driver.find_element_by_css_selector(".nike-unite-submit-button").click()
        # mark email as used
        print("All Data Filled")
    except exceptions.NoSuchElementException as E:
        print("Submit Button Irresponsive")
        raise E



    sprint(NOTE_STYLE,"Awaiting Mobile Verification Modal...")

    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#nike-unite-mobile-verification-code-view")))
        time.sleep(0.5)
        
        print("Entering Phone Number for Verification")
    except exceptions.NoSuchElementException as E:
        print("Error occurred during Number Box search, Probably Network")
        raise E
    except exceptions.TimeoutException as E:
        print("couldn't locate Phone number modal, unknown error occured")
        raise E



    """
    # get number
    phone_i_l = None
    if country == "GB":
        nexmo.get_uk()
    else:
        # country us
        nexmo.get_us()
    """
    print("getting number...")
    phone_number = freesmsverifications.get_number()

    #print("repeate ",error)
    
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=\"tel\"]")))
        time.sleep(0.5)
        for k in phone_number:
            time.sleep(0.2)
            driver.find_element_by_css_selector(
                "input[type=\"tel\"]").send_keys(k)
        ActionChains(driver).move_by_offset(0, 1)
        time.sleep(0.24)
        a = ActionChains(driver)
        a.move_to_element(driver.find_element_by_css_selector(
                "input[type=\"tel\"]"))
        a.perform()
        time.sleep(0.2)

        
        a = ActionChains(driver)
        a.move_by_offset(1, 1)
        a.perform()
        
        time.sleep(0.24)
        
        print("Submitting number")
        time.sleep(0.6)
        send_b = driver.find_element_by_css_selector(".sendCodeButton")
        
        a = ActionChains(driver)
        a.move_to_element_with_offset(send_b,1,5)
        a.perform()
        time.sleep(0.1)
        a = ActionChains(driver)
        a.move_by_offset(1,5)
        a.perform()
        time.sleep(0.1)
        a = ActionChains(driver)
        a.move_to_element(send_b)
        a.perform()
        
        time.sleep(1)
        
        send_b.click()
    
    except exceptions.NoSuchElementException as E:
        print("Error occurred during number verification")
        raise E
    except exceptions.TimeoutException as E:
        print("couldn't locate Phone number verification modal, unknown error occured")
        raise E
    
    
    

    vcode = freesmsverifications.get_message(phone_number)


    time.sleep(0.24)
    sprint(NOTE_STYLE, "Entering Verification code...")
    driver.find_element_by_css_selector(
        ".verifyCode input").send_keys(vcode)
    
    a = ActionChains(driver)
    a.move_by_offset(1, 1)
    a.perform()
    a = ActionChains(driver)
    a.move_by_offset(1, 0)
    a.perform()
    
    time.sleep(0.5)
    sprint(NOTE_STYLE, "Submitting verification code...")
    
    a = ActionChains(driver)
    a.move_by_offset(1, 1)
    a.perform()
    
    driver.find_element_by_css_selector("input[value=\"CONTINUE\"]").click()

    print("submitted")
    print("waiting to verify if account successfully generated")
    try:
        WebDriverWait(driver, config.page_load_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-qa=\"user-name\"]")))
        print("Verified")
        time.sleep(1)
    except exceptions.NoSuchElementException as E:
        print("Couldn't verify if account was created (Modal)")
        raise E
    except exceptions.TimeoutException as E:
        print("timeout for account new account profile")
        raise E

    if __name__ == "__main__":
        #time.sleep(11000)
        pass
    #try:
    #    driver.find_element_by_css_selector(".mobileNumber-div")
    #except exceptions.NoSuchElementException as E:
    #    print("Error occurred during number verification")
    #    raise E
    driver.close()
    """
    print("Submitting")
    time.sleep(10000)
    # driver.close()
    """

# print(_valid_dob("12991990"))
# print(_valid_pw("apedf5A434"))
# print(_valid_email("ryan@p"))


