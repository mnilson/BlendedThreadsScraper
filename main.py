import argparse
import smtplib

import requests
from bs4 import BeautifulSoup


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "blendedthread.ca",
    "Referer": "https://blendedthread.ca/collections/in-stock",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.183 Safari/537.36",
}


def contains(content: str, param: str) -> bool:
    return param.upper() in content.upper()


def send_email(subject: str, content: str) -> None:
    # send the email
    ses_user = args.ses_user
    ses_pw = args.ses_pw
    from_addr = args.from_email
    to_addr = args.to_email
    msg = f'From: {from_addr}\nTo: {to_addr}\nSubject: {subject}\n\n{content}'

    hostname = 'email-smtp.us-west-2.amazonaws.com'
    port = 587
    with smtplib.SMTP(hostname, port=port) as s:
        s.connect(hostname, port=port)
        s.starttls()
        s.login(ses_user, ses_pw)
        s.sendmail(from_addr, to_addr, msg)


def main() -> None:
    url = "https://blendedthread.ca/collections/in-stock"
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        products_to_check = ['scrap', 'mystery']
        for product_to_check in products_to_check:
            product_to_check = 'scrap'
            soup = BeautifulSoup(str(response.content), "html.parser")
            divs = soup.find_all('div', class_='figcaption under text-center')
            msg = ''
            for div in divs:
                item = div.p.text.replace('  ', '').replace('\\n', '')
                if product_to_check.upper() in item.upper():
                    find_all = div.find_all('span', "money")
                    print(f'{item}={find_all[0].text}')
                    msg += f'{item}={find_all[0].text}. '
            print(msg)
            if len(msg) > 1:
                send_email(product_to_check, msg)
    else:
        print(f'Send text to Michael that it isn\'t working. {response.status_code}')


parser = argparse.ArgumentParser()
parser.add_argument('--ses_user', required=True)
parser.add_argument('--ses_pw', required=True)
parser.add_argument('--from_email', required=True)
parser.add_argument('--to_email', required=True)
args = parser.parse_args()

if __name__ == '__main__':
    main()


