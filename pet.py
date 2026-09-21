# -*- coding: utf-8 -*-
"""仓鼠美叽 桌宠 v10 - 预缩放 GIF，运行时直接加载对应尺寸"""
import sys, os, random, math, time, json, queue

def res(p):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, p)

CFG_PATH = os.path.join(os.path.expanduser("~"), ".meji_pet_config.json")
DEFAULTS = {"size": 60, "activity": 15}

def load_cfg():
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            return {**DEFAULTS, **json.load(f)}
    except:
        return dict(DEFAULTS)

def save_cfg(cfg):
    try:
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False)
    except:
        pass

from PySide6.QtWidgets import QApplication, QLabel, QMenu, QWidget
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QAction, QMovie

FACES = {
    "idle":     "meji_idle_t.gif",
    "happy":    "meji_happy_t.gif",
    "hug":      "meji_hug_t.gif",
    "money":    "meji_angry_t.gif",
    "sleep":    "meji_sleep_t.gif",
    "eat":      "meji_eat_t.gif",
    "excited":  "meji_excited_t.gif",
    "smug":     "meji_smug_t.gif",
    "kiss":     "meji_kiss_t.gif",
    "laugh":    "meji_laugh_t.gif",
    "phone":    "meji_phone_t.gif",
    "wave":     "meji_fan_t.gif",
    "hug2":     "meji_hug2_t.gif",
    "joy":      "meji_joy_t.gif",
    "drunk":    "meji_drunk_t.gif",
    "cry":      "meji_cry_t.gif",
    "bliss":    "meji_bliss_t.gif",
    "wronged":  "meji_wronged_t.gif",
    "pout":     "meji_pout_t.gif",
    "think":    "meji_think_t.gif",
    "shy":      "meji_shy_t.gif",
    "gift":     "meji_gift_t.gif",
    "flower":   "meji_flower_t.gif",
    "drink":    "meji_drink_t.gif",
    "rain":     "meji_rain_t.gif",
    "present":  "meji_present_t.gif",
    "relax":    "meji_relax_t.gif",
    "fume":     "meji_fume_t.gif",
    "furious":  "meji_furious_t.gif",
    "lieflat":  "meji_lieflat_t.gif",
    "stomp":    "meji_stomp_t.gif",
    "cheer":    "meji_cheer_t.gif",
    "cool":     "meji_cool_t.gif",
    "surprised":"meji_surprised_t.gif",
    "sushi":    "meji_sushi_t.gif",
    "salad":    "meji_salad_t.gif",
    "innocent": "meji_innocent_t.gif",
    "blowkiss": "meji_blowkiss_t.gif",
    "glare":    "meji_glare_t.gif",
    "away":     "meji_away_t.gif",
}

STATE_FACE = {
    "idle": "idle", "walk": "idle", "drag": "fume",
    "happy": "happy", "excited": "excited", "laugh": "laugh",
    "cheer": "cheer", "flower": "flower", "joy": "joy",
    "smug": "smug", "cool": "cool", "shy": "shy",
    "angry": "pout", "pout": "pout", "fume": "fume",
    "furious": "furious", "stomp": "stomp", "glare": "glare",
    "cry": "cry", "wronged": "wronged", "innocent": "innocent",
    "eat": "eat", "salad": "salad", "drink": "drink", "drunk": "drunk",
    "hug": "hug", "hug2": "hug2", "kiss": "kiss", "blowkiss": "blowkiss",
    "sleep": "sleep", "bliss": "bliss", "lieflat": "lieflat", "relax": "relax",
    "phone": "phone", "think": "think", "sushi": "sushi",
    "gift": "gift", "present": "present", "rain": "rain",
    "surprised": "surprised", "away": "away", "money": "money",
    "tap": "surprised", "feed": "eat", "pet": "hug", "wave": "wave",
    "hungry": "cry", "dance": "cheer", "dizzy": "surprised",
}

W = 200
AUTO_INTERVAL = 600

AUTO_POOL = [
    ("idle", 10), ("bliss", 4), ("lieflat", 4), ("relax", 3), ("joy", 3),
    ("happy", 3), ("smug", 2), ("think", 2), ("phone", 2),
    ("laugh", 2), ("flower", 2), ("cool", 2),
    ("excited", 1), ("cheer", 1), ("shy", 1), ("sleep", 2),
    ("hug2", 1), ("kiss", 1), ("blowkiss", 1),
    ("sushi", 1), ("money", 1),
    ("gift", 1), ("present", 1), ("rain", 1), ("drunk", 1),
]

# 单击切换池：全部可循环播放的表情；排除 away（会走出屏幕的稀有“走开再回来”动作）
CLICK_POOL = [k for k in FACES.keys() if k != "away"]


class Particle(QWidget):
    def __init__(self, parent_pet, emoji):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label = QLabel(self)
        self.label.setStyleSheet("font-size: 18px;")
        self.label.setText(emoji)
        self.label.adjustSize()
        self.resize(self.label.size())
        self.life = 1.0
        self.vy = random.uniform(-2.5, -1.0)
        self.vx = random.uniform(-1.0, 1.0)
        lbl = parent_pet.label
        cx = parent_pet.x() + lbl.x() + lbl.width()//2 + random.randint(-20, 20)
        top = parent_pet.y() + lbl.y()
        self.move(cx, top)
        self.show()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_pos)
        self._timer.start(33)

    def update_pos(self):
        self.move(self.x() + self.vx, self.y() + self.vy)
        self.vy += 0.03
        self.life -= 0.015
        if self.life <= 0:
            self._timer.stop()
            self.close()


class Pet(QWidget):
    manager = None
    pet_index = 0

    def __init__(self):
        super().__init__()
        self.cfg = load_cfg()
        self.idx = Pet.pet_index
        Pet.pet_index += 1

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.label.setAttribute(Qt.WA_TranslucentBackground)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.resize(W, W)

        self.movies = {}
        self.movie_sizes = {}
        self.current_movie = None
        self.current_face_key = None
        self._load_movies()

        screen = QApplication.primaryScreen().geometry()
        self.screen_w = screen.width()
        self.screen_h = screen.height()

        self.px = float(random.randint(100, self.screen_w - W - 100))
        self.py = float(random.randint(200, self.screen_h - W - 100))
        self.move(int(self.px), int(self.py))

        self.state = "idle"
        self.state_end = 0
        self.auto_state = "idle"
        self.last_auto_time = time.time()
        self.face("idle")

        self.fullness = 80.0
        self.mood = 80.0
        self._drag_pos = None
        self._press_start = None
        self._moved = False
        self._click_token = 0
        self.walk_target = None
        self._away_mode = False

        self.particles = []
        self.build_menu()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(33)

        self.decay_timer = QTimer(self)
        self.decay_timer.timeout.connect(self.decay)
        self.decay_timer.start(2000)

    def _gif_dir(self):
        sz = self.cfg.get("size", 60)
        return res(os.path.join("assets", str(sz)))

    def _load_movies(self):
        from PIL import Image as PImage
        # 先停止并释放旧的 movie，避免多次切换尺寸泄漏
        for old in getattr(self, "movies", {}).values():
            try:
                old.stop()
            except Exception:
                pass
        d = self._gif_dir()
        self.movies = {}
        self.movie_sizes = {}
        for k, fn in FACES.items():
            path = os.path.join(d, fn)
            if os.path.exists(path):
                m = QMovie(path)
                m.setCacheMode(QMovie.CacheAll)
                pi = PImage.open(path)
                self.movie_sizes[k] = QSize(pi.width, pi.height)
                pi.close()
                self.movies[k] = m

    def build_menu(self):
        self.menu = QMenu()
        self.menu.setStyleSheet(
            "QMenu{background:#fff5f8;border:1px solid #ffd6e7;padding:4px;}"
            "QMenu::item{padding:6px 24px;border-radius:4px;}"
            "QMenu::item:selected{background:#ffd6e7;}")
        face_menu = self.menu.addMenu("🎭 逗它")
        for label, action in [
            ("😊 开心一下", "happy"),
            ("😴 让它睡", "sleep"),
            ("🍪 喂东西", "eat"),
            ("😭 惹它哭", "cry"),
        ]:
            act = QAction(label, self)
            act.triggered.connect(lambda checked, a=action: self.act(a))
            face_menu.addAction(act)
        self.menu.addSeparator()
        summon_act = QAction("🐣 再召唤一只", self)
        summon_act.triggered.connect(self.summon)
        self.menu.addAction(summon_act)
        size_menu = self.menu.addMenu("📐 大小")
        self._size_actions = {}
        for label, val in [("小 (50px)",50),("中 (60px)",60),("大 (100px)",100),("特大 (150px)",150)]:
            act = QAction(label, self)
            act.setCheckable(True)
            act.setChecked(self.cfg.get("size") == val)
            act.triggered.connect(lambda checked=False, v=val: self.set_size(v))
            size_menu.addAction(act)
            self._size_actions[val] = act
        act_menu = self.menu.addMenu("⚡ 活跃度")
        self._act_actions = {}
        for label, val in [("安静 (10)",10),("悠闲 (30)",30),("正常 (50)",50),("活泼 (80)",80),("超活跃 (100)",100)]:
            act = QAction(label, self)
            act.setCheckable(True)
            act.setChecked(self.cfg.get("activity") == val)
            act.triggered.connect(lambda checked=False, v=val: self.set_activity(v))
            act_menu.addAction(act)
            self._act_actions[val] = act
        self.menu.addSeparator()
        if self.idx > 0:
            qa = QAction("❌ 收起这只", self)
            qa.triggered.connect(self.close_pet)
        else:
            qa = QAction("❌ 全部退出", self)
            qa.triggered.connect(self.quit_all)
        self.menu.addAction(qa)
        # 弹出前刷新选中标记
        self.menu.aboutToShow.connect(self._refresh_menu_checks)

    def _refresh_menu_checks(self):
        cur_size = self.cfg.get("size")
        for val, act in getattr(self, "_size_actions", {}).items():
            act.setChecked(cur_size == val)
        cur_act = self.cfg.get("activity")
        for val, act in getattr(self, "_act_actions", {}).items():
            act.setChecked(cur_act == val)

    def summon(self):
        if self.manager and len(self.manager.pets) < 5:
            self.manager.spawn()

    def set_size(self, v):
        self.cfg["size"] = v
        save_cfg(self.cfg)
        self._load_movies()
        self.face(self.auto_state)
        if self.manager:
            for p in self.manager.pets:
                if p is not self:
                    p.cfg["size"] = v
                    p._load_movies()
                    p.face(p.auto_state)

    def set_activity(self, v):
        self.cfg["activity"] = v
        save_cfg(self.cfg)
        if self.manager:
            for p in self.manager.pets:
                p.cfg["activity"] = v

    def face(self, f):
        face_key = STATE_FACE.get(f, "idle")
        if self.current_movie:
            try:
                self.current_movie.stop()
            except:
                pass
        # 先按新表情尺寸定好容器并居中，再挂帧播放，避免首帧沿用旧尺寸造成“变大一帧”
        sz = self.movie_sizes.get(face_key, QSize(60, 60))
        self.label.setFixedSize(sz)
        self.label.move((W - sz.width())//2, (W - sz.height())//2)
        m = self.movies.get(face_key)
        if m:
            m.setSpeed(70)
            self.label.setMovie(None)
            self.label.setMovie(m)
            m.jumpToFrame(0)
            m.start()
            self.current_movie = m
            self.current_face_key = face_key

    def spawn_hearts(self, n=5):
        for _ in range(n):
            self.particles.append(Particle(self, "♥"))

    def setState(self, s, dur=2000):
        self.state = s
        self.face(s)
        self.state_end = time.time() * 1000 + dur

    def act(self, name):
        if name == "feed":
            self.fullness = min(100, self.fullness+25)
            self.setState(random.choice(["eat","salad","drink"]), 2600)
        elif name == "pet":
            self.mood = min(100, self.mood+20)
            self.setState("hug", 2000)
            self.spawn_hearts(6)
        elif name == "sleep":
            self.setState("sleep", 5000)
        elif name == "walk":
            self.start_walk()
            return
        elif name in STATE_FACE:
            # 通用表情（开心 happy、哭 cry 等菜单/托盘动作）
            dur = 3000 if name == "cry" else 2500
            self.setState(name, dur)
        self.last_auto_time = time.time()

    def start_away(self):
        self._away_mode = True
        self.state = "walk"
        self.state_end = time.time() * 1000 + 30000
        self.face("away")
        self.last_auto_time = time.time()
        tx = float(self.screen_w + W)
        self.walk_target = (tx, self.py)

    def come_back(self):
        self._away_mode = False
        self.show()
        self.px = float(self.screen_w + W)
        self.py = float(random.randint(200, self.screen_h - W - 100))
        self.move(int(self.px), int(self.py))
        self.state = "walk"
        self.state_end = time.time() * 1000 + 30000
        self.face("idle")
        tx = float(random.randint(100, self.screen_w // 2))
        self.walk_target = (tx, self.py)

    def start_walk(self):
        self.state = "walk"
        self.state_end = time.time() * 1000 + 4000
        self.face("idle")
        cx, cy = self.px, self.py
        # 小范围挪动，避免干扰工作
        tx = max(40, min(self.screen_w - W - 40, cx + random.randint(-80, 80)))
        ty = max(80, min(self.screen_h - W - 80, cy + random.randint(-50, 50)))
        self.walk_target = (float(tx), float(ty))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._press_start = e.globalPosition().toPoint()
            self._moved = False
        elif e.button() == Qt.RightButton:
            self.menu.exec(e.globalPosition().toPoint())

    def mouseMoveEvent(self, e):
        if self._drag_pos:
            delta = e.globalPosition().toPoint() - self._press_start
            if not self._moved and (abs(delta.x()) > 5 or abs(delta.y()) > 5):
                self._moved = True
                self.face("drag")
            if self._moved:
                gp = e.globalPosition().toPoint()
                nx = gp.x() - self._drag_pos.x()
                ny = gp.y() - self._drag_pos.y()
                # 钳制在屏幕内，防止拖丢
                nx = max(0, min(self.screen_w - W, nx))
                ny = max(0, min(self.screen_h - W, ny))
                self.move(nx, ny)
                self.px = float(nx)
                self.py = float(ny)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            was_drag = self._moved
            self._drag_pos = None
            self._moved = False
            if was_drag:
                self.face(self.auto_state)
                self.state = self.auto_state
                self.last_auto_time = time.time()
            else:
                # 延迟单击，给双击留出识别窗口，避免双击喂食同时触发单击反应
                self._click_token += 1
                token = self._click_token
                gap = QApplication.doubleClickInterval()
                QTimer.singleShot(gap, lambda t=token: self._do_single_click(t))

    def _do_single_click(self, token):
        if token != self._click_token:
            return  # 已被双击取消
        # 单击=切换常驻表情：随机挑一个与当前不同的可循环表情，一直停留到
        # 下次点击或约10分钟自动轮换；双击喂食/拖拽等临时互动结束后会回到它
        pool = [k for k in CLICK_POOL if k != self.auto_state]
        c = random.choice(pool)
        self.auto_state = c
        self.state = c
        self.state_end = 0  # 常驻表情不参与到时回弹（state==auto_state 已保证）
        self.face(c)
        self.last_auto_time = time.time()

    def mouseDoubleClickEvent(self, e):
        # 取消挂起的单击反应
        self._click_token += 1
        self.act("feed")

    def tick(self):
        t = time.time()
        tms = t * 1000

        # 仅“临时反应”到时才回弹：临时反应 state≠常驻auto_state 且有结束时间；
        # 常驻表情（idle/点击选中/自动轮换，state==auto_state）绝不能逐帧重载，否则会卡在第一帧
        if (self.state not in ("idle", "drag", "walk")
                and self.state != self.auto_state
                and tms > self.state_end):
            self.face(self.auto_state)
            self.state = self.auto_state

        if not self._drag_pos and not self._away_mode:
            elapsed = t - self.last_auto_time
            interval = AUTO_INTERVAL * (1.0 + self.cfg.get("activity", 15)/200.0)
            if elapsed >= interval:
                self.do_auto_step()

        if self.walk_target and self.state == "walk":
            tx, ty = self.walk_target
            dx = tx - self.px
            dy = ty - self.py
            dist = math.hypot(dx, dy)
            if dist < 4:
                self.walk_target = None
                if self._away_mode:
                    self.hide()
                    QTimer.singleShot(4000, self.come_back)
                else:
                    # 小范围走动结束，回到自动表情
                    self.face(self.auto_state)
                    self.state = self.auto_state
            else:
                step = min(4.0, dist)
                self.px += dx/dist * step
                self.py += dy/dist * step
                self.move(int(self.px), int(self.py))
        elif not self._drag_pos:
            # 分辨率改变后把美叽钳回屏幕内
            if (self.px < 0 or self.px > self.screen_w - W or
                    self.py < 0 or self.py > self.screen_h - W):
                self.px = max(0, min(self.screen_w - W, self.px))
                self.py = max(0, min(self.screen_h - W, self.py))
                self.move(int(self.px), int(self.py))

    def do_auto_step(self):
        self.last_auto_time = time.time()
        if self.fullness < 25:
            c = random.choice(["cry","wronged","innocent"])
        elif self.mood < 25:
            c = random.choice(["pout","fume","wronged","glare"])
        else:
            roll = random.random()
            # 约5%：走开再回来（稀有事件）
            if roll < 0.05:
                self.start_away()
                return
            names = [x[0] for x in AUTO_POOL]
            weights = [x[1] for x in AUTO_POOL]
            c = random.choices(names, weights=weights, k=1)[0]
            # 约12%：换表情后小范围挪动一下
            if random.random() < 0.12:
                self.auto_state = c
                self.face(c)
                self.state = c
                QTimer.singleShot(random.randint(800, 2000), self.start_walk)
                return
        self.auto_state = c
        self.face(c)
        self.state = c

    def decay(self):
        self.fullness = max(0, self.fullness - 0.03)
        self.mood = max(0, self.mood - 0.015)

    def close_pet(self):
        if self.manager:
            self.manager.remove_pet(self)
        self.close()

    def quit_all(self):
        if self.manager:
            self.manager.quit_all()


class PetManager:
    def __init__(self):
        self.pets = []
        self.tray = None
        self.cmd_queue = queue.Queue()

    def spawn(self):
        if len(self.pets) >= 5:
            return None
        p = Pet()
        self.pets.append(p)
        p.show()
        return p

    def remove_pet(self, pet):
        if pet in self.pets:
            self.pets.remove(pet)

    def setup_tray(self):
        try:
            import pystray
            from PIL import Image as PImage
            ic = PImage.open(res(os.path.join("assets","60","meji_idle_t.gif"))).convert("RGBA")
            ic = ic.resize((64,64), PImage.LANCZOS)
            def mk(act_name):
                def inner(icon, item):
                    self.cmd_queue.put(act_name)
                return inner
            def do_quit(icon, item):
                self.cmd_queue.put("__quit__")
            menu = pystray.Menu(
                pystray.MenuItem("喂瓜子", mk("feed")),
                pystray.MenuItem("摸摸头", mk("pet")),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("召唤一只", mk("__spawn__")),
                pystray.MenuItem("退出", do_quit),
            )
            self.tray = pystray.Icon("meji", ic, "仓鼠美叽", menu)
            import threading
            threading.Thread(target=self.tray.run, daemon=True).start()
            self.poll_timer = QTimer()
            self.poll_timer.timeout.connect(self._poll_cmds)
            self.poll_timer.start(100)
        except Exception as e:
            print("tray:", e)

    def _poll_cmds(self):
        try:
            while True:
                cmd = self.cmd_queue.get_nowait()
                if cmd == "__quit__":
                    self.quit_all()
                    return
                elif cmd == "__spawn__":
                    if len(self.pets) < 5:
                        self.spawn()
                else:
                    for p in self.pets:
                        p.act(cmd)
        except queue.Empty:
            pass

    def quit_all(self):
        for p in self.pets:
            p.close()
        os._exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mgr = PetManager()
    Pet.manager = mgr
    mgr.spawn()
    mgr.setup_tray()
    sys.exit(app.exec())
