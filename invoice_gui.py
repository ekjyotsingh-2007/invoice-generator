import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import os

from invoice_backend import generate_invoice_pdf

# Ensure folders exist
os.makedirs("invoices", exist_ok=True)

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Generator")
        self.root.geometry("950x600")

        self.items = []

        self.build_header()
        self.build_item_section()
        self.build_table()
        self.build_footer()

    def build_header(self):
        frame = tk.LabelFrame(self.root, text="Invoice Details", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        fields = [
            "Company Name", "Company Address", "Contact Line",
            "Bill No", "Client Name", "Subject", "GST %"
        ]

        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(frame, text=field).grid(row=i//2, column=(i%2)*2, sticky="w")
            entry = tk.Entry(frame, width=45)
            entry.grid(row=i//2, column=(i%2)*2 + 1, padx=5, pady=2)
            self.entries[field] = entry

        self.entries["GST %"].insert(0, "18")

    def build_item_section(self):
        frame = tk.LabelFrame(self.root, text="Add Item", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        self.desc = tk.Entry(frame, width=45)
        self.qty = tk.Entry(frame, width=10)
        self.unit = tk.Entry(frame, width=10)
        self.rate = tk.Entry(frame, width=10)

        tk.Label(frame, text="Description").grid(row=0, column=0)
        self.desc.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Qty").grid(row=0, column=2)
        self.qty.grid(row=0, column=3)

        tk.Label(frame, text="Unit").grid(row=0, column=4)
        self.unit.grid(row=0, column=5)

        tk.Label(frame, text="Rate").grid(row=0, column=6)
        self.rate.grid(row=0, column=7)

        tk.Button(frame, text="Add Item", command=self.add_item)\
            .grid(row=0, column=8, padx=10)

    def build_table(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10)

        columns = ("Sr", "Description", "Qty", "Rate", "Amount")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160 if col == "Description" else 90)

        self.tree.pack(fill="both", expand=True)

    def build_footer(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Delete Selected Item",
            command=self.delete_item,
            bg="red",
            fg="white",
            font=("Arial", 11),
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame,
            text="Generate Invoice",
            command=self.generate_pdf,
            bg="darkblue",
            fg="white",
            font=("Arial", 12),
        ).pack(side="left", padx=10)

    def add_item(self):
        try:
            qty = float(self.qty.get())
            rate = float(self.rate.get())
        except ValueError:
            messagebox.showerror("Error", "Qty and Rate must be numbers")
            return

        amount = qty * rate
        sr = len(self.items) + 1
        qty_disp = f"{qty} {self.unit.get()}"

        item = [sr, self.desc.get(), qty_disp, rate, amount]
        self.items.append(item)
        self.tree.insert("", "end", values=item)

        self.desc.delete(0, tk.END)
        self.qty.delete(0, tk.END)
        self.unit.delete(0, tk.END)
        self.rate.delete(0, tk.END)

    def delete_item(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "No item selected")
            return

        for item in selected:
            values = self.tree.item(item)["values"]

            # remove from internal list
            for stored_item in self.items:
                if stored_item[0] == values[0]:
                    self.items.remove(stored_item)
                    break

            # remove from GUI table
            self.tree.delete(item)

        # re-number rows
        for index, item in enumerate(self.items, start=1):
            item[0] = index

        # refresh table
        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in self.items:
            self.tree.insert("", "end", values=row)

    def generate_pdf(self):
        if not self.items:
            messagebox.showerror("Error", "No items added")
            return

        info = {
            "company_name": self.entries["Company Name"].get(),
            "company_address": self.entries["Company Address"].get(),
            "contact_line": self.entries["Contact Line"].get(),
            "bill_no": self.entries["Bill No"].get(),
            "bill_date": date.today().strftime("%d-%m-%Y"),
            "client_name": self.entries["Client Name"].get(),
            "subject": self.entries["Subject"].get()
        }

        gst = float(self.entries["GST %"].get())
        filename = f"invoices/invoice_{info['bill_no']}.pdf"

        generate_invoice_pdf(filename, info, self.items, gst)
        messagebox.showinfo("Success", f"Invoice generated:\n{filename}")

# -------- RUN --------
root = tk.Tk()
app = InvoiceApp(root)
root.mainloop()