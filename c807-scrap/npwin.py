import urwid
import mysql.connector

# Conexión a la base de datos MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="production_db"
    )

def get_data_from_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders_issues;")
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def insert_into_db(title, order_id, status_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO orders_issues (title, order_id, status_id) VALUES (%s, %s, %s)",
                   (title, order_id, status_id))
    connection.commit()
    cursor.close()
    connection.close()

def update_db(id, title, order_id, status_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE orders_issues SET title = %s, order_id = %s, status_id = %s WHERE id = %s",
                   (title, order_id, status_id, id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_from_db(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM orders_issues WHERE id = %s", (id,))
    connection.commit()
    cursor.close()
    connection.close()

class CRUDApp:
    def __init__(self):
        self.palette = [
            ('header', 'white', 'dark blue'),
            ('body', 'light gray', 'black'),
            ('button', 'light cyan', 'black'),
            ('button focus', 'white', 'dark cyan', 'bold'),
            ('reversed', 'standout', ''),
            ('border', 'yellow', 'black'),
        ]

        self.main_menu = urwid.Padding(
            urwid.LineBox(
                urwid.ListBox(urwid.SimpleFocusListWalker([
                    urwid.AttrMap(urwid.Button("Ver todos los registros", on_press=self.show_table), None, focus_map='button focus'),
                    urwid.AttrMap(urwid.Button("Crear nuevo registro", on_press=self.create_new_record), None, focus_map='button focus'),
                    urwid.AttrMap(urwid.Button("Salir", on_press=self.exit_program), None, focus_map='button focus'),
                ])),
                title=" Menú Principal ",
                tlcorner='╔', tline='═', lline='║',
                trcorner='╗', rline='║', blcorner='╚', bline='═', brcorner='╝',
                title_attr='header'
            ),
            left=2, right=2
        )
        self.main_loop = urwid.MainLoop(self.main_menu, self.palette, unhandled_input=self.handle_input)
        self.main_loop.run()

    def show_table(self, button):
        data = get_data_from_db()
        body = [urwid.Text("ID | Título | Order ID | Status ID")]
        body.extend([urwid.AttrMap(urwid.Button(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}",
                                                on_press=self.show_detail, user_data=row),
                                   None, focus_map='button focus') for row in data])
        body.append(urwid.AttrMap(urwid.Button("Volver al Menú Principal", on_press=self.back_to_main), None, focus_map='button focus'))

        table_box = urwid.LineBox(
            urwid.ListBox(urwid.SimpleFocusListWalker(body)),
            title=" Lista de Issues ",
            tlcorner='╔', tline='═', lline='║',
            trcorner='╗', rline='║', blcorner='╚', bline='═', brcorner='╝',
            title_attr='header'
        )
        self.main_loop.widget = urwid.Padding(table_box, left=2, right=2)

    def show_detail(self, button, data):
        detail_text = urwid.Text(f"ID: {data[0]}\nTítulo: {data[1]}\nOrder ID: {data[2]}\nStatus ID: {data[3]}")
        options = urwid.Pile([
            detail_text,
            urwid.AttrMap(urwid.Button("Editar", on_press=self.edit_record, user_data=data), None, focus_map='button focus'),
            urwid.AttrMap(urwid.Button("Eliminar", on_press=self.delete_record, user_data=data), None, focus_map='button focus'),
            urwid.AttrMap(urwid.Button("Volver al Menú Principal", on_press=self.back_to_main), None, focus_map='button focus'),
        ])

        detail_box = urwid.LineBox(
            urwid.Filler(options),
            title=" Detalles del Issue ",
            tlcorner='╔', tline='═', lline='║',
            trcorner='╗', rline='║', blcorner='╚', bline='═', brcorner='╝',
            title_attr='header'
        )
        self.main_loop.widget = urwid.Padding(detail_box, left=2, right=2)

    def create_new_record(self, button):
        self.show_form(None)

    def edit_record(self, button, data):
        self.show_form(data)

    def show_form(self, data):
        if data:
            title = urwid.Edit("Título: ", data[1])
            order_id = urwid.Edit("Order ID: ", str(data[2]))
            status_id = urwid.Edit("Status ID: ", str(data[3]))
        else:
            title = urwid.Edit("Título: ")
            order_id = urwid.Edit("Order ID: ")
            status_id = urwid.Edit("Status ID: ")

        save_button = urwid.AttrMap(urwid.Button("Guardar", on_press=self.save_record, user_data=(data[0] if data else None, title, order_id, status_id)), None, focus_map='button focus')
        back_button = urwid.AttrMap(urwid.Button("Cancelar", on_press=self.back_to_main), None, focus_map='button focus')

        form_box = urwid.LineBox(
            urwid.Filler(urwid.Pile([title, order_id, status_id, save_button, back_button])),
            title=" Formulario de Issue ",
            tlcorner='╔', tline='═', lline='║',
            trcorner='╗', rline='║', blcorner='╚', bline='═', brcorner='╝',
            title_attr='header'
        )
        self.main_loop.widget = urwid.Padding(form_box, left=2, right=2)

    def save_record(self, button, data):
        id, title, order_id, status_id = data
        if id:
            update_db(id, title.edit_text, int(order_id.edit_text), int(status_id.edit_text))
        else:
            insert_into_db(title.edit_text, int(order_id.edit_text), int(status_id.edit_text))
        self.back_to_main(button)

    def delete_record(self, button, data):
        delete_from_db(data[0])
        self.back_to_main(button)

    def back_to_main(self, button):
        self.main_loop.widget = self.main_menu

    def exit_program(self, button):
        raise urwid.ExitMainLoop()

    def handle_input(self, key):
        if key in ('q', 'Q'):
            self.exit_program(None)

if __name__ == '__main__':
    CRUDApp()
