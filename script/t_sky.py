import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Lead import Lead
from script.models.Category import Category
import logging

import requests
import re
from bs4 import BeautifulSoup
import urllib3
import urllib.parse
from time import sleep

max_retries = 2
max_threads = 2
timeout = 5

log_file_path = 'app.log'  # Log file path
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(log_file_path),
    logging.StreamHandler(sys.stdout)
])
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('peewee').setLevel(logging.WARNING)

agency_titles = [
    "Social Media Marketing Agency",
    "Digital Marketing Agency",
    "Content Marketing Agency",
    "E-commerce Marketing Agency",
    "Branding Agency",
    "Influencer Marketing Agency",
    "Performance Marketing Agency",
    "SEO & Social Media Agency",
    "Paid Media Agency",
    "Online Marketing Agency",
    "Growth Marketing Agency",
    "DTC Marketing Agency",
    "Social Media Advertising Agency",
    "Community Management Agency",
    "Digital Advertising Agency",
    "Social Media Strategy Agency",
    "Content Creation Agency",
    "Creative Agency",
    "Social Media Consulting",
    "Brand Strategy Agency"
]

states = [
    None,
    102356536, 105141335, 106522560, 105057336, 104508036, 100587095, 100134827, 102869081, 100270819, 105149562,
    105730022, 104703990, 104022923, 100152180, 105490917, 103420483, 102098694, 103622308, 104035573, 107163060,
    106516799, 104629187, 105763813, 106032500, 101098412, 102448103, 103977389, 103051080, 101651951, 101630962,
    103255397, 106981407, 103950076, 102986501, 101949407, 102571732, 101318387, 105080838, 102748797, 102095887,
    104470941, 105982022, 90009497, 90009496, 102299470, 104305776, 100459316, 103644278, 104551092, 106583973,
    103873152, 102772228, 100642566, 102890883, 104621616, 104655384, 102199904, 101728226, 103564821, 102044150,
    100025096, 102237789, 90009551, 105149290, 105333783, 106057199, 104379274, 105912732, 100565514, 106215326,
    100425729, 103883259, 101452733, 103030111, 100446943, 101355337, 103350119, 104738515, 101934083, 102478259,
    102713980, 105238872, 104677530, 105769538, 101282230, 106315325, 105015875, 100456013, 105733447, 106768907,
    102974008, 106373116, 106155005, 104514075, 106774002, 100876405, 105705451, 106693272, 106740205, 105646813,
    106137034, 103119917, 101728296, 106670623, 104170880, 100364837, 102927786, 104065273, 103619019, 103819153,
    102890719, 100733275, 105992277, 105587166, 103239229
]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

category = Category.select().where(Category.title == 'Cold DM Sam').first()


def first_request(url):
    first_header = {
        "accept": "application/vnd.linkedin.normalized+json+2.1",
        "accept-language": "en-US,en;q=0.9",
        "csrf-token": "ajax:1203836939889297251",
        "priority": "u=1, i",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-li-lang": "en_US",
        "x-li-page-instance": "urn:li:page:d_flagship3_search_srp_companies_load_more;NJu0zFeZS1i8rcLk+xpATg==",
        "x-li-pem-metadata": "Voyager - Companies SRP=search-results",
        "x-li-track": "{\"clientVersion\":\"1.13.30397\",\"mpVersion\":\"1.13.30397\",\"osName\":\"web\",\"timezoneOffset\":-6,\"timezone\":\"America/Chicago\",\"deviceFormFactor\":\"DESKTOP\",\"mpName\":\"voyager-web\",\"displayDensity\":1.25,\"displayWidth\":1366.25,\"displayHeight\":768.75}",
        "x-restli-protocol-version": "2.0.0",
        "cookie": "JSESSIONID=ajax:1203836939889297251; bcookie=\"v=2&6a0006e1-c38e-49dd-8cfc-e4c3bb779bf6\"; bscookie=\"v=1&202502101412098db53c85-974d-4243-8f39-bee0660c49c3AQFa1d6o5aRQmfdPY0h5L_yMwAyuVtfE\"; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; aam_uuid=63334531971435902132157243844532731244; fid=AQH1DkUeNdu92AAAAZTwNCFZ0GmSmzKu88r5OBMvnCWvR39aH57yaMOrBKNSm8DIWIpXWrjmDqt17Q; _gcl_au=1.1.1790500958.1739196741; li_at=AQEDAVefyzkCCROSAAABlPA0vlcAAAGVFEFCV1YAS0O7PIxlzA0Zkmp_FaAXNK3WFrdeMSefEsVnXoY23TSxgP7FW2ujBzE9unsQtZhG5feWRubSSrmJyQNMOq0pUxCrRY_fIA3kLIs5HuJL54lwmTTl; liap=true; li_rm=AQG4GuccBkgsSQAAAZTwNL9BgwMYP6dJuh-wypPLD0JX24hhOjB6a0ebWl3en2bz_SwYW3EK7yem_LATjSj-dQhwgx3Tbontekpdrxz0vHfXEz4_YZ2tiBF8BSB_kbHITxm4GUlcG4Ju-HehidLrraDZ802XYSW2ADLdFp5eIrlKqnIyTKBCtVbSWcbuzQhHJoPvQvm_ClB6rDoeDImsUJzajNRIu-sTe-4oxJGSa4e36_FqU1yD5x93xTXFfNtOA4lnOUwPfFtg-4YSoSCMd2KITTpHsbbZfULS0GKqt9KR1sBwCWhWUWax970fn967Eiw6BQONBYeYzNh1L6k; timezone=America/Chicago; li_theme=light; li_theme_set=app; li_sugr=ac4a2a3d-6089-46df-8502-ede533f8db69; _guid=4adb89a1-6414-4a97-bba3-340a5b5289de; AnalyticsSyncHistory=AQKJ30bY1mWvPQAAAZTwNMuWqD6oAT7u82O9PsiGgPnbIY43geAk-RlOP_9DjM-4qbgorYcvrEYyB_9pKSPulg; lms_ads=AQFuGOQfD5bF0gAAAZTwNMy-8XhTrjOfQU-KPyNjxZYbrrHRL6dfDCODzz1wI1kg2cIeLW-H0eqwmIPlQ5nis6b6Yuf4NozP; lms_analytics=AQFuGOQfD5bF0gAAAZTwNMy-8XhTrjOfQU-KPyNjxZYbrrHRL6dfDCODzz1wI1kg2cIeLW-H0eqwmIPlQ5nis6b6Yuf4NozP; dfpfpt=cb202871f7114348bd930953cbbf9ca8; lang=\"v=2&lang=en-us\"; s_cc=true; gpv_pn=www.linkedin.com%2Fpremium%2Fsurvey%2F; s_plt=1.40; s_pltp=www.linkedin.com%2Fpremium%2Fsurvey%2F; fptctx2=taBcrIH61PuCVH7eNCyH0HyAAKgSb15ZEqidLg30r8PnB2oKa6QeSyVlCGLmVQtPDrCPl7V%252bF3jEKeWn5hDT2m6TCIvFqYA3bAspggCeUy844LwmhdD2p6Q7B24vixNuraqzXSZOZGvdev84T1GETEzuCxi7p714iSwsLo%252fxjHJbfTOgv4dkT2ZgR%252b4LCuI%252flc%252ffOCXqmEf2OzJqB3lAqw2IYM2bwbZIIl1LQoSpSaRK3fw2Kb%252fvdE%252fcgQYQLbmtMxLt6YJDm8br5Nhoz3pJ3%252bRfbMwF0CwUjkTCdzkSuRKcH0Wqc3Ewtsp4y%252fNe8%252bjK94bXTvxxEpNkqsTkOOu4YG1WW1lKzeAPwi2bwC5vJgE%253d; s_ips=628; s_tslv=1739199517760; s_sq=lnkdprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dwww.linkedin.com%25252Fpremium%25252Fsurvey%25252F%2526link%253DLike%2526region%253Dember82%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dwww.linkedin.com%25252Fpremium%25252Fsurvey%25252F%2526pidt%253D1%2526oid%253D%25250A%25250A%252520%252520%252520%252520%25250A%252520%252520%252520%252520%252520%252520%252520%252520%25250A%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%25250A%252520%252520%252520%252520%25250A%252520%252520%252520%252520%25250A%25250A%25250A%25250A%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%25250A%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520Like%25250A%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%252520%25250A%252520%252520%252520%252520%252520%252520%252520%252520%25250A%252520%252520%2526oidt%253D3%2526ot%253DSUBMIT; s_tp=18187; s_ppv=www.linkedin.com%2Fpremium%2Fsurvey%2F%2C100%2C3%2C18186%2C34%2C34; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C20130%7CMCMID%7C62813572210788082062107472301413338791%7CMCAAMLH-1739851799%7C7%7CMCAAMB-1739851799%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1739254199s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-1035840515; __cf_bm=y0QFSyOod4A5TXWjnHDon.Bii1yZsTj8zZr_iAVXfWE-1739247008-1.0.1.1-NsDaQ9Emzmx3ZM.UvC3doaNjDtMGt.pMewIBjbyf5_I_AnVFABmm_8pLqQfxeIJUayYjRD80m6IBTGUiqvXAdg; UserMatchHistory=AQLD8rmofyq5WAAAAZTzN4gocX5TEbjWMjOFceBvpShRxERjJWaiUIM4uBYvy4ConraK8mmV_1S0RL5QWWHtvJDlX3BdSDxJ8-oR9DPdFLDGqu37nd5Cyou7putcv_T5ECTlKhAAuABdlYb9ryuxE-E1My7nhnqZMISA_GuoGQROXqelsNhpwkWuHdygkMnB7oa8k3H-WuR4sRWpZ9OQS723VdOL7NRu5n4Z73rIxh-Tcf8G0jigzFqlnvOux0O_zaFDKH4HgI5QY4hZTQMdWE7zfedLVstJ--LlCTx4o2jUhaNVOlyJBuqrs9WYtKVX8KuYAI7SGW4HvfbRhSJVMO0Qh4SUM1bJfW35bag7XLlMvvYiJA; lidc=\"b=TB41:s=T:r=T:a=T:p=T:g=4868:u=2:x=1:i=1739247291:t=1739286128:v=2:sig=AQHQZMH6cXJTnpdfX2AJAuewYiX8_Q6p\"",
        "Referer": "https://www.linkedin.com/search/results/companies/?keywords=Social%20media%20marketing%20agency&origin=GLOBAL_SEARCH_HEADER&page=5&sid=oW4",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    return requests.get(url, headers=first_header, timeout=30, verify=False)


def extract_instagram_username(url):
    for attempt in range(max_retries):
        try:
            # Send GET request to the website
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive"
            }
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <a> tags with href containing "instagram.com"
            instagram_links = soup.find_all("a", href=re.compile(r"(https?://)?(www\.)?instagram\.com/"))

            if instagram_links:
                # Extract Instagram username from the first valid link
                for link in instagram_links:
                    href = link.get('href')
                    if href:
                        # Clean up the URL to extract the username
                        username = re.sub(r"(https?://)?(www\.)?instagram\.com/", "", href).split('/')[0]

                        username = username.split('?')[0]  # Remove query parameters if any
                        return username

            instagram_data = soup.find(attrs={'data-options': True})
            if instagram_data:
                match = re.search(r'"avatars":{.*?"([^"]+)"', str(instagram_data))
                if match:
                    href = match.group(1)
                    username = re.sub(r"(https?://)?(www\.)?instagram\.com/", "", href).split('/')[0]
                    username = username.split('?')[0]
                    return username

            return None
        except Exception as e:
            sleep(1)  # Wait before retrying
    return None


def write_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    response = requests.get(url, headers=headers, timeout=30, verify=False)

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        website_link = soup.find('a', class_='link-no-visited-state',
                                 attrs={'aria-describedby': "websiteLinkDescription"})
        if website_link:
            redirect_url = website_link.get('href')
            parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(redirect_url).query)
            real_url = parsed_url['url'][0]  # Extract the real URL from the 'url' query parameter
            username = extract_instagram_username(real_url)

            if username:
                try:
                    # Lead.get_or_create(username=username, category=category)
                    logging.info(f"Lead Created successfully: {username}")

                except Exception as e:
                    logging.error(f"Failed to insert lead {username}: {str(e)}")

    except Exception as e:
        logging.error(f'Problem parsing company url : {str(e)}')


# with open('t.json', 'r', encoding='utf-8') as file:

for agency_title in agency_titles:
    for state in states:
        for offset in range(0, 1001, 10):  #

            logging.info(f"Agency Title: {agency_title}, State:{state}, Offset: {offset}")
            # Encode the agency title for the URL
            encoded_agency_title = urllib.parse.quote(agency_title)

            global_url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{offset},origin:GLOBAL_SEARCH_HEADER,query:(keywords:{encoded_agency_title},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.92cc53470cef3c578ab1d34676d5320c'
            state_url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{offset},origin:FACETED_SEARCH,query:(keywords:{encoded_agency_title},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:companyHqGeo,value:List({state})),(key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.92cc53470cef3c578ab1d34676d5320c'

            url = state_url if state else global_url

            response = first_request(url)
            print(response.text)

            try:
                data = response.json()

                print(data)

                try:
                    total_results = data["data"]["data"]["searchDashClustersByAll"]["paging"]["total"]
                    logging.info(f"Total results : {total_results}")

                    if offset >= total_results:
                        logging.error(f"Reached the end for state {state}. Breaking the loop.")
                        break
                except Exception as e:
                    logging.error(f"Problem calculating pagination : {str(e)}")

                for included in data["included"]:

                    if "template" in included:
                        if included["template"] == 'UNIVERSAL':
                            write_html(included["navigationUrl"])

            except Exception as e:
                logging.error(str(e))
