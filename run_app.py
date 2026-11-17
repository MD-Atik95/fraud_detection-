"""Fraud Monitor as a desktop app:  python run_app.py
Starts the backend and opens the interface in its own window (pywebview).
If pywebview/WebView2 is missing it falls back to the default browser."""
import os, socket, sys, threading, time, webbrowser

import uvicorn

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


def free_port(start=8000):
    for p in range(start, start + 20):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("No free port found")


def ensure_model():
    from fraud import config
    if os.path.exists(config.MODEL_PATH):
        return
    from fraud.train import train
    csv = os.path.join(ROOT, "data", "creditcard.csv")
    print("First run: training the model (a few minutes)...")
    train(csv=csv if os.path.exists(csv) else None)


def main():
    ensure_model()
    port = free_port()
    url = f"http://127.0.0.1:{port}/"
    server = uvicorn.Server(uvicorn.Config("fraud.api:app", host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(120):                       # wait until the server answers
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                break
        time.sleep(0.5)

    try:
        import webview
        webview.create_window("Fraud Monitor", url, width=1280, height=820, min_size=(900, 600))
        webview.start()                        # blocks until the window is closed
    except Exception as e:
        print("Native window unavailable (", e, ") - opening the browser instead. Press Ctrl+C to stop.")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    server.should_exit = True


if __name__ == "__main__":
    main()
