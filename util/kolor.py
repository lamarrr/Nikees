from typing import List, Tuple, Dict, Any
import sys
import enum
"""

Kolor
==========

8 bit command line text visualization or coloring as you may prefer
ANSI Standard compliant
"""


# full of verbosity and unnecessary code repetiton but for performance purposes

__all__ = [
    "StyleRule", "Symbol",
    "background", "foreground", "underline", "faint", "bold", "italic", "swap", "conceal", "cross_out"
]


# supported colors
__COLORS: Dict[str, str] = {
    "black":   "\033[%s;5;0m",
    "red":     "\033[%s;5;1m",
    "green":   "\033[%s;5;2m",
    "yellow":  "\033[%s;5;3m",
    "blue":    "\033[%s;5;4m",
    "magenta": "\033[%s;5;5m",
    "cyan":    "\033[%s;5;6m",
    "white":   "\033[%s;5;7m"
}

__COL_OPS: Dict[str, Tuple[str]] = {
    "reset":        ("\033[0m",),
    "bold":         ("\033[1m", "\033[22m"),
    "faint":        ("\033[2m", "\033[22m"),
    "italic":       ("\033[3m", "\033[23m"),
    "underline":    ("\033[4m", "\033[24m"),
    "slow_blink":   ("\033[5m", "\033[25m"),
    "rapid_blink":  ("\033[6m", "\033[25m"),
    "swap":         ("\033[7m", "\033[27m"),
    "conceal":      ("\033[8m", "\033[28m"),
    "crossed_out":  ("\033[9m", "\033[29m"),
    "default_font": ("\033[10m",)
}


__X_GROUND: Dict[str, Tuple[str]] = {
    # set background, default terminal background
    "foreground": ("38", "\033[39m"),
    "background": ("48", "\033[49m"),
}


class StyleRule:

    def __init__(self, **kwargs):
        self._bg = kwargs.get("background", None)
        self._fg = kwargs.get("foreground", None)
        self._pr = kwargs.get("prefix", None)
        self._po = kwargs.get("postfix", None)
        self._ul = kwargs.get("underline", False)
        self._ft = kwargs.get("faint", False)
        self._bl = kwargs.get("bold", False)
        self._it = kwargs.get("italic", False)
        self._sw = kwargs.get("swap", False)
        self._cn = kwargs.get("conceal", False)
        self._cr = kwargs.get("cross_out", False)
        self._pr_style = kwargs.get("prefix_style", None)
        self._po_style = kwargs.get("postfix_style", None)

        if self._pr_style:
            self._pr = self._pr_style.style(self._pr)
        if self._po_style:
            self._po = self._po_style.style(self._po)

    def style(self, string: str):
        result = string
        if self._bg:
            result = background(result, self._bg)
        if self._fg:
            result = foreground(result, self._fg)
        if self._ul:
            result = underline(result)
        if self._ft:
            result = faint(result)
        if self._bl:
            result = bold(result)
        if self._it:
            result = italic(result)
        if self._sw:
            result = swap(result)
        if self._cn:
            result = conceal(result)
        if self._cr:
            result = cross_out(result)
        if self._pr:
            result = "%s %s" % (self._pr, result)
        if self._po:
            result = "%s %s" % (result, self._po)
        return result

    def print(self,*values,**kwargs):
        sep = kwargs.get("sep"," ")
        end = kwargs.get("end","\n")
        file = kwargs.get("file",sys.stdout)
        flush = kwargs.get("flush",False)
        new_str = sep.join(tuple(str(value) for value in values))
        new_str = self.style(new_str)
        print(new_str,end=end,flush=flush,file=file)


def sprint(style=None, *values, **kwargs):
    assert type(style) == StyleRule, "Only StyleRule types are allowed"
    if style:
        string = kwargs.get("sep", " ").join(tuple(str(v) for v in values))
        string = style.style(string)
        print(string, **kwargs)
    else:
        print(*values, **kwargs)


class Symbol:
    bullet = "●"
    check = "✓"
    checkbox_on = "☒"
    checkbox_off = "☐"
    dot = "•"
    ellipsis = "…"
    error = "✖"
    info = "ℹ"
    radio_on = "◉"
    radio_off = "◯"
    square_off = "◻"
    square_on = "◼"
    star = "★"
    warning = "⚠"


def background(value: Any, color):
    """
    set background color
    """
    # Background ESC[ … 48;5;<n> … m Select background color
    return "%s%s%s" % (__COLORS[color] % __X_GROUND["background"][0], value, __X_GROUND["background"][1])


def foreground(value: Any, color):
    # Foreground ESC[ … 38;5;<n> … m Select foreground color
    return "%s%s%s" % (__COLORS[color] % __X_GROUND["foreground"][0], value, __X_GROUND["foreground"][1])


def underline(value: Any):
    """
    underline
    ---------
    underline a text
    """
    return "%s%s%s" % (__COL_OPS["underline"][0], value, __COL_OPS["underline"][1])


def faint(value: Any):
    """
    faint
    -----
    make a text faint (reduce colour intensity)
    """
    return "%s%s%s" % (__COL_OPS["faint"][0], value, __COL_OPS["faint"][1])


def bold(value: Any):
    """
    bold
    ----
    make a bold text
    """
    return "%s%s%s" % (__COL_OPS["bold"][0], value, __COL_OPS["bold"][1])


def italic(value: Any):
    """
    italic
    ------
    italicize a given text
    """
    return "%s%s%s" % (__COL_OPS["italic"][0], value, __COL_OPS["italic"][1])


def swap(value: Any):
    """
    swap
    ----
    swap foreground and background colors
    """
    return "%s%s%s" % (__COL_OPS["swap"][0], value, __COL_OPS["swap"][1])


def conceal(value: Any):
    """
    conceal
    ----------
    """
    return "%s%s%s" % (__COL_OPS["conceal"][0], value, __COL_OPS["conceal"][1])


def cross_out(value: Any):
    """
    cross_out
    ---------
    cross out (rule through) a given text
    """
    return "%s%s%s" % (__COL_OPS["cross_out"][0], value, __COL_OPS["cross_out"][1])


if __name__ == "__main__":
    print(background("hello world", color="red"), foreground(" hi there", color="blue"))
    WARNING_PREFIX_STYLE = StyleRule(bold=True,foreground="yellow")
    WARNING_STYLE = StyleRule(prefix=Symbol.warning ,prefix_style=WARNING_PREFIX_STYLE)
    sprint(WARNING_STYLE, "Warning, Level 2 Breach")
    
    ERROR_PREFIX_STYLE = StyleRule(bold=True,foreground="red")
    ERROR_STYLE = StyleRule(prefix=Symbol.error,prefix_style=ERROR_PREFIX_STYLE)
    sprint(ERROR_STYLE, "Error Loading Page")

    SUCCESS_PREFIX_STYLE = StyleRule(bold=True,foreground="green")
    SUCCESS_STYLE = StyleRule(prefix=Symbol.check ,prefix_style=SUCCESS_PREFIX_STYLE)
    sprint(SUCCESS_STYLE, "Successfully Loaded")

    SUCCESS_STYLE.print("hello",1,2,3)