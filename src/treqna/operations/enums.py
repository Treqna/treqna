from enum import Enum, IntEnum


class OperationCategory(Enum):
    READ = "read"
    WRITE = "write"
    INSPECT = "inspect"
    VALIDATE = "validate"
    REPAIR = "repair"
    NORMALIZE = "normalize"
    TRANSFORM = "transform"
    COMPRESS = "compress"
    DECOMPRESS = "decompress"
    EXTRACT = "extract"
    EMBED = "embed"
    ANALYZE = "analyze"
    PREVIEW = "preview"
    OPTIMIZE = "optimize"
    METADATA = "metadata"


class OperationPriority(IntEnum):
    LOW = 10
    NORMAL = 50
    HIGH = 80
    CRITICAL = 100


class OperationCapability(Enum):
    STREAMING = "streaming"
    THREAD_SAFE = "thread_safe"
    DETERMINISTIC = "deterministic"
    REVERSIBLE = "reversible"
    LOSSLESS = "lossless"
    BATCH_SUPPORT = "batch_support"
    ASYNC_SUPPORT = "async_support"
