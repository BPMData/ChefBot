"""Recipe conversations, saved on the device so you can come back to them."""
import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

log = logging.getLogger("chefbot")


def data_dir() -> Path:
    # Flet sets FLET_APP_STORAGE_DATA to the app's private folder on phones and in packaged apps.
    base = os.environ.get("FLET_APP_STORAGE_DATA") or str(Path.home() / ".chefbot")
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass
class Conversation:
    """One recipe and everything said about it.

    `messages` holds what the model sees (system, user, assistant). Pictures live in `photos`,
    keyed by the index of the assistant message they belong to, so they never go to the model.
    """
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created: float = field(default_factory=time.time)
    updated: float = field(default_factory=time.time)
    title: str = "New recipe"
    settings: dict = field(default_factory=dict)
    messages: list[dict] = field(default_factory=list)
    photos: dict[str, str] = field(default_factory=dict)   # str(message index) -> file name

    def chat_messages(self) -> list[dict]:
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]


class History:
    def __init__(self, folder: Path | None = None):
        self.folder = folder or data_dir()
        self.file = self.folder / "conversations.json"
        self.photo_dir = self.folder / "photos"
        self.photo_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[Conversation]:
        try:
            raw = json.loads(self.file.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError):
            raw = None
        if not isinstance(raw, list):
            # Unreadable: move it aside instead of letting the next save() write over every saved recipe.
            backup = self.file.with_name(f"conversations.unreadable-{int(time.time())}.json")
            self.file.replace(backup)
            log.warning("Saved recipes were unreadable; kept them as %s and started a fresh list", backup.name)
            return []
        convs = []
        for item in raw:
            try:
                convs.append(Conversation(**item))
            except TypeError:
                continue
        return sorted(convs, key=lambda c: c.updated, reverse=True)

    def save(self, conv: Conversation) -> None:
        conv.updated = time.time()
        convs = [c for c in self.load() if c.id != conv.id]
        convs.insert(0, conv)
        self._write(convs)       # no cap: recipes stay until you delete them

    def delete(self, conv_id: str) -> None:
        convs = self.load()
        for c in convs:
            if c.id == conv_id:
                self._delete_photos(c)
        self._write([c for c in convs if c.id != conv_id])

    def save_photo(self, conv: Conversation, message_index: int, image: bytes) -> Path:
        name = f"{conv.id}-{message_index}.png"
        path = self.photo_dir / name
        path.write_bytes(image)
        conv.photos[str(message_index)] = name
        return path

    def prune_photos(self, keep: set[str] | frozenset[str] = frozenset()) -> int:
        """Delete photo files no saved conversation uses (e.g. after deleting a message). `keep` names files that
        are still needed though not saved (a reply in progress, an edit that may be undone). Returns how many."""
        used = {name for c in self.load() for name in c.photos.values()} | set(keep)
        gone = 0
        for f in self.photo_dir.glob("*.png"):
            if f.name not in used:
                f.unlink(missing_ok=True)
                gone += 1
        return gone

    def photo_path(self, name: str) -> Path:
        return self.photo_dir / name

    def _delete_photos(self, conv: Conversation) -> None:
        for name in conv.photos.values():
            (self.photo_dir / name).unlink(missing_ok=True)

    def _write(self, convs: list[Conversation]) -> None:
        tmp = self.file.with_suffix(".tmp")
        tmp.write_text(json.dumps([asdict(c) for c in convs], ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.file)
