from typing import Literal

from pydantic import BaseModel, Field

from ..services.diff import DiffHunk


class DiffRequest(BaseModel):
    text1: str
    text2: str


class DiffResponse(BaseModel):
    hunks: list[DiffHunk]


class CounterRequest(BaseModel):
    text_input: str
    filter_option: Literal["Character", "Word", "Line", "Custom Delimiter"] = "Character"
    custom_delimiter: str = ""


class CounterResponse(BaseModel):
    count: int
    output: str


class ColumnExtractorRequest(BaseModel):
    text: str
    column_number: int = Field(..., ge=1)
    delimiter: str = ","


class ColumnExtractorResponse(BaseModel):
    columns: list[str]


class TextRequest(BaseModel):
    text: str


class CleanTextResponse(BaseModel):
    cleaned: str


class TextStats(BaseModel):
    num_chars: int
    num_chars_no_space: int
    num_lines: int
    num_words: int
    num_sentences: int
    num_unique_words: int
    percent_unique_words: float
    length_shortest_word: int
    length_longest_word: int
    avg_word_length: float


class RandomNumberRequest(BaseModel):
    min_val: int = 0
    max_val: int = 100


class RandomNumberResponse(BaseModel):
    value: int


class RandomStringRequest(BaseModel):
    length: int = Field(16, ge=1, le=4096)


class RandomStringResponse(BaseModel):
    value: str


class ShuffleRequest(BaseModel):
    text: str


class ShuffleResponse(BaseModel):
    value: str
