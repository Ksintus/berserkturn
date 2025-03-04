import asyncio
import challonge
from enum import Enum #для того, чтобы нормально написать тип турнира без ошибок, почему то когда пишешь без енума вообще на выбывание ставит и пофиг, какой ты там тип прописал
import time #это для того, чтобы создавать рандом ссылку, но можно ссылку и от руки писать
import tkinter as tk #графика
from tkinter import messagebox #графика
import pyperclip #ссылку на турик скопировать
import webbrowser #открыть ссылку
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) #я так понял это прикол только винды, на линуксе ошибку при лупе не выдавало 

class TournamentType(Enum):
    SWISS = "swiss"

my_username = None
my_api_key = None

async def create_tournament():
    global my_username, my_api_key

    my_user = await challonge.get_user(my_username, my_api_key)

    tournament_name = tournament_name_entry.get()
    if not tournament_name:
        messagebox.showerror("Ошибка", "Название турнира не может быть пустым!")
        return

    unique_url = f"tournament_{int(time.time())}"

    new_tournament = await my_user.create_tournament(
        name=tournament_name,
        url=unique_url,
        tournament_type=TournamentType.SWISS
    )

    await new_tournament.setup_swiss_points(
        match_win=3,
        match_tie=1,
        game_win=0,
        game_tie=0,
        bye=3
    )

    rounds_count = int(rounds_entry.get())
    await new_tournament.setup_swiss_rounds(rounds_count=rounds_count)

    participants = participants_entry.get("1.0", tk.END).strip().split("\n")
    participants = [name.strip() for name in participants if name.strip()]

    for participant in participants:
        await new_tournament.add_participant(participant)

    await new_tournament.start()

    tournament_url = new_tournament.full_challonge_url

    show_tournament_link(tournament_url)

def show_tournament_link(url):

    link_window = tk.Toplevel(root)
    link_window.title("Ссылка на турнир")
    link_window.geometry("400x150")

    tk.Label(link_window, text="Турнир успешно создан! Ссылка:").pack(pady=10)
    tk.Label(link_window, text=url, fg="blue", cursor="hand2").pack(pady=5)

    def copy_link():
        pyperclip.copy(url)
        messagebox.showinfo("Успех", "Ссылка скопирована в буфер обмена!")

    copy_button = tk.Button(link_window, text="Скопировать ссылку", command=copy_link)
    copy_button.pack(pady=5)

    def open_link():
        webbrowser.open(url)

    open_button = tk.Button(link_window, text="Перейти по ссылке", command=open_link)
    open_button.pack(pady=5)

def run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_tournament())
    loop.close()

def open_tournament_window():
    global my_username, my_api_key

    my_username = username_entry.get()
    my_api_key = api_key_entry.get()

    if not my_username or not my_api_key:
        messagebox.showerror("Ошибка", "Логин и API-ключ не могут быть пустыми!")
        return

    login_window.destroy()

    global root, tournament_name_entry, rounds_entry, participants_entry
    root = tk.Tk()
    root.title("Создание турнира на Challonge")
    root.geometry("400x400")

    tk.Label(root, text="Название турнира:").pack(pady=5)
    tournament_name_entry = tk.Entry(root, width=40)
    tournament_name_entry.pack(pady=5)

    tk.Label(root, text="Количество раундов:").pack(pady=5)
    rounds_entry = tk.Entry(root, width=40)
    rounds_entry.pack(pady=5)

    tk.Label(root, text="Участники (по одному на строку):").pack(pady=5)
    participants_entry = tk.Text(root, width=40, height=10)
    participants_entry.pack(pady=5)

    create_button = tk.Button(root, text="Создать турнир", command=run_async)
    create_button.pack(pady=20)

    root.mainloop()

login_window = tk.Tk()
login_window.title("Авторизация на Challonge")
login_window.geometry("400x200")

tk.Label(login_window, text="Логин на Challonge:").pack(pady=5)
username_entry = tk.Entry(login_window, width=40)
username_entry.pack(pady=5)

tk.Label(login_window, text="API-ключ:").pack(pady=5)
api_key_entry = tk.Entry(login_window, width=40)
api_key_entry.pack(pady=5)

confirm_button = tk.Button(login_window, text="Продолжить", command=open_tournament_window)
confirm_button.pack(pady=20)

login_window.mainloop()