import pandas as pd
from requests_html import HTMLSession, user_agent
import random
import time

"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")
file_handler = logging.FileHandler(f"{__name__}.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
"""


class Scrap:
    def __init__(self, df, func, to_cont, nums=1, render=False) -> None:
        # option to render the page for javascript generated content
        self.render = render
        # total data to be scrapped is around 740 cities/provinces, so a dividen of 20 is enough to split the dataset into 37 sets
        self.FIXED_DIV = 20
        # the standard numbers of item on a single page is 15
        self.ITEMS_PER_PAGE = 15
        # some time the webpage lock us out, we need to restart scrapping from the previous checkpoint
        self.to_cont = to_cont
        # the number of pages we want to go through
        self.nums = nums
        # a count variable inplace to keep track of the last item added (this is used to ensure adding items to array is in strict o(1) time and also is helpful when we need to point the new data to the head of the array)
        self.count = 0
        # select the functionality(shopping,sight-seeing etc, note: keyword must be matching the url address )
        self.func = func
        # transform the dataframe (change the http links to retrieve functional information)
        self.df = self.transform(df.copy())
        # initialize arrays to store scrapped data (fixed_div * the targeted page number * number of items per page
        self.total_data = self.FIXED_DIV * self.nums * self.ITEMS_PER_PAGE
        self.names, self.places, self.links, self.imgs = (
            [None],
            [None],
            [None],
            [None],
        )

        # initialize the dataframe to store into the csv later
        self.data_df = {
            "names": self.names,
            "places": self.places,
            "links": self.links,
            "imgs": self.imgs,
        }

        # a index variable to act as the unique file name to prevent overwriting of previous files
        self.index = 0

    # This function helps to change the html page to prefered site e.g sight/restaurant/shopping
    def transform(self, df):
        df["links"] = df["links"].replace({"/place/": f"/{self.func}/"}, regex=True)
        return df

    # The looping function that retrives all info given a target city/province across all pages
    def scrap_info(self):
        # start session
        session = HTMLSession()
        self.init_arrs()

        # loop through each city/province,e.g. shanghai,beijing etc
        for i in range(self.to_cont, len(self.df)):
            # set up fake user agent
            ua = self.assign_ua()

            # rotate the sleep commend so not to overflood the website

            # establish link to the target city/province
            r = session.get(self.df.links[i], headers=ua)
            if self.render:
                r.html.render()
            print()
            print("-------------City break---------------------")
            self.slp(low=1, high=15)
            r = self.verify_check(r, i)

            # get the city/province name
            p = self.df.city[i]
            print(p)

            # check if the next page is available
            next_page = self.check_next_page(r)

            print(f"First Page: {r.html}")
            print(f"Second Page: {next_page}")

            # loop the page to add all items on the page
            self.page_loop(session, next_page, r, p, i)

        # to add the last csv file that does not amount up to the desinated quanity
        self.add_csv(i)

    def init_arrs(self):
        # initialize the array before we establish connection to the webpage as we need to adjust the size of the arrays according to different parameters in a inheritant situation
        self.names *= self.total_data
        self.places *= self.total_data
        self.links *= self.total_data
        self.imgs *= self.total_data

    def assign_ua(self):
        ua = user_agent("chrome")
        return {"User-Agent": ua}

    def page_loop(self, session, next_page, r, p, i):
        # retrieve all information for a target city/province across all pages (limit to self.nums to prevent blocking)
        for _ in range(self.nums):
            # find and add all tourist attractions on the current page
            self._add_info(r, p, i)

            # reassign the next page value
            ua = self.assign_ua()

            self.slp(low=1, high=5)

            if next_page is not None:
                r = session.get(next_page, headers=ua)
                if self.render:
                    r.html.render()

                r = self.verify_check(r, i)

                next_page = self.check_next_page(r)

                print(f"Current Page: {r.html}")
                print(f"Next Page: {next_page}")

            else:
                break

    def verify_check(self, r, i):
        print("verify check...")
        print(r.html)
        if "verify" in str(r.html):
            input("NEED TO VERIFY TO CONTINUE")
            session = HTMLSession()
            ua = self.assign_ua()
            r = session.get(self.df.links[i], headers=ua)
            print("verified!")
        return r

    def check_next_page(self, r):
        next_page = r.html.find(".nextpage", first=True)
        next_page = next_page.absolute_links if next_page else None
        return list(next_page)[0] if next_page else None

    # the main function that retrives information by scrapping the relevant html tags
    # and add the data to memory
    def _add_info(self, r, p, i):
        # the class tag amounting up to 10 items, each item contains the main information of the tourist attraction
        items = r.html.find(".list_mod2")

        # loop through all the tourist attraction on the page
        for item in items:
            self.get_standard_items(item)
            self.places[self.count] = p
            self.count += 1

            # save during scrapping to prevent lost of progress if any errors occured during the scrapping
            if self.count == self.total_data:
                self.add_csv(i)
                self.count = 0
        print(f"Count:{self.count}")

    def get_standard_items(self, item):
        # the secondary/temporary holder tag
        temp = item.find("dt", first=True)

        name = self.get_name(temp)
        link = self.get_link(temp)
        img = self.get_img(item)

        # update the array
        self.names[self.count] = name
        self.links[self.count] = link
        self.imgs[self.count] = img

    def get_name(self, temp):
        name = temp.find("a", first=True)
        return name.text if name else None

    def get_link(self, temp):
        link = temp.find("a", first=True)
        return list(link.absolute_links)[0] if link else None

    def get_img(self, item):
        img = item.find(".leftimg img", first=True)
        return str(img.html).split('"')[1] if img else None

    # to add to csv_file
    def add_csv(self, i):
        print("Added new csv")

        pd.DataFrame(self.data_df).to_csv(
            f"../csv/{self.func}_data_{self.index}_{i}.csv", index=False
        )
        self.index += 1

    def slp(self, low=1, high=15):
        slp = random.randint(low, high)
        print(f"waiting for {slp} secs")
        time.sleep(slp)
