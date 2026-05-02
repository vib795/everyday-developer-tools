import random
import re
import string

from fastapi import APIRouter

from ..schemas.string_tools import (
    CleanTextResponse,
    ColumnExtractorRequest,
    ColumnExtractorResponse,
    CounterRequest,
    CounterResponse,
    DiffRequest,
    DiffResponse,
    RandomNumberRequest,
    RandomNumberResponse,
    RandomStringRequest,
    RandomStringResponse,
    ShuffleRequest,
    ShuffleResponse,
    TextRequest,
    TextStats,
)
from ..services.diff import structured_diff

router = APIRouter(prefix="/api/string", tags=["string"])


@router.post("/diff", response_model=DiffResponse)
def diff(payload: DiffRequest) -> DiffResponse:
    return DiffResponse(hunks=structured_diff(payload.text1, payload.text2))


@router.post("/count", response_model=CounterResponse)
def counter(payload: CounterRequest) -> CounterResponse:
    text = payload.text_input
    if payload.filter_option == "Character":
        return CounterResponse(count=len(text), output="\n".join(text))
    if payload.filter_option == "Word":
        words = text.split()
        return CounterResponse(count=len(words), output="\n".join(words))
    if payload.filter_option == "Line":
        return CounterResponse(count=len(text.split("\n")), output=text)
    delim = payload.custom_delimiter
    if not delim:
        return CounterResponse(count=0, output="")
    parts = text.split(delim)
    return CounterResponse(count=len(parts), output=delim.join(parts))


@router.post("/columns", response_model=ColumnExtractorResponse)
def columns(payload: ColumnExtractorRequest) -> ColumnExtractorResponse:
    idx = payload.column_number - 1
    extracted: list[str] = []
    for line in payload.text.split("\n"):
        cells = line.split(payload.delimiter)
        if len(cells) > idx:
            extracted.append(cells[idx].strip())
    return ColumnExtractorResponse(columns=extracted)


@router.post("/clean", response_model=CleanTextResponse)
def clean(payload: TextRequest) -> CleanTextResponse:
    text = re.sub(r"\s+", " ", payload.text).strip()
    text = re.sub(r"([.!?])\s*", r"\1 ", text)
    parts = re.split(r"([.!?] )", text)
    cleaned = "".join(s.capitalize() if i % 2 == 0 else s for i, s in enumerate(parts))
    return CleanTextResponse(cleaned=cleaned)


@router.post("/stats", response_model=TextStats)
def stats(payload: TextRequest) -> TextStats:
    text = payload.text
    words = text.split()
    num_words = len(words)
    num_chars = len(text)
    num_chars_no_space = len(text.replace(" ", ""))
    num_lines = text.count("\n") + 1 if text else 0
    num_sentences = len(re.findall(r"[.!?]", text))
    word_lengths = [len(w) for w in words]
    unique_words = set(words)
    return TextStats(
        num_chars=num_chars,
        num_chars_no_space=num_chars_no_space,
        num_lines=num_lines,
        num_words=num_words,
        num_sentences=num_sentences,
        num_unique_words=len(unique_words),
        percent_unique_words=(len(unique_words) / num_words) * 100 if num_words else 0,
        length_shortest_word=min(word_lengths) if word_lengths else 0,
        length_longest_word=max(word_lengths) if word_lengths else 0,
        avg_word_length=sum(word_lengths) / num_words if num_words else 0,
    )


@router.post("/random-number", response_model=RandomNumberResponse)
def random_number(payload: RandomNumberRequest) -> RandomNumberResponse:
    lo, hi = payload.min_val, payload.max_val
    if lo > hi:
        lo, hi = hi, lo
    return RandomNumberResponse(value=random.randint(lo, hi))


@router.post("/random-string", response_model=RandomStringResponse)
def random_string(payload: RandomStringRequest) -> RandomStringResponse:
    chars = string.ascii_letters + string.digits + string.punctuation
    return RandomStringResponse(value="".join(random.choice(chars) for _ in range(payload.length)))


@router.post("/shuffle", response_model=ShuffleResponse)
def shuffle(payload: ShuffleRequest) -> ShuffleResponse:
    text = payload.text
    return ShuffleResponse(value="".join(random.sample(text, len(text))) if text else "")
