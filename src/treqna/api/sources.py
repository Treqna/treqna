from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, kw_only=True)
class DataSource(ABC):
    @property
    @abstractmethod
    def source_type(self) -> str:
        ...


@dataclass(frozen=True, kw_only=True)
class PathSource(DataSource):
    path: Path

    @property
    def source_type(self) -> str:
        return "path"


@dataclass(frozen=True, kw_only=True)
class BytesSource(DataSource):
    data: bytes

    @property
    def source_type(self) -> str:
        return "bytes"


@dataclass(frozen=True, kw_only=True)
class StreamSource(DataSource):
    stream: Any

    @property
    def source_type(self) -> str:
        return "stream"


@dataclass(frozen=True, kw_only=True)
class URLSource(DataSource):
    url: str

    @property
    def source_type(self) -> str:
        return "url"


@dataclass(frozen=True, kw_only=True)
class FolderSource(DataSource):
    folder_path: Path

    @property
    def source_type(self) -> str:
        return "folder"


def coerce_source(input_data: Any) -> DataSource:
    if isinstance(input_data, DataSource):
        return input_data
    if isinstance(input_data, Path):
        if input_data.is_dir():
            return FolderSource(folder_path=input_data)
        return PathSource(path=input_data)
    if isinstance(input_data, str):
        if input_data.startswith(("http://", "https://")):
            return URLSource(url=input_data)
        invalid_chars = ("<", ">", "{", "}")
        if "\n" not in input_data and not any(c in input_data for c in invalid_chars):
            try:
                p = Path(input_data)
                if p.exists():
                    if p.is_dir():
                        return FolderSource(folder_path=p)
                    return PathSource(path=p)
                is_path_like = (
                    len(input_data) < 260
                    and ("/" in input_data or "\\" in input_data or "." in input_data)
                )
                if is_path_like:
                    return PathSource(path=p)
            except OSError:
                pass
        return BytesSource(data=input_data.encode("utf-8"))
    if isinstance(input_data, bytes):
        return BytesSource(data=input_data)
    return StreamSource(stream=input_data)


def extract_raw_payload(source: DataSource) -> str | bytes:
    if isinstance(source, PathSource):
        if source.path.exists() and source.path.is_file():
            return source.path.read_bytes()
        return str(source.path)
    if isinstance(source, BytesSource):
        return source.data
    if isinstance(source, URLSource):
        return source.url
    if isinstance(source, FolderSource):
        return str(source.folder_path)
    if isinstance(source, StreamSource):
        if hasattr(source.stream, "read"):
            val = source.stream.read()
            if isinstance(val, (str, bytes)):
                return val
        return str(source.stream)
    return str(source)

