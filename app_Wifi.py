import network
import time
import os

def show_fw():
    try:
        print("os.uname():", os.uname())
    except Exception as e:
        print("os.uname() error:", e)

def connect_wifi(ssid, passwd, timeout=20):
    """
    Pico W 用の接続関数
    - ssid, passwd: 文字列
    - timeout: 接続待ち時間（秒）
    戻り値: True=接続成功, False=失敗
    """
    show_fw()

    wlan = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)

    # APモードを無効化して干渉を避ける
    try:
        if ap.active():
            print("Disabling AP mode")
            ap.active(False)
    except Exception as e:
        print("AP disable error:", e)

    try:
        wlan.active(True)
    except Exception as e:
        print("wlan.active(True) error:", e)
        return False

    # 既に接続済みならそのまま
    if wlan.isconnected():
        print("already connected:", wlan.ifconfig())
        return True

    # スキャンして SSID が見えるか確認
    try:
        nets = wlan.scan()
        found = []
        for n in nets:
            ss = n[0]
            if isinstance(ss, bytes):
                try:
                    ss = ss.decode()
                except:
                    ss = repr(ss)
            found.append(ss)
        print("scan found:", found)
        if ssid not in found:
            print("Warning: target SSID not found in scan. It may be hidden, out of range, 5GHz-only, or blocked by AP settings.")
    except Exception as e:
        print("scan failed:", e)

    print("Trying to connect to:", ssid)
    try:
        wlan.connect(ssid, passwd)
    except Exception as e:
        print("wlan.connect() error:", e)
        return False

    start = time.ticks_ms()
    last_status = None

    # タイムアウトまで待つ
    while time.ticks_diff(time.ticks_ms(), start) < timeout * 1000:
        try:
            if wlan.isconnected():
                print("connected:", wlan.ifconfig())
                return True
        except Exception as e:
            print("isconnected() error:", e)

        # status の変化を表示（生の値を出す）
        try:
            st = wlan.status()
        except Exception as e:
            st = "status_error:" + str(e)

        if st != last_status:
            print("status:", st)
            last_status = st

        time.sleep(0.5)

    print("connect timeout after {}s".format(timeout))
    try:
        wlan.disconnect()
    except Exception as e:
        print("disconnect error:", e)
    return False

# 使い方例（実際の SSID/PASS に置き換えて実行）
# connect_wifi("YourSSID", "YourPassword", timeout=25)