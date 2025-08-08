# stdlib
from dataclasses import dataclass
from time import sleep

# third-party
from blessed import Terminal
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align


term = Terminal()
console = Console()
answer_prefix_enabled = True


@dataclass
class UIModel:
    question: str
    score: str
    answer_prefix: str = ""
    answer: str = ""


def render(m: UIModel) -> Layout:
    t = Text(m.answer_prefix + m.answer)

    layout = Layout()

    # splitting base horiztonally -
    layout.split(
        Layout(name="upper", size=3),
        Layout(Panel(m.question, title="Question", border_style="magenta")),
    )
    # spliting top |
    layout["upper"].split_row(
        Layout(Panel(t, title="Answer", border_style="cyan")),
        Layout(Panel(Align.center(m.score), title="Score", border_style="magenta"), size=10),
    )
    return layout


def prompt_answer(question: str, answer_prefix: str, score: str, initial: str = "") -> str | None:
    m = UIModel(question=question, score=score, answer=initial, answer_prefix=answer_prefix)  # initilize the UI model

    with term.cbreak(), Live(render(m), console=console, screen=True, refresh_per_second=30) as live:
        while True:
            k = term.inkey(timeout=0)
            if not k:
                sleep(0.01)
                continue

            if k.name == "KEY_ENTER":
                return m.answer_prefix + m.answer
            elif k.name == "KEY_BACKSPACE":
                m.answer = m.answer[:-1]
            elif k.name == "KEY_ESCAPE":
                m.answer = ""
                break
            elif not k.is_sequence:
                m.answer += str(k)

            live.update(render(m))


if __name__ == "__main__":
    while True:
        QUESTION = "What the broadcast address of the network 192.168.4.4/24"
        SCORE = "1/4"
        if answer_prefix_enabled:
            ANSWER_PREFIX = "192.168.4."
        else:
            ANSWER_PREFIX = ""

        ans = prompt_answer(QUESTION, ANSWER_PREFIX, SCORE)
        console.print(Panel(f"You typed: [bold]{ans or ''}[/bold]", title="Result", title_align="left"))
        sleep(2)
