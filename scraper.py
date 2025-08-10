import asyncio
import re
from typing import NamedTuple
from playwright.async_api import async_playwright, Page, Browser
from playwright_stealth import Stealth
from models import UIModel
from frontend import prompt_answer, render, term, console
from rich.live import Live
from rich.panel import Panel
from time import sleep


class AnswerInfo(NamedTuple):
    num_of_questions: int
    answer1_context: str | None
    answer2_context: str | None


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

async def countdown(m: UIModel, live: Live, seconds: int):
    m.timer = seconds
    while m.timer > 0:
        await asyncio.sleep(1)
        m.timer -= 1
        live.update(render(m))


async def main():
    s = AsyncWebScraper()
    await s.setup("https://www.subnetting.net/Subnetting.aspx")

    m = UIModel(
        timer=5 * 60,
        question="",
        score="",
        num_of_questions=1,
        selected_answer=1,
        answer1_context="Answer",
        answer2_context="Answer",
        answer1="",
        answer2="",
    )

    with term.cbreak(), Live(Panel("Loading..."), console=console, screen=True, refresh_per_second=30) as live:
        timer_task = asyncio.create_task(countdown(m, live, (5 * 60)-1))
        try:
            while True:
                if m.timer <= 0:
                    break

                m.score = await s.get_score()
                m.question = await s.get_question()
                ai = await s.get_answer()

                m.num_of_questions = ai.num_of_questions
                m.selected_answer = 1
                m.answer1_context = ai.answer1_context or "Answer"
                m.answer2_context = ai.answer2_context or "Answer"
                m.answer1 = ""
                m.answer2 = ""

                result = await asyncio.to_thread(prompt_answer, m, live)
                if not result or m.timer <= 0:
                    break
                answer1, answer2 = result

                await s.set_answer_input(answer1=answer1 or "", answer2=answer2 or "")
                await s.submit_question()
                await s.next_question()
        finally:
            if not timer_task.done():
                timer_task.cancel()
            await s.close_browser()


if __name__ == "__main__":
    asyncio.run(main())