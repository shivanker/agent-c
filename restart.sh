#! /usr/bin/bash

sudo systemctl restart sushibot
sudo journalctl -u sushibot -f
