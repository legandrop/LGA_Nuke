"""
_______________________________________________________________________________________________________________

  LGA_Render_Complete v1.2 | Lega
  Calcula la duracion al finalizar el render y la agrega en un knob en el tab User del nodo write
  Reproduce un sonido y envia un correo con los detalles del render si la opcion 'Send Mail' esta activada

  Para enviar mail hay que crear 3 variables de entorno con la informacion del mail que envia y el que recibe
  el que envia tiene que ser de Outlook.
  Las tres variables se crean asi:
  setx Nuke_Write_Mail_From "tuMail@outlook.com"
  setx Nuke_Write_Mail_Pass "tuPass"
  setx Nuke_Write_Mail_To "tuMail@gmail.com"
_______________________________________________________________________________________________________________

"""

import nuke
import os
import datetime
from PySide2.QtMultimedia import QSound
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import platform

# --- Configuración de archivo INI para settings de mail ---
CONFIG_FILE_NAME = "RenderComplete.ini"
CONFIG_SECTION = "Mail"
CONFIG_FROM_KEY = "from_email"
CONFIG_PASS_KEY = "from_password"
CONFIG_TO_KEY = "to_email"


def get_config_path():
    """Devuelve la ruta completa al archivo de configuración de mail."""
    try:
        appdata_path = os.getenv("APPDATA")
        if not appdata_path:
            print("Error: No se pudo encontrar la variable de entorno APPDATA.")
            return None
        config_dir = os.path.join(appdata_path, "LGA", "ToolPack")
        return os.path.join(config_dir, CONFIG_FILE_NAME)
    except Exception as e:
        print(f"Error al obtener la ruta de configuración: {e}")
        return None


def ensure_config_exists():
    """
    Asegura que el directorio de configuración y el archivo .ini existan.
    Si no existen, los crea con valores vacíos.
    """
    config_file_path = get_config_path()
    if not config_file_path:
        return
    config_dir = os.path.dirname(config_file_path)
    try:
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            print(f"Directorio de configuración creado: {config_dir}")
        if not os.path.exists(config_file_path):
            config = configparser.ConfigParser()
            config[CONFIG_SECTION] = {
                CONFIG_FROM_KEY: "",
                CONFIG_PASS_KEY: "",
                CONFIG_TO_KEY: "",
            }
            with open(config_file_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)
            print(
                f"Archivo de configuración creado: {config_file_path}. Por favor, complételo con sus datos de mail."
            )
    except Exception as e:
        print(f"Error al asegurar la configuración: {e}")


def get_mail_settings_from_config():
    """
    Lee los datos de mail desde el archivo .ini.
    Devuelve (from_email, from_password, to_email) o (None, None, None) si hay errores o faltan datos.
    """
    config_file_path = get_config_path()
    if not config_file_path or not os.path.exists(config_file_path):
        print(
            f"Archivo de configuración no encontrado en la ruta esperada: {config_file_path}"
        )
        return None, None, None
    try:
        config = configparser.ConfigParser()
        config.read(config_file_path, encoding="utf-8")
        if (
            config.has_section(CONFIG_SECTION)
            and config.has_option(CONFIG_SECTION, CONFIG_FROM_KEY)
            and config.has_option(CONFIG_SECTION, CONFIG_PASS_KEY)
            and config.has_option(CONFIG_SECTION, CONFIG_TO_KEY)
        ):
            from_email = config.get(CONFIG_SECTION, CONFIG_FROM_KEY).strip()
            from_password = config.get(CONFIG_SECTION, CONFIG_PASS_KEY).strip()
            to_email = config.get(CONFIG_SECTION, CONFIG_TO_KEY).strip()
            if from_email and from_password and to_email:
                return from_email, from_password, to_email
            else:
                print(f"Uno o más datos de mail en {config_file_path} están vacíos.")
                return None, None, None
        else:
            missing = []
            if not config.has_section(CONFIG_SECTION):
                missing.append(f"Sección [{CONFIG_SECTION}]")
            if not config.has_option(CONFIG_SECTION, CONFIG_FROM_KEY):
                missing.append(f"Clave {CONFIG_FROM_KEY}")
            if not config.has_option(CONFIG_SECTION, CONFIG_PASS_KEY):
                missing.append(f"Clave {CONFIG_PASS_KEY}")
            if not config.has_option(CONFIG_SECTION, CONFIG_TO_KEY):
                missing.append(f"Clave {CONFIG_TO_KEY}")
            print(
                f"Configuración incompleta en {config_file_path}. Falta: {', '.join(missing)}"
            )
            return None, None, None
    except configparser.Error as e:
        print(f"Error al leer el archivo de configuración {config_file_path}: {e}.")
        return None, None, None
    except Exception as e:
        print(f"Error inesperado al leer la configuración: {e}.")
        return None, None, None


# Asegurarse de que el archivo de configuración existe al iniciar
ensure_config_exists()


def start_time():
    if not nuke.root().knob("Km_Render_Start_Time"):
        nuke.root().addKnob(nuke.EvalString_Knob("Km_Render_Start_Time"))
        nuke.root().knob("Km_Render_Start_Time").setVisible(False)

    Current_time_str = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    nuke.root().knob("Km_Render_Start_Time").setValue(Current_time_str)


def total_time():
    time1_str = nuke.root().knob("Km_Render_Start_Time").getValue()
    time1 = datetime.datetime.strptime(time1_str, "%Y-%m-%d %H:%M:%S")
    time2 = datetime.datetime.now()
    duration = time2 - time1
    duration_in_s = duration.total_seconds()
    hours, remainder = divmod(duration_in_s, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


def send_email(subject, body, to_email=None):
    from_email, password, default_to_email = get_mail_settings_from_config()
    if not from_email or not password or not default_to_email:
        config_path = get_config_path() or "AppData\\LGA\\ToolPack\\RenderComplete.ini"
        print(
            f"No se pudieron leer los datos de mail desde: {config_path}\nRevise la consola para detalles y asegúrese de que el archivo esté completo."
        )
        return
    if to_email is None:
        to_email = default_to_email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP("smtp.office365.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.close()
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar correo: {e}")


def add_render_time_knob(write_node, render_time):
    if not write_node.knobs().get("render_time"):
        render_time_knob = nuke.String_Knob("render_time", "Render Time")
        write_node.addKnob(render_time_knob)
    write_node["render_time"].setValue(render_time)


def Render_Complete():
    render_time = total_time()

    # Reproducir el sonido
    sound_file_path = os.path.join(os.path.dirname(__file__), "LGA_Render_Complete.wav")
    QSound.play(sound_file_path)

    # Verificar si el knob "send_mail" existe y esta activado
    write_node = nuke.thisNode()
    send_mail_state = False
    if "send_mail" in write_node.knobs():
        send_mail_state = write_node["send_mail"].value()

    # Agregar o actualizar el knob con el tiempo de render
    add_render_time_knob(write_node, render_time)

    if send_mail_state:
        # Obtener el destinatario del correo electronico de las variables de entorno
        to_email = os.getenv("Nuke_Write_Mail_To", "default_to_email@example.com")

        # Formatear el cuerpo del correo
        script_name = os.path.basename(nuke.root().name())
        render_directory = os.path.dirname(write_node.knob("file").value())
        render_file = write_node.knob("file").getEvaluatedValue()
        body = (
            f"Script Name: {script_name}\n"
            f"Render Directory: {render_directory}\n"
            f"Render File: {render_file}\n"
            f"Render Time: {render_time}\n"
            "El render ha finalizado exitosamente."
        )

        # Enviar correo electronico
        send_email(subject="Render Finished", body=body, to_email=to_email)


# Agregar callbacks de Nuke
nuke.addBeforeRender(start_time)
nuke.addAfterRender(Render_Complete)
