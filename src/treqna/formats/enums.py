from enum import Enum, IntEnum


class FormatFamily(Enum):
    STRUCTURED = "structured"
    TABULAR = "tabular"
    HIERARCHICAL = "hierarchical"
    BINARY = "binary"
    TEXT = "text"
    DOCUMENT = "document"
    GRAPH = "graph"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    ARCHIVE = "archive"
    CUSTOM = "custom"


class FormatCapability(Enum):
    READ = "read"
    WRITE = "write"
    STREAM_READ = "stream_read"
    STREAM_WRITE = "stream_write"
    METADATA_EXTRACT = "metadata_extract"
    METADATA_EMBED = "metadata_embed"
    VALIDATE_SCHEMA = "validate_schema"
    REPAIR_SYNTAX = "repair_syntax"
    PREVIEW_GENERATE = "preview_generate"


class EncodingEnum(Enum):
    UTF8 = "utf-8"
    UTF16 = "utf-16"
    UTF32 = "utf-32"
    ASCII = "ascii"
    LATIN1 = "latin-1"
    BINARY = "binary"
    AUTO_DETECT = "auto_detect"


class CompressionEnum(Enum):
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    XZ = "xz"
    ZIP = "zip"
    TAR = "tar"
    ZSTD = "zstd"


class StreamingEnum(Enum):
    UNSUPPORTED = "unsupported"
    INPUT_ONLY = "input_only"
    OUTPUT_ONLY = "output_only"
    BIDIRECTIONAL = "bidirectional"


class MetadataSupportEnum(Enum):
    NONE = "none"
    BASIC = "basic"
    EXTENDED = "extended"
    FULL = "full"


class RepairSupportEnum(Enum):
    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"


class PreviewSupportEnum(Enum):
    NONE = "none"
    TEXTUAL = "textual"
    THUMBNAIL = "thumbnail"
    FULL_RENDER = "full_render"


class ValidationSupportEnum(Enum):
    NONE = "none"
    SYNTAX_ONLY = "syntax_only"
    SCHEMA_STRICT = "schema_strict"


class PluginPriority(IntEnum):
    LOW = 10
    NORMAL = 50
    HIGH = 80
    CRITICAL = 100
