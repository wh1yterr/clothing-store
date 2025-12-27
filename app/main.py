import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psycopg2
import csv
import subprocess
import os

class DBApp:
    def __init__(self, root):
        self.root = root
        root.title("Универсальное приложение для взаимодействия с БД")
        root.geometry("1000x700")
        root.resizable(True, True)

        # Статус-бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов")
        status_bar = tk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Подключение к БД
        self.conn = None
        self.cur = None
        self.connect_frame = tk.Frame(root)
        self.connect_frame.pack(pady=10)

        tk.Label(self.connect_frame, text="Хост:").grid(row=0, column=0)
        self.host_entry = tk.Entry(self.connect_frame)
        self.host_entry.grid(row=0, column=1)
        self.host_entry.insert(0, "localhost")

        tk.Label(self.connect_frame, text="Порт:").grid(row=0, column=2)
        self.port_entry = tk.Entry(self.connect_frame)
        self.port_entry.grid(row=0, column=3)
        self.port_entry.insert(0, "5432")

        tk.Label(self.connect_frame, text="База данных:").grid(row=1, column=0)
        self.db_entry = tk.Entry(self.connect_frame)
        self.db_entry.grid(row=1, column=1)

        tk.Label(self.connect_frame, text="Пользователь:").grid(row=1, column=2)
        self.user_entry = tk.Entry(self.connect_frame)
        self.user_entry.grid(row=1, column=3)

        tk.Label(self.connect_frame, text="Пароль:").grid(row=2, column=0)
        self.pass_entry = tk.Entry(self.connect_frame, show="*")
        self.pass_entry.grid(row=2, column=1)

        tk.Button(self.connect_frame, text="Подключиться", command=self.connect_db).grid(row=2, column=2, columnspan=2)

        # Notebook для вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Вкладки будут добавлены после подключения

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host_entry.get(),
                port=self.port_entry.get(),
                database=self.db_entry.get(),
                user=self.user_entry.get(),
                password=self.pass_entry.get()
            )
            self.cur = self.conn.cursor()
            messagebox.showinfo("Успех", "Подключено к БД")
            self.status_var.set("Подключено")
            self.create_interfaces()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status_var.set("Ошибка подключения")

    def create_interfaces(self):
        # Вкладка "Операции с данными"
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text="Операции с данными")
        self.create_data_interface()

        # Вкладка "Конструктор запросов"
        self.query_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.query_tab, text="Конструктор запросов")
        self.create_query_interface()

        # Вкладка "Сервисные функции"
        self.service_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.service_tab, text="Сервисные функции")
        self.create_service_interface()

    def create_data_interface(self):
        # Выбор таблицы
        tk.Label(self.data_tab, text="Выберите таблицу:").pack(pady=5)
        self.table_list = ttk.Combobox(self.data_tab)
        self.table_list.pack()
        tk.Button(self.data_tab, text="Обновить список таблиц", command=self.load_tables).pack(pady=5)

        # Таблица для данных
        self.data_tree = ttk.Treeview(self.data_tab, show='headings', height=15)
        self.data_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Кнопки CRUD
        btn_frame = tk.Frame(self.data_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="Загрузить данные", command=self.load_data).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Добавить запись", command=self.add_record_window).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_record_window).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Удалить", command=self.delete_record).pack(side=tk.LEFT)

        # Прокрутка
        scrollbar = ttk.Scrollbar(self.data_tab, orient=tk.VERTICAL, command=self.data_tree.yview)
        self.data_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_tables(self):
        try:
            self.cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in self.cur.fetchall()]
            self.table_list['values'] = tables
            self.status_var.set(f"Загружено {len(tables)} таблиц")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_data(self):
        table = self.table_list.get()
        if not table:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return

        try:
            self.cur.execute(f"SELECT * FROM {table} LIMIT 100")
            rows = self.cur.fetchall()
            columns = [desc[0] for desc in self.cur.description]

            self.data_tree["columns"] = columns
            for col in columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100, anchor='center')

            for i in self.data_tree.get_children():
                self.data_tree.delete(i)

            for row in rows:
                self.data_tree.insert('', 'end', values=row)

            self.status_var.set(f"Загружено {len(rows)} записей из {table}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_record_window(self):
        table = self.table_list.get()
        if not table:
            return

        try:
            self.cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
            columns = self.cur.fetchall()

            window = tk.Toplevel()
            window.title("Добавить запись")
            entries = []
            for i, (col, dtype) in enumerate(columns):
                tk.Label(window, text=col).grid(row=i, column=0)
                entry = tk.Entry(window)
                entry.grid(row=i, column=1)
                entries.append((col, entry))

            def save():
                values = [entry.get() for _, entry in entries]
                cols = ', '.join([col for col, _ in columns])
                placeholders = ', '.join(['%s'] * len(values))
                query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
                try:
                    self.cur.execute(query, values)
                    self.conn.commit()
                    messagebox.showinfo("Успех", "Запись добавлена")
                    window.destroy()
                    self.load_data()
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

            tk.Button(window, text="Сохранить", command=save).grid(row=len(columns), column=0, columnspan=2)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def edit_record_window(self):
        table = self.table_list.get()
        selected = self.data_tree.selection()
        if not table or not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись")
            return

        values = self.data_tree.item(selected[0])['values']
        columns = self.data_tree["columns"]

        # Предполагаем, что первый столбец - первичный ключ
        pk_col = columns[0]
        pk_val = values[0]

        window = tk.Toplevel()
        window.title("Редактировать запись")
        entries = []
        for i, col in enumerate(columns):
            tk.Label(window, text=col).grid(row=i, column=0)
            entry = tk.Entry(window)
            entry.insert(0, values[i])
            entry.grid(row=i, column=1)
            entries.append((col, entry))

        def save():
            sets = ', '.join([f"{col} = %s" for col, _ in entries[1:]])  # Исключаем PK
            values = [entry.get() for _, entry in entries[1:]]
            query = f"UPDATE {table} SET {sets} WHERE {pk_col} = %s"
            values.append(pk_val)
            try:
                self.cur.execute(query, values)
                self.conn.commit()
                messagebox.showinfo("Успех", "Запись обновлена")
                window.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(window, text="Сохранить", command=save).grid(row=len(columns), column=0, columnspan=2)

    def delete_record(self):
        table = self.table_list.get()
        selected = self.data_tree.selection()
        if not table or not selected:
            return

        values = self.data_tree.item(selected[0])['values']
        columns = self.data_tree["columns"]
        pk_col = columns[0]
        pk_val = values[0]

        if messagebox.askyesno("Подтверждение", "Удалить запись?"):
            query = f"DELETE FROM {table} WHERE {pk_col} = %s"
            try:
                self.cur.execute(query, (pk_val,))
                self.conn.commit()
                messagebox.showinfo("Успех", "Запись удалена")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def create_query_interface(self):
        tk.Label(self.query_tab, text="SQL-запрос:").pack(pady=5)
        self.query_text = tk.Text(self.query_tab, height=10)
        self.query_text.pack(fill=tk.X, padx=5)

        btn_frame = tk.Frame(self.query_tab)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Выполнить", command=self.execute_query).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Выгрузить в CSV", command=self.export_to_csv).pack(side=tk.LEFT)

        self.query_tree = ttk.Treeview(self.query_tab, show='headings', height=15)
        self.query_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(self.query_tab, orient=tk.VERTICAL, command=self.query_tree.yview)
        self.query_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def execute_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            return

        try:
            self.cur.execute(query)
            if query.lower().startswith("select"):
                rows = self.cur.fetchall()
                columns = [desc[0] for desc in self.cur.description]

                self.query_tree["columns"] = columns
                for col in columns:
                    self.query_tree.heading(col, text=col)
                    self.query_tree.column(col, width=100, anchor='center')

                for i in self.query_tree.get_children():
                    self.query_tree.delete(i)

                for row in rows:
                    self.query_tree.insert('', 'end', values=row)

                self.status_var.set(f"Выполнено: {len(rows)} строк")
            else:
                self.conn.commit()
                messagebox.showinfo("Успех", "Запрос выполнен")
                self.status_var.set("Запрос выполнен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def export_to_csv(self):
        rows = []
        for child in self.query_tree.get_children():
            rows.append(self.query_tree.item(child)['values'])

        if not rows:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return

        columns = self.query_tree["columns"]
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
            messagebox.showinfo("Успех", "Данные выгружены в CSV")

    def create_service_interface(self):
        btn_frame = tk.Frame(self.service_tab)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Резервное копирование", command=self.backup_db).pack(pady=5)
        tk.Button(btn_frame, text="Восстановление", command=self.restore_db).pack(pady=5)
        tk.Button(btn_frame, text="Сброс в архив", command=self.archive_data).pack(pady=5)

    def backup_db(self):
        db_name = self.db_entry.get()
        file_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")])
        if file_path:
            try:
                subprocess.run(["pg_dump", "-U", self.user_entry.get(), "-h", self.host_entry.get(), "-p", self.port_entry.get(), db_name, "-f", file_path], check=True, env={"PGPASSWORD": self.pass_entry.get()})
                messagebox.showinfo("Успех", "Бэкап создан")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def restore_db(self):
        file_path = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql")])
        if file_path:
            db_name = self.db_entry.get()
            try:
                subprocess.run(["psql", "-U", self.user_entry.get(), "-h", self.host_entry.get(), "-p", self.port_entry.get(), "-d", db_name, "-f", file_path], check=True, env={"PGPASSWORD": self.pass_entry.get()})
                messagebox.showinfo("Успех", "БД восстановлена")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def archive_data(self):
        # Предполагаем, что есть таблица для архива, например, orders. Адаптировать под нужную.
        # Создаем VIEW для архивных данных и удаляем старые записи.
        table = "orders"  # Пример, заменить на реальную
        archive_view = "archive_orders"
        try:
            # Создаем VIEW из старых данных (например, старше года)
            self.cur.execute(f"""
                CREATE OR REPLACE VIEW {archive_view} AS
                SELECT * FROM {table} WHERE order_date < NOW() - INTERVAL '1 year'
            """)
            
            # Удаляем старые данные
            self.cur.execute(f"DELETE FROM {table} WHERE order_date < NOW() - INTERVAL '1 year'")
            self.conn.commit()
            messagebox.showinfo("Успех", f"Данные архивированы в VIEW {archive_view}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DBApp(root)
    root.mainloop()