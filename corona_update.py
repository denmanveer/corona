#!/usr/bin/python3
"""
Script to send email with latest stats on CoronaVirus.
"""
__author__ = "Manveer Singh"

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import re
from datetime import datetime
import smtplib
from argparse import ArgumentParser

class GettingStats():
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=self.chrome_options)

    def get_wm_data(self, countries):
        """
        Getting Data from WorldMeter
        :param countries: List of countries whose stats we want to fetch
        """
        output_data = '>> According to new stats about coronavirus from worldometers.info:\n'
        countries = {country.lower() for country in countries}
        try:
            print("Getting Data from WorldOMeters")
            pattern_regex = re.compile(r"(?P<name>\w+\s?\D*?\s?)\s(?P<confirmed_cases>\d+\,?\d+|\d?)\s\+?.*",
                                       re.MULTILINE)
            self.driver.get('https://www.worldometers.info/coronavirus/')
            table = self.driver.find_element_by_xpath('//*[@id="main_table_countries"]/tbody[1]')
            table_body = table.text
            for record in table_body.splitlines():
                match = re.match(pattern_regex, record)
                if match.group('name').lower() in countries:
                    output_data += f"Confirmed cases in {match.group('name')} are " \
                                   f"{match.group('confirmed_cases')}\n"
            return output_data
        except:
            print("Error :", sys.exc_info()[0])
            self.driver.quit()
            raise

    def get_canada_data(self):
        """
        Getting  Canada Specific Data
        """
        ret_text = "\n>> Areas in Canada with cases of COVID-19:\n"
        try:
            print("Getting Data from Canada.ca")
            self.driver.get('https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-'
                            'infection.html')
            table = self.driver.find_element_by_xpath('/html/body/main/div[3]/table[1]')
            for x in table.text.splitlines()[2:]:
                pattern_regex = re.compile(r"(?P<name>^\w+\s?\D*?\s?\D*)\s(?P<confirmed_cases>\d{1,3})\s(\d{1,3})",
                                           re.MULTILINE)
                match = re.match(pattern_regex, x)
                if match:
                    if not (match.group('name') == 'Total cases'):
                        ret_text += f"Confirmed cases in {match.group('name')} are {match.group('confirmed_cases')}\n"
                    else:
                        last_line = f"Total Cases according to canada.ca are {match.group('confirmed_cases')}"
            self.driver.close()
            return ret_text+last_line
        except:
            print("Error :", sys.exc_info()[0])
            self.driver.quit()
            raise

    def send_email(self, body, emails):
        """
        Send Email with the data received
        :param body: The email body having all the stats
        :param emails: The list of emails where stats will be sent
        """
        subject = f"Coronavirus stats as of {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        body += "\n\n\n>> Check the link for more updates: https://www.worldometers.info/coronavirus/ " \
                "and https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection.html\n"
        body += "\nDisclaimer: Data from WorldoMeter and Canada.ca sometime can't match as they both update their " \
                "data at different time"
        msg = f"Subject: {subject}\n\n{body}"
        try:
            print("Sending Email")
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login('email', 'pass')
            for email in emails:
                server.sendmail('sender_email',email,msg)
            print(f"Email was Successfully sent to : {emails}")
            server.quit()
        except:
            print("Error :", sys.exc_info()[0])
            server.quit()
            raise


if __name__ == "__main__":
    parser = ArgumentParser("Script to send latest stats of coronavirua via email")
    parser.add_argument('--countries', '-c', nargs='+', default=['Canada', 'India'], help="Name of countries whom "
                                                                                          "stats you want to check")
    parser.add_argument('--emails', '-e', nargs='+', default=['talk2me@manveerkhurana.com'], help="List of email "
                                                                                                  "addresses")
    args = parser.parse_args()
    stats = GettingStats()
    all_data = stats.get_wm_data(args.countries)
    can_data = stats.get_canada_data()
    stats.send_email(all_data+can_data, args.emails)
