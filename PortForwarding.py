import tkinter as tk
from tkinter import ttk
import threading
import socket

default_source_port = ""
default_target_port = "40000"

if __name__ == '__main__':
    root = tk.Tk()
    root.title('ポートフォワーディングツール')
    root.geometry("300x210")
    root.resizable(width=False, height=False)

    source_port_var = tk.StringVar()
    source_port_var.set(str(default_source_port))
    target_port_var = tk.StringVar()
    target_port_var.set(str(default_target_port))

    stop_threads = False
    target_socket = None

    def accept_connections(source_port, target_port):
        global target_socket
        try:
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.bind(('localhost', target_port))
            target_socket.listen(1)
            print(f'ポート{target_port}でリッスン中...')

            while not stop_threads:
                client_socket, client_addr = target_socket.accept()
                print(f'接続受信: {client_addr}')

                source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                source_socket.connect(('localhost', source_port))

                threading.Thread(target=forward_data, args=(client_socket, source_socket)).start()
                threading.Thread(target=forward_data, args=(source_socket, client_socket)).start()
        except Exception as e:
            print(f'エラー: {e}')

    def forward_data(source_socket, target_socket):
        try:
            while True:
                data = source_socket.recv(4096)
                if not data:
                    break
                target_socket.sendall(data)
        except ConnectionAbortedError:
            pass
        finally:
            source_socket.close()
            target_socket.close()

    def start_forwarding():
        global stop_threads
        stop_threads = False
        source_port = int(source_port_var.get())
        target_port = int(target_port_var.get())
        threading.Thread(target=accept_connections, args=(source_port, target_port)).start()

    def stop_forwarding():
        global stop_threads, target_socket
        stop_threads = True
        if target_socket:
            target_socket.close()
        print('ポートフォワーディングを停止しました。')

    target_label = ttk.Label(root, text='元のポート:')
    target_label.pack(pady=5)
    target_port_entry = ttk.Entry(root, textvariable=source_port_var)
    target_port_entry.pack(pady=5)

    source_label = ttk.Label(root, text='開放したいポート:')
    source_label.pack(pady=5)
    source_port_entry = ttk.Entry(root, textvariable=target_port_var)
    source_port_entry.pack(pady=5)

    start_button = ttk.Button(root, text='開始', command=start_forwarding)
    start_button.pack(pady=10)

    stop_button = ttk.Button(root, text='停止', command=stop_forwarding)
    stop_button.pack(pady=5)

    root.mainloop()
