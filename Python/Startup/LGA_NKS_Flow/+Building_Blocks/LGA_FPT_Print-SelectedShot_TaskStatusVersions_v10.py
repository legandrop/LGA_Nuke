"""

Imprime la version en Hiero, version en ShotGrid (SG), estado de la version en SG,
descripcion y URLs de las tareas asociadas para los clips seleccionados en el timeline.
Tambien imprime los comentarios que haya en la version del clip seleccionado
Esta version nueva imprime la descripcion del shot, de la task, y el tiempo estimado y fecha de inicio y fin de la task
v08: agrega la fecha de update del shot y de la task
v10: muestra de manera limpia los attachments con frame numbers y links de descarga

"""

import hiero.core
import os
import re
import shotgun_api3
import sys


class ShotGridManager:
    def __init__(self, url, login, password):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)

    def find_shot_and_tasks(self, project_name, shot_code):
        projects = self.sg.find(
            "Project", [["name", "is", project_name]], ["id", "name"]
        )
        if projects:
            project_id = projects[0]["id"]
            filters = [
                ["project", "is", {"type": "Project", "id": project_id}],
                ["code", "is", shot_code],
            ]
            fields = ["id", "code", "description"]
            shots = self.sg.find("Shot", filters, fields)
            if shots:
                shot_id = shots[0]["id"]
                tasks = self.find_tasks_for_shot(shot_id)
                return shots[0], tasks
            else:
                print("No se encontro el shot.")
        else:
            print("No se encontro el proyecto en ShotGrid.")
        return None, None

    def find_tasks_for_shot(self, shot_id):
        filters = [["entity", "is", {"type": "Shot", "id": shot_id}]]
        fields = [
            "id",
            "content",
            "sg_description",
            "sg_status_list",
            "sg_estimated_days",
            "start_date",
            "due_date",
        ]
        return self.sg.find("Task", filters, fields)

    def find_version_by_code(self, shot_id, version_code):
        filters = [
            ["entity", "is", {"type": "Shot", "id": shot_id}],
            ["code", "contains", version_code],
        ]
        fields = ["id", "code", "created_at", "user", "sg_status_list", "description"]
        versions = self.sg.find("Version", filters, fields)
        return versions

    def get_task_url(self, task_id):
        return f"{self.sg.base_url}/detail/Task/{task_id}"

    def get_version_notes(self, version_id):
        filters = [["note_links", "in", {"type": "Version", "id": version_id}]]
        fields = ["content", "user"]
        return self.sg.find("Note", filters, fields)

    def get_version_notes_debug(self, version_id):
        """Obtiene notas con TODOS los campos posibles para debugging"""
        filters = [["note_links", "in", {"type": "Version", "id": version_id}]]
        # Intentar obtener todos los campos posibles
        fields = [
            "id",
            "content",
            "user",
            "created_at",
            "updated_at",
            "subject",
            "note_links",
            "attachments",
            "sg_status_list",
            "sg_note_type",
            "sg_frame_number",
            "sg_frame_range",
            "sg_timecode",
            "sg_annotation_links",
            "sg_review_notes",
            "sg_client_note",
            "sg_internal_note",
            "sg_department",
            "sg_priority",
            "sg_addressings_cc",
            "sg_addressings_to",
            "sg_note_from",
            "sg_note_to",
            "sg_playlist",
            "sg_version",
            "sg_media_url",
            "sg_uploaded_movie",
            "sg_uploaded_movie_frame_rate",
            "sg_uploaded_movie_image",
            "sg_uploaded_movie_mp4",
            "sg_uploaded_movie_webm",
            "sg_annotation_image",
            "sg_annotation_data",
        ]
        return self.sg.find("Note", filters, fields)

    def get_attachment_details(self, attachment_id):
        """Obtiene todos los detalles de un attachment especifico"""
        filters = [["id", "is", attachment_id]]
        fields = [
            "id",
            "code",
            "description",
            "this_file",
            "image",
            "sg_file_type",
            "created_at",
            "updated_at",
            "created_by",
            "sg_status_list",
            "attachment_links",
            "sg_path_to_movie",
            "sg_path_to_frames",
            "sg_uploaded_movie",
            "url",
            "local_path",
            "local_path_linux",
            "local_path_mac",
            "local_path_windows",
            "local_storage",
        ]
        attachments = self.sg.find("Attachment", filters, fields)
        return attachments[0] if attachments else None

    def extract_frame_from_attachment_name(self, attachment_name):
        """Extrae el numero de frame del nombre del attachment"""
        if ".png" in attachment_name:
            # Buscar patron como "annot_version_51150.16.png"
            frame_match = re.search(r"\.(\d+)\.png$", attachment_name)
            if frame_match:
                return frame_match.group(1)
        return "Unknown"

    def get_attachment_download_url(self, attachment_details):
        """Extrae la URL de descarga del attachment"""
        if attachment_details.get("this_file") and isinstance(
            attachment_details["this_file"], dict
        ):
            return attachment_details["this_file"].get("url", "No URL found")
        return "No URL found"


class HieroOperations:
    def __init__(self, shotgrid_manager):
        self.sg_manager = shotgrid_manager

    def parse_exr_name(self, file_name):
        base_name = re.sub(r"_%04d\.exr$", "", file_name)
        version_match = re.search(r"_v(\d+)", base_name)
        version_number = version_match.group(1) if version_match else "Unknown"
        return base_name, version_number

    def process_selected_clips(self):
        seq = hiero.ui.activeSequence()
        if seq:
            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()
            if selected_clips:
                for clip in selected_clips:
                    file_path = clip.source().mediaSource().fileinfos()[0].filename()
                    exr_name = os.path.basename(file_path)
                    base_name, hiero_version_number = self.parse_exr_name(exr_name)
                    project_name = base_name.split("_")[0]
                    parts = base_name.split("_")
                    shot_code = "_".join(parts[:5])

                    shot, tasks = self.sg_manager.find_shot_and_tasks(
                        project_name, shot_code
                    )
                    if shot:
                        # Imprimir la descripcion del shot
                        print(f"- Shot name: {shot['code']}")
                        print(
                            f"  Description: {shot.get('description', 'No description available')}"
                        )

                        # Mostrar la informacion de la tarea Comp antes de verificar versiones
                        comp_task = next(
                            (task for task in tasks if "Comp" in task["content"]), None
                        )
                        if comp_task:
                            estimated_days = comp_task.get("sg_estimated_days", 0)
                            print(
                                f"- Task: {comp_task['content']} (Status: {comp_task['sg_status_list']})"
                            )
                            print(
                                f"  Description: {comp_task.get('sg_description', 'No description available')}"
                            )
                            print(
                                f"  Start Date: {comp_task.get('start_date', 'No start date available')}"
                            )
                            print(
                                f"  Due Date: {comp_task.get('due_date', 'No due date available')}"
                            )
                            print(f"  Estimated Duration: {estimated_days} days")
                            print(
                                f"  URL: {self.sg_manager.get_task_url(comp_task['id'])}"
                            )

                        # Luego verificar si hay versiones disponibles
                        versions = self.sg_manager.find_version_by_code(
                            shot["id"], f"_v{hiero_version_number}"
                        )
                        if versions:
                            version = versions[
                                0
                            ]  # Assuming the first match is the correct version
                            print(f"- Version Hiero: v{hiero_version_number}")
                            print(f"- Version SG: {version['code']}")
                            print(f"- Version SG status: {version['sg_status_list']}")
                            print(f"- Description: {version['description']}")

                            notes = self.sg_manager.get_version_notes(version["id"])
                            if notes:
                                print("  - Comments:")
                                for note in notes:
                                    print(
                                        f"    - {note['content']} (User: {note['user']['name']})"
                                    )
                            else:
                                print("  - No comments found.")

                            # Obtener notas con attachments y mostrar de manera organizada
                            debug_notes = self.sg_manager.get_version_notes_debug(
                                version["id"]
                            )

                            if debug_notes:
                                print("\n  - Comments with Review Attachments:")

                                for note in debug_notes:
                                    # Mostrar el comentario
                                    user_name = (
                                        note["user"]["name"]
                                        if note.get("user")
                                        else "Unknown"
                                    )
                                    print(
                                        f"    • \"{note['content']}\" (by {user_name})"
                                    )

                                    # Mostrar attachments de este comentario
                                    if note.get("attachments"):
                                        for attachment_ref in note["attachments"]:
                                            attachment_id = attachment_ref["id"]
                                            attachment_details = (
                                                self.sg_manager.get_attachment_details(
                                                    attachment_id
                                                )
                                            )

                                            if attachment_details:
                                                frame_number = self.sg_manager.extract_frame_from_attachment_name(
                                                    attachment_ref["name"]
                                                )
                                                download_url = self.sg_manager.get_attachment_download_url(
                                                    attachment_details
                                                )

                                                print(
                                                    f"      → Frame {frame_number}: {attachment_ref['name']}"
                                                )
                                                print(
                                                    f"        Download: {download_url}"
                                                )
                                    else:
                                        print("      → No attachments")
                                    print()  # Linea en blanco entre comentarios
                            else:
                                print("\n  - No comments with attachments found.")
                        else:
                            print(
                                f"No versions found for Hiero version v{hiero_version_number} in ShotGrid."
                            )
                    else:
                        print("No se encontro el shot correspondiente en ShotGrid.")
            else:
                print("No se han seleccionado clips en el timeline.")
        else:
            print("No se encontro una secuencia activa en Hiero.")


def main():
    global msg_manager
    sg_url = os.getenv("SHOTGRID_URL")
    sg_login = os.getenv("SHOTGRID_LOGIN")
    sg_password = os.getenv("SHOTGRID_PASSWORD")

    if not sg_url or not sg_login or not sg_password:
        print(
            "Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas."
        )
        return

    sg_manager = ShotGridManager(sg_url, sg_login, sg_password)
    hiero_ops = HieroOperations(sg_manager)
    hiero_ops.process_selected_clips()


if __name__ == "__main__":
    main()
