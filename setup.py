from cx_Freeze import setup, Executable

setup(
    name="Nombre de tu aplicación",
    version="1.0",
    description="Descripción de tu aplicación",
    executables=[Executable("test.py")]
)