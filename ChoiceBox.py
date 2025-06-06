import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import random
import os
import time


# 读取设置文件
def read_settings(file_path):
    settings = {}
    try:
        # 打开设置文件并逐行读取键值对
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                key, value = line.strip().split("=")
                settings[key] = value
    except Exception as e:
        # 如果读取失败，显示错误消息框
        messagebox.showerror("错误", f"无法读取设置文件: {e}")
    return settings


# 写入设置文件
def write_settings(file_path, settings):
    try:
        # 将设置字典写入文件，每行一个键值对
        with open(file_path, 'w', encoding='utf-8') as file:
            for key, value in settings.items():
                file.write(f"{key}={value}\n")
    except Exception as e:
        # 如果写入失败，显示错误消息框
        messagebox.showerror("错误", f"无法写入设置文件: {e}")


# 打开设置窗口
def open_settings():
    global settings, choice_list
    # 创建一个新的顶级窗口用于设置
    settings_window = tk.Toplevel(root)
    settings_window.title("设置    by晓炙云溪")
    settings_window.geometry("550x140")  # 调整窗口宽度以容纳新布局

    # 设置项：奖池路径（路径）
    pool_path_label = tk.Label(settings_window, text="奖池路径:", font=("Arial", 12))
    pool_path_label.grid(row=0, column=0, pady=5, sticky="w")
    pool_path_entry = tk.Entry(settings_window, width=40, font=("Arial", 12))
    pool_path_entry.insert(0, settings.get("pool_path", ""))
    pool_path_entry.grid(row=0, column=1, padx=10, pady=5)

    # 浏览按钮，用于选择奖池文件
    def browse_pool_path():
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            pool_path_entry.delete(0, tk.END)
            pool_path_entry.insert(0, path)

    browse_button = tk.Button(settings_window, text="浏览", command=browse_pool_path, font=("Arial", 12), width=8,
                              height=1)
    browse_button.grid(row=0, column=2, pady=5)

    # 保存设置按钮的回调函数
    def save_settings():
        try:
            # 更新设置并写入文件
            settings["pool_path"] = pool_path_entry.get()
            write_settings(settings_file_path, settings)
            initialize_choice_list()  # 重新初始化奖池
            messagebox.showinfo("成功", "设置已保存！")
            settings_window.destroy()
        except Exception as e:
            # 如果保存失败，显示错误消息框
            messagebox.showerror("错误", f"保存设置失败: {e}")

    save_button = tk.Button(settings_window, text="保存", command=save_settings, font=("Arial", 14), width=10, height=2)
    save_button.grid(row=2, column=1, pady=10)


# 初始化奖池
def initialize_choice_list():
    global choice_list, settings
    pool_path = settings.get("pool_path", "")
    # 检查奖池路径是否有效
    if not pool_path or not os.path.exists(pool_path):
        messagebox.showerror("错误", "奖池路径无效，请检查设置！")
        return []

    try:
        # 读取奖池文件内容并初始化抽奖列表
        with open(pool_path, 'r', encoding='utf-8') as file:
            choices = file.read().splitlines()
        choice_list = choices.copy()
    except Exception as e:
        # 如果读取失败，显示错误消息框
        messagebox.showerror("错误", f"无法读取奖池文件: {e}")
        return []


# 转盘动画
def roll_animation(choices, winner):
    global rolling
    rolling = True
    # 禁用所有按钮以防止重复点击
    for button in [quick_pick_button, wheel_pick_button, multi_pick_button, settings_button]:
        button.config(state=tk.DISABLED)
    # 模拟30次滚动效果
    for i in range(30):
        if not rolling:
            break
        result_label.config(text=f"滚动中... {random.choice(choices)}")
        root.update()
        time.sleep(0.05 * (i // 10 + 1))  # 滚动速度逐渐变慢
    result_label.config(text=f"抽取结果: {winner}")
    # 启用所有按钮
    for button in [quick_pick_button, wheel_pick_button, multi_pick_button, settings_button]:
        button.config(state=tk.NORMAL)
    rolling = False


# 快速抽取
def quick_pick():
    global choice_list, settings
    # 检查抽奖列表是否为空
    if not choice_list:
        messagebox.showwarning("警告", "抽奖列表为空，请检查文件内容！")
        return

    winner = random.choice(choice_list)
    result_label.config(text=f"抽取结果: {winner}")


# 转盘抽取
def wheel_pick():
    global choice_list, settings, rolling
    # 检查抽奖列表是否为空
    if not choice_list:
        messagebox.showwarning("警告", "抽奖列表为空，请检查文件内容！")
        return
    # 检查是否已经有转盘在滚动
    if rolling:
        messagebox.showwarning("警告", "转盘正在滚动，请稍后再试！")
        return

    winner = random.choice(choice_list)
    roll_animation(choice_list, winner)


# 多人抽取函数（使用 random.sample() 确保无重复）
def multi_pick():
    global choice_list, settings, multi_pick_count_entry

    # 检查抽奖列表是否为空
    if not choice_list:
        messagebox.showwarning("警告", "抽奖列表为空，请检查文件内容！")
        return

    # 获取多人抽取数量
    try:
        multi_pick_count = int(multi_pick_count_entry.get())
        if multi_pick_count < 1:
            raise ValueError
    except ValueError:
        # 如果输入无效，显示错误消息框
        messagebox.showerror("错误", "多人抽取数量无效，请输入有效的数字！")
        return

    # 检查抽取数量是否超过奖池大小
    if multi_pick_count > len(choice_list):
        messagebox.showerror("错误", f"抽取数量不能超过奖池大小（当前奖池大小：{len(choice_list)}）！")
        return

    # 使用 random.sample() 进行无重复抽取
    results = random.sample(choice_list, multi_pick_count)

    # 显示抽取结果
    result_text = "\n".join(results)
    messagebox.showinfo("多人抽取结果", f"抽取结果如下：\n{result_text}")


# 初始化GUI
def init_gui():
    global root, result_label, choice_list, settings, settings_file_path, rolling, multi_pick_count_entry
    # 创建主窗口
    root = tk.Tk()
    root.title("抽奖系统    by晓炙云溪")
    root.geometry("500x500")

    # 标签用于显示结果
    result_label = tk.Label(root, text="请点击按钮开始抽奖", font=("Arial", 16))
    result_label.pack(pady=20)

    # 快速抽取按钮
    global quick_pick_button
    quick_pick_button = tk.Button(root, text="快速抽取", command=quick_pick, font=("Arial", 14), width=15, height=2)
    quick_pick_button.pack(pady=10)

    # 转盘抽取按钮
    global wheel_pick_button
    wheel_pick_button = tk.Button(root, text="转盘抽取", command=wheel_pick, font=("Arial", 14), width=15, height=2)
    wheel_pick_button.pack(pady=10)

    # 多项抽取按钮及数量设置框
    multi_pick_frame = tk.Frame(root)  # 创建一个框架用于放置多项抽取相关组件
    multi_pick_frame.pack(pady=10)  # 将框架添加到主窗口，设置垂直外边距
    global multi_pick_button
    multi_pick_button = tk.Button(multi_pick_frame, text="多项抽取", command=multi_pick, font=("Arial", 14), width=15,
                                  height=2)  # 创建多项抽取按钮
    multi_pick_button.pack(side=tk.LEFT, padx=10)  # 将按钮放置在框架左侧，并设置水平外边距
    multi_pick_count_label = tk.Label(multi_pick_frame, text="数量:", font=("Arial", 12))  # 创建标签，提示用户输入抽取数量
    multi_pick_count_label.pack(side=tk.LEFT, padx=5)  # 将标签放置在框架左侧，并设置水平外边距
    multi_pick_count_entry = tk.Entry(multi_pick_frame, font=("Arial", 12), width=5)  # 创建输入框，用于输入多项抽取的数量
    multi_pick_count_entry.insert(0, settings.get("multi_pick_count", "1"))  # 设置输入框的默认值为配置中的多项抽取数量
    multi_pick_count_entry.pack(side=tk.LEFT)  # 将输入框放置在框架左侧

    # 设置按钮
    global settings_button
    settings_button = tk.Button(root, text="设置", command=open_settings, font=("Arial", 14), width=15, height=2)
    settings_button.pack(pady=10)

    # 读取设置
    settings_file_path = "settings.txt"
    settings = read_settings(settings_file_path)

    # 初始化奖池
    initialize_choice_list()

    # 定义全局变量，防止转盘重复点击
    rolling = False

    # 捕获窗口关闭事件，修复退出时的报错
    def on_closing():
        global rolling
        rolling = False  # 确保滚动动画已停止
        root.quit()  # 优雅地退出程序

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


if __name__ == "__main__":
    choice_list = []  # 全局变量存储抽奖列表
    settings = {}  # 全局变量存储设置
    init_gui()
