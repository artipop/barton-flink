from typing import Iterable, Tuple, Any

from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import ProcessWindowFunction


class SileroVadProcessWindowFunction(ProcessWindowFunction):
    def process(self, key: str, context: ProcessWindowFunction.Context,
                elements: Iterable[Tuple[str, int]]) -> Iterable[str]:
        count = 0
        for _ in elements:
            count += 1
        yield "Window: {} count: {}".format(context.window(), count)


class PyannoteVadProcessWindowFunction(ProcessWindowFunction):
    def process(self, key: str, context: ProcessWindowFunction.Context,
                elements: Iterable[Tuple[str, int]]) -> Iterable[str]:
        count = 0
        for _ in elements:
            count += 1
        yield "Window: {} count: {}".format(context.window(), count)


class SimpleTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value: Any, record_timestamp: int) -> int:
        return record_timestamp
