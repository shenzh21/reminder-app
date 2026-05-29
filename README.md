# ⏰ 定时提醒

一个轻量的 Windows 桌面定时提醒工具，支持一次性提醒和重复提醒，可最小化到系统托盘。

## ✨ 功能特性

- **一次性提醒** — 指定时间点弹窗提醒
- **重复提醒** — 从指定时间起，每 30 分钟或每 1 小时循环提醒
- **系统托盘** — 关闭窗口后最小化到托盘，右键图标可恢复或退出
- **提醒弹窗** — 置顶弹窗 + 声音提示，确保不遗漏
- **数据持久化** — 提醒数据自动保存，重启应用后自动恢复
- **暂停/恢复** — 可暂停提醒而不删除，恢复后自动计算下次触发时间
- **音效开关** — 每条提醒可单独控制是否播放提示音
- **弹窗自动关闭** — 提醒弹窗 3 分钟无操作自动关闭，支持 Enter / 空格键快速关闭
- **托盘单击** — 单击托盘图标即可恢复主窗口

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
pyinstaller --clean --onedir --windowed --name "定时提醒" ^
  --exclude-module PIL.BufrStubImagePlugin ^
  --exclude-module PIL.FitsStubImagePlugin ^
  --exclude-module PIL.GribStubImagePlugin ^
  --exclude-module PIL.Hdf5StubImagePlugin ^
  --exclude-module PIL.McIdasImagePlugin ^
  --exclude-module PIL.MicImagePlugin ^
  --exclude-module PIL.SpiderImagePlugin ^
  --exclude-module PIL.SgiImagePlugin ^
  --exclude-module PIL.FpxImagePlugin ^
  --exclude-module PIL.IcnsImagePlugin ^
  --exclude-module PIL.PalmImagePlugin ^
  --exclude-module PIL.PcdImagePlugin ^
  --exclude-module PIL.PcxImagePlugin ^
  --exclude-module PIL.PsdImagePlugin ^
  --exclude-module PIL.TgaImagePlugin ^
  --exclude-module PIL.XpmImagePlugin ^
  --exclude-module PIL.XbmImagePlugin ^
  --exclude-module PIL.IptcImagePlugin ^
  --exclude-module PIL.ImtImagePlugin ^
  --exclude-module PIL.DcxImagePlugin ^
  --exclude-module PIL.EpsImagePlugin ^
  --exclude-module PIL.FliImagePlugin ^
  --exclude-module PIL.FtexImagePlugin ^
  --exclude-module PIL.GbrImagePlugin ^
  --exclude-module PIL.ImImagePlugin ^
  --exclude-module PIL.Jpeg2KImagePlugin ^
  --exclude-module PIL.MpegImagePlugin ^
  --exclude-module PIL.MpoImagePlugin ^
  --exclude-module PIL.PixarImagePlugin ^
  --exclude-module PIL.PpmImagePlugin ^
  --exclude-module PIL.PdfImagePlugin ^
  --exclude-module tkinter.test ^
  --exclude-module unittest ^
  --exclude-module pydoc ^
  --exclude-module curses ^
  reminder_app.py
```

打包后的应用位于 `dist/定时提醒/` 文件夹，入口为 `dist/定时提醒/定时提醒.exe`。

> 📌 **打包说明**
> - 使用 `--onedir` 模式（非 `--onefile`），启动更快，无需每次解压临时目录
> - 排除了不需要的 Pillow 图片格式插件和标准库模块，减小体积
> - 图标已预嵌入为 base64，运行时无需 `ImageDraw` 模块
> - 如需分发包，将 `dist/定时提醒/` 文件夹压缩为 zip 上传即可

## 🕐 重复提醒示例

| 设定时间 | 重复间隔 | 提醒时间 |
|----------|----------|----------|
| 14:25 | 每 30 分钟 | 14:25、14:55、15:25、15:55 … |
| 09:00 | 每 1 小时 | 09:00、10:00、11:00 … |
| 08:30 | 仅一次 | 08:30（仅触发一次） |

## 🛠 技术栈

### 桌面版
- **Python 3** + **tkinter**（GUI）
- **pystray**（系统托盘）
- **Pillow**（托盘图标生成）
- **PyInstaller**（打包 exe）

### Web 版
- **HTML + CSS + JavaScript**（纯前端，无后端依赖）
- **localStorage**（本地数据持久化）
- **Web Audio API**（声音提醒）
- **Notification API**（浏览器通知）

---

## 🌐 Web 版

纯前端实现，一个 HTML 文件即可运行，无需服务器。

### 快速使用

1. 直接在浏览器中打开 `index.html`
2. 或部署到任意静态托管服务（GitHub Pages、Netlify、Vercel 等）

### 功能特性

- ✅ 一次性提醒和重复提醒
- ✅ 弹窗 + 声音提醒
- ✅ 浏览器通知（需授权）
- ✅ 数据保存在浏览器本地
- ✅ 默认自带两个提醒：25分（[bell]）和整点（[bell]）
- ✅ 支持移动端访问

---

## ⚖️ 许可证

[MIT License](LICENSE)

---

> 💡 本项目代码由 AI 辅助生成。
