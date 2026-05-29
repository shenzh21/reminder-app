"""
定时提醒应用
- 支持指定时间一次性提醒
- 支持指定时间点 + 重复间隔（每30分钟/每1小时）
- 支持最小化到系统托盘
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import sys
import base64
import io
from datetime import datetime, timedelta
from PIL import Image
import pystray
import winsound

# ── 全局状态 ──────────────────────────────────────────────
APP_VERSION = "1.4.0"
reminders = []        # 存储所有提醒
reminder_id_counter = 0
tray_icon = None
root = None
reminder_list_frame = None

# 持久化文件路径（保存在 exe 同目录或脚本同目录下）
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后，使用 exe 所在目录
    _APP_DIR = os.path.dirname(sys.executable)
else:
    # 普通 Python 脚本，使用脚本所在目录
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(_APP_DIR, 'reminders.json')


def save_reminders():
    """将当前提醒列表保存到 JSON 文件"""
    data = []
    for r in reminders:
        data.append({
            'id': r['id'],
            'hour': r['hour'],
            'minute': r['minute'],
            'message': r['message'],
            'repeat_interval': r['repeat_interval'],
            'enabled': r.get('enabled', True),
            'sound': r.get('sound', False),
            'next_trigger': r['next_trigger'].strftime('%Y-%m-%d %H:%M:%S') if r['next_trigger'] else None,
        })
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_reminders():
    """从 JSON 文件加载提醒列表，自动跳过已过期的一次性提醒"""
    global reminder_id_counter, reminders
    if not os.path.exists(SAVE_FILE):
        return
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return

    now = datetime.now()
    loaded = []
    for item in data:
        next_trigger = None
        if item.get('next_trigger'):
            try:
                next_trigger = datetime.strptime(item['next_trigger'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue

        repeat_interval = item['repeat_interval']

        # 一次性提醒：如果下次触发时间已过，则跳过不加载
        if repeat_interval is None:
            if next_trigger is None or next_trigger <= now:
                continue
        else:
            # 重复提醒：如果下次触发时间已过，从保存的时间往后推
            if next_trigger is not None and next_trigger <= now:
                while next_trigger <= now:
                    next_trigger += timedelta(minutes=repeat_interval)

        loaded.append({
            'id': item['id'],
            'hour': item['hour'],
            'minute': item['minute'],
            'message': item['message'],
            'repeat_interval': repeat_interval,
            'enabled': item.get('enabled', True),
            'sound': item.get('sound', False),
            'next_trigger': next_trigger,
        })
        if item['id'] > reminder_id_counter:
            reminder_id_counter = item['id']

    reminders = loaded


def create_tray_icon_image():
    """从预嵌入的 base64 数据加载系统托盘图标"""
    icon_b64 = (
        'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAB4UlEQVR4nO2bMW6EMBBF'
        'x1+cI2UqmtQ5AoeIlAvkLLlApD0ER0idhiplLpIIaYmQBcb2GNvj4VWrhcXz/4xt'
        'WGyii4sLzZicjfUvH7++50631yyxmVoElzLE5BT+8PTsfY2fr88sRpizhYeIDjEj'
        'lRHmDOEpRPuawTXCpBR/pnCXERwTIFG83R5nsDXShKeuBkgXz60GSBfPNaHjNsZhf'
        'Hv8/zy8f7OvN8e1d//AroD+7mptmbdZ4vOtArQkPsYE5LyfL8FR/PC9kJTsh8aLlk'
        'o/piuAlINWs+9bBSDloMWRf48tXXD9QHr5++gAKQcklPVzRFID+spH/1l4jPi92aA'
        'jAdiCUzw5FjVg3Mjg8t1aXOrH5S06qpAcwosZMB70361KUDcLDJnEV2tATlBbdnNm'
        'f0Z9BXRUgCXLOUf7KqfBoZBoZxeY7q+WQv9fr51Fj/3qDKQckHLgOthKN3DpQMkV'
        'WrnZ0gVSDvYOtDIb7I3+CyDlwHVQehUcZT+oAqSZ4Bsvjk6QPiMcxY+Qi0ipAp/S'
        'D+4CkxATQsRHzwK1mhATF0JOXrtamwmxiyUR2lCNJnBWihpOw6UXTqZYMA1OACWr'
        'IdVqcZMiGNX7Bdao3TFio3bPkI3aXWOS9g1eXJBu/gA1Lwf5Iv8/vwAAAABJRU5E'
        'rkJggg=='
    )
    icon_data = base64.b64decode(icon_b64)
    return Image.open(io.BytesIO(icon_data))


def show_reminder_popup(title, message, sound=True):
    """弹出提醒窗口（在新线程中运行，避免阻塞）"""
    def _show():
        if sound:
            try:
                winsound.Beep(1000, 300)
            except Exception:
                pass

        popup = tk.Toplevel(root)
        popup.title(title)
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.configure(bg='#F0F4FF')

        # 居中显示
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - 400) // 2
        y = (popup.winfo_screenheight() - 200) // 2
        popup.geometry(f"400x200+{x}+{y}")

        # 提醒图标
        icon_label = tk.Label(popup, text="⏰", font=("Segoe UI Emoji", 36), bg='#F0F4FF')
        icon_label.pack(pady=(15, 0))

        # 提醒内容
        msg_label = tk.Label(popup, text=message, font=("微软雅黑", 14), bg='#F0F4FF', wraplength=360)
        msg_label.pack(pady=(5, 10))

        # 确认按钮
        btn = tk.Button(popup, text="知道了", font=("微软雅黑", 11), width=10,
                        command=popup.destroy, bg='#4A90D9', fg='white',
                        activebackground='#2C5F9E', activeforeground='white', relief='flat')
        btn.pack(pady=(0, 10))
        btn.focus_set()

        # Enter / 空格 关闭弹窗
        popup.bind('<Return>', lambda e: popup.destroy())
        popup.bind('<space>', lambda e: popup.destroy())

        # 3 分钟后自动关闭
        popup.after(180000, popup.destroy)

        popup.focus_force()

    root.after(0, _show)


def compute_next_trigger(base_hour, base_minute, repeat_interval):
    """
    根据基准时间和重复间隔，计算下一次触发时间。
    repeat_interval: None (不重复), 30 (每30分钟), 60 (每60分钟)
    返回 datetime 或 None（表示已过且不重复）
    """
    now = datetime.now()
    base_time = now.replace(hour=base_hour, minute=base_minute, second=0, microsecond=0)

    if repeat_interval is None:
        # 一次性提醒：精确到某日某时某分，过期则不再提醒
        if base_time > now:
            return base_time
        else:
            return None

    # 重复提醒：只以分钟为准，从基准时间不断加间隔直到超过当前时间
    # 例如 13:30 每30分钟 → 14:00, 14:30, 15:00, ... 跨天也继续
    next_trigger = base_time
    while next_trigger <= now:
        next_trigger += timedelta(minutes=repeat_interval)
    return next_trigger


def reminder_checker():
    """后台线程：每秒检查是否有提醒需要触发"""
    while True:
        now = datetime.now()
        to_remove = []
        for r in reminders:
            # 已关闭的提醒跳过检查
            if not r.get('enabled', True):
                continue
            if r['next_trigger'] is None:
                to_remove.append(r)
                continue
            if now >= r['next_trigger']:
                show_reminder_popup("⏰ 定时提醒", r['message'], sound=r.get('sound', False))
                if r['repeat_interval'] is None:
                    to_remove.append(r)
                else:
                    # 计算下一次触发时间
                    r['next_trigger'] = r['next_trigger'] + timedelta(minutes=r['repeat_interval'])
                    r['_updated'] = True
        has_updates = False
        need_refresh = False
        for r in to_remove:
            reminders.remove(r)
            has_updates = True
            need_refresh = True
        # 重复提醒触发后也需要保存更新后的下次触发时间并刷新列表
        for r in reminders:
            if '_updated' in r:
                del r['_updated']
                has_updates = True
                need_refresh = True
        if has_updates:
            save_reminders()
        if need_refresh:
            root.after(0, refresh_reminder_list)
        time.sleep(1)


# ── GUI 构建 ──────────────────────────────────────────────

def add_reminder():
    """添加一个新提醒"""
    global reminder_id_counter

    hour = hour_var.get()
    minute = minute_var.get()
    message = msg_entry.get().strip()
    repeat = repeat_var.get()

    if not message:
        messagebox.showwarning("提示", "请输入提醒内容！")
        return

    if repeat == "仅一次":
        repeat_interval = None
    elif repeat == "每30分钟":
        repeat_interval = 30
    else:
        repeat_interval = 60

    next_trigger = compute_next_trigger(hour, minute, repeat_interval)
    if next_trigger is None:
        messagebox.showinfo("提示", "指定的时间已过，无法设置一次性提醒。")
        return

    reminder_id_counter += 1
    reminders.append({
        'id': reminder_id_counter,
        'hour': hour,
        'minute': minute,
        'message': message,
        'repeat_interval': repeat_interval,
        'enabled': True,
        'sound': False,
        'next_trigger': next_trigger,
    })
    save_reminders()
    refresh_reminder_list()
    msg_entry.delete(0, tk.END)


def delete_reminder(rid):
    """删除指定提醒"""
    global reminders
    reminders = [r for r in reminders if r['id'] != rid]
    save_reminders()
    refresh_reminder_list()


def toggle_reminder(rid):
    """切换提醒的启用/关闭状态"""
    for r in reminders:
        if r['id'] == rid:
            r['enabled'] = not r.get('enabled', True)
            # 重新启用时，重新计算下次触发时间
            if r['enabled']:
                r['next_trigger'] = compute_next_trigger(r['hour'], r['minute'], r['repeat_interval'])
                if r['next_trigger'] is None:
                    # 一次性提醒已过期，保持关闭
                    r['enabled'] = False
            break
    save_reminders()
    refresh_reminder_list()


def toggle_sound(rid):
    """切换提醒的音效开关"""
    for r in reminders:
        if r['id'] == rid:
            r['sound'] = not r.get('sound', False)
            break
    save_reminders()
    refresh_reminder_list()


def refresh_reminder_list():
    """刷新提醒列表显示"""
    for widget in reminder_list_frame.winfo_children():
        widget.destroy()

    if not reminders:
        tk.Label(reminder_list_frame, text="暂无提醒", font=("微软雅黑", 10),
                 fg='#999999', bg='#FAFAFA').pack(pady=20)
        return

    for r in reminders:
        is_enabled = r.get('enabled', True)
        row_bg = '#FAFAFA' if is_enabled else '#F0F0F0'
        fg_color = '#333333' if is_enabled else '#AAAAAA'

        row = tk.Frame(reminder_list_frame, bg=row_bg)
        row.pack(fill='x', padx=10, pady=3)

        repeat_str = "仅一次" if r['repeat_interval'] is None else f"每{r['repeat_interval']}分钟"
        if is_enabled:
            next_str = r['next_trigger'].strftime("%H:%M:%S") if r['next_trigger'] else "已过期"
        else:
            next_str = "已暂停"
        text = f"⏰ {r['hour']:02d}:{r['minute']:02d} | {repeat_str} | {next_str} | {r['message']}"

        tk.Label(row, text=text, font=("微软雅黑", 9), bg=row_bg, fg=fg_color,
                 anchor='w').pack(side='left', fill='x', expand=True)

        # 删除按钮
        tk.Button(row, text="✕", font=("微软雅黑", 9), fg='red', bg=row_bg,
                  relief='flat', command=lambda rid=r['id']: delete_reminder(rid)).pack(side='right')

        # 音效开关按钮
        is_sound = r.get('sound', False)
        sound_text = "🔔" if is_sound else "🔕"
        tk.Button(row, text=sound_text, font=("微软雅黑", 9), bg=row_bg,
                  relief='flat', command=lambda rid=r['id']: toggle_sound(rid)).pack(side='right', padx=(0, 2))

        # 启停开关按钮
        toggle_text = "⏸" if is_enabled else "▶"
        toggle_fg = '#E6A817' if is_enabled else '#4A90D9'
        tk.Button(row, text=toggle_text, font=("微软雅黑", 10), fg=toggle_fg, bg=row_bg,
                  relief='flat', command=lambda rid=r['id']: toggle_reminder(rid)).pack(side='right', padx=(0, 2))


def minimize_to_tray():
    """最小化到系统托盘"""
    root.withdraw()


def restore_from_tray(icon, item):
    """从系统托盘恢复窗口"""
    root.after(0, root.deiconify)


def quit_app(icon=None, item=None):
    """退出应用"""
    if tray_icon:
        tray_icon.stop()
    root.after(0, root.destroy)


def setup_tray():
    """设置系统托盘图标"""
    global tray_icon
    icon_image = create_tray_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem("显示主窗口", restore_from_tray, default=True),
        pystray.MenuItem("退出", quit_app),
    )
    tray_icon = pystray.Icon("reminder_app", icon_image, "定时提醒", menu)
    tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
    tray_thread.start()


def on_closing():
    """点击关闭按钮时最小化到托盘而非退出"""
    minimize_to_tray()


def build_ui():
    """构建主界面"""
    global root, hour_var, minute_var, repeat_var, msg_entry, reminder_list_frame

    root = tk.Tk()
    root.title(f"⏰ 定时提醒 v{APP_VERSION}")
    root.geometry("480x520")
    root.resizable(False, False)
    root.configure(bg='#F0F4FF')

    # 居中显示
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 480) // 2
    y = (root.winfo_screenheight() - 520) // 2
    root.geometry(f"480x520+{x}+{y}")

    # ── 标题 ──
    title_frame = tk.Frame(root, bg='#4A90D9', height=50)
    title_frame.pack(fill='x')
    title_frame.pack_propagate(False)
    tk.Label(title_frame, text=f"⏰ 定时提醒 v{APP_VERSION}", font=("微软雅黑", 16, "bold"),
             bg='#4A90D9', fg='white').pack(expand=True)

    # ── 设置区域 ──
    setting_frame = tk.Frame(root, bg='#F0F4FF', padx=15, pady=10)
    setting_frame.pack(fill='x')

    # 时间选择行
    time_row = tk.Frame(setting_frame, bg='#F0F4FF')
    time_row.pack(fill='x', pady=(0, 8))

    tk.Label(time_row, text="提醒时间:", font=("微软雅黑", 11), bg='#F0F4FF').pack(side='left')

    hour_var = tk.IntVar(value=datetime.now().hour)
    minute_var = tk.IntVar(value=datetime.now().minute)

    hour_spin = tk.Spinbox(time_row, from_=0, to=23, textvariable=hour_var, width=3,
                           font=("微软雅黑", 12), justify='center')
    hour_spin.pack(side='left', padx=(5, 2))
    tk.Label(time_row, text=":", font=("微软雅黑", 14, "bold"), bg='#F0F4FF').pack(side='left')
    minute_spin = tk.Spinbox(time_row, from_=0, to=59, textvariable=minute_var, width=3,
                             font=("微软雅黑", 12), justify='center')
    minute_spin.pack(side='left', padx=(2, 10))

    # 重复选择
    tk.Label(time_row, text="重复:", font=("微软雅黑", 11), bg='#F0F4FF').pack(side='left')
    repeat_var = tk.StringVar(value="仅一次")
    repeat_combo = ttk.Combobox(time_row, textvariable=repeat_var, width=10,
                                 values=["仅一次", "每30分钟", "每1小时"],
                                 state='readonly', font=("微软雅黑", 10))
    repeat_combo.pack(side='left', padx=5)

    # 提醒内容行
    msg_row = tk.Frame(setting_frame, bg='#F0F4FF')
    msg_row.pack(fill='x', pady=(0, 8))

    tk.Label(msg_row, text="提醒内容:", font=("微软雅黑", 11), bg='#F0F4FF').pack(side='left')
    msg_entry = tk.Entry(msg_row, font=("微软雅黑", 11), width=28)
    msg_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)

    # 添加按钮
    add_btn = tk.Button(setting_frame, text="➕ 添加提醒", font=("微软雅黑", 11, "bold"),
                        command=add_reminder, bg='#4A90D9', fg='white',
                        activebackground='#2C5F9E', activeforeground='white', relief='flat',
                        cursor='hand2', height=1)
    add_btn.pack(fill='x', pady=(0, 5))

    # ── 分隔线 ──
    ttk.Separator(root, orient='horizontal').pack(fill='x', padx=15, pady=5)

    # ── 提醒列表区域 ──
    tk.Label(root, text="📋 提醒列表", font=("微软雅黑", 12, "bold"),
             bg='#F0F4FF', anchor='w').pack(fill='x', padx=15, pady=(5, 0))

    list_container = tk.Frame(root, bg='#FAFAFA', bd=1, relief='solid')
    list_container.pack(fill='both', expand=True, padx=15, pady=(5, 10))

    # 可滚动列表
    canvas = tk.Canvas(list_container, bg='#FAFAFA', highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=canvas.yview)
    reminder_list_frame = tk.Frame(canvas, bg='#FAFAFA')

    reminder_list_frame.bind('<Configure>',
                             lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.create_window((0, 0), window=reminder_list_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # ── 底部状态栏 ──
    status_frame = tk.Frame(root, bg='#E8ECF5', height=30)
    status_frame.pack(fill='x')
    status_frame.pack_propagate(False)
    tk.Label(status_frame, text="💡 关闭窗口将最小化到系统托盘 | 右键托盘图标可退出",
             font=("微软雅黑", 8), bg='#E8ECF5', fg='#666666').pack(expand=True)

    # 初始显示
    refresh_reminder_list()

    # 关闭按钮行为
    root.protocol("WM_DELETE_WINDOW", on_closing)

    return root


def main():
    global root
    app = build_ui()

    # 加载持久化的提醒数据
    load_reminders()
    refresh_reminder_list()

    # 启动系统托盘
    setup_tray()

    # 启动后台提醒检查线程
    checker = threading.Thread(target=reminder_checker, daemon=True)
    checker.start()

    app.mainloop()


if __name__ == "__main__":
    main()
