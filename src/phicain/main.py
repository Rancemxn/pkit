# -*- coding: utf-8 -*-

import kivy
import time
import re

kivy.require("2.0.0")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import threading
import sys
import io
import shutil
from contextlib import redirect_stdout, redirect_stderr
from plyer import filechooser
import traceback

import unpack as t
from loguru import logger as loguru_global_logger
import logging


class KivyLoggingHandler(logging.Handler):
    def __init__(self, kivy_text_stream_writer):
        super().__init__()
        self.kivy_writer = kivy_text_stream_writer
        self.setFormatter(
            logging.Formatter(
                "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(processName)s (%(process)d) | %(threadName)s (%(thread)d) | %(filename)s:%(lineno)d | %(funcName)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    def emit(self, record):
        try:
            msg = self.format(record)
            level_name_upper = record.levelname.upper()
            color_hex = LOG_COLORS.get(level_name_upper, "FFFFFF")
            self.kivy_writer.write(msg + "\n")

        except Exception:
            self.handleError(record)


def remove_ansi_codes(text):
    if not text:
        return ""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


MAX_TEXTINPUT_CHARS = 20000
LOG_COLORS = {
    "DEBUG": "909090",
    "INFO": "FFFFFF",
    "SUCCESS": "00FF00",
    "WARNING": "FFFF00",
    "ERROR": "FF0000",
    "CRITICAL": "FF0000",
}


def kivy_markup_log_format(record):
    level_name = record["level"].name
    color_hex = LOG_COLORS.get(level_name, "FFFFFF")
    colored_message_template = f"[color={color_hex}]{{message}}[/color]"

    log_line_parts = [
        "{time:YYYY-MM-DD HH:mm:ss.SSS}",
        "| {level.name: <8}",
        "| {process.name} ({process.id})",
        "| {thread.name} ({thread.id})",
        "| {file.name}:{line}",
        "| {function}",
        f"| {colored_message_template}",
    ]

    if record["exception"]:
        exception_color = LOG_COLORS.get("ERROR", "FF0000")
        colored_exception_template = f"[color={exception_color}]{{exception}}[/color]"
        log_line_parts.append(f"\n{colored_exception_template}")

    log_line_parts.append("\n")

    final_format_string = " ".join(log_line_parts)

    return final_format_string


class KivyTextStream(io.TextIOBase):
    def __init__(
        self, text_input_update_callback, buffer_interval=0.2, max_buffer_size=8192
    ):
        super().__init__()
        self.text_input_update_callback = text_input_update_callback
        self._buffer = io.StringIO()
        self._lock = threading.Lock()
        self._buffer_interval = buffer_interval
        self._max_buffer_size = max_buffer_size
        self._schedule_event = None
        self._last_flush_time = time.time()

    def write(self, s):
        chars_written = 0
        with self._lock:
            chars_written = self._buffer.write(s)
            current_size = self._buffer.tell()
            now = time.time()
            if current_size >= self._max_buffer_size or (
                self._schedule_event is None
                and (now - self._last_flush_time) >= self._buffer_interval
            ):
                if self._schedule_event:
                    Clock.unschedule(self._schedule_event)
                    self._schedule_event = None
                self._schedule_flush_now()
            elif self._schedule_event is None:
                next_flush_delay = max(
                    0, self._buffer_interval - (now - self._last_flush_time)
                )
                self._schedule_event = Clock.schedule_once(
                    self._flush_buffer_to_ui, next_flush_delay
                )
        return chars_written

    def _schedule_flush_now(self):
        Clock.schedule_once(self._flush_buffer_to_ui, 0)

    def _flush_buffer_to_ui(self, dt):
        message_to_send = ""
        with self._lock:
            self._schedule_event = None
            self._last_flush_time = time.time()
            if self._buffer.tell() > 0:
                message_to_send = self._buffer.getvalue()
                self._buffer.seek(0)
                self._buffer.truncate(0)
            else:
                return
        if message_to_send:
            self.text_input_update_callback(message_to_send)

    def flush(self):
        with self._lock:
            if self._schedule_event:
                Clock.unschedule(self._schedule_event)
                self._schedule_event = None
            if self._buffer.tell() > 0:
                self._schedule_flush_now()

    def isatty(self):
        return True


class RealtimeOutputApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._last_ui_update_time = time.time()
        self._ui_update_pending = False
        self._deferred_scroll_event = None

    def build(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.button = Button(
            text="解包",
            size_hint_y=None,
            height="48dp",
            font_name="HYSongYunLangHeiW-1.ttf",
        )
        self.button.bind(on_press=self.start_task_and_capture_output)
        self.bcp = Button(
            text="复制",
            size_hint_y=None,
            height="48dp",
            font_name="HYSongYunLangHeiW-1.ttf",
        )
        self.bcp.bind(on_press=self.bcppp)

        self.output_text_area = TextInput(
            text="点击按钮开始...\n",
            readonly=True,
            multiline=True,
            font_name="HYSongYunLangHeiW-1.ttf",
        )
        self.output_text_area.markup = True
        layout.add_widget(self.button)
        layout.add_widget(self.bcp)
        layout.add_widget(self.output_text_area)
        return layout

    def update_output_on_main_thread(self, message_to_append):
        if self._ui_update_pending and (time.time() - self._last_ui_update_time < 0.1):
            return

        self._ui_update_pending = True
        current_text = self.output_text_area.text
        new_text = current_text + message_to_append

        if len(new_text) > MAX_TEXTINPUT_CHARS:
            new_text = new_text[-MAX_TEXTINPUT_CHARS:]
            first_newline_after_truncate = new_text.find("\n")
            if (
                first_newline_after_truncate != -1
                and first_newline_after_truncate < len(new_text) * 0.3
            ):
                new_text = new_text[first_newline_after_truncate + 1 :]

        if self.output_text_area.text != new_text:
            try:
                self.output_text_area.text = new_text
            except Exception as e:
                print(
                    f"ERROR setting TextInput text with markup: {e}",
                    file=sys.__stderr__,
                )
                plain_message = message_to_append.replace("[color=", "").replace(
                    "[/color]", ""
                )
                self.output_text_area.text = (
                    current_text + f"[KIVY_MARKUP_ERROR] {plain_message}"
                )

            if self._deferred_scroll_event:
                Clock.unschedule(self._deferred_scroll_event)
            self._deferred_scroll_event = Clock.schedule_once(
                self._scroll_to_bottom, 0.05
            )

        self._last_ui_update_time = time.time()
        self._ui_update_pending = False

    def _scroll_to_bottom(self, dt):
        if self.output_text_area:
            self.output_text_area.scroll_y = 0
        self._deferred_scroll_event = None

    def start_task_and_capture_output(self, instance):
        self.output_text_area.text = "[color=00ff00]任务开始，准备捕获输出...[/color]\n"
        self.button.disabled = True
        thread = threading.Thread(target=self.run_function_with_capture, daemon=True)
        thread.start()

    def run_function_with_capture(self):
        kivy_stream_adapter = KivyTextStream(
            self.update_output_on_main_thread,
            buffer_interval=0.3,
            max_buffer_size=8192,
        )
        loguru_sink_id = None
        kivy_std_logging_handler = None

        try:
            try:
                loguru_global_logger.remove()
            except ValueError:
                pass
            loguru_sink_id = loguru_global_logger.add(
                kivy_stream_adapter,
                format=kivy_markup_log_format,
                level="DEBUG",
                colorize=False,  # 让 {exception} 输出纯文本 traceback
            )
            if loguru_sink_id is None:
                loguru_global_logger.warning(
                    "[KivyApp] Loguru Kivy sink 添加可能失败。"
                )

            loguru_global_logger.info("--- Loguru Kivy Sink 已配置 ---")

            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            kivy_std_logging_handler = KivyLoggingHandler(kivy_stream_adapter)
            root_logger.addHandler(kivy_std_logging_handler)
            loguru_global_logger.info("--- Python 内置 logging Kivy Handler 已配置 ---")

            # --- 重定向 stdout 和 stderr ---
            loguru_global_logger.info("--- 标准流重定向已配置 ---")
            with (
                redirect_stdout(kivy_stream_adapter),
                redirect_stderr(kivy_stream_adapter),
            ):
                loguru_global_logger.info("准备执行")
                t.t()
                loguru_global_logger.success("执行完毕。")

            loguru_global_logger.info(
                "--- 目标函数执行完毕，流已恢复，准备移除处理器 ---"
            )

        except Exception as e:
            tb_str = traceback.format_exc()
            cleaned_tb = remove_ansi_codes(tb_str)  # 清理 traceback 的 ANSI
            final_error_message = (
                f"[color=ff0000]\n--- 捕获线程发生意外错误 ---\n{cleaned_tb}[/color]\n"
            )
            Clock.schedule_once(
                lambda dt: self.update_output_on_main_thread(final_error_message)
            )
        finally:
            if loguru_sink_id is not None:
                try:
                    loguru_global_logger.remove(loguru_sink_id)
                except:
                    pass
            if kivy_std_logging_handler:
                logging.getLogger().removeHandler(kivy_std_logging_handler)

            print("完成.")
            Clock.schedule_once(self.enable_button_on_main_thread)

    def enable_button_on_main_thread(self, dt):
        self.button.disabled = False

    def p(self):
        shutil.copytree("unpack-result", path, dirs_exist_ok=True)
        Clock.schedule_once(lambda dt: self.update_output_on_main_thread("完成\n"))

    def bcppp(self, *args, **kwargs):
        try:
            path = filechooser.choose_dir(title="请选择保存文件夹...")[0]

            Clock.schedule_once(
                lambda dt: self.update_output_on_main_thread(f"目标文件夹:{path}\n")
            )
            Clock.schedule_once(
                lambda dt: self.update_output_on_main_thread("正在复制, 请勿离开应用\n")
            )
            threading.Thread(target=self.p, daemon=True).start()
        except:
            pass


if __name__ == "__main__":
    RealtimeOutputApp().run()
