#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Arris cable modem plugin for collectd

This plugin scrapes upstream/downstream channel information from an Arris cable modem status page.

Author: Jacob Kupersmith <jake@jkup.org>
URL: https://github.com/jakup/collectd-surfboard
Last Updated: 2018-05-28
"""

import collectd
import requests
from BeautifulSoup import BeautifulSoup

HOST = ''
URL = 'http://192.168.100.1'


def config_func(config):
    host_set = False
    url_set = False
    for node in config.children:
        key = node.key.lower()
        value = node.values[0]
        if key == 'host':
            global HOST
            HOST = value
            host_set = True
        elif key == 'url':
            global URL
            URL = value
            url_set = True
        else:
            collectd.info('arris_modem plugin: unknown config key "%s"' % key)

    if host_set:
        collectd.info('arris_modem plugin: Using overridden host %s' % HOST)

    if url_set:
        collectd.info('arris_modem plugin: Using overridden url %s' % URL)
    else:
        collectd.info('arris_modem plugin: Using default url %s' % URL)


def read_func():
    val = collectd.Values(host=HOST, plugin='arris_modem')

    resp = requests.get('%s/cgi-bin/status' % URL)
    soup = BeautifulSoup(resp.content)
    for table in soup.findAll('table'):
        try:
            table_name = table.tr.th.text
        except:
            continue

        if table_name == 'Downstream Bonded Channels':
            for r in table.findAll('tr')[2:]:
                row = map(lambda x: x.text, r.findAll('td'))

                freq_hz = float(row[4].split(' ')[0]) * 1000000.0  # 0.0 MHz
                power = float(row[5].split(' ')[0])  # 0.0 dBmV
                snr = float(row[6].split(' ')[0])  # 0.0 dB
                corrected = int(row[7])
                uncorrectables = int(row[8])

                val.dispatch(type='ds',
                             type_instance='ch%s' % row[3],
                             values=[freq_hz, power, snr, corrected, uncorrectables])

        elif table_name == 'Upstream Bonded Channels':
            for r in table.findAll('tr')[2:]:
                row = map(lambda x: x.text, r.findAll('td'))

                symrate = float(row[4].split(' ')[0])  # 0 kSym/s
                freq_hz = float(row[5].split(' ')[0]) * 1000000.0  # 0.0 MHz
                power = float(row[6].split(' ')[0])  # 0.0 dBmV

                val.dispatch(type='us',
                             type_instance='ch%s' % row[3],
                             values=[symrate, freq_hz, power])


collectd.register_config(config_func)
collectd.register_read(read_func)
