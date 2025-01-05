import requests
from bs4 import BeautifulSoup

# Step 1: Define the main page URL
main_page_url = "https://bulkacc.com/"
sign_in_path = "/Home/SignIn"

# Step 2: Create a session to maintain cookies and other session-related data
session = requests.Session()

# Step 3: Access the main page
response = session.get(main_page_url)
if response.status_code == 200:
    print("Accessed the main page successfully!")
else:
    raise Exception(f"Failed to access main page. Status code: {response.status_code}")

# Step 4: Simulate clicking the "Sign In" button
sign_in_url = main_page_url.strip("/") + sign_in_path
sign_in_response = session.get(sign_in_url, allow_redirects=True)  # Follow redirects to the login page
soup = BeautifulSoup(sign_in_response.text, "html.parser")
return_url = soup.find("input", {"id": "ReturnUrl"})['value']
token_input = soup.find("input", {"name": "__RequestVerificationToken"})['value']

# Step 5: Check the response
if sign_in_response.status_code != 200:
    raise Exception(f"Failed to access sign-in page. Status code: {sign_in_response.status_code}")

login_url = sign_in_response.url

login_data = {
    "Email": "mostafaaabedi@gmail.com",
    "Password": "Qwert12#",
    "RememberMe": "false",
    "__RequestVerificationToken": token_input,
    "ReturnUrl": return_url
}

response = session.post(login_url, data=login_data)
if response.status_code != 200 or "Sign In" in response.text:
    raise Exception("Login failed. Check your credentials.")

print("Logged in successfully!")


cookies = session.cookies.get_dict()
cookies_string = "; ".join([f"{key}={value}" for key, value in cookies.items()])

soup = BeautifulSoup(response.text, "html.parser")
form = soup.find("form")
if not form:
    raise Exception("Auto-submitting form not found!")

form_action = form["action"]
form_data = {input_tag["name"]: input_tag["value"] for input_tag in form.find_all("input", {"type": "hidden"})}

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": cookies_string,
    # "Cookie": ".AspNetCore.OpenIdConnect.Nonce.CfDJ8C3mcq76zeRGh7c0nH5k2aGOY215HKrvGc2bEt_jTV6ZZzDO8H-BIPQF_39FEFvQ02xSSFLVRievOFyUZqND6pTzTL5w_3FURhYg3Wo0-3D5N0UTdzoBupsV5o7OG903ev6rAo4ejq90aPAbaN6v-I7jyz250yYfx_wPcRywFbZkXBKXIgP136XTF7E3RiCSdNK-AY_AUW3rRZD1_3ObtmBQpdeCl4xVT5QK3aCs9bS3euPOdhMA_u4K1MFIIKIsiPlkOv1q-EsQ44OCtkM21SM=N; .AspNetCore.Correlation.skmWjFXMn6Gb-jqc-anJdXk4idOkOjWhyaMe5jqAZfE=N",
    "Origin": "null",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-site",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

form_response = session.post(form_action, data=form_data, headers=headers, cookies=cookies)

if form_response.status_code != 200:
    print('Error login')
    print(form_response.status_code)

print(form_response.status_code)

# Step 5: Make a GET request to the target URL with the email and service parameters
params = {
    "email": "leiass9lmfma_admin@276491777.xyz",  # Update with the correct email if needed
    "service": "Instagram",
}

target_url = "https://bulkacc.com/TempMail/GetCode"

response = session.get(target_url, params=params)
if response.status_code == 200:
    print(response.json()['data']['content'])
else:
    print(f"Failed to fetch data from {target_url}. Status code: {response.status_code}")

soup = BeautifulSoup(response.json()['data']['content'], "html.parser")
form = soup.find("form")
