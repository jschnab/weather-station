import time
from dataclasses import dataclass
from enum import Enum
from typing import Literal

import RPi.GPIO as GPIO

from weather_station.utils.log import get_logger

LOGGER = get_logger()

INVALID_RESULT: float = -1.0
READ_RETRIES: int = 10
READ_RETRIES_INTERVAL: float = 0.1


class SensorError(Enum):
    NO_ERROR = 0
    MISSING_DATA = 1
    CHECKSUM = 2
    NO_DATA = 3


@dataclass
class SensorResult:
    error: SensorError
    temperature: float = INVALID_RESULT
    humidity: float = INVALID_RESULT

    @property
    def is_valid(self) -> bool:
        return all(
            [
                self.temperature != INVALID_RESULT,
                self.humidity != INVALID_RESULT,
            ]
        )

    @property
    def ok(self) -> bool:
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

    def read_retry(
        self,
        retries: int = READ_RETRIES,
        interval: float = READ_RETRIES_INTERVAL,
    ) -> SensorResult:
        for retn in range(retries):
            LOGGER.debug(f"Trying to read sensor data {retn + 1}/{retries}")
            result = self._read()
            if result.ok:
                LOGGER.debug("Read was successful")
                break
            LOGGER.debug(f"Sleeping for {interval} seconds")
            time.sleep(interval)
        else:
            LOGGER.debug("Read was not successful")
        return result

    def _read(self) -> SensorResult:
        LOGGER.debug(f"Setting up pin {self.pin} for output")
        GPIO.setup(self.pin, GPIO.OUT)
        LOGGER.debug(f"Pin {self.pin} is ready for output")

        # send initial high and pull down to low
        LOGGER.debug("Sending high-low pulse")
        self._send_and_sleep(GPIO.HIGH, 0.05)
        self._send_and_sleep(GPIO.LOW, 0.02)
        LOGGER.debug("Successfully sent high-low pulse")

        # change to input using pull up
        LOGGER.debug(f"Setting up pin {self.pin} for input using pull up")
        GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_UP)
        LOGGER.debug(f"Pin {self.pin} is ready for input using pull up")

        LOGGER.debug("Collecting input")
        data = self._collect_input()
        LOGGER.debug("Successfully collected input")

        pull_up_lengths = self._parse_pull_up_lengths(data)

        if len(pull_up_lengths) == 0:
            LOGGER.debug("No data was collected")
            return SensorResult(SensorError.NO_DATA)

        if len(pull_up_lengths) != 40:
            LOGGER.debug("Incomplete sensor data")
            return SensorResult(SensorError.MISSING_DATA)

        LOGGER.debug("Calculating bits")
        bits = self._calculate_bits(pull_up_lengths)
        LOGGER.debug("Successfully calculated bits")

        LOGGER.debug("Converting to bytes")
        bytes_ = self._bits_to_bytes(bits)
        LOGGER.debug("Successfully converting to bytes")

        if bytes_[4] != self.checksum(bytes_):
            LOGGER.debug("Bad checksum")
            return SensorResult(SensorError.CHECKSUM)

        LOGGER.debug("Sensor data is correct")
        return SensorResult(
            SensorError.NO_ERROR,
            self._calculate_temperature(bytes_),
            self._calculate_humidity(bytes_),
        )

    def _send_and_sleep(self, sig: Literal[0, 1], sleep: float) -> None:
        GPIO.output(self.pin, sig)
        time.sleep(sleep)

    def _collect_input(self) -> list[bool]:
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

    def _parse_pull_up_lengths(self, data: list[bool]) -> list[int]:
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

    def _calculate_bits(self, pull_up_lengths: list[int]) -> list[int]:
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

    def _bits_to_bytes(self, bits: list[int]) -> list[int]:
        bytes_ = []
        byte = 0

        for idx in range(len(bits)):
            byte <<= 1
            byte |= bits[idx]
            if (idx + 1) % 8 == 0:
                bytes_.append(byte)
                byte = 0

        return bytes_

    def checksum(self, bytes_: list[int]) -> int:
        return bytes_[0] + bytes_[1] + bytes_[2] + bytes_[3] & 255

    def _calculate_temperature(self, bytes_: list[int]) -> float:
        temp = (((bytes_[2] & 0x7F) << 8) + bytes_[3]) / 10
        if temp > 125:
            return bytes_[2]
        if bytes_[2] & 0x80:
            return -temp
        return temp

    def _calculate_humidity(self, bytes_: list[int]) -> float:
        return (((bytes_[0] & 0x7F) << 8) + bytes_[1]) / 10
