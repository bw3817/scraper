"""
Scrape a page from State Department of Assessment and Taxation (SDAT) site to obtain
find basic owner and transfer information.
"""

import requests
from bs4 import BeautifulSoup, element as bs4_element


class ScrapeSDAT:
    """Scrape SDAT site to find basic owner and transfer information."""

    def parse_html(self, table):
        """
        Parse HTML table content.
        :param table: BeautifulSoup4 table object
        :return: None
        """
        # parse table rows
        tbody = table.find('tbody')
        trs = tbody.find_all('tr', class_=['tr_blanc', 'tr_bleu1'])
        band_set = None
        bandwidths = None
        total = len(trs)

        with tqdm(total=total) as pbar:
            for tr_no, tr in enumerate(trs):
                band_set, bandwidths = self._parse_table_row(tr, band_set, bandwidths)
                pbar.update(1)

    @staticmethod
    def get_table_data(soup, table_id):
        """
        Parses page and returns HTML tables on the page.
        :return: list of beautifulsoup4 objects, each representing an HTML table
        """
        return soup.find('table', id=table_id)

    @staticmethod
    def _parse_owner_info(table):
        """
        Parse a page from SDAT and return two beautifulsoup4 TableRow objects.
        :param table: beautifulsoup4 Table object
        :return: list of two beautifulsoup4 TableRow objects
        """
        owner_info_found = False
        rows = table.find_all('tr')

        for row_number, row in enumerate(rows):
            if owner_info_found:
                return rows[row_number: row_number + 2]

            for td in row.find_all('th'):
                text = ' '.join(td.get_text().split())
                if text == 'Owner Information':
                    owner_info_found = True

    @staticmethod
    def _parse_transfer_info(table):
        """
        Parse a page from SDAT and return a beautifulsoup4 Table object.
        :param table: beautifulsoup4 Table object
        :return: a beautifulsoup4 Table object
        """
        transfer_info_found = False
        rows = table.find_all('tr')

        for row in rows:
            if transfer_info_found:
                td = row.find('td')
                return td.find('table')

            for td in row.find_all('th'):
                text = ' '.join(td.get_text().split())
                if text == 'Transfer Information':
                    transfer_info_found = True

    def get_owner_info(self, table):
        """
        Parse a page from SDAT and return two beautifulsoup4 TableRow objects.
        :param table: beautifulsoup4 Table object
        :return: list
        """
        separator = "<br/>"
        two_rows = self._parse_owner_info(table)
        mailing_address = list()

        for row in two_rows:
            tds = row.find_all('td')
            td_text = tds[1].get_text(strip=True, separator=separator)
            for part in td_text.split(separator):
                mailing_address.append(part)

        return mailing_address

    def get_transfer_info(self, table):
        """
        Parse a page from SDAT and return two beautifulsoup4 TableRow objects.
        :param table: beautifulsoup4 Table object
        :return: list
        """
        separator = "<br/>"
        valid_headers = ('Seller:', 'Date:', 'Price:', 'Type:', 'Deed1:', 'Deed2:')
        inner_table = self._parse_transfer_info(table)
        transfer_info = list()

        for tr in inner_table.find_all('tr'):
            for td in tr.find_all('td'):
                text = td.get_text(strip=True, separator=separator)
                if text:
                    parsed_text = text.split(separator)
                    if len(parsed_text) > 1 and parsed_text[0] in valid_headers:
                        transfer_info.append(parsed_text)

        return transfer_info

    def scrape(self, property_url):
        """
        Parses page and returns HTML tables on the page.
        :return: list of beautifulsoup4 objects, each representing an HTML table
        """
        page = requests.get(property_url)
        soup = BeautifulSoup(page.text, 'lxml')
        detail_search_table = self.get_table_data(soup, table_id='detailSearch')
        owner_info = self.get_owner_info(detail_search_table)
        print(owner_info)
        transfer_info = self.get_transfer_info(detail_search_table)
        print(transfer_info)


if __name__ == '__main__':
    base_url = "https://sdat.dat.maryland.gov/RealProperty/Pages/viewdetails.aspx"
    sdat_property_url = f"{base_url}?County=03&SearchType=ACCT&Ward=16&Section=10&Block=0097%20&Lot=054"
    scraper = ScrapeSDAT()
    scraper.scrape(sdat_property_url)

