import logging
import linecache
from types import TracebackType
from html import escape

from .misc import bot
from .config import LOG_ID


def _get_exception_line_context(tb: TracebackType, line_offset: int = 4) -> str:
    filename = tb.tb_frame.f_code.co_filename
    line_number = tb.tb_lineno

    linecache.checkcache(filename)
    lines = []

    for ln in range(line_number - 3, line_number + 3):
        line = linecache.getline(filename, ln)
        formatted_line = f'' \
                         f'{ln}' \
                         f'{" →" if ln == line_number else "  "}' \
                         f'{"".join([" " for _ in range(line_offset - 2)])}' \
                         f'{line}'
        lines.append(formatted_line)

    resp = ''.join(lines)
    return resp


class TgFormatter(logging.Formatter):

    def formatException(self, ei):
        msg = escape(super().formatException(ei))

        # add few code lines
        code_lines = escape(_get_exception_line_context(ei[2]))
        sep = '==========================='
        resp = f'<code>{msg}\n\n{sep}\n\n{code_lines}</code>'
        return resp


class TgHandler(logging.Handler):
    def __init__(self, level):
        super().__init__(level)
        log_format = '<b>{asctime} | {name} | {levelname}</b>\n<code>{message}</code>'
        dt_format = '%d-%m-%Y > %H:%M:%S'
        self.setFormatter(TgFormatter(fmt=log_format, datefmt=dt_format, style='{'))

    def emit(self, record):
        msg = self.format(record)
        try:
            bot.send_message(LOG_ID, msg, parse_mode='HTML')
        except Exception as e:
            logging.exception(e)


logger = logging.getLogger('omer_broadcast')
logger.setLevel(logging.INFO)
logger.addHandler(TgHandler(logging.WARNING))
logger.addHandler(logging.StreamHandler())
