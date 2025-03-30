import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Literal

import RPi.GPIO as GPIO

INVALID_RESULT: float = -1.0
READ_RETRIES: int = 10


class SensorError(Enum):
    NO_ERROR = 0
    MISSING_DATA = 1
    CHECKSUM = 2
    NOT_FOUND = 3


@dataclass
class SensorResult:
    error: SensorError
    temperature: float = INVALID_RESULT
    humidity: float = INVALID_RESULT

    @property
    def is_valid(self):
        return all(
            [
                self.temperature != INVALID_RESULT,
                self.humidity != INVALID_RESULT,
            ]
        )

    @property
    def ok(self):
        return self.error == SensorError.NO_ERROR


class SensorState(Enum):
    INIT_PULL_DOWN = 0
    INIT_PULL_UP = 1
    DATA_FIRST_PULL_DOWN = 2
    DATA_PULL_UP = 3
    DATA_PULL_DOWN = 4


class DHT22:
    def __init__(self, pin: int) -> None:
        GPIO.setmode(GPIO.BCM)
        self.pin = pin

    def read_retry(self, retries: int = READ_RETRIES) -> SensorResult:
        for _ in range(retries):
            result = self._read()
            if result.ok:
                break
        return result

    def _read(self) -> SensorResult:
        GPIO.setup(self.pin, GPIO.OUT)

        # send initial high and pull down to low
        self._send_and_sleep(GPIO.HIGH, 0.05)
        self._send_and_sleep(GPIO.LOW, 0.02)

        # change to input using pull up
        GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_UP)

        data = self._collect_input()

        pull_up_lengths = self._parse_pull_up_lengths(data)

        if len(pull_up_lengths) == 0:
            return SensorResult(SensorError.NOT_FOUND)

        if len(pull_up_lengths) != 40:
            return SensorResult(SensorError.MISSING_DATA)

        bits = self._calculate_bits(pull_up_lengths)

        bytes_ = self._bits_to_bytes(bits)

        if bytes_[4] != self.checksum(bytes_):
            return SensorResult(SensorError.CHECKSUM)

        return SensorResult(
            SensorError.NO_ERROR,
            self._calculate_temperature(bytes_),
            self._calculate_humidity(bytes_),
        )

    def _send_and_sleep(self, sig: Literal[0, 1], sleep: float) -> None:
        GPIO.output(self.pin, sig)
        time.sleep(sleep)

    def _collect_input(self) -> List[bool]:
        cnt = 0
        cnt_limit = 100
        last = -1
        data = []

        # loop until input does not change for 'limit' times
        while True:
            cur = GPIO.input(self.pin)
            data.append(cur)
            if last != cur:
                cnt = 0
                last = cur
            else:
                cnt += 1
                if cnt > cnt_limit:
                    break

        return data

    def _parse_pull_up_lengths(self, data: List[bool]) -> List[int]:
        state = SensorState.INIT_PULL_DOWN
        lengths = []
        cur_length = 0

        for idx in range(len(data)):
            cur = data[idx]
            cur_length += 1

            match state:
                case SensorState.INIT_PULL_DOWN:
                    if cur == GPIO.LOW:
                        state = SensorState.INIT_PULL_UP

                case SensorState.INIT_PULL_UP:
                    if cur == GPIO.HIGH:
                        state = SensorState.DATA_FIRST_PULL_DOWN

                case SensorState.DATA_FIRST_PULL_DOWN:
                    if cur == GPIO.LOW:
                        state = SensorState.DATA_PULL_UP

                case SensorState.DATA_PULL_UP:
                    # the length of this pull up will determine if it is 0 or 1
                    if cur == GPIO.HIGH:
                        cur_length = 0
                        state = SensorState.DATA_PULL_DOWN

                case SensorState.DATA_PULL_DOWN:
                    if cur == GPIO.LOW:
                        # pulled down, store the length of the previous pull
                        # up period
                        lengths.append(cur_length)
                        state = SensorState.DATA_PULL_UP

        return lengths

    def _calculate_bits(self, pull_up_lengths: List[int]) -> List[int]:
        # find shortest and longest periods
        shortest = 1000
        longest = 0

        for idx in range(len(pull_up_lengths)):
            length = pull_up_lengths[idx]
            shortest = min(shortest, length)
            longest = max(longest, length)

        # use the halfway to determine whether the priod is long or short
        half = shortest + (longest - shortest) / 2
        bits = []

        for idx in range(len(pull_up_lengths)):
            bits.append(int(pull_up_lengths[idx] > half))

        return bits

    def _bits_to_bytes(self, bits: List[int]) -> List[int]:
        bytes_ = []
        byte = 0

        for idx in range(len(bits)):
            byte <<= 1
            byte |= bits[idx]
            if (idx + 1) % 8 == 0:
                bytes_.append(byte)
                byte = 0

        return bytes_

    def checksum(self, bytes_) -> int:
        return bytes_[0] + bytes_[1] + bytes_[2] + bytes_[3] & 255

    def _calculate_temperature(self, bytes_) -> float:
        temp = float(((bytes_[2] & 0x7F) << 8) + bytes_[3]) / 10
        if temp > 125:
            return bytes_[2]
        if bytes_[2] & 0x80:
            return -temp
        return temp

    def _calculate_humidity(self, bytes_) -> float:
        return ((bytes_[0] << 8) + bytes_[1]) / 10
