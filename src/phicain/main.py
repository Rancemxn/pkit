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
from contextlib import redirect_stdout, redirect_stderr
import traceback

import unpack as t
from loguru import logger as loguru_global_logger
import logging


class KivyLoggingHandler(logging.Handler):
    def __init__(self, kivy_text_stream_writer):
        super().__init__()
        self.kivy_writer = kivy_text_stream_writer
        # 为 logging 模块的日志定义一个接近 Loguru 的格式，但不含 Kivy Markup
        # Kivy Markup 应该由 Loguru 的 format 函数专门处理
        self.setFormatter(
            logging.Formatter(
                "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(processName)s (%(process)d) | %(threadName)s (%(thread)d) | %(filename)s:%(lineno)d | %(funcName)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    def emit(self, record):
        try:
            msg = self.format(record)
            # 我们希望 logging 的输出也可能有颜色，但这需要更复杂的逻辑，
            # 或者接受它们是纯文本，或者让 KivyTextStream 尝试解析一些基本模式。
            # 为了简单，这里我们先让它输出纯文本，可以考虑后续添加 Markup。
            # 例如，根据 record.levelname 给 msg 包裹颜色。
            level_name_upper = record.levelname.upper()
            color_hex = LOG_COLORS.get(
                level_name_upper, "FFFFFF"
            )  # 使用之前定义的 LOG_COLORS

            # 手动为 logging 的消息添加颜色 markup
            # 注意：Formatter 中的 %(message)s 已经是实际消息了
            # 我们需要一种方式只给消息本身加颜色，或者给整行加颜色。
            # 这里简单地给整行日志基于级别添加一个通用颜色（如果需要）。
            # 更精细的控制会更复杂。
            # 为了与 Loguru 行为一致（Loguru 的 format 函数处理颜色），这里我们只传递格式化后的消息。
            # 如果要颜色，KivyLoggingHandler 的 formatter 或者 emit 需要更复杂。
            # 简单起见，logging 的日志暂时不加 Kivy Markup 颜色，以免与 Loguru 混淆或增加复杂性。
            # 或者，我们创建一个函数，将 logging.LogRecord 转换为类似 Loguru record 的字典，
            # 然后传递给 kivy_markup_log_format，但这可能过度设计了。

            # --- 简化：logging 的日志暂时不加 Kivy Markup 颜色 ---
            # --- 如果需要，可以在这里添加 Markup，但要注意格式 ---
            # color_prefix = f"[color={color_hex}]"
            # color_suffix = "[/color]"
            # styled_msg = f"{color_prefix}{msg}{color_suffix}"
            # self.kivy_writer.write(styled_msg + '\n')

            self.kivy_writer.write(msg + "\n")  # 先保持纯文本

        except Exception:
            self.handleError(record)


def remove_ansi_codes(text):
    if not text:
        return ""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


# 你的目标函数（被执行的函数）
def function_that_prints_stuff():
    loguru_global_logger.debug("这是一个 DEBUG 级别的消息。")
    loguru_global_logger.info("这是一个 INFO 级别的消息。")
    loguru_global_logger.success("这是一个 SUCCESS 级别的消息。")  # Loguru 特有的
    loguru_global_logger.warning("这是一个 WARNING 级别的消息。")
    loguru_global_logger.error("这是一个 ERROR 级别的消息。")
    try:
        x = 1 / 0
    except ZeroDivisionError:
        loguru_global_logger.exception("发生了一个异常！")  # 会包含 traceback

    print("一条普通的 print 输出 (无颜色)")

    # 调用你的 unpack.t()
    loguru_global_logger.info("准备调用 unpack.t()...")
    t.t()
    loguru_global_logger.info("unpack.t() 调用完毕。")


MAX_TEXTINPUT_CHARS = 20000  # 可以适当再调整
# KIVY_MARKUP_FORMATTER 是一个函数，用于根据日志级别返回 Kivy Markup 颜色标签
# 你可以根据自己的喜好定义颜色 (十六进制 RGB)
LOG_COLORS = {
    "DEBUG": "909090",  # 灰色
    "INFO": "FFFFFF",  # 白色 (假设 TextInput 背景是暗色) 或 "000000" (如果背景亮色)
    "SUCCESS": "00FF00",  # 绿色
    "WARNING": "FFFF00",  # 黄色
    "ERROR": "FF0000",  # 红色
    "CRITICAL": "FF0000",  # 红色 (通常和 ERROR 一样或更醒目)
}


def kivy_markup_log_format(record):
    level_name = record["level"].name
    color_hex = LOG_COLORS.get(level_name, "FFFFFF")

    # 构建包含 Loguru 令牌的字符串模板
    # 我们只对颜色部分使用 Python 的 .format()
    # 其他 {token} 留给 Loguru 处理

    # 核心消息部分，用 Kivy Markup 包裹 Loguru 的 {message} 令牌
    colored_message_template = f"[color={color_hex}]{{message}}[/color]"  # 注意这里的 {{message}}，外层花括号是f-string的，内层是给loguru的

    log_line_parts = [
        "{time:YYYY-MM-DD HH:mm:ss.SSS}",
        "| {level.name: <8}",
        "| {process.name} ({process.id})",
        "| {thread.name} ({thread.id})",
        "| {file.name}:{line}",
        "| {function}",
        f"| {colored_message_template}",  # 将处理好的带颜色的消息模板放入
    ]

    if record["exception"]:
        exception_color = LOG_COLORS.get("ERROR", "FF0000")
        # Loguru 的 {exception} 令牌会自动处理异常的格式化
        colored_exception_template = f"[color={exception_color}]{{exception}}[/color]"
        log_line_parts.append(f"\n{colored_exception_template}")

    log_line_parts.append("\n")  # 确保每条日志后有换行

    # 将所有部分连接成一个单一的 Loguru 格式字符串
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
        # 返回 True 可能有助于 Loguru 启用某些特性，但我们是手动处理颜色
        # 对于 colorize=True，Loguru 可能会尝试输出 ANSI。
        # 但由于我们用 format 函数，这个可能不那么重要了。
        return True  # 尝试设为True


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

        # --- 修改开始 ---
        self.output_text_area = TextInput(
            text="点击按钮开始...\n",
            readonly=True,
            multiline=True,
            font_name="HYSongYunLangHeiW-1.ttf",
            # markup=True,  # <--- *** 从构造函数中移除这一行 ***
            # background_color=(0,0,0,1),
            # foreground_color=(1,1,1,1),
        )
        self.output_text_area.markup = True  # <--- *** 在创建实例后设置 markup 属性 ***
        # --- 修改结束 ---

        layout.add_widget(self.button)
        layout.add_widget(self.output_text_area)
        return layout

    def update_output_on_main_thread(self, message_to_append):
        if self._ui_update_pending and (time.time() - self._last_ui_update_time < 0.1):
            return

        self._ui_update_pending = True
        # start_time = time.time() # 移除未使用的变量

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

        # TextInput 的 text 属性在启用 markup 时，如果内容包含未闭合或错误的 markup 会出问题。
        # Loguru 的 format 函数需要确保产生的 markup 是合法的。
        # 我们之前的 kivy_markup_log_format 应该能产生合法的单行 markup。
        if self.output_text_area.text != new_text:
            try:
                self.output_text_area.text = new_text
            except Exception as e:
                # 如果设置 text 失败（通常是 markup 错误），打印错误到控制台并尝试无 markup 添加
                print(
                    f"ERROR setting TextInput text with markup: {e}",
                    file=sys.__stderr__,
                )
                # 尝试移除 markup 后添加，或者只添加错误信息
                plain_message = message_to_append.replace("[color=", "").replace(
                    "[/color]", ""
                )  # 简单移除
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
        self.output_text_area.text = (
            "[color=00ff00]任务开始，准备捕获输出...[/color]\n"  # 也可以用 markup
        )
        self.button.disabled = True
        thread = threading.Thread(target=self.run_function_with_capture, daemon=True)
        thread.start()

    def run_function_with_capture(self):
        kivy_stream_adapter = KivyTextStream(
            self.update_output_on_main_thread,
            buffer_interval=0.3,
            max_buffer_size=8192,  # 增加 buffer size
        )
        loguru_sink_id = None
        kivy_std_logging_handler = None  # 用于标准 logging

        try:
            # --- 配置 Loguru ---
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

            # --- 配置内置 logging ---
            root_logger = logging.getLogger()
            # 移除所有现有的处理器，以避免重复到控制台或冲突
            # （如果其他库依赖这些处理器，这可能有副作用，谨慎使用）
            # for handler in root_logger.handlers[:]:
            #     root_logger.removeHandler(handler) # 这可能会移除 Kivy 自己的控制台日志处理器

            root_logger.setLevel(logging.DEBUG)  # 确保根 logger 捕获所有级别
            kivy_std_logging_handler = KivyLoggingHandler(kivy_stream_adapter)
            root_logger.addHandler(kivy_std_logging_handler)
            loguru_global_logger.info(
                "--- Python 内置 logging Kivy Handler 已配置 ---"
            )  # 用 Loguru 记录配置日志

            # 测试内置 logging
            logging.debug("这是一条来自内置 logging 的 DEBUG 消息。")
            logging.info("这是一条来自内置 logging 的 INFO 消息。")
            logging.warning("这是一条来自内置 logging 的 WARNING 消息。")
            try:
                x = 1 / 0
            except ZeroDivisionError:
                logging.exception("内置 logging 捕获到一个异常！")

            # --- 重定向 stdout 和 stderr ---
            loguru_global_logger.info("--- 标准流重定向已配置 ---")
            with (
                redirect_stdout(kivy_stream_adapter),
                redirect_stderr(kivy_stream_adapter),
            ):
                loguru_global_logger.info(
                    "准备执行目标函数 function_that_prints_stuff。"
                )
                function_that_prints_stuff()
                loguru_global_logger.success("目标函数执行完毕。")

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
                    print(
                        f"[信息] Loguru Kivy sink (ID: {loguru_sink_id}) 已移除。",
                        file=sys.__stderr__,
                    )
                except ValueError:
                    print(
                        f"[警告] 移除 Loguru Kivy sink (ID: {loguru_sink_id}) 失败。",
                        file=sys.__stderr__,
                    )

            if kivy_std_logging_handler:
                logging.getLogger().removeHandler(kivy_std_logging_handler)
                print(
                    "[信息] Python logging Kivy handler 已移除。", file=sys.__stderr__
                )

            # 考虑是否要恢复 logging 模块的默认处理器，或 Loguru 的默认处理器
            # 以便在 Kivy 任务结束后，日志仍能输出到控制台
            # try:
            #     loguru_global_logger.add(sys.stderr, level="INFO")
            # except TypeError: pass # 可能已存在
            # if not logging.getLogger().hasHandlers(): # 如果没有处理器了
            #     logging.basicConfig(level=logging.INFO)

            Clock.schedule_once(self.enable_button_on_main_thread)

    def enable_button_on_main_thread(self, dt):
        self.button.disabled = False


if __name__ == "__main__":
    RealtimeOutputApp().run()
