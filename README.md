# ⏰ 定时提醒

一个轻量的 Windows 桌面定时提醒工具，支持一次性提醒和重复提醒，可最小化到系统托盘。

## ✨ 功能特性

- **一次性提醒** — 指定时间点弹窗提醒
- **重复提醒** — 从指定时间起，每 30 分钟或每 1 小时循环提醒
- **系统托盘** — 关闭窗口后最小化到托盘，右键图标可恢复或退出
- **提醒弹窗** — 置顶弹窗 + 声音提示，确保不遗漏
- **数据持久化** — 提醒数据自动保存，重启应用后自动恢复

## 📸 截图

<img width="964" height="1104" alt="image" src="https://github.com/user-attachments/assets/1eee60fe-40a9-477c-88fe-5568770b0ecd" />


## 🚀 使用方法

### 直接运行（无需 Python 环境）

从 [Releases](../../releases) 下载 `定时提醒.zip`，解压后双击 `定时提醒.exe` 即可运行。

### 从源码运行

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行
python reminder_app.py
```

### 打包为 exe

```bash
# 激活虚拟环境后
pyinstaller --onedir --windowed --name "定时提醒" reminder_app.py
```

打包后的应用位于 `dist/定时提醒/` 文件夹，入口为 `dist/定时提醒/定时提醒.exe`。

## 🕐 重复提醒示例

| 设定时间 | 重复间隔 | 提醒时间 |
|----------|----------|----------|
| 14:25 | 每 30 分钟 | 14:25、14:55、15:25、15:55 … |
| 09:00 | 每 1 小时 | 09:00、10:00、11:00 … |
| 08:30 | 仅一次 | 08:30（仅触发一次） |

## 🛠 技术栈

- **Python 3** + **tkinter**（GUI）
- **pystray**（系统托盘）
- **Pillow**（托盘图标生成）
- **PyInstaller**（打包 exe）

## ⚖️ 许可证

[MIT License](LICENSE)

---

> 💡 本项目代码由 AI 辅助生成。
