# 仓鼠美叽 · 桌面宠物 MeiJiPet

一只趴在你 Windows 桌面上的白色小仓鼠「美叽」——基于 **PySide6 / Qt** 的真·透明桌面宠物。它播放**真实的 GIF 表情动画**（逐像素 alpha 透明、无边框、置顶悬浮），会自己发呆、走动、撒娇、走开又回来，也能被点击、拖拽、喂食。

![platform](https://img.shields.io/badge/platform-Windows%2010%2F11%20x64-4B8BBE)
![code license](https://img.shields.io/badge/code-MIT-6db33f)
![assets](https://img.shields.io/badge/assets-%C2%A9%20%E7%BE%8E%E5%8F%BD%E5%92%8C%E5%A4%A7%E9%BC%A0%20%C2%B7%20%E9%9D%9E%E5%95%86%E4%B8%9A-db4437)

| 待机 | 开心 | 耍帅 | 吃东西 | 思考 | 抱抱 |
| :--: | :--: | :--: | :--: | :--: | :--: |
| ![idle](assets/150/meji_idle_t.gif) | ![happy](assets/150/meji_happy_t.gif) | ![cool](assets/150/meji_cool_t.gif) | ![eat](assets/150/meji_eat_t.gif) | ![think](assets/150/meji_think_t.gif) | ![hug](assets/150/meji_hug_t.gif) |

---

## 素材署名与版权（请先阅读）

桌面宠物的**程序代码为作者自制**；但仓鼠「美叽」这一形象与全部表情 GIF，版权归原创 IP **美叽和大鼠** 所有：

- 原作者：**@美叽和大鼠**（全网同名）
- 抖音号：`52635980092`　·　Bilibili：[UID 386231630](https://space.bilibili.com/386231630)
- 角色家族：灰耗子「大鼠」、仓鼠「美叽」、黄狗「旺财」、小猫「砂糖」

本仓库是**非盈利的个人学习 / 二创项目**，已按作者要求在此**显著注明出处**（而非写在角落）。素材**禁止商业用途与私自印刷**；自用头像 / 壁纸 / 表情可以，非商业转载与二创需注明作者。如原作者认为不妥，联系后会立即删除相关素材。

> 代码部分以 [MIT License](LICENSE) 开放；`assets/` 目录中的美术素材**不适用** MIT，版权归原作者所有。

---

## 功能特性

- **真 GIF 动画**：用 `QMovie` 直接播放 GIF，40 个表情全部是会动的循环动画（0.7 倍速，更悠闲自然），不是静态图伪装。
- **逐像素透明**：`WA_TranslucentBackground` + 分层窗口，边缘干净、没有色键（紫边 / 黑边）问题，可任意叠加在桌面和其他窗口上。
- **点击切换表情**：单击美叽就会随机换一个表情并**一直停留**，直到你再次点击或它自己到点轮换。
- **自动生活节奏**：无人打扰时每隔约 10–15 分钟自己换个状态发呆；偶发稀有事件「**走开一会儿再回来**」，以及极小范围的来回挪动，不干扰正常工作。
- **可互动**：双击喂食、拖拽（会露出不爽表情）、右键菜单逗它、摸摸头掉爱心、最多召唤 5 只。
- **隐式状态系统**：有饥饿度 / 心情值，会影响它的自发动作（饿了委屈、心情不好闹脾气），但**不显示任何数值条**，全靠动作和表情体会。
- **四档大小 + 五档活跃度**：右键菜单随时切换，设置自动保存。
- **系统托盘 + 右键菜单**：喂瓜子、摸摸头、召唤、退出；无台词气泡、不弹通知、**不开机自启**。
- **单文件 / 安装包两种分发**：可打包成免安装绿色 EXE，也可用 Inno Setup 生成带桌面快捷方式和卸载器的正规安装包（每用户安装，免 UAC）。

## 交互方式

| 操作 | 效果 |
| --- | --- |
| **单击** | 随机切换到一个新表情并常驻停留（39 个可循环表情，不含「走开」） |
| **双击** | 喂食（吃饭 / 沙拉 / 喝东西），结束后回到你刚选的表情 |
| **按住拖拽** | 把美叽拖到任意位置，拖动时露出不爽脸，松手回到当前表情 |
| **右键美叽** | 菜单：逗它（开心 / 睡觉 / 喂食 / 惹哭）、再召唤一只、大小、活跃度、退出 |
| **托盘左键菜单** | 喂瓜子、摸摸头（掉爱心）、召唤一只、退出 |

## 行为与状态说明

- **自动轮换**：间隔随「活跃度」变化，约 10–15 分钟一次；点击会重新计时。
- **稀有「走开再回来」**：约 5% 概率自己走出屏幕、消失几秒再溜达回来。
- **小范围走动**：换表情后偶发在原地 ±80px 内小幅挪动，不会满屏乱跑。
- **饥饿 / 心情**：随时间缓慢下降；喂食补充饥饿、摸摸头提升心情；过低时会自发出现委屈 / 生气类表情。数值完全隐藏。
- **多只**：最多 5 只，各自独立行动；改大小 / 活跃度会同步给所有个体。

---

## 安装与使用

### 方式一：安装包（推荐给普通用户）

1. 到 [Releases](../../releases) 下载 `MejiPet_Setup_v*.exe`。
2. 双击安装（中文向导，**无需管理员权限**），默认创建桌面与开始菜单快捷方式。
3. 从桌面快捷方式「仓鼠美叽」启动；卸载用开始菜单里的「卸载仓鼠美叽」或系统「设置 → 应用」。

### 方式二：绿色单文件

下载 `MejiPet.exe`，双击即用，首次启动会自解压约 10 秒。删除该文件即卸载，配置文件位于 `C:\Users\<你>\.meji_pet_config.json`。

### 方式三：从源码运行

```bash
pip install -r requirements.txt
python pet.py
```

> 仅支持 **Windows 10 / 11（64 位）**。macOS / Linux 不适用（依赖 Win32 分层窗口与系统托盘）。

---

## 从源码构建

### 1) 打包绿色单文件 EXE（PyInstaller）

```bash
pyinstaller --noconfirm --clean --onefile --windowed ^
  --name MejiPet --icon meji.ico ^
  --collect-all PySide6 --collect-all pystray ^
  --add-data "assets;assets" pet.py
```

产物在 `dist/MejiPet.exe`，已内置 Python 运行时、Qt、托盘库与全部表情素材，目标机器无需安装 Python。

### 2) 生成安装包（Inno Setup 6）

- 安装 [Inno Setup 6](https://jrsoftware.org/isdl.php)，并放入简体中文语言包 `ChineseSimplified.isl`。
- 用 Inno Setup 编译器打开 `MejiPet.iss` 编译，或命令行：

```bash
ISCC.exe MejiPet.iss
```

安装脚本为**每用户安装**（装到 `%LOCALAPPDATA%\Programs\MejiPet`，免 UAC），创建桌面 / 开始菜单快捷方式和卸载器，**不写任何开机启动项**。

### 3) 表情素材处理流水线

`assets/<尺寸>/` 下的透明 GIF 由脚本从白底母版统一处理得到（去白底、并集裁切、边缘外扩身体色消除黑边、空闲表情稳像去左右晃、共享调色板量化）：

- `regen2.py`：正式的素材重切流水线（四尺寸 50 / 60 / 100 / 150）。
- `swap_assets.py`：校验并原子替换正式素材（带备份、幂等）。
- `fix_away.py`：单独重算「走开再回来」特写的尺寸与画布。
- `make_icon.py` / `gen_iss.py`：生成应用图标、生成 Inno 脚本。

---

## 项目结构

```
meji-pet/
├─ pet.py                # 桌宠主程序（状态机、透明窗口、托盘、交互）
├─ assets/               # 表情素材（运行时必需）
│  ├─ 50/ 60/ 100/ 150/  # 四档预缩放透明 GIF，每档 40 个
│  └─ meji_*.gif         # 白底母版（素材流水线输入）
├─ meji.ico              # 应用 / 安装包图标
├─ MejiPet.iss           # Inno Setup 安装脚本
├─ requirements.txt
├─ regen2.py / swap_assets.py / fix_away.py   # 素材处理流水线
├─ make_icon.py / gen_iss.py                  # 图标 / 安装脚本生成
├─ test_static.py        # 静态资源检查（尺寸 / 透明 / 数量）
├─ test_logic.py         # 无头逻辑测试（offscreen）
├─ test_click_switch.py  # 点击切换 / 常驻不卡帧测试
├─ visual_test.py        # 真实 GUI + PrintWindow 抓帧测试
├─ test_exe_pkg.py       # 校验 EXE 内是否打包全部素材
├─ capture_pet.py        # 分层窗口抓帧工具
├─ quit_harness.py       # 托盘退出的确定性验证
└─ accept_click.py       # 真机点击切换验收
```

## 配置

设置保存在 `%USERPROFILE%\.meji_pet_config.json`，例如：

```json
{ "size": 50, "activity": 30 }
```

- `size`：`50` 小 / `60` 中 / `100` 大 / `150` 特大。
- `activity`：`10 / 30 / 50 / 80 / 100`，越高自发行为越频繁（自动轮换间隔相应变长，动作更密）。

## 技术栈

- **PySide6 (Qt 6)**：无边框置顶分层透明窗口、`QMovie` 播放 GIF、右键 `QMenu`。
- **pystray + Pillow**：系统托盘图标与菜单、GIF / 图标处理。
- **PyInstaller**：单文件打包；**Inno Setup 6**：Windows 安装包。
- Win32 `PrintWindow(PW_RENDERFULLCONTENT)` 用于分层窗口的自动化抓帧测试。

## 常见问题

- **蓝色 SmartScreen 提示未知发布者**：安装包 / EXE 未购买代码签名证书，点「更多信息 → 仍要运行」即可，属正常现象。
- **杀毒软件误报**：PyInstaller 单文件程序的常见误报，加信任即可。
- **第一次启动很慢**：单文件版本首次运行需自解压到临时目录，约 10 秒。
- **如何彻底卸载**：安装版用卸载器；绿色版删除 `MejiPet.exe`，再按需删除 `.meji_pet_config.json`。

---

## 致谢

再次感谢原创 IP **@美叽和大鼠** 创作出这么可爱的美叽。本项目仅为粉丝向、非盈利的学习与桌面美化二创，一切美术素材的权利归原作者所有。
