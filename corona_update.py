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
import os
import json
from pprint import pprint
from inspect import getmembers


class GettingStats():
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=self.chrome_options)

    def get_wm_data(self, countries, all):
        """
        Getting Data from WorldMeter
        :param countries: List of countries whose stats we want to fetch
        :param all: Flag to check all data is required or not
        """
        output_data = '>> According to new stats about coronavirus from worldometers.info:\n'
        countries = {country.lower() for country in countries}
        all_data = {}
        try:
            print("Getting Data from WorldOMeters")
            pattern_regex = re.compile(r"(?P<name>\w+\s?\D*?\s?)\s(?P<confirmed_cases>\d+\,?\d+|\d?)\s\+?.*",
                                       re.MULTILINE)
            self.driver.get('https://www.worldometers.info/coronavirus/')
            table = self.driver.find_element_by_xpath('/html/body/div[3]/div[3]/div/div[3]/div[1]/div/table')
            table_body = table.text
            for record in table_body.splitlines()[12:]:
                match = re.match(pattern_regex, record)
                if all:
                    all_data[match.group('name')] = match.group('confirmed_cases')
                if match.group('name').lower() in countries:
                    output_data += f"Confirmed cases in {match.group('name')} are " \
                                   f"{match.group('confirmed_cases')}\n"
            if all_data:
                self.add_to_file(all_data)
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
            self.driver.get('https://health-infobase.canada.ca/covid-19/iframe/table.html')
            table = self.driver.find_element_by_xpath('/html/body/div/table')
            for x in table.text.splitlines()[2:]:
                pattern_regex = re.compile(r"(?P<name>^\w+\s?\D*?\s?\D*)\s(?P<confirmed_cases>\d{0,2}?\,?\d{1,5})\s(\d{1,3})\s(?P<deaths>\d{1,3})",
                                           re.MULTILINE)
                match = re.match(pattern_regex, x)
                if match:
                    if not (match.group('name') == 'Canada'):
                        ret_text += f"Cases in {match.group('name')} are {match.group('confirmed_cases')} and " \
                                    f"Deaths are {match.group('deaths')}\n"
                    else:
                        last_line = f"According to canada.ca total confirmed cases are {match.group('confirmed_cases')} " \
                                    f"and total deaths are {match.group('deaths')}"
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

    def add_to_file(self, data):
        """
        This method add the data to the file for history
        :param data: Data to transfer to file
        """
        data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data_in_json'))
        date = datetime.now().strftime('%Y-%m-%d')
        data_dict = {date: data}
        if not os.path.isfile(data_file):
            with open(data_file, mode='w') as file:
                file.write(json.dumps(data_dict, indent=2))
        else:
            with open(data_file) as file:
                data_json = json.load(file)
            merge_dict = {**data_json, **data_dict}
            with open(data_file, mode='w') as f:
                f.write(json.dumps(merge_dict, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser("Script to send latest stats of coronavirua via email")
    parser.add_argument('--countries', '-c', nargs='+', default=['Canada', 'India'], help="Name of countries whom "
                                                                                          "stats you want to check")
    parser.add_argument('--emails', '-e', nargs='+', default=['talk2me@manveerkhurana.com'], help="List of email "
                                                                                                  "addresses")
    parser.add_argument('--all', '-a', action='store_true', help="This will list data of all the countries")
    args = parser.parse_args()
    stats = GettingStats()
    all_data = stats.get_wm_data(args.countries, args.all)
    can_data = stats.get_canada_data()
    stats.send_email(all_data+can_data, args.emails)
