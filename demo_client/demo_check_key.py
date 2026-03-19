import argparse
import json
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import requests

BASE_URL = "http://127.0.0.1:8000/api"
PUBLIC_VALIDATE_URL = f"{BASE_URL}/support-tickets/public-validate-key/"


def validate_by_key(key: str) -> dict:
    resp = requests.post(PUBLIC_VALIDATE_URL, json={"key": key}, timeout=15)
    resp.raise_for_status()
    return resp.json()


def format_human_result(key: str, data: dict) -> str:
    valid = bool(data.get("valid"))
    if not valid:
        reason = data.get("reason") or "UNKNOWN"
        return "\n".join([
            f"Ключ: {key}",
            "Статус: НЕДЕЙСТВИТЕЛЕН",
            f"Причина: {reason}",
        ])

    return "\n".join([
        f"Ключ: {key}",
        "Статус: ДЕЙСТВИТЕЛЕН",
        f"Продукт: {data.get('product')}",
        f"Тип лицензии: {data.get('license_type')}",
        f"Дата начала: {data.get('start_date')}",
        f"Дата конца: {data.get('end_date')}",
        f"Активации: {data.get('current_activations')} / {data.get('max_activations')}",
    ])


def print_result(key: str, data: dict) -> None:
    print("\n=== РЕЗУЛЬТАТ ДЛЯ КЛЮЧА:", key, "===\n")
    print(format_human_result(key, data))


def run_cli() -> None:
    print("ДЕМО ПРОВЕРКИ ЛИЦЕНЗИИ ПО КЛЮЧУ\n")
    print("Программа делает одно: вы вводите КЛЮЧ, она показывает сведения об этом ключе.\n")

    while True:
        key = input("Введите ключ (или пусто для выхода): ").strip()
        if not key:
            print("Выход.")
            break

        try:
            data = validate_by_key(key)
        except Exception as e:
            print("Ошибка при обращении к серверу:", e)
            continue

        print_result(key, data)
        print("\n" + "-" * 40 + "\n")


def run_gui() -> None:
    root = tk.Tk()
    root.title("Demo: Проверка лицензионного ключа")
    root.geometry("720x520")

    padding = {"padx": 10, "pady": 6}

    frame_top = ttk.Frame(root)
    frame_top.pack(fill="x", **padding)

    ttk.Label(frame_top, text="Введите лицензионный ключ:").pack(anchor="w")

    key_var = tk.StringVar(value="")

    entry = ttk.Entry(frame_top, textvariable=key_var, width=80)
    entry.pack(fill="x", **padding)
    entry.focus_set()
    entry.focus_force()

    # В некоторых сборках exe вставка (Ctrl+V) иногда не срабатывает,
    # поэтому обрабатываем вставку явно из буфера обмена.
    def _paste_from_clipboard(event=None) -> str:
        try:
            text = root.clipboard_get()
        except tk.TclError:
            return "break"
        entry.delete(0, "end")
        entry.insert(0, text)
        return "break"

    entry.bind("<Control-v>", _paste_from_clipboard)
    entry.bind("<Control-V>", _paste_from_clipboard)
    entry.bind("<Insert>", _paste_from_clipboard)
    entry.bind("<Shift-Insert>", _paste_from_clipboard)

    frame_actions = ttk.Frame(root)
    frame_actions.pack(fill="x", **padding)

    status_var = tk.StringVar(value="Готово.")

    def set_status(msg: str) -> None:
        status_var.set(msg)

    def render_result(key: str, data: dict | None, error: str | None) -> None:
        # Clear
        result_text.configure(state="normal")
        result_text.delete("1.0", "end")

        if error:
            result_text.insert("end", f"Ошибка: {error}\n\n")
            if data is not None:
                result_text.insert("end", "Ответ сервера (JSON):\n")
                result_text.insert("end", json.dumps(data, ensure_ascii=False, indent=2))
        else:
            result_text.insert("end", format_human_result(key, data or {}))
            result_text.insert("end", "\n\n")
            result_text.insert("end", "Ответ сервера (JSON):\n")
            result_text.insert("end", json.dumps(data or {}, ensure_ascii=False, indent=2))

        result_text.configure(state="disabled")
        btn_check.configure(state="normal")
        set_status("Готово.")

    def worker(key: str) -> None:
        try:
            data = validate_by_key(key)
            root.after(0, lambda: render_result(key, data, None))
        except Exception as e:
            # Try to extract DRF error payload if present
            err_text = str(e)
            try:
                # If it's an HTTPError, it may contain response body via e.response
                resp = getattr(e, "response", None)
                if resp is not None:
                    err_text = f"HTTP {resp.status_code}: {resp.text[:500]}"
                    data = resp.json() if "application/json" in (resp.headers.get("Content-Type") or "") else None
                else:
                    data = None
            except Exception:
                data = None
            root.after(0, lambda: render_result(key, data, err_text))

    def on_check() -> None:
        key = (key_var.get() or "").strip()
        if not key:
            set_status("Введите ключ.")
            return
        set_status("Отправляю запрос на сервер...")
        btn_check.configure(state="disabled")

        threading.Thread(target=worker, args=(key,), daemon=True).start()

    btn_check = ttk.Button(frame_actions, text="Проверить", command=on_check)
    btn_check.pack(side="left")

    def on_clear() -> None:
        key_var.set("")
        status_var.set("Готово.")
        result_text.configure(state="normal")
        result_text.delete("1.0", "end")
        result_text.configure(state="disabled")

    btn_clear = ttk.Button(frame_actions, text="Очистить", command=on_clear)
    btn_clear.pack(side="left", **{"padx": 8})

    ttk.Label(root, textvariable=status_var).pack(anchor="w", **padding)

    result_text = ScrolledText(root, height=16, wrap="word")
    result_text.pack(fill="both", expand=True, padx=10, pady=8)
    result_text.configure(state="disabled")

    # Initial hint
    result_text.configure(state="normal")
    result_text.insert("end", "Введите ключ и нажмите \"Проверить\".\n")
    result_text.configure(state="disabled")

    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo: проверка лицензионного ключа")
    parser.add_argument("--cli", action="store_true", help="Запуск в консольном режиме")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()

