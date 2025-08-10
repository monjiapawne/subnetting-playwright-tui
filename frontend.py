# stdlib
from dataclasses import dataclass
from time import sleep
import re

# third-party
from blessed import Terminal
from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from models import UIModel


term = Terminal()
console = Console()
answer_prefix_enabled = True

def digits_coloured(text: str) -> Text:
    t = Text(text or "")
    for m in re.finditer(r"\d+", t.plain):
        t.stylize("bold cyan", m.start(), m.end())
    return t


def format_mmss(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))
    m, s = divmod(total_seconds, 60)
    return f"{m:02}:{s:02}"


def render(m: UIModel) -> Layout:
    a1_color = "cyan" if m.selected_answer == 1 else "bright_black"
    a2_color = "cyan" if m.selected_answer == 2 else "bright_black"
    layout = Layout()
    layout.split(
        Layout(name="upper", size=3),
        Layout(Panel(digits_coloured(m.question), title="Question", border_style="magenta")),
    )
    answers = Layout(name="answers")
    layout["upper"].split_row(
        answers,
        Layout(Panel(Align.center(m.score), title="Score", border_style="magenta"), size=10),
        Layout(Panel(Align.center(f"Time: {format_mmss(m.timer)}"),title="Timer", border_style="magenta"), size=16),
    )
    if m.num_of_questions == 2:
        answers.split_row(
            Layout(Panel(m.answer1, title=m.answer1_context or "Answer", border_style=a1_color), ratio=1),
            Layout(Panel(m.answer2, title=m.answer2_context or "Answer", border_style=a2_color), ratio=1),
        )
    else:
        answers.update(Panel(m.answer1, title=m.answer1_context or "Answer", border_style=a1_color))
    return layout


def prompt_answer(m: UIModel, live: Live) -> tuple[str, str | None] | None:
    live.update(render(m))
    while True:
        k = term.inkey(timeout=0)
        if not k:
            sleep(0.01)
            continue

        if k.name == "KEY_ENTER":
            if m.num_of_questions == 2:
                if m.selected_answer == 1 and m.answer1 and not m.answer2:
                    m.selected_answer = 2
                    live.update(render(m))
                    continue
                if m.answer1 and m.answer2:
                    return (m.answer1, m.answer2)
                continue
            else:
                return (m.answer1, None)

        elif k.name == "KEY_TAB":
            m.selected_answer = 2 if m.selected_answer == 1 else 1

        elif k.name == "KEY_BACKSPACE":
            if m.selected_answer == 1:
                m.answer1 = m.answer1[:-1]
            else:
                m.answer2 = m.answer2[:-1]

        elif k.name == "KEY_ESCAPE":
            return None

        elif not k.is_sequence:
            if m.selected_answer == 1:
                m.answer1 += str(k)
            else:
                m.answer2 += str(k)

        live.update(render(m))
