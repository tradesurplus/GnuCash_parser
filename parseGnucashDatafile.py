#!/usr/bin/python3

import datetime
import gzip
from tabulate import tabulate
import xml.etree.ElementTree as ET


SRCDIR = '/home/john/Documents'
DATAFILE = 'mmt.30Jun2023.gnucash'
OUTPUTFILE = 'gnucash.datafile.xml'
GZIPFILE = SRCDIR + '/' + DATAFILE
GUNZIPFILE = SRCDIR + '/' + OUTPUTFILE
TESTDATE = datetime.datetime(2022, 12, 22)
SEARCHSTR = 'Membership'

ns = {'cd': 'http://www.gnucash.org/XML/cd',
      'cust': "http://www.gnucash.org/XML/cust",
      'gnc': 'http://www.gnucash.org/XML/gnc',
      'invoice': "http://www.gnucash.org/XML/invoice",
      'owner': "http://www.gnucash.org/XML/owner",
      'split': "http://www.gnucash.org/XML/split",
      'trn': 'http://www.gnucash.org/XML/trn',
      'ts': "http://www.gnucash.org/XML/ts"}

with gzip.open(GZIPFILE, 'rt') as gf:
    file_content = gf.read()
    gunf = open(GUNZIPFILE, 'wt')
    gunf.write(file_content)
    gunf.close()
    gf.close()

with open(GUNZIPFILE) as gunf:
    tree = ET.parse(gunf)
    root = tree.getroot()

    def get_customer_name(guid):
        for custelem in root.findall('.//gnc:GncCustomer', ns):
            if custelem.find("./cust:guid", ns).text == guid:
                this_cust_name = custelem.find("./cust:name", ns).text
                return this_cust_name

    def str_search(note):
        if SEARCHSTR in note:
            return True

    inv_details = []
    for invelem in root.findall('.//gnc:GncInvoice', ns):
        node = invelem.find("./invoice:posted/ts:date", ns)
        if node is not None:
            date_str = node.text
        posted_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S +0000")
        node = invelem.find("./invoice:notes", ns)
        if node is not None:
            inv_notes = node.text
        if posted_date > TESTDATE and str_search(inv_notes):
            inv_owner_guid = invelem.find(".//owner:id", ns).text
            cust_name = get_customer_name(inv_owner_guid)
            inv_id = invelem.find('./invoice:id', ns).text
            short_date = datetime.datetime.strftime(posted_date, "%d/%m/%Y")
            inv_details_item = [cust_name, inv_id, short_date]
            inv_details.append(inv_details_item)

    inv_details.sort()
    print(tabulate(inv_details, headers=['Name', 'Ref', 'Date']))
