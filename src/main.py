import asyncio
import itertools
import os
from enum import Enum
from pathlib import Path
from shutil import copy2
from typing import Callable, Optional

import psutil
from nicegui import ui

BIBLE_BOOKS = {
    "Genesis": {"name": "Genesis", "abbreviations": ["Gen", "Ge", "Gn"], "number": 1},
    "Exodus": {"name": "Exodus", "abbreviations": ["Ex", "Exo", "Exod"], "number": 2},
    "Leviticus": {
        "name": "Leviticus",
        "abbreviations": ["Lev", "Le", "Lv"],
        "number": 3,
    },
    "Numbers": {
        "name": "Numbers",
        "abbreviations": ["Num", "Nu", "Nm", "Nb"],
        "number": 4,
    },
    "Deuteronomy": {
        "name": "Deuteronomy",
        "abbreviations": ["Deut", "Deu", "De", "Dt"],
        "number": 5,
    },
    "Joshua": {"name": "Joshua", "abbreviations": ["Josh", "Jos", "Jsh"], "number": 6},
    "Judges": {
        "name": "Judges",
        "abbreviations": ["Judg", "Jdg", "Jg", "Jdgs"],
        "number": 7,
    },
    "Ruth": {
        "name": "Ruth",
        "abbreviations": ["Ruth", "Rut", "Rth", "Ru"],
        "number": 8,
    },
    "1 Samuel": {
        "name": "1 Samuel",
        "abbreviations": [
            "1Sam",
            "1sa",
            "1 Sam",
            "1 Sm",
            "1 Sa",
            "1 S",
            "I Sam",
            "I Sa",
            "1Sa",
            "1S",
            "1st Samuel",
            "1st Sam",
            "First Samuel",
            "First Sam",
        ],
        "number": 9,
    },
    "2 Samuel": {
        "name": "2 Samuel",
        "abbreviations": [
            "2Sam",
            "2Sa",
            "2 Sam",
            "2 Sm",
            "2 Sa",
            "2 S",
            "II Sam",
            "II Sa",
            "2Sa",
            "2S",
            "2nd Samuel",
            "2nd Sam",
            "Second Samuel",
            "Second Sam",
        ],
        "number": 10,
    },
    "1 Kings": {
        "name": "1 Kings",
        "abbreviations": [
            "1 Kings",
            "1 Kgs",
            "1 Ki",
            "1Kgs",
            "1Kin",
            "1Ki",
            "1K",
            "I Kgs",
            "I Ki",
            "1st Kings",
            "1st Kgs",
            "First Kings",
            "First Kgs",
        ],
        "number": 11,
    },
    "2 Kings": {
        "name": "2 Kings",
        "abbreviations": [
            "2 Kings",
            "2 Kgs",
            "2 Ki",
            "2Kgs",
            "2Kin",
            "2Ki",
            "2K",
            "II Kgs",
            "II Ki",
            "2nd Kings",
            "2nd Kgs",
            "Second Kings",
            "Second Kgs",
        ],
        "number": 12,
    },
    "1 Chronicles": {
        "name": "1 Chronicles",
        "abbreviations": [
            "1 Chron",
            "1 Chr",
            "1 Ch",
            "1Chron",
            "1Chr",
            "1Ch",
            "I Chron",
            "I Chr",
            "I Ch",
            "1st Chronicles",
            "1st Chron",
            "First Chronicles",
            "First Chron",
        ],
        "number": 13,
    },
    "2 Chronicles": {
        "name": "2 Chronicles",
        "abbreviations": [
            "2 Chron",
            "2 Chr",
            "2 Ch",
            "2Chron",
            "2Chr",
            "2Ch",
            "II Chron",
            "II Chr",
            "II Ch",
            "2nd Chronicles",
            "2nd Chron",
            "Second Chronicles",
            "Second Chron",
        ],
        "number": 14,
    },
    "Ezra": {"name": "Ezra", "abbreviations": ["Ezra", "Ezr", "Ez"], "number": 15},
    "Nehemiah": {"name": "Nehemiah", "abbreviations": ["Neh", "Ne"], "number": 16},
    "Esther": {"name": "Esther", "abbreviations": ["Esth", "Est", "Es"], "number": 17},
    "Job": {"name": "Job", "abbreviations": ["Job", "Jb"], "number": 18},
    "Psalm": {
        "name": "Psalm",
        "abbreviations": ["Psalm", "Psa", "Ps", "Pslm", "Psm", "Pss"],
        "number": 19,
    },
    "Proverbs": {
        "name": "Proverbs",
        "abbreviations": ["Prov", "Pro", "Prv", "Pr"],
        "number": 20,
    },
    "Ecclesiastes": {
        "name": "Ecclesiastes",
        "abbreviations": ["Ecc", "Eccles", "Eccle", "Ecc", "Ec", "Qoh"],
        "number": 21,
    },
    "Song of Solomon": {
        "name": "Song of Solomon",
        "abbreviations": [
            "Song",
            "SOS",
            "Song of Songs",
            "So",
            "Canticle of Canticles",
            "Canticles",
            "Cant",
        ],
        "number": 22,
    },
    "Isaiah": {"name": "Isaiah", "abbreviations": ["Isa", "Is"], "number": 23},
    "Jeremiah": {
        "name": "Jeremiah",
        "abbreviations": ["Jer", "Je", "Jr"],
        "number": 24,
    },
    "Lamentations": {
        "name": "Lamentations",
        "abbreviations": ["Lam", "La"],
        "number": 25,
    },
    "Ezekiel": {
        "name": "Ezekiel",
        "abbreviations": ["Ezek", "Eze", "Ezk"],
        "number": 26,
    },
    "Daniel": {"name": "Daniel", "abbreviations": ["Dan", "Da", "Dn"], "number": 27},
    "Hosea": {"name": "Hosea", "abbreviations": ["Hos", "Hi"], "number": 28},
    "Joel": {"name": "Joel", "abbreviations": ["Joel", "Joe", "Jl"], "number": 29},
    "Amos": {"name": "Amos", "abbreviations": ["Amos", "Amo", "Am"], "number": 30},
    "Obadiah": {
        "name": "Obadiah",
        "abbreviations": ["Obad", "Oba", "Ob"],
        "number": 31,
    },
    "Jonah": {"name": "Jonah", "abbreviations": ["Jonah", "Jon", "Jnh"], "number": 32},
    "Micah": {"name": "Micah", "abbreviations": ["Mic", "Mc"], "number": 33},
    "Nahum": {"name": "Nahum", "abbreviations": ["Nah", "Na", "Nam"], "number": 34},
    "Habakkuk": {"name": "Habakkuk", "abbreviations": ["Hab", "Hb"], "number": 35},
    "Zephaniah": {
        "name": "Zephaniah",
        "abbreviations": ["Zeph", "Zep", "Zp"],
        "number": 36,
    },
    "Haggai": {"name": "Haggai", "abbreviations": ["Hag", "Hg"], "number": 37},
    "Zechariah": {
        "name": "Zechariah",
        "abbreviations": ["Zech", "Zec", "Zc"],
        "number": 38,
    },
    "Malachi": {"name": "Malachi", "abbreviations": ["Mal", "Ml"], "number": 39},
    "Matthew": {
        "name": "Matthew",
        "abbreviations": ["Mat", "Matt", "Mt"],
        "number": 40,
    },
    "Mark": {
        "name": "Mark",
        "abbreviations": ["Mark", "Mar", "Mrk", "Mk", "Mr"],
        "number": 41,
    },
    "Luke": {"name": "Luke", "abbreviations": ["Luke", "Lik", "Lk", "Luk"], "number": 42},
    "John": {
        "name": "John",
        "abbreviations": ["John", "Joh", "Jhn", "Jn"],
        "number": 43,
    },
    "Acts": {"name": "Acts", "abbreviations": ["Acts", "Act", "Ac"], "number": 44},
    "Romans": {"name": "Romans", "abbreviations": ["Rom", "Ro", "Rm"], "number": 45},
    "1 Corinthians": {
        "name": "1 Corinthians",
        "abbreviations": [
            "1 Cor",
            "1 Co",
            "I Cor",
            "I Co",
            "1Cor",
            "1Co",
            "I Corinthians",
            "1Corinthians",
            "1st Corinthians",
            "First Corinthians",
        ],
        "number": 46,
    },
    "2 Corinthians": {
        "name": "2 Corinthians",
        "abbreviations": [
            "2 Cor",
            "2 Co",
            "II Cor",
            "II Co",
            "2Cor",
            "2Co",
            "II Corinthians",
            "2Corinthians",
            "2nd Corinthians",
            "Second Corinthians",
        ],
        "number": 47,
    },
    "Galatians": {"name": "Galatians", "abbreviations": ["Gal", "Ga"], "number": 48},
    "Ephesians": {"name": "Ephesians", "abbreviations": ["Eph", "Ephes"], "number": 49},
    "Philippians": {
        "name": "Philippians",
        "abbreviations": ["Phil", "Php", "Pp"],
        "number": 50,
    },
    "Colossians": {"name": "Colossians", "abbreviations": ["Col", "Co"], "number": 51},
    "1 Thessalonians": {
        "name": "1 Thessalonians",
        "abbreviations": [
            "1 Thess",
            "1 Thes",
            "1 Th",
            "I Thessalonians",
            "I Thess",
            "I Thes",
            "I Th",
            "1Thessalonians",
            "1Thess",
            "1Thes",
            "1Th",
            "1st Thessalonians",
            "1st Thess",
            "First Thessalonians",
            "First Thess",
        ],
        "number": 52,
    },
    "2 Thessalonians": {
        "name": "2 Thessalonians",
        "abbreviations": [
            "2 Thess",
            "2 Thes",
            "2 Th",
            "II Thessalonians",
            "II Thess",
            "II Thes",
            "II Th",
            "2Thessalonians",
            "2Thess",
            "2Thes",
            "2Th",
            "2nd Thessalonians",
            "2nd Thess",
            "Second Thessalonians",
            "Second Thess",
        ],
        "number": 53,
    },
    "1 Timothy": {
        "name": "1 Timothy",
        "abbreviations": [
            "1 Tim",
            "1 Ti",
            "I Timothy",
            "I Tim",
            "I Ti",
            "1Timothy",
            "1Tim",
            "1Ti",
            "1st Timothy",
            "1st Tim",
            "First Timothy",
            "First Tim",
        ],
        "number": 54,
    },
    "2 Timothy": {
        "name": "2 Timothy",
        "abbreviations": [
            "2 Tim",
            "2 Ti",
            "II Timothy",
            "II Tim",
            "II Ti",
            "2Timothy",
            "2Tim",
            "2Ti",
            "2nd Timothy",
            "2nd Tim",
            "Second Timothy",
            "Second Tim",
        ],
        "number": 55,
    },
    "Titus": {"name": "Titus", "abbreviations": ["Titus", "Tit", "Ti"], "number": 56},
    "Philemon": {
        "name": "Philemon",
        "abbreviations": ["Phi", "Phm", "Philem", "Pm"],
        "number": 57,
    },
    "Hebrews": {"name": "Hebrews", "abbreviations": ["Heb"], "number": 58},
    "James": {
        "name": "James",
        "abbreviations": ["James", "Jam", "Jas", "Jm"],
        "number": 59,
    },
    "1 Peter": {
        "name": "1 Peter",
        "abbreviations": [
            "1 Pet",
            "1 Pe",
            "1 Pt",
            "1 P",
            "I Pet",
            "I Pt",
            "I Pe",
            "1Peter",
            "1Pet",
            "1Pe",
            "1Pt",
            "1P",
            "I Peter",
            "1st Peter",
            "First Peter",
        ],
        "number": 60,
    },
    "2 Peter": {
        "name": "2 Peter",
        "abbreviations": [
            "2 Pet",
            "2 Pe",
            "2 Pt",
            "2 P",
            "II Peter",
            "II Pet",
            "II Pt",
            "II Pe",
            "2Peter",
            "2Pet",
            "2Pe",
            "2Pt",
            "2P",
            "2nd Peter",
            "Second Peter",
        ],
        "number": 61,
    },
    "1 John": {
        "name": "1 John",
        "abbreviations": [
            "1 John",
            "1 Jhn",
            "1 Jn",
            "1 J",
            "1John",
            "1Jhn",
            "1Joh",
            "1Jn",
            "1Jo",
            "1J",
            "I John",
            "I Jhn",
            "I Joh",
            "I Jn",
            "I Jo",
            "1st John",
            "First John",
        ],
        "number": 62,
    },
    "2 John": {
        "name": "2 John",
        "abbreviations": [
            "2 John",
            "2 Jhn",
            "2 Jn",
            "2 J",
            "2John",
            "2Jhn",
            "2Joh",
            "2Jn",
            "2Jo",
            "2J",
            "II John",
            "II Jhn",
            "II Joh",
            "II Jn",
            "II Jo",
            "2nd John",
            "Second John",
        ],
        "number": 63,
    },
    "3 John": {
        "name": "3 John",
        "abbreviations": [
            "3 John",
            "3 Jhn",
            "3 Jn",
            "3 J",
            "3John",
            "3Jhn",
            "3Joh",
            "3Jn",
            "3Jo",
            "3J",
            "III John",
            "III Jhn",
            "III Joh",
            "III Jn",
            "III Jo",
            "3rd John",
            "Third John",
        ],
        "number": 64,
    },
    "Jude": {
        "name": "Jude",
        "abbreviations": ["Jude", "Jde", "Jud", "Jd"],
        "number": 65,
    },
    "Revelation": {
        "name": "Revelation",
        "abbreviations": ["Rev", "Re", "The Revelation"],
        "number": 66,
    },
}

BIBLE_BOOK_NUMBERS = {}
for book_data in BIBLE_BOOKS.values():
    BIBLE_BOOK_NUMBERS[book_data["name"].lower()] = book_data["number"]
    for abbreviation in book_data["abbreviations"]:
        BIBLE_BOOK_NUMBERS[abbreviation.lower()] = book_data["number"]


class BibleSection(Enum):
    FULL = 0
    OLD = 1
    NEW = 2


def get_bible_book_number(book: str, section=BibleSection.FULL):
    book_num = BIBLE_BOOK_NUMBERS.get(book.lower())
    if book_num is None:
        return None
    if section == BibleSection.NEW and book_num < 40:
        return None
    if section == BibleSection.OLD and book_num >= 40:
        return None
    return (
        book_num
        if section in (BibleSection.FULL, BibleSection.OLD)
        else (book_num - 40) + 1
    )


def fix_filename(filename: str, file_id: int) -> str:
    filename_parts = filename.split("_") if "_" in filename else filename.split(" ")
    if len(filename_parts) > 0:
        first_part = filename_parts[0]
        last_part = filename_parts[-1]

        try:
            last_part_number = int(last_part.lower().replace(".mp3", ""))
        except ValueError:
            last_part_number = None

        if last_part_number:
            return f"{str(last_part_number).zfill(3)} {first_part}.mp3"
        else:
            try:
                first_part_number = int(first_part_number.lower().replace(".mp3", ""))
            except ValueError:
                first_part_number = None
            if first_part_number:
                return filename
    return f"{str(file_id).zfill(3)} {filename}"

def home_directory() -> str:
    return os.path.expanduser("~")


def connected_drives() -> dict:
    partitions = psutil.disk_partitions(all=True)
    return {
        partition.mountpoint: partition.device.replace("\\", "")
        for partition in partitions
        if partition.fstype != ""
    }


def home_drive() -> str:
    partitions = psutil.disk_partitions(all=True)
    return next(
        (p for p in partitions if home_directory().startswith(p.mountpoint)), None
    )


class DriveSelect(ui.select):
    def __init__(self, label: str = "Drive", on_change: Optional[Callable] = None):
        options = connected_drives()

        super().__init__(
            options=options, label=label, on_change=on_change, with_input=False
        )

        self.classes("w-1/4")


class FolderPicker(ui.dialog):
    def __init__(
        self, label: Optional[str] = None, drive_label: Optional[str] = "Drive"
    ):
        super().__init__()

        with self, ui.card():
            if label:
                ui.label(label)
            with ui.row().classes("w-full justify-start"):
                self.drive = DriveSelect(
                    label=drive_label, on_change=lambda: self.update_grid(True)
                )
            self.grid = (
                ui.aggrid(
                    {
                        "columnDefs": [{"field": "name", "headerName": "Folder"}],
                        "rowSelection": "single",
                    },
                    html_columns=[0],
                )
                .classes("w-96")
                .on("cellDoubleClicked", self.handle_double_click)
            )
            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=self.close).props("outline")
                ui.button("Select", on_click=self._handle_select)

            if self.drive.value is None:
                user_drive = home_drive()
                if user_drive is None:
                    return
                drive_path = user_drive.mountpoint
                self.drive.value = drive_path
            else:
                drive_path = self.drive.value
            self.path = Path(drive_path)
            self.last_selection = self.path
            self.update_grid(False)

    def update_grid(self, drive_changed=False):
        if drive_changed:
            if self.drive.value is None:
                user_drive = home_drive()
                if user_drive is None:
                    return
                drive_path = user_drive.mountpoint
            else:
                drive_path = self.drive.value
            self.path = Path(drive_path)
            self.last_selection = self.path

        paths = list(p for p in self.path.glob("*") if p.is_dir())

        self.grid.options["rowData"] = [
            {
                "name": f"📁 <strong>{p.name}</strong>",
                "path": str(p),
            }
            for p in paths
        ]

        parent = str(self.path.parent)
        if parent and parent != "":
            self.grid.options["rowData"].insert(
                0,
                {
                    "name": "📁 <strong>..</strong>",
                    "path": parent,
                },
            )
        self.grid.update()

    async def handle_double_click(self, msg: dict) -> None:
        self.path = Path(msg["args"]["data"]["path"])
        self.last_selection = self.path
        self.update_grid(False)

    async def _handle_select(self):
        rows = await ui.run_javascript(
            f"getElement({self.grid.id}).gridOptions.api.getSelectedRows()"
        )
        selection = list([r["path"] for r in rows])
        if len(selection) <= 0:
            selection = self.last_selection
        else:
            selection = selection[0]
        self.submit(str(selection))


def pick_folder(label: str, input_ctr: ui.input):
    async def _pick_folder():
        folder = await FolderPicker(label)
        if folder:
            input_ctr.set_value(folder)

    return _pick_folder


def handle_export_contents(
    content_type: str, src_directory: str, dst_directory: str, dst_name: str = "01"
):
    if content_type == "Bible":
        section = BibleSection.FULL
    elif content_type == "New Testament":
        section = BibleSection.NEW
    elif content_type == "Old Testament":
        section = BibleSection.OLD
    else:
        section = None

    subfolder_map = dict()
    root_folder = os.path.join(dst_directory, dst_name)
    root_path = Path(root_folder)
    subfolder_map[src_dir] = root_path
    for dirpath, dirnames, filenames in os.walk(src_directory):
        has_mp3 = any(f.endswith(".mp3") for f in filenames)
        if len(dirnames) == 0 and not has_mp3:
            continue

        subfolder_ids = itertools.count(start=1)
        for dirname in dirnames:
            subfolder = os.path.join(dirpath, dirname)
            if not any(f.endswith(".mp3") for f in os.listdir(subfolder)):
                continue

            sub_dst_path = Path(
                os.path.join(dst_directory, subfolder.replace(src_directory, ""))
            )
            sub_dst_id = (
                next(subfolder_ids)
                if section is None
                else get_bible_book_number(sub_dst_path.name, section)
            )
            if sub_dst_id is None or sub_dst_id <= 0:
                if section is None:
                    sub_dst_id = next(subfolder_ids)
                else:
                    raise ValueError(f"Could not resolve the book number for {sub_dst_path.name}")

            subfolder_path = Path(os.path.join(root_path, str(sub_dst_id).zfill(2)))
            subfolder_path.mkdir(parents=True, exist_ok=True)
            subfolder_map[subfolder] = subfolder_path

        file_ids = itertools.count(start=1)
        for filename in filenames:
            if filename.endswith(".mp3"):
                if dirpath in subfolder_map:
                    dest_folder_path = subfolder_map[dirpath]
                else:
                    dest_folder_path = root_path

                src_file = Path(os.path.join(dirpath, filename))
                dest_file = Path(
                    os.path.join(
                        dest_folder_path, fix_filename(filename, next(file_ids))
                    )
                )
                copy2(src_file, dest_file)


async def export_contents():
    results.clear()
    save_button.disable()
    with results:
        ui.spinner("dots", size="xl")
    try:
        await asyncio.to_thread(
            handle_export_contents,
            content_type.value,
            src_dir.value,
            dst_dir.value,
            dst_name.value,
        )
    except Exception as ex:
        ui.notify(f"Error: {ex}", position="top", type="negative")
    else:
        ui.notify("Content Saved!", position="top", type="positive")
    finally:
        src_dir.clear()
        dst_dir.clear()
        dst_name.set_value("01")
        results.clear()
        save_button.enable()


ui.colors(primary="#C53030", secondary="#429300")
with ui.row():
    ui.label("SeedPlayer Content Tool").classes(
        "text-2xl font-bold leading-tight text-red-700"
    )
with ui.row().classes("w-full"):
    content_type = ui.select(
        options=["Bible", "Old Testament", "New Testament", "Other"],
        label="Content Type",
        value="Bible",
    ).classes("w-1/2")
with ui.row():
    with ui.column():
        with ui.input("Source Directory") as src_dir:
            ui.button(
                on_click=pick_folder("Please Select Source Content Folder", src_dir),
            ).props("icon=create_new_folder flat")
    with ui.column().bind_visibility_from(src_dir, "value"):
        with ui.input("Destination Directory") as dst_dir:
            ui.button(
                on_click=pick_folder(
                    "Please Select Destination Content Folder", dst_dir
                ),
            ).props("icon=create_new_folder flat")
        dst_name = ui.input(
            label="Destination Folder Name", placeholder="Folder Name", value="01"
        )
with ui.row().bind_visibility_from(dst_dir, "value"):
    save_button = ui.button("Save", on_click=export_contents).props(
        "icon-right=save_alt"
    )
results = ui.row().classes("w-full justify-center")


ui.run(
    native=True,
    window_size=(800, 600),
    fullscreen=False,
    reload=False,
    title="SeedPlayer Content Tool",
    favicon="🌱",
)
