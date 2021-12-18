import aiohttp
import asyncio
from bs4 import BeautifulSoup

class PlayerGatherer:
    def __init__(self, player_links, event):
        self.player_links = player_links
        self.player_list = {}
        self.event = event
    
    def format_link(self, link):
        return f'https://bwf.tournamentsoftware.com/sport/{link}'

    def format_player_link(self, link):
        return f"https://bwf.tournamentsoftware.com/player-profile/{link}"

    def get_player_list(self):
        return self.player_list

    def format_date(self, date):
        vals = date.split('/')
        return f"{vals[2]}-{vals[0]}-{vals[1]}"

    async def grab_player(self, link, session):
        async with session.get(self.format_link(link)) as resp:
            html_text = await resp.text()

            soup = BeautifulSoup(html_text, 'lxml')
            player_name = soup.find('div', class_='subtitle').find('h2').text

            info_link = soup.find('div', class_='subtitle').find('a')['href']

            details = dict()

            name = player_name[:player_name.index("Profile")].upper().strip()
            player_id = info_link[1:]
            
            index = player_id.index('/')+1
            player_id = player_id[index:]

            details['id'] = player_id
            self.player_list[name] = details
    
    async def grab_player_info(self, name, details, session):
        async with session.get(self.format_player_link(details['id'])) as resp:
            html_text = await resp.text()
            soup = BeautifulSoup(html_text, 'lxml')
            detail_section = soup.find('dl', class_='list list--flex list--bordered').findAll('div', class_='list__item')
            details['event'] = self.event
            
            details['country'] = None
            country = soup.find('div', class_='media__content-subinfo')
            if country:
                country = country.find('span', class_='nav-link__value').text
                country = country.upper().strip()
                details['country'] = country

            details['date of birth'] = None
            details['play r or l'] = None
            details['height'] = None
            for detail in detail_section:
                section = detail.find('dt', class_='list__label').text.lower().strip()
                value = detail.find('span', class_='nav-link__value').text.strip()

                if section == 'date of birth':
                    value = self.format_date(value)
                elif section == 'play r or l':
                    value = 'R' if value == 'Right handed' else 'L'
                elif section == 'height':
                    splitter = value.split(' ')
                    value = splitter[0]
                else:
                    continue

                details[section] = value
        
            print(f"{str(name)} : {str(details)}")

    async def grab_all_players(self):
        async with aiohttp.ClientSession() as session:
            loop = asyncio.get_event_loop()
            tasks = asyncio.gather(*[self.grab_player(link=player_link, session=session) for player_link in self.player_links], return_exceptions=True)
            loop.run_until_complete(tasks)

    async def grab_all_player_info(self):
        async with aiohttp.ClientSession() as session:
            loop = asyncio.get_event_loop()
            tasks = asyncio.gather(*[self.grab_player_info(name=name, details=details, session=session) for name, details in self.player_list.items()], return_exceptions=True)
            loop.run_until_complete(tasks)
