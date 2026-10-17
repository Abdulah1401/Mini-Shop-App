# mobile/main.py
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.metrics import dp
from kivy.clock import Clock

# GANTI dengan IP server Anda saat testing di HP (contoh: 192.168.1.10:8000)
API = "http://10.0.2.2:8000"   # 10.0.2.2 = localhost dari Android Emulator

session = requests.Session()

# ==================== LOGIN ====================
class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation="vertical", padding=dp(30), spacing=dp(15))
        layout.add_widget(Label(text="[b]MiniShop[/b]", markup=True, font_size=dp(32), size_hint=(1, 0.3)))
        
        self.username = TextInput(hint_text="Username", multiline=False, size_hint=(1, None), height=dp(48))
        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(1, None), height=dp(48))
        layout.add_widget(self.username)
        layout.add_widget(self.password)

        btn_login = Button(text="Masuk", size_hint=(1, None), height=dp(50), background_color=(1, 0.4, 0.1, 1))
        btn_login.bind(on_release=self.do_login)
        layout.add_widget(btn_login)

        btn_reg = Button(text="Daftar", size_hint=(1, None), height=dp(50))
        btn_reg.bind(on_release=self.do_register)
        layout.add_widget(btn_reg)

        self.status = Label(text="", color=(1, 0.3, 0.3, 1))
        layout.add_widget(self.status)
        layout.add_widget(BoxLayout())
        self.add_widget(layout)

    def do_login(self, *_):
        try:
            r = session.post(f"{API}/login", json={
                "username": self.username.text,
                "password": self.password.text,
            }, timeout=10)
            if r.status_code == 200:
                token = r.json()["token"]
                session.headers.update({"Authorization": f"Bearer {token}"})
                self.manager.current = "home"
                self.manager.get_screen("home").load_products()
            else:
                self.status.text = r.json().get("detail", "Gagal login")
        except Exception as e:
            self.status.text = f"Error: {e}"

    def do_register(self, *_):
        try:
            r = session.post(f"{API}/register", json={
                "username": self.username.text,
                "password": self.password.text,
            }, timeout=10)
            self.status.text = "Berhasil daftar, silakan login" if r.status_code == 200 else r.json().get("detail", "Gagal")
        except Exception as e:
            self.status.text = f"Error: {e}"

# ==================== KARTU PRODUK ====================
class ProductCard(BoxLayout):
    def __init__(self, product, app_ref, **kw):
        super().__init__(orientation="vertical", size_hint_y=None, height=dp(230), padding=dp(6), spacing=dp(4), **kw)
        self.product = product
        self.app_ref = app_ref

        img = AsyncImage(source=product["image"], size_hint=(1, 0.55))
        name = Label(text=product["name"], size_hint=(1, 0.15), font_size=dp(13), shorten=True, shorten_from="right")
        price = Label(text=f"Rp {product['price']:,}".replace(",", "."), size_hint=(1, 0.15), font_size=dp(14), color=(1, 0.4, 0.1, 1), bold=True)
        btn = Button(text="+ Keranjang", size_hint=(1, 0.15), font_size=dp(12), background_color=(1, 0.4, 0.1, 1))
        btn.bind(on_release=lambda *_: self.app_ref.add_to_cart(product["id"]))

        for w in (img, name, price, btn):
            self.add_widget(w)

# ==================== HOME ====================
class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical")

        top = BoxLayout(size_hint=(1, None), height=dp(56), padding=dp(10))
        top.add_widget(Label(text="[b]MiniShop[/b]", markup=True, font_size=dp(20), size_hint=(0.5, 1)))
        btn_cart = Button(text="🛒 Keranjang", size_hint=(0.3, 1), font_size=dp(12))
        btn_cart.bind(on_release=lambda *_: setattr(self.manager, "current", "cart"))
        btn_out = Button(text="Keluar", size_hint=(0.2, 1), font_size=dp(12))
        btn_out.bind(on_release=self.logout)
        top.add_widget(btn_cart)
        top.add_widget(btn_out)
        root.add_widget(top)

        self.grid = GridLayout(cols=2, spacing=dp(8), padding=dp(8), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.grid)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        if not self.grid.children:
            self.load_products()

    def load_products(self):
        self.grid.clear_widgets()
        try:
            r = requests.get(f"{API}/products", timeout=10)
            for p in r.json():
                self.grid.add_widget(ProductCard(p, self))
        except Exception as e:
            self.grid.add_widget(Label(text=f"Gagal memuat: {e}"))

    def add_to_cart(self, pid):
        try:
            r = session.post(f"{API}/cart", json={"product_id": pid, "qty": 1}, timeout=10)
            print("Cart:", r.status_code, r.text)
        except Exception as e:
            print("Error add cart:", e)

    def logout(self, *_):
        session.headers.pop("Authorization", None)
        self.manager.current = "login"

# ==================== CART ====================
class CartScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical")

        top = BoxLayout(size_hint=(1, None), height=dp(56), padding=dp(10))
        back = Button(text="← Kembali", size_hint=(0.4, 1), on_release=lambda *_: setattr(self.manager, "current", "home"))
        top.add_widget(back)
        top.add_widget(Label(text="[b]Keranjang[/b]", markup=True, size_hint=(0.6, 1)))
        root.add_widget(top)

        self.items_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), padding=dp(8))
        self.items_box.bind(minimum_height=self.items_box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.items_box)
        root.add_widget(scroll)

        self.total_label = Label(text="Total: Rp 0", size_hint=(1, None), height=dp(40), font_size=dp(16))
        root.add_widget(self.total_label)

        btn_checkout = Button(text="Checkout", size_hint=(1, None), height=dp(56), background_color=(1, 0.4, 0.1, 1))
        btn_checkout.bind(on_release=self.checkout)
        root.add_widget(btn_checkout)
        self.add_widget(root)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.items_box.clear_widgets()
        try:
            r = session.get(f"{API}/cart", timeout=10)
            data = r.json()
            for it in data["items"]:
                row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
                row.add_widget(Label(text=f"{it['name']} x{it['qty']}", size_hint=(0.6, 1)))
                row.add_widget(Label(text=f"Rp {it['subtotal']:,}".replace(",", "."), size_hint=(0.3, 1)))
                rm = Button(text="✕", size_hint=(0.1, 1))
                rm.bind(on_release=lambda *_, pid=it["id"]: self.remove_item(pid))
                row.add_widget(rm)
                self.items_box.add_widget(row)
            self.total_label.text = f"Total: Rp {data['total']:,}".replace(",", ".")
        except Exception as e:
            self.items_box.add_widget(Label(text=f"Error: {e}"))

    def remove_item(self, pid):
        session.delete(f"{API}/cart/{pid}", timeout=10)
        Clock.schedule_once(lambda *_: self.refresh(), 0.2)

    def checkout(self, *_):
        try:
            r = session.post(f"{API}/checkout", json={"address": "Jl. Contoh No. 123, Jakarta", "payment_method": "COD"}, timeout=10)
            if r.status_code == 200:
                oid = r.json()["order_id"]
                self.total_label.text = f"✅ Order {oid} dibuat!"
                Clock.schedule_once(lambda *_: self.refresh(), 1.5)
            else:
                self.total_label.text = f"❌ {r.json().get('detail')}"
        except Exception as e:
            self.total_label.text = f"Error: {e}"

# ==================== APP ====================
class MiniShopApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(CartScreen(name="cart"))
        return sm

if __name__ == "__main__":
    MiniShopApp().run()
