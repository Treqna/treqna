from enum import Enum, auto


class OperationEnum(Enum):
    DETECT = auto()
    INSPECT = auto()
    PARSE = auto()
    GENERATE_UDM = auto()
    TRANSFORM = auto()
    VALIDATE = auto()
    WRITE = auto()
    FINALIZE = auto()


class PipelineStageEnum(Enum):
    DETECT = "detect"
    INSPECT = "inspect"
    PARSE = "parse"
    GENERATE_UDM = "generate_udm"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    WRITE = "write"
    FINALIZE = "finalize"


class StageEnum(Enum):
    DETECT = "detect"
    INSPECT = "inspect"
    PARSE = "parse"
    GENERATE_UDM = "generate_udm"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    WRITE = "write"
    FINALIZE = "finalize"


class ResultStatusEnum(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class UDMValueKindEnum(Enum):
    PRIMITIVE = "primitive"
    TEXT = "text"
    BINARY = "binary"
    TABULAR = "tabular"
    HIERARCHICAL = "hierarchical"
    COLLECTION = "collection"
    OBJECT = "object"
