import asyncio
import re
from playwright.async_api import async_playwright, Page, Browser
from playwright_stealth import Stealth

# Colors
CYAN = '\033[1;36m'
RESET = '\033[0;37m'

class AsyncWebScraper:
    def __init__(self):
      self.page: Page
      self.browser: Browser
      self.answer1: str | None = None
      self.answer2: str | None = None

    async def setup(self, url: str):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        await Stealth().apply_stealth_async(self.context)
        self.page = await self.context.new_page()
        await self.page.goto(url)


    # Helper functions
    @staticmethod
    def color_digits(s: str) -> str:
        return re.sub(r"(\d+)", f"{CYAN}\\1{RESET}", s)
    
    async def get_score(self):
        score = await self.page.inner_text('#MainContent_lblRunningTotal')
        print(self.color_digits(score))

    async def get_question(self):
        q = await self.page.inner_text('#MainContent_QuestionArea')
        print(self.color_digits(q))
        self.answer = None

    async def get_answer(self):
        try:
            await self.page.inner_text('#MainContent_lblTwo', timeout=2000)
            a1 = await self.page.inner_text('#MainContent_lblOne')
            a2 = await self.page.inner_text('#MainContent_lblTwo')
            self.answer1 = input(a1)
            self.answer2 = input(a2)
        except:
            pass

        while not self.answer1:
          self.answer1 = input(': ')

    async def set_answer_input(self):
        await self.page.locator("#txtFirstString").fill(self.answer)

    async def submit_question(self):
        await self.page.locator("#btnSubmit").click()

    async def next_question(self):
        await self.page.locator("#btnNext").click()

    async def close_browser(self):
        await self.browser.close()
       

async def main():
    s = AsyncWebScraper()
    await s.setup("https://www.subnetting.net/Subnetting.aspx")
    while True:
      await s.get_score()
      await s.get_question()
      await s.get_answer()
      await s.set_answer_input()
      await s.submit_question()
      await s.next_question()
    #await scraper.close_browser()

asyncio.run(main())
