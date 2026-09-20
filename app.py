import tkinter as tk
import requests

# तुमचे मूळ स्थान आणि गंतव्य स्थानाचे अक्षांश-रेखांश (Lat, Lon)
ORIGIN_LAT, ORIGIN_LON = 19.0760, 72.8777
DEST_LAT, DEST_LON = 19.2183, 72.9781

def get_commute_time():
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{ORIGIN_LON},{ORIGIN_LAT};{DEST_LON},{DEST_LAT}?overview=false"
        res = requests.get(url, timeout=5).json()
        duration_sec = res['routes'][0]['duration']
        distance_km = res['routes'][0]['distance'] / 1000
        mins = int(duration_sec // 60)
        return f"🚗 Office: {mins} mins ({distance_km:.1f} km)"
    except Exception:
        return "🚗 Traffic: Updating..."

def update_label():
    text = get_commute_time()
    label.config(text=text)
    root.after(120000, update_label)

root = tk.Tk()
root.title("Live Traffic Widget")
root.attributes('-topmost', True)
root.overrideredirect(True)
root.geometry("260x45+1100+40")
root.configure(bg="#1e1e1e")

label = tk.Label(root, text="Loading...", font=("Segoe UI", 10, "bold"), fg="#00ffcc", bg="#1e1e1e")
label.pack(expand=True)

def start_move(event):
    root.x = event.x
    root.y = event.y

def on_motion(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

label.bind("<ButtonPress-1>", start_move)
label.bind("<B1-Motion>", on_motion)
label.bind("<Button-3>", lambda e: root.destroy())

update_label()
root.mainloop()
