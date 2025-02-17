import npyscreen

class MenuForm(npyscreen.Form):
    def create(self):
        # Define las opciones del menú
        self.menu_options = [
            "File", "Edit", "View", "Help"
        ]
        # Agrega el widget MultiLine para el menú principal
        self.menu = self.add(npyscreen.MultiLine, 
                            values=self.menu_options, 
                            max_height=len(self.menu_options) + 2, 
                            scroll_exit=True)
        self.menu.when_cursor_moved = self.update_submenu

        # Agrega el widget MultiLine para el submenú
        self.submenu = self.add(npyscreen.MultiLine, 
                                relx=20, 
                                rely=2, 
                                max_height=5, 
                                values=[],
                                scroll_exit=True)

    def update_submenu(self):
        # Determina el índice del elemento seleccionado
        selected_index = self.menu.value
        # Opciones de submenú basadas en la opción seleccionada
        submenus = {
            0: ["New", "Open", "Save", "Exit"],
            1: ["Cut", "Copy", "Paste"],
            2: ["Toolbar", "Sidebar"],
            3: ["About", "Documentation"]
        }
        # Actualiza los valores del submenú si la selección es válida
        if selected_index is not None and selected_index in submenus:
            self.submenu.values = submenus[selected_index]
        else:
            self.submenu.values = []
        self.submenu.display()

class TestApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', MenuForm)

if __name__ == "__main__":
    app = TestApp()
    app.run()
