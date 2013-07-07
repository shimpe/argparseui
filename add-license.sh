#!/bin/sh
headache -h headache-conf/header.txt -c headache-conf/headache.conf `find | grep [\.]py$ | grep -v bitstring | grep -v pyeeg | grep -v mainwindow`
headache -h headache-conf/header.txt -c headache-conf/headache.conf `find | grep [\.]md$`
