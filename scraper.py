import asyncio
import re
from typing import NamedTuple
from playwright.async_api import async_playwright, Page, Browser
from playwright_stealth import Stealth
from frontend import prompt_answer, render, UIModel, console
from rich.live import Live
from rich.panel import Panel
from time import sleep
from frontend import term, console, UIModel, prompt_answer


class AnswerInfo(NamedTuple):
    num_of_questions: int
    answer1_context: str | None
    answer2_context: str | None


# Colors
CYAN = "\033[1;36m"
RESET = "\033[0;37m"


class AsyncWebScraper:
    def __init__(self):
        self.page: Page
        self.browser: Browser
        self.answer1: str | None = None
        self.answer2: str | None = None

    async def setup(self, url: str):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        await Stealth().apply_stealth_async(self.context)
        self.page = await self.context.new_page()
        await self.page.goto(url)

    # Helper functions
    @staticmethod
    def color_digits(s: str) -> str:
        return re.sub(r"(\d+)", f"{CYAN}\\1{RESET}", s)

    async def get_score(self):
        return await self.page.inner_text("#MainContent_lblRunningTotal")

    async def get_question(self):
        return await self.page.inner_text("#MainContent_QuestionArea")

    async def get_answer(self) -> AnswerInfo:
        loc2 = self.page.locator("#MainContent_lblTwo")

        if await loc2.is_visible():
            a1 = await self.page.inner_text("#MainContent_lblOne")
            a2 = await self.page.inner_text("#MainContent_lblTwo")
            return AnswerInfo(num_of_questions=2, answer1_context=a1, answer2_context=a2)
        else:
            return AnswerInfo(
                num_of_questions=1,
                answer1_context=None,
                answer2_context=None,
            )

    async def set_answer_input(self, answer1: str, answer2: str):
        await self.page.locator("#txtFirstString, #txtFirstInt").fill(answer1)
        if answer2:
            await self.page.locator("#txtSecondString, #txtSecondInt").fill(answer2)

    async def submit_question(self):
        await self.page.locator("#btnSubmit").click()

    async def next_question(self):
        await self.page.locator("#btnNext").click()

    async def close_browser(self):
        await self.browser.close()


async def main():
    s = AsyncWebScraper()
    await s.setup("https://www.subnetting.net/Subnetting.aspx")

    # prepare a reusable ui to be edited, so we can write over top of it and it persists.
    m = UIModel(
        question="",
        score="",
        num_of_questions=1,
        selected_answer=1,
        answer1_context="Answer",
        answer2_context="Answer",
        answer1="",
        answer2="",
    )

    with term.cbreak(), Live(
        Panel("Loading..."), console=console, screen=True, refresh_per_second=30
    ) as live:
        while True:
            score = await s.get_score()
            question = await s.get_question()
            ai = await s.get_answer()

            # resets input and updates questions
            m.question = question
            m.score = score
            m.num_of_questions = ai.num_of_questions
            m.selected_answer = 1
            m.answer1_context = ai.answer1_context or "Answer"
            m.answer2_context = ai.answer2_context or "Answer"
            m.answer1 = "10.51.0."
            m.answer2 = ""

            result = prompt_answer(m, live)
            answer1, answer2 = result

            await s.set_answer_input(answer1=answer1 or "", answer2=answer2 or "")
            await s.submit_question()
            await s.next_question()

    # await scraper.close_browser()


asyncio.run(main())
