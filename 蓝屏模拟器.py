import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import sys
import subprocess

# 经典蓝屏颜色
BLUE_SCREEN_COLOR = '#012456'
TEXT_COLOR = '#FFFFFF'

# 蓝屏错误库
BLUE_SCREENS = {
    "SYSTEM_THREAD_EXCEPTION_NOT_HANDLED": {
        "code": "0x1000007E",
        "description": "系统线程遇到未处理的异常。\n这通常是由有缺陷的硬件或软件驱动程序引起的。",
        "common_cause": "显卡/声卡等外设驱动程序不兼容或损坏。"
    },
    "IRQL_NOT_LESS_OR_EQUAL": {
        "code": "0x0000000A",
        "description": "驱动程序尝试访问其无权访问的内存地址。\n这通常是一个非常低级的驱动程序错误。",
        "common_cause": "新安装的硬件驱动程序、有缺陷的防病毒软件或损坏的系统服务。"
    },
    "CRITICAL_PROCESS_DIED": {
        "code": "0x000000EF",
        "description": "一个对系统运行至关重要的进程已意外终止。",
        "common_cause": "关键系统文件损坏、硬盘错误或恶意软件感染。"
    }
}

class AdvancedBlueScreenSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("高级蓝屏模拟器 v3.0 - 带惊慌检测")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # 变量初始化
        self.bs_window = None
        self.alt_pressed = False
        self.shift_pressed = False
        self.exit_countdown = 10
        self.countdown_active = False
        self.last_activity_time = time.time()  # 最后活动时间
        self.panic_check_active = False  # 惊慌检测是否激活
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title = ttk.Label(main_frame, text="🖥️ 高级蓝屏模拟器 v3.0", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # 版本说明
        subtitle = ttk.Label(main_frame, 
                           text="新增功能: 3分钟无操作检测 + 惊慌提示窗口", 
                           font=("Arial", 10), foreground="blue")
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # 第一部分：Python模拟器
        sim_frame = ttk.LabelFrame(main_frame, text="🎭 Python蓝屏模拟器", padding="15")
        sim_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(sim_frame, text="选择蓝屏错误类型:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.error_var = tk.StringVar()
        self.error_combo = ttk.Combobox(sim_frame, textvariable=self.error_var, 
                                      state="readonly", width=65)
        self.error_combo['values'] = list(BLUE_SCREENS.keys())
        self.error_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.error_combo.current(0)
        
        # 预览区域
        preview_frame = ttk.Frame(sim_frame)
        preview_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.preview_text = tk.Text(preview_frame, height=6, width=75, 
                                   bg="#F0F0F0", relief=tk.FLAT, wrap=tk.WORD)
        self.preview_text.pack()
        self.update_preview()
        
        # 模拟器控制按钮
        btn_frame = ttk.Frame(sim_frame)
        btn_frame.grid(row=3, column=0, pady=(5, 0))
        ttk.Button(btn_frame, text="🚀 启动蓝屏模拟", 
                  command=self.launch_python_simulator, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❓ 退出说明", 
                  command=self.show_exit_help, width=15).pack(side=tk.LEFT, padx=5)
        
        # 第二部分：BAT生成器
        bat_frame = ttk.LabelFrame(main_frame, text="⚙️ BAT脚本生成器", padding="15")
        bat_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(bat_frame, text="为BAT脚本选择错误类型:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.bat_error_var = tk.StringVar()
        self.bat_error_combo = ttk.Combobox(bat_frame, textvariable=self.bat_error_var,
                                          state="readonly", width=65)
        self.bat_error_combo['values'] = list(BLUE_SCREENS.keys())
        self.bat_error_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.bat_error_combo.current(0)
        
        # BAT文件路径选择
        path_frame = ttk.Frame(bat_frame)
        path_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(path_frame, text="保存路径:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=os.path.join(os.getcwd(), "blue_screen.bat"))
        ttk.Entry(path_frame, textvariable=self.path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="浏览...", 
                  command=self.browse_path).pack(side=tk.LEFT)
        
        # BAT生成按钮
        ttk.Button(bat_frame, text="⚙️ 生成BAT脚本", 
                  command=self.generate_bat_script, width=20).pack(pady=(5,0))
        
        # 第三部分：惊慌检测设置
        panic_frame = ttk.LabelFrame(main_frame, text="😱 惊慌检测设置", padding="15")
        panic_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 检测时间设置
        time_frame = ttk.Frame(panic_frame)
        time_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(time_frame, text="无操作检测时间:").pack(side=tk.LEFT)
        self.panic_time_var = tk.StringVar(value="180")
        time_spinbox = ttk.Spinbox(time_frame, from_=30, to=600, textvariable=self.panic_time_var,
                                 width=8)
        time_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(time_frame, text="秒 (默认:180秒=3分钟)").pack(side=tk.LEFT)
        
        # 提示消息设置
        ttk.Label(panic_frame, text="惊慌提示消息:").grid(row=1, column=0, sticky=tk.W, pady=(0,5))
        
        self.panic_msg_var = tk.StringVar(value="别慌！这不是真的蓝屏死机！\n\n这只是一个模拟程序。\n你的电脑完全没有问题！\n\n点击下面的按钮安全退出。")
        panic_msg_entry = tk.Text(panic_frame, height=4, width=65, wrap=tk.WORD)
        panic_msg_entry.insert(1.0, self.panic_msg_var.get())
        panic_msg_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.panic_msg_entry = panic_msg_entry
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪 - 选择功能并开始")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              font=("Arial", 9), foreground="gray",
                              relief=tk.SUNKEN, padding=5)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        # 安全提示
        ttk.Label(main_frame, 
                 text="⚠️ 注意: 所有功能均为模拟，不会对系统造成实际伤害。仅用于娱乐目的。",
                 font=("Arial", 8), foreground="orange").grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # 绑定事件
        self.error_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        self.bat_error_combo.bind('<<ComboboxSelected>>', lambda e: self.update_bat_preview())
    
    def update_preview(self):
        """更新Python模拟器预览"""
        selected = self.error_var.get()
        info = BLUE_SCREENS[selected]
        text = f"错误代码: {info['code']}\n描述: {info['description']}\n常见原因: {info['common_cause']}"
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, text)
    
    def update_bat_preview(self):
        """更新BAT预览"""
        selected = self.bat_error_var.get()
        self.status_var.set(f"将生成针对 {selected} 错误的BAT脚本")
    
    def browse_path(self):
        """选择BAT文件保存路径"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".bat",
            filetypes=[("批处理文件", "*.bat"), ("所有文件", "*.*")],
            initialfile="blue_screen.bat"
        )
        if filename:
            self.path_var.set(filename)
    
    def launch_python_simulator(self):
        """启动Python蓝屏模拟器"""
        selected = self.error_var.get()
        
        # 获取惊慌检测设置
        try:
            panic_timeout = int(self.panic_time_var.get())
        except:
            panic_timeout = 180
            self.panic_time_var.set("180")
        
        panic_message = self.panic_msg_entry.get(1.0, tk.END).strip()
        
        # 在新线程中启动模拟器
        thread = threading.Thread(target=self.run_python_simulation, 
                                 args=(selected, panic_timeout, panic_message))
        thread.daemon = True
        thread.start()
        
        self.status_var.set(f"蓝屏模拟已启动 (惊慌检测: {panic_timeout}秒)")
        messagebox.showinfo("提示", 
                          f"蓝屏模拟器已启动！\n\n退出方法:\n"
                          f"1. 同时按住 ALT+SHIFT 10秒钟\n"
                          f"2. 或等待 {panic_timeout} 秒触发惊慌提示\n"
                          f"3. 或按 Ctrl+Alt+Del 强制关闭")
    
    def run_python_simulation(self, error_type, panic_timeout, panic_message):
        """运行Python蓝屏模拟"""
        info = BLUE_SCREENS[error_type]
        
        # 创建蓝屏窗口
        self.bs_window = tk.Toplevel(self.root)
        self.bs_window.title("蓝屏死机")
        self.bs_window.attributes('-fullscreen', True, '-topmost', True)
        self.bs_window.configure(bg=BLUE_SCREEN_COLOR)
        
        # 移除窗口装饰
        try:
            self.bs_window.overrideredirect(True)
        except:
            pass
        
        # 初始化活动时间
        self.last_activity_time = time.time()
        
        # 获取屏幕尺寸
        screen_width = self.bs_window.winfo_screenwidth()
        screen_height = self.bs_window.winfo_screenheight()
        
        # 创建画布
        canvas = tk.Canvas(self.bs_window, bg=BLUE_SCREEN_COLOR, 
                         highlightthickness=0, cursor='none')
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绘制蓝屏内容
        self.draw_blue_screen(canvas, screen_width, screen_height, info, error_type, panic_timeout)
        
        # 绑定键盘事件
        self.bs_window.bind('<KeyPress>', self.on_key_press)
        self.bs_window.bind('<KeyRelease>', self.on_key_release)
        
        # 启动退出检测线程
        exit_thread = threading.Thread(target=self.exit_detection_loop)
        exit_thread.daemon = True
        exit_thread.start()
        
        # 启动惊慌检测线程
        panic_thread = threading.Thread(target=self.panic_detection_loop,
                                       args=(panic_timeout, panic_message))
        panic_thread.daemon = True
        panic_thread.start()
        
        # 启动窗口
        self.bs_window.mainloop()
    
    def draw_blue_screen(self, canvas, width, height, info, error_type, panic_timeout):
        """绘制蓝屏界面内容"""
        # 哭脸表情
        canvas.create_text(width/2, height*0.15, text=":(", 
                         font=("Segoe UI", 120, "bold"), fill=TEXT_COLOR, anchor=tk.CENTER)
        
        # 主标题
        canvas.create_text(width/2, height*0.15 + 140, 
                         text="你的设备遇到问题，需要重启。",
                         font=("Segoe UI", 36), fill=TEXT_COLOR, anchor=tk.CENTER)
        
        # 错误信息
        info_x = width * 0.1
        info_y = height * 0.4
        line_height = 32
        
        lines = [
            f"我们只收集某些错误信息，然后你可以重新启动。",
            f"完成 0%",
            "",
            f"如果想了解更多信息，则可以稍后在线搜索此错误: {info['code']}",
            "",
            info['description'],
            "",
            f"** 常见原因: {info['common_cause']}",
            "",
            "*** 技术支持信息:",
            f"*** 停止代码: {info['code']}",
            f"*** 失败的操作: {error_type}",
            "",
            f"*** 退出提示1: 同时按住 ALT+SHIFT {self.exit_countdown}秒",
            f"*** 退出提示2: 无操作 {panic_timeout//60} 分钟后显示帮助",
            f"*** 最后活动: {time.strftime('%H:%M:%S')}"
        ]
        
        for i, line in enumerate(lines):
            y = info_y + (i * line_height)
            canvas.create_text(info_x, y, text=line, 
                             font=("Segoe UI", 18), fill=TEXT_COLOR, anchor=tk.W)
        
        # 进度条
        bar_width = width * 0.8
        bar_height = 4
        bar_x = (width - bar_width) / 2
        bar_y = height * 0.85
        
        canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height, 
                              fill="#2A5CAA", outline="")
        
        # 进度动画
        self.animate_progress(canvas, bar_x, bar_y, bar_width, info_x, info_y, line_height)
        
        # 保存画布引用
        self.bs_canvas = canvas
        self.bs_info_x = info_x
        self.bs_info_y = info_y
        self.bs_line_height = line_height
    
    def animate_progress(self, canvas, bar_x, bar_y, bar_width, info_x, info_y, line_height):
        """进度条动画"""
        def update_progress(percent=0):
            if percent <= 100 and self.bs_window and self.bs_window.winfo_exists():
                # 更新百分比文本
                canvas.delete("percent_text")
                canvas.create_text(info_x, info_y + line_height, 
                                 text=f"完成 {int(percent)}%",
                                 font=("Segoe UI", 18), fill=TEXT_COLOR, 
                                 anchor=tk.W, tags="percent_text")
                
                # 更新进度条光标
                cursor_x = bar_x + (bar_width * (percent / 100))
                canvas.delete("cursor")
                canvas.create_rectangle(cursor_x-2, bar_y-8, cursor_x+2, bar_y+12,
                                      fill=TEXT_COLOR, outline="", tags="cursor")
                
                # 更新最后活动时间显示
                canvas.delete("last_activity")
                last_activity_text = f"*** 最后活动: {time.strftime('%H:%M:%S')}"
                canvas.create_text(info_x, info_y + (15 * line_height), 
                                 text=last_activity_text,
                                 font=("Segoe UI", 18), fill=TEXT_COLOR, 
                                 anchor=tk.W, tags="last_activity")
                
                # 继续动画
                self.bs_window.after(100, update_progress, percent + 0.3)
        
        update_progress()
    
    def on_key_press(self, event):
        """键盘按下事件 - 更新活动时间"""
        self.last_activity_time = time.time()
        
        if event.keysym == 'Alt_L' or event.keysym == 'Alt_R':
            self.alt_pressed = True
        elif event.keysym == 'Shift_L' or event.keysym == 'Shift_R':
            self.shift_pressed = True
        
        # 检查是否同时按下ALT+SHIFT
        if self.alt_pressed and self.shift_pressed and not self.countdown_active:
            self.start_exit_countdown()
    
    def on_key_release(self, event):
        """键盘释放事件 - 更新活动时间"""
        self.last_activity_time = time.time()
        
        if event.keysym == 'Alt_L' or event.keysym == 'Alt_R':
            self.alt_pressed = False
        elif event.keysym == 'Shift_L' or event.keysimp == 'Shift_R':
            self.shift_pressed = False
        
        # 如果任一键释放，重置倒计时
        if not (self.alt_pressed and self.shift_pressed):
            self.exit_countdown = 10
            self.countdown_active = False
    
    def start_exit_countdown(self):
        """开始退出倒计时"""
        self.countdown_active = True
        countdown_thread = threading.Thread(target=self.run_exit_countdown)
        countdown_thread.daemon = True
        countdown_thread.start()
    
    def run_exit_countdown(self):
        """运行退出倒计时"""
        original_countdown = self.exit_countdown
        
        while self.exit_countdown > 0 and self.alt_pressed and self.shift_pressed:
            time.sleep(1)
            self.exit_countdown -= 1
            
            # 在蓝屏上显示倒计时
            if self.bs_window and self.bs_window.winfo_exists():
                try:
                    self.bs_canvas.delete("exit_countdown")
                    countdown_text = f"*** ALT+SHIFT倒计时: {self.exit_countdown}秒"
                    self.bs_canvas.create_text(self.bs_info_x, self.bs_info_y + (13 * self.bs_line_height), 
                                             text=countdown_text,
                                             font=("Segoe UI", 18), fill="#FFFF00",  # 黄色强调
                                             anchor=tk.W, tags="exit_countdown")
                except:
                    pass
        
        # 如果倒计时结束，关闭窗口
        if self.exit_countdown <= 0 and self.bs_window and self.bs_window.winfo_exists():
            self.bs_window.after(0, self.bs_window.destroy)
            self.status_var.set("蓝屏模拟已通过ALT+SHIFT退出")
        
        # 重置变量
        self.exit_countdown = original_countdown
        self.countdown_active = False
    
    def panic_detection_loop(self, panic_timeout, panic_message):
        """惊慌检测循环"""
        self.panic_check_active = True
        
        while self.panic_check_active and self.bs_window and self.bs_window.winfo_exists():
            current_time = time.time()
            inactive_time = current_time - self.last_activity_time
            
            # 检查是否达到惊慌检测时间
            if inactive_time >= panic_timeout:
                # 触发惊慌提示
                self.bs_window.after(0, self.show_panic_window, panic_message)
                self.panic_check_active = False
                break
            
            # 在蓝屏上显示倒计时
            if self.bs_window and self.bs_window.winfo_exists():
                try:
                    remaining = panic_timeout - int(inactive_time)
                    mins = remaining // 60
                    secs = remaining % 60
                    
                    self.bs_canvas.delete("panic_countdown")
                    panic_text = f"*** 惊慌检测: {mins:02d}:{secs:02d} 后显示帮助"
                    self.bs_canvas.create_text(self.bs_info_x, self.bs_info_y + (14 * self.bs_line_height), 
                                             text=panic_text,
                                             font=("Segoe UI", 18), fill="#FFA500",  # 橙色强调
                                             anchor=tk.W, tags="panic_countdown")
                except:
                    pass
            
            time.sleep(1)  # 每秒检查一次
    
    def show_panic_window(self, message):
        """显示惊慌提示窗口"""
        if not self.bs_window or not self.bs_window.winfo_exists():
            return
        
        # 创建置顶提示窗口
        panic_window = tk.Toplevel(self.bs_window)
        panic_window.title("别慌！这是模拟程序！")
        panic_window.attributes('-topmost', True)
        
        # 居中显示
        window_width = 500
        window_height = 350
        screen_width = panic_window.winfo_screenwidth()
        screen_height = panic_window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        panic_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        panic_window.resizable(False, False)
        
        # 设置窗口样式
        panic_window.configure(bg='#FFFFE0')  # 浅黄色背景
        panic_window.iconbitmap(default='')  # 清除图标
        
        # 添加内容
        # 标题
        title_label = tk.Label(panic_window, text="😅 别慌！这不是真的蓝屏！", 
                              font=("Arial", 20, "bold"), bg='#FFFFE0', fg='#FF0000')
        title_label.pack(pady=20)
        
        # 图标
        icon_label = tk.Label(panic_window, text="🖥️⚠️", 
                            font=("Arial", 40), bg='#FFFFE0')
        icon_label.pack(pady=10)
        
        # 消息内容
        msg_frame = tk.Frame(panic_window, bg='#FFFFE0')
        msg_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        message_label = tk.Label(msg_frame, text=message, 
                               font=("Arial", 12), bg='#FFFFE0', 
                               fg='#000000', justify=tk.LEFT, wraplength=450)
        message_label.pack()
        
        # 退出按钮
        button_frame = tk.Frame(panic_window, bg='#FFFFE0')
        button_frame.pack(pady=20)
        
        exit_button = tk.Button(button_frame, text="✅ 点击这里安全退出", 
                              command=lambda: self.exit_panic_mode(panic_window),
                              font=("Arial", 14, "bold"), 
                              bg='#4CAF50', fg='white',
                              padx=30, pady=10, cursor='hand2')
        exit_button.pack()
        
        # 关闭整个程序按钮
        full_exit_button = tk.Button(button_frame, text="完全退出程序", 
                                   command=self.exit_full_program,
                                   font=("Arial", 10), 
                                   bg='#FF5722', fg='white',
                                   padx=10, pady=5)
        full_exit_button.pack(pady=10)
        
        # 提示标签
        hint_label = tk.Label(panic_window, 
                            text="提示: 关闭此窗口后，蓝屏模拟仍会继续运行。",
                            font=("Arial", 9), bg='#FFFFE0', fg='#666666')
        hint_label.pack(pady=10)
    
    def exit_panic_mode(self, panic_window):
        """退出惊慌模式"""
        panic_window.destroy()
        self.status_var.set("已显示惊慌提示窗口")
    
    def exit_full_program(self):
        """完全退出程序"""
        if self.bs_window and self.bs_window.winfo_exists():
            self.bs_window.destroy()
        self.root.quit()
    
    def exit_detection_loop(self):
        """退出检测循环"""
        while self.bs_window and self.bs_window.winfo_exists():
            time.sleep(0.1)
        self.panic_check_active = False
    
    def show_exit_help(self):
        """显示退出帮助"""
        try:
            panic_timeout = int(self.panic_time_var.get())
        except:
            panic_timeout = 180
        
        messagebox.showinfo("退出说明",
                          "退出蓝屏模拟器的方法:\n\n"
                          f"1. 同时按住 ALT 和 SHIFT 键10秒钟\n"
                          f"2. 无操作 {panic_timeout} 秒后自动显示帮助窗口\n"
                          "3. 按 Ctrl+Alt+Delete 调出安全菜单\n"
                          "4. 在惊慌提示窗口中点击退出按钮\n\n"
                          "提示: 请确保蓝屏窗口是当前活动窗口。")
    
    def generate_bat_script(self):
        """生成BAT蓝屏脚本"""
        error_type = self.bat_error_var.get()
        info = BLUE_SCREENS[error_type]
        bat_path = self.path_var.get()
        
        # 获取惊慌检测设置
        try:
            panic_timeout = int(self.panic_time_var.get())
        except:
            panic_timeout = 180
        
        panic_message = self.panic_msg_entry.get(1.0, tk.END).strip()
        
        # 创建Python脚本内容（包含惊慌检测）
        python_code = f'''import tkinter as tk
import time
import threading

BLUE_SCREEN_COLOR = '#012456'
TEXT_COLOR = '#FFFFFF'

class BlueScreenSimulator:
    def __init__(self):
        self.window = None
        self.last_activity = time.time()
        self.panic_timeout = {panic_timeout}
        self.panic_message = """{panic_message}"""
        
    def create_blue_screen(self):
        self.window = tk.Tk()
        self.window.title("蓝屏死机")
        self.window.attributes('-fullscreen', True, '-topmost', True)
        self.window.configure(bg=BLUE_SCREEN_COLOR)
        
        try:
            self.window.overrideredirect(True)
        except:
            pass
        
        # 绑定键盘事件
        self.window.bind('<KeyPress>', self.on_activity)
        self.window.bind('<KeyRelease>', self.on_activity)
        
        # 画布和内容
        canvas = tk.Canvas(self.window, bg=BLUE_SCREEN_COLOR, highlightthickness=0, cursor='none')
        canvas.pack(fill=tk.BOTH, expand=True)
        
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()
        
        # 绘制内容
        canvas.create_text(width/2, height*0.15, text=":(", 
                          font=("Arial", 120, "bold"), fill=TEXT_COLOR, anchor=tk.CENTER)
        canvas.create_text(width/2, height*0.15+140, 
                          text="你的设备遇到问题，需要重启。",
                          font=("Arial", 36), fill=TEXT_COLOR, anchor=tk.CENTER)
        
        info_x = width * 0.1
        info_y = height * 0.4
        
        lines = [
            "错误代码: {code}",
            "错误类型: {type}",
            "",
            "描述: {desc}",
            "",
            "常见原因: {cause}",
            "",
            f"*** 无操作 {panic_timeout//60} 分钟后显示帮助",
            "*** 按 Alt+F4 或 Ctrl+Alt+Del 退出"
        ]
        
        desc = info['description'].replace('\\n', ' ')
        cause = info['common_cause']
        
        for i, line in enumerate(lines):
            text = line.format(code=info['code'], type=error_type, 
                              desc=desc, cause=cause)
            canvas.create_text(info_x, info_y + (i*35), text=text,
                              font=("Arial", 18), fill=TEXT_COLOR, anchor=tk.W)
        
        # 启动惊慌检测
        panic_thread = threading.Thread(target=self.panic_detection)
        panic_thread.daemon = True
        panic_thread.start()
        
        # 退出快捷键
        def exit_app(event=None):
            self.window.destroy()
        
        self.window.bind('<Alt_L><F4>', exit_app)
        self.window.bind('<Control_L><Alt_L><Delete>', exit_app)
        
        self.window.mainloop()
    
    def on_activity(self, event=None):
        self.last_activity = time.time()
    
    def panic_detection(self):
        while self.window and self.window.winfo_exists():
            if time.time() - self.last_activity > self.panic_timeout:
                self.window.after(0, self.show_panic_message)
                break
            time.sleep(1)
    
    def show_panic_message(self):
        panic_win = tk.Toplevel(self.window)
        panic_win.title("别慌！")
        panic_win.attributes('-topmost', True)
        panic_win.geometry("400x300")
        panic_win.configure(bg='#FFFFE0')
        
        tk.Label(panic_win, text="别慌！这是模拟程序！", 
                font=("Arial", 16, "bold"), bg='#FFFFE0').pack(pady=20)
        
        message_lines = self.panic_message.split('\\n')
        for line in message_lines:
            tk.Label(panic_win, text=line, font=("Arial", 12), 
                    bg='#FFFFE0').pack()
        
        tk.Button(panic_win, text="安全退出", 
                 command=self.window.destroy,
                 font=("Arial", 14), bg='#4CAF50', fg='white').pack(pady=20)

if __name__ == "__main__":
    simulator = BlueScreenSimulator()
    simulator.create_blue_screen()
'''
        
        # 创建BAT文件内容
        bat_content = f'''@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    蓝屏模拟脚本 - {error_type}
echo    错误代码: {info['code']}
echo    惊慌检测: {panic_timeout}秒后触发
echo ========================================
echo.
echo 注意: 这是一个模拟程序，不会对系统造成伤害。
echo.
echo 按 Ctrl+C 取消运行，按任意键继续...
pause >nul

REM 创建临时Python脚本
echo {python_code.replace('\n', '\necho ')} > "%TEMP%\\bs_simulator.py"

echo.
echo 正在启动蓝屏模拟器...
echo 请等待...

REM 运行Python脚本
python "%TEMP%\\bs_simulator.py"

REM 清理
del "%TEMP%\\bs_simulator.py" >nul 2>&1

echo.
echo 蓝屏模拟已结束。
echo 按任意键退出...
pause >nul
'''
        
        try:
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            self.status_var.set(f"BAT脚本已生成: {bat_path}")
            
            # 询问是否运行
            if messagebox.askyesno("成功", 
                                  f"BAT脚本已生成到:\n{bat_path}\n\n"
                                  f"包含 {panic_timeout} 秒惊慌检测功能\n"
                                  f"是否立即运行测试？"):
                subprocess.Popen(f'start cmd /k "{bat_path}"', shell=True)
                
        except Exception as e:
            messagebox.showerror("错误", f"生成BAT文件失败:\n{str(e)}")

# 运行主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedBlueScreenSimulator(root)
    root.mainloop()