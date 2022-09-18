import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import requests
import sys
import time
import traceback

driver = webdriver.Firefox()

#scroll to bottom of page
def wait(time):
    WebDriverWait(driver, time)
def scroll():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#click button after scrolling to bottom of page
def click_button(btnid):
    scroll()
    driver.find_element(By.ID, btnid).click()

#select option from a drop down menu
def select_option(menu_id, option):
    element = driver.find_element(By.ID, menu_id)
    # driver.execute_script("arguments[0].scrollIntoView(false);", element)
    select = Select(element)
    select.select_by_visible_text(option)

#fill a text field
def fill_field(fld_id, text):
    field = driver.find_element(By.ID, fld_id)
    field.send_keys(text)

#open the nie website
def start():
    driver.get("https://icp.administracionelectronica.gob.es/icpplustieb/index")
    driver.find_element(By.ID, "cookie_action_close_header").click()

#fill in and continue on the select city page
def go_to_city_page(city):
    select_option("form", city)
    click_button("btnAceptar")

#choose the correct type of appointment for NIE page
def go_to_appointment_page(appointmentType):
    scroll()
    select_option("tramiteGrupo[0]", appointmentType)
    click_button("btnAceptar")
#could make this better

#conditions page after appointment page
def go_to_conditions_page():
    click_button("btnEntrar")

#input basic info to ask for appointment
def go_to_info_page(nie, name, country, expiry):
    driver.find_element(By.ID, "rdbTipoDocPas").click()
    fill_field("txtIdCitado", passport)
    fill_field("txtDesCitado", name)
    try:
        select_option("txtPaisNac", country)
    except selenium.common.exceptions.NoSuchElementException:
        pass
    try:
        fill_field("txtAnnoCitado", expiry)
    except selenium.common.exceptions.NoSuchElementException:
        pass
    click_button("btnEnviar")

#ask for an appointment
def require_appointment():
    click_button("btnEnviar")

#Select second office because it could return a single preselcted office or multiple where you have to make a choice
def go_to_office_page():
    try:
        driver.find_element(By.ID, "idSede").send_keys(Keys.DOWN)
    except:
        pass
    click_button("btnSiguiente")

def push_message(title, body):
    print(requests.post(
        "https://api.pushbullet.com/v2/pushes",
        data={
            "type": "note", "title": title,
            "body": "(" + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ") " + body
        },
        headers={"Access-Token": os.environ["PUSHBULLET_API_KEY"]}
    ).json())

#if there are no offices to choose from, exit
def no_appointment():
    click_button("btnSalir")

#info to be inputted after office selection - last step
def add_info_compl(tel, email):
    fill_field("txtTelefonoCitado", tel)
    fill_field("emailUNO", email)
    fill_field("emailDOS", email)
    click_button("btnSiguiente")

start()
try:

    city = sys.argv[1] # as defined in the list of cities that the page has
    passport = sys.argv[2]
    name = sys.argv[3]
    country = sys.argv[4]   # as defined in the list of countries that the page has ( in UPPERCASE )
    birthyear = sys.argv[5] 
    tel = sys.argv[6] # Spanish phone number without country code
    email = sys.argv[7]
    appointmentType = sys.argv[8] # as defined in the list of appointment types of the selected city

    print ("Looking for appointment of type: " + appointmentType)
    print ("\tCity of appointment: " + city)
    print ("\tName: " + name)
    print ("\tPassport: " + passport)
    print ("\tCountry: " + country)
    print ("\tYear of birth: " + birthyear)
    print ("\tEmail: " + email)
    print ("\tTelephone: " + tel)
    
    while True:
        go_to_city_page(city)
        time.sleep(1)
        go_to_appointment_page(appointmentType)
        time.sleep(1)
        go_to_conditions_page()
        time.sleep(1)
        go_to_info_page(passport, name, country, birthyear)
        time.sleep(1)
        require_appointment()
        time.sleep(1)
        try:
            go_to_office_page()
            add_info_compl(tel, email)
            if "no hay citas" not in driver.page_source.lower():
                push_message("NIE appointment found!", "Appointment found")
                break
            else:
                click_button("btnSubmit")
        except:
            traceback.print_exc()
            no_appointment()
        time.sleep(100)
except KeyboardInterrupt:
    wait(100)

#error page URL https://sede.administracionespublicas.gob.es/icpplustieb/acOfertarCita

#office selection page URL is https://sede.administracionespublicas.gob.es/icpplustieb/acCitar

#for the info_compl page URL is https://sede.administracionespublicas.gob.es/icpplustieb/acVerFormulario

#could get generic back page: https://sede.administracionespublicas.gob.es/icpplustieb/infogenerica
#use click_button("btnSubmit") if so
