import sys, logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#The background is set with 40 plus the number of the color, and the foreground with 30

#Here follow the sequences to get a colored output
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color=True):
    """Change the format message. Return the message with the new format
    
    :param message: the message to be changed
    :param use_color: boolean. If ``True``, add color to the message"""
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message
    
COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}

class ColoredFormatter(logging.Formatter):
    """A formatter for the python :mod:`logging` module that colors the log messages depending on their severity"""
    
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color
        
    def format(self, record):
        """TODO
        
        :param record: TODO"""
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)
        
FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
COLOR_FORMAT = formatter_message(FORMAT, True)

root_logger = None

def enable_colored_logging(stream=sys.stderr, level=None):
    """Enable colored logging
    
    :param stream: TODO
    :param level: TODO"""
    global root_logger
    if not root_logger:
        root_logger = logging.getLogger()
        if len(root_logger.handlers) == 0:
            hdlr = logging.StreamHandler(stream)
            if hasattr(stream, 'isatty') and stream.isatty():
                hdlr.setFormatter(ColoredFormatter(COLOR_FORMAT))
            root_logger.addHandler(hdlr)
    if level is not None:
        root_logger.setLevel(level)
    logging.getLogger('paste.httpserver').setLevel(logging.WARNING)