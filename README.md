# MB7621_modem_scraper
Python project to scrap Motorola MB7621 webpage info, save to sqlite db and do some charting. 

I have been having problems with my cable internet service, and one of the troubleshooting steps I took was to purchase a new modem. Still had the same problems. In order to convince my cable company that there were issues that had nothing to do with modem or house, I decided to collect some data. To that end I embarked on a project to learn python coding/charting, jupyter lab, web scraping and github. Before you are the fruits of my labor. 

## What's Here?

- MB7621 is a python module that contains all the webpage scrapping code. 
- example.ipynb provides simple example of how to use the module
- collect_data.py is a more complicated example that collects the web scrappings into a sqlite database at a user specified interval. 
- reboot_modem.py does just that...reboots your modem.

## How to Get Started?

First you need an environment to run in. I've provided an environment.yml file that you can use with conda like so:

```conda env create --file envname.yml```

That will create an environment called modem. Activate it via ```conda activate modem```.

Then you should be able to run ```jupyter lab``` and open the example.ipynb. 



