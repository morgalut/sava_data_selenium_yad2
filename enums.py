from enum import Enum

class URLs(Enum):
    YAD2_ITEM_URL = 'https://www.yad2.co.il/realestate/item/{token}'
    YAD2_URL = 'https://www.yad2.co.il/realestate/forsale'

class Captcha(Enum):
    URL_CAPTCHA = 'https://www.yad2.co.il/captcha'

class Selectors(Enum):
    TITLE = 'h1.heading_heading__SB617'
    PRICE = 'span.price_price__xQt90'
    DESCRIPTION = 'h2.address_address__CNi30'
    BUILDING_ITEM = 'span.building-item_itemValue__2jk14'
    DESCRIPTION_TEXT = 'p.description_description__l3oun'
    FEED_TITLE = ".feeditem.main .title"
    FEED_PRICE = ".price"
    FEED_DESCRIPTION = ".description"

class MenuChoice(Enum):
    ALL = '1'
    TOKEN = '2'
    DISPLAY = '3'
    EXIT = '4'
