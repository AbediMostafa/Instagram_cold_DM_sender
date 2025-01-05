import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


class TmpMail:
    ig = None
    code = None
    account = None
    counter = 1
    session = None
    base_url = 'https://bulkacc.com/Home/SignIn'
    mail_url = "https://bulkacc.com/TempMail/GetCode"
    login_url = None
    token_input = None
    json_response = None
    first_login_response = None

    def __init__(self, ig):
        self.ig = ig
        self.account = self.ig.account

        if not self.account.email:
            raise Exception("Account email not set")

        self.session = requests.Session()

    def get_code(self):
        self.account.add_cli('Starting to get Code sent to email')

        (self.get_login_url()
         .go_to_login_page()
         .first_login()
         .second_login()
         .get_email()
         .extract_code()
         )

        return self.code

    def get_login_url(self):
        login_resp = self.session.get(self.base_url)
        self.login_url = login_resp.url
        self.account.add_cli('Got login url successfully')

        return self

    def go_to_login_page(self):
        login_page = self.session.get(self.login_url)

        if "__RequestVerificationToken" in login_page.text:
            soup = BeautifulSoup(login_page.text, "html.parser")
            self.token_input = soup.find("input", {"name": "__RequestVerificationToken"})['value']
            self.account.add_cli('Got token input successfully')

        else:
            raise Exception("Couldn't find __RequestVerificationToken on the login page")

        return self

    def first_login(self):
        load_dotenv()

        login_data = {
            "Email": os.getenv('BULKACC_USERNAME'),
            "Password": os.getenv('BULKACC_PASSWORD'),
            "RememberMe": "true",
            "__RequestVerificationToken": self.token_input,
        }

        self.first_login_response = self.session.post(self.login_url, data=login_data)

        if self.first_login_response.status_code != 200:
            raise Exception("Login failed. Check your credentials.")

        self.account.add_cli('Logged in first time successfully')

        return self

    def second_login(self):
        soup = BeautifulSoup(self.first_login_response.text, "html.parser")
        form = soup.find("form")

        if not form:
            raise Exception("Auto-submitting form not found!")

        form_action = form["action"]
        form_data = {input_tag["name"]: input_tag["value"] for input_tag in form.find_all("input", {"type": "hidden"})}

        form_response = self.session.post(form_action, data=form_data)

        if form_response.status_code != 200:
            raise Exception(f"Error Second login. Status code : {form_response.status_code}")

        self.account.add_cli('Logged in second time successfully')
        return self

    def get_email(self):

        params = {
            "email": self.account.email,  # Update with the correct email if needed
            "service": "Instagram",
        }

        response = self.session.get(self.mail_url, params=params)

        while response.status_code == 404:

            if self.counter > 5:
                break

            self.account.add_cli(f'Got 404 for the {self.counter} time')
            response = self.session.get(self.mail_url, params=params)
            self.ig.pause(2000 + self.counter, 3000 + self.counter)
            self.counter += 1

        if response.status_code == 200:
            try:
                self.json_response = response.json()
                self.account.add_cli('Email got successfully')
            except Exception as e:
                raise Exception(f'Problem Getting json data from incoming Email {str(e)}')
        else:
            raise Exception(f"Failed to fetch data from email url. Status code: {response.status_code}")

        return self

    def extract_code(self):
        html_content = self.json_response['data']['content']

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Look for the paragraph containing the code
        # Assuming the code is within a <p> tag or <font> tag
        code_element = soup.find('font', size="6")  # Looking for the <font> tag with size="6"

        # Extract and print the code
        if code_element:
            self.code = code_element.text.strip()
            self.account.add_cli(f"Extracted code: {self.code}")
        else:
            raise Exception("There is no code in incoming Email")
