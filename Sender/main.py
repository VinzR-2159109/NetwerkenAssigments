import tkinter as tk
from tkinter import filedialog, messagebox
from emailSend import EmailSender
from fileUpload import FileUploader
from ackRequest import AckRequest
import paho.mqtt.client as paho
import uuid

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Netwerken Assignment 1 - File Uploader")
        self.master.geometry("700x250")
        
        # MQTT Client
        self.client = paho.Client(client_id=str(uuid.uuid4()), userdata=None, protocol=paho.MQTTv5, callback_api_version=paho.CallbackAPIVersion.VERSION2)
        self.client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("VinzRoosen", "cnVlz@QoG2vTTvyO")
        self.client.on_message = self.on_message
        self.client.on_connect = lambda client, userdata, flags, rc, properties=None: print("CONNACK received with code %s." % rc)
        self.client.connect("7fff47e5b4c74408957f70f5064d717b.s1.eu.hivemq.cloud", 8883)
        self.client.subscribe("fileServer")
        self.client.loop_start()
        
        # Main Frame
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Pane
        self.left_pane = tk.Frame(self.main_frame)
        self.left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.left_pane, text="1. Select a file:")
        self.label.pack(pady=5)
        
        self.browse_button = tk.Button(self.left_pane, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.email_label = tk.Label(self.left_pane, text="2. Enter receiving email:")
        self.email_label.pack(pady=5)
        self.email_entry = tk.Entry(self.left_pane, width= 40)
        self.email_entry.pack(pady=5)

        self.label = tk.Label(self.left_pane, text="3. Send the file:")
        self.label.pack(pady=5)

        self.upload_button = tk.Button(self.left_pane, text="Send", command=self.upload_file)
        self.upload_button.pack(pady=5)
        
        self.uploaded_file_label = tk.Label(self.left_pane, text="")
        self.uploaded_file_label.pack(pady=5)

        self.file_path = ""
        self.items = []

        # Right Pane with List Box
        self.right_pane = tk.Frame(self.main_frame, width=200)
        self.right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.listbox_label = tk.Label(self.right_pane, text="List Box:")
        self.listbox_label.pack(pady=5)

        self.refresh_button = tk.Button(self.right_pane, text="Refresh", command=self.send_request_to_flask)
        self.refresh_button.pack(pady=5)

        self.listbox_frame = tk.Frame(self.right_pane)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Column Headers
        tk.Label(self.listbox_frame, text="ID", width=10, relief=tk.RIDGE).grid(row=0, column=0)
        tk.Label(self.listbox_frame, text="Receiver", width=30, relief=tk.RIDGE).grid(row=0, column=1)
        tk.Label(self.listbox_frame, text="Status", width=15, relief=tk.RIDGE).grid(row=0, column=2)

        # Listbox
        self.listbox = tk.Listbox(self.listbox_frame)
        self.listbox.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        if msg.topic == "fileServer" and msg.payload.startswith(b"file received:"):
            file_id = msg.payload.split(b":")[1].strip().decode("utf-8")
            for i, item in enumerate(self.items):
                if file_id == item[0]:
                    self.items[i] = (file_id, item[1], "Received")
                    self.listbox.delete(i)
                    self.listbox.insert(i, self.items[i])

    def browse_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.uploaded_file_label.config(text=f"Selected file: {self.file_path}")

    def upload_file(self):
        if not self.file_path:
            messagebox.showerror("No file selected", "Please select a file first.")
            return

        uploader = FileUploader(self.file_path)
        file_key, error = uploader.upload()
        
        if file_key:
            email_address = self.email_entry.get()
            email_sender = EmailSender('smtp-relay.brevo.com', 587, 'vinz.roosen@student.uhasselt.be', 'MS86k0F5UfGv3rCj')
            success, email_error = email_sender.send_email(email_address, 'File Upload URL', f"Here is the URL of the uploaded file: http://localhost:5000/get_file?value={file_key}")
            
            if success:
                self.listbox.insert(tk.END, (file_key, email_address, "Sent"))
                self.items.append((file_key, email_address, "Sent"))
                messagebox.showinfo("Upload successful", "The file has been successfully uploaded and emailed.")
            else:
                messagebox.showerror("Email sending failed", email_error)
        else:
            messagebox.showerror("Upload failed", error)

    def send_request_to_flask(self):
        flask_url = "http://localhost:5000/get_ack"
        ack_request = AckRequest(flask_url)
        response_data = ack_request.send_request()
        
        for id in response_data:
            for i, item in enumerate(self.items):
                if id == item[0]:
                    self.items[i] = (id, item[1], "Received")
                    self.listbox.delete(i)
                    self.listbox.insert(i, self.items[i])
                        
def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
