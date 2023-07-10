import subprocess
import logging
from typing import List
import os
import re


class Option:
    """An Option is either a command line optimization setting or a parameter.

    It is essentially a list of the possible values that can be taken. Each item
    is command line parameter. In GCC, all of these are single settings, so only
    need one string to describe them, rather than a list.
    """

    def __len__(self):
        """Number of available settings. Note that the absence of a value is not
        included in this, it is implicit.
        """
        raise NotImplementedError()

    def __getitem__(self, key: int) -> str:
        """Get the command line argument associated with an index (key)."""
        raise NotImplementedError()

    def __str__(self) -> str:
        """Get the name of this option."""
        raise NotImplementedError()

class GccOOption(Option):
    """This class represents the :code:`-O0`, :code:`-O1`, :code:`-O2`,
    :code:`-O3`, :code:`-Os`, and :code:`-Ofast` options.

    This class starts with no values, we fill them in with
    :code:`_gcc_parse_optimize()`. The suffixes to append to :code:`-O` are
    stored in self.values.
    """

    def __init__(self):
        self.values = []

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key: int) -> str:
        return "-O" + self.values[key]

    def __str__(self) -> str:
        return "-O"

    def __repr__(self) -> str:
        return f"<GccOOption values=[{','.join(self.values)}]>"

class GccFlagAlignOption(Option):
    """Alignment flags. These take several forms. See the GCC documentation."""

    def __init__(self, name: str, values: List[str]):
        #logger.warning("Alignment options not properly handled %s", name)
        self.name = name
        self.values = values 

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key: int) -> str:
        return f"-f{self.name}={self.values[key]}"
    
    def __str__(self) -> str:
        return f"-f{self.name}"

    def __repr__(self) -> str:
        return f"<ccFlagAlignOption name={self.name}, values=[{','.join(self.values)}]>"


class GccFlagOption(Option):
    """An ordinary :code:`-f` flag.

    These have two possible settings. For a given flag name there are
    :code:`'-f<name>' and :code:`'-fno-<name>. If :code:`no_fno` is true, then
    there is only the :code:`-f<name>` form.
    """

    def __init__(self, name: str, no_fno: bool = False):
        self.name = name
        self.no_fno = no_fno

    def __len__(self):
        return 1 if self.no_fno else 2

    def __getitem__(self, key: int) -> str:
        return f"-f{'' if key == 0 else 'no-'}{self.name}"

    def __str__(self) -> str:
        return f"-f{self.name}"

    def __repr__(self) -> str:
        return f"<GccFlagOption name={self.name}>"

class GccFlagEnumOption(Option):
    """A flag of style :code:`-f<name>=[val1, val2, ...]`.

    :code:`self.name` holds the name. :code:`self.values` holds the values.
    """

    def __init__(self, name: str, values: List[str]):
        self.name = name
        self.values = values

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key: int) -> str:
        return f"-f{self.name}={self.values[key]}"

    def __str__(self) -> str:
        return f"-f{self.name}"

    def __repr__(self) -> str:
        return f"<GccFlagEnumOption name={self.name}, values=[{','.join(self.values)}]>"

class GccFlagIntOption(Option):
    """A flag of style :code:`-f<name>=<integer>` where the integer is between
    min and max.
    """

    def __init__(self, name: str, min: int, max: int):
        self.name = name
        self.min = min
        self.max = max

    def __len__(self):
        return self.max - self.min + 1

    def __getitem__(self, key: int) -> str:
        return f"-f{self.name}={self.min + key}"

    def __str__(self) -> str:
        return f"-f{self.name}"

    def __repr__(self) -> str:
        return f"<GccFlagIntOption name={self.name}, min={self.min}, max={self.max}>"

class GccParamIntOption(Option):
    """A parameter :code:`--param=<name>=<integer>`, where the integer is
    between min and max.
    """

    def __init__(self, name: str, min: int, max: int):
        self.name = name
        self.min = min
        self.max = max

    def __len__(self):
        return self.max - self.min + 1

    def __getitem__(self, key: int) -> str:
        return f"--param={self.name}={self.min + key}"

    def __str__(self) -> str:
        return f"--param={self.name}"

    def __repr__(self) -> str:
        return f"<GccParamIntOption name={self.name}, min={self.min}, max={self.max}>"


def _gcc_parse_optimize() -> List[Option]:
    """Parse the optimization help string from the GCC binary to find options."""

    # Call 'gcc --help=optimize -Q'
    result = subprocess.check_output(["gcc", "--help=optimize", "-Q"],universal_newlines=True)
    #print("result = ",result)
    
    # Split into lines. Ignore the first line.
    out = result.split("\n")[1:]
    #print("out = ",out)

    # Regex patterns to match the different options
    O_num_pat = re.compile("-O<number>")
    O_pat = re.compile("-O([a-z]+)")
    flag_align_eq_pat = re.compile("-f(align-[-a-z]+)=")
    flag_pat = re.compile("-f([-a-z0-9]+)")
    flag_enum_pat = re.compile("-f([-a-z0-9]+)=\\[([-A-Za-z_\\|]+)\\]")
    flag_interval_pat = re.compile("-f([-a-z0-9]+)=<([0-9]+),([0-9]+)>")
    flag_number_pat = re.compile("-f([-a-z0-9]+)=<number>")

    # The list of options as it gets built up.
    options = {}

    def add_gcc_o(value: str):
        # -O flag
        name = "O"
        # There are multiple -O flags. We add one value at a time.
        opt = options[name] = options.get(name, GccOOption())
        # There shouldn't be any way to overwrite this with the wrong type.
        assert type(opt) == GccOOption
        opt.values.append(value)

    # Add an align flag
    def add_gcc_flag_align(name: str):
        # Align flag.
        opt = options.get(name)
        values = ['16','32','64','128','256']
        if opt:
            # We should only ever be overwriting a straight flag
            assert type(opt) == GccFlagOption
        # Always overwrite
        options[name] = GccFlagAlignOption(name,values)

    # Add a flag
    def add_gcc_flag(name: str):
        # Straight flag.
        # If there is something else in its place already (like a flag enum),
        # then we don't overwrite it.  Straight flags always have the lowest
        # priority
        options[name] = options.get(name, GccFlagOption(name))
    
    # Add an enum flag
    def add_gcc_flag_enum(name: str, values: List[str]):
        # Enum flag.
        opt = options.get(name)
        if opt:
            # We should only ever be overwriting a straight flag
            assert type(opt) == GccFlagOption
        # Always overwrite
        options[name] = GccFlagEnumOption(name, values)
    
    # Add an integer flag
    def add_gcc_flag_int(name: str, min: int, max: int):
        # Int flag.
        opt = options.get(name)
        if opt:
            # We should only ever be overwriting a straight flag
            assert type(opt) == GccFlagOption
        # Always overwrite
        options[name] = GccFlagIntOption(name, min, max)

    def parse_line(line: str):
        # The first bit of the line is the specification
        bits = line.split()
        if not bits:
            return
        spec = bits[0]

        # -O<number>
        m = O_num_pat.fullmatch(spec)
        if m:
            for i in range(4):
                add_gcc_o(str(i))
            return

        # -Ostr
        m = O_pat.fullmatch(spec)
        if m:
            add_gcc_o(m.group(1))
            return

        # -falign-str=
        # These have quite complicated semantics
        m = flag_align_eq_pat.fullmatch(spec)
        if m:
            name = m.group(1)
            #print("name = ",name)
            add_gcc_flag_align(name)
            return
        
        # -fflag
        m = flag_pat.fullmatch(spec)
        if m:
            name = m.group(1)
            add_gcc_flag(name)
            return
        
        # -fflag=[a|b]
        m = flag_enum_pat.fullmatch(spec)
        if m:
            name = m.group(1)
            values = m.group(2).split("|")

            #print("name = ",name," values = ",values)
            add_gcc_flag_enum(name, values)
            return

        # -fflag=<min,max>
        m = flag_interval_pat.fullmatch(spec)
        if m:
            name = m.group(1)
            min = int(m.group(2))
            max = int(m.group(3))
            add_gcc_flag_int(name, min, max)
            return
        
        # -fflag=<number>
        m = flag_number_pat.fullmatch(spec)
        if m:
            name = m.group(1)
            min = 0
            max = 2 << 31 - 1
            add_gcc_flag_int(name, min, max)
            return

        #logger.warning("Unknown GCC optimization flag spec, '%s'", line)


    #Parse all the lines
    for line in out:
        parse_line(line.strip())

    #print(list(map(lambda x: x[1], sorted(list(options.items())))))
    return list(map(lambda x: x[1], sorted(list(options.items()))))
def _gcc_parse_params() -> List[Option]:
    """Parse the param help string from the GCC binary to find options."""

    # Pretty much identical to _gcc_parse_optimize
    #logger.debug("Parsing GCC param space")

    # Call 'gcc --help=param -Q'
    result = subprocess.check_output(["gcc", "--help=param", "-Q"],universal_newlines=True)
    #print("result = ",result)

    # Split into lines. Ignore the first line.
    out = result.split("\n")[1:]
    #print("out = ",out)

    param_enum_pat = re.compile("--param=([-a-zA-Z0-9]+)=\\[([-A-Za-z_\\|]+)\\]")
    param_interval_pat = re.compile("--param=([-a-zA-Z0-9]+)=<(-?[0-9]+),([0-9]+)>")
    param_number_pat = re.compile("--param=([-a-zA-Z0-9]+)=")
    param_old_interval_pat = re.compile(
        "([-a-zA-Z0-9]+)\\s+default\\s+(-?\\d+)\\s+minimum\\s+(-?\\d+)\\s+maximum\\s+(-?\\d+)"
    )

    params = {}

    def add_gcc_param_enum(name: str, values: List[str]):
        # Enum param.
        opt = params.get(name)
        assert not opt
        params[name] = GccParamEnumOption(name, values)

    def add_gcc_param_int(name: str, min: int, max: int):
        # Int flag.
        opt = params.get(name)
        assert not opt
        params[name] = GccParamIntOption(name, min, max)

    def parse_line(line: str):
        bits = line.split()
        if not bits:
            return

        # TODO(hugh): Not sure what the correct behavior is there.
        if len(bits) <= 1:
            return

        spec = bits[0]
        default = bits[1]

        # --param=name=[a|b]
        m = param_enum_pat.fullmatch(spec)
        if m:
            name = m.group(1)
            values = m.group(2).split("|")
            assert not default or default in values
            add_gcc_param_enum(name, values)
            return

        # --param=name=<min,max>
        m = param_interval_pat.fullmatch(spec)
        if m:
            name = m.group(1)
            min = int(m.group(2))
            max = int(m.group(3))
            if is_int(default):
                assert not default or min <= int(default) <= max
                add_gcc_param_int(name, min, max)
                return

        # --param=name=
        m = param_number_pat.fullmatch(spec)
        if m:
            name = m.group(1)
            min = 0
            max = 2 << 31 - 1
            if is_int(default):
                dflt = int(default)
                min = min if dflt >= min else dflt
                add_gcc_param_int(name, min, max)
                return
        # name  default num minimum num maximum num
        m = param_old_interval_pat.fullmatch(line)
        if m:
            name = m.group(1)
            default = int(m.group(2))
            min = int(m.group(3))
            max = int(m.group(4))
            if min <= default <= max:
                # For now we will only consider fully described params
                add_gcc_param_int(name, min, max)
                return

        #logger.warning("Unknown GCC param flag spec, '%s'", line)

    # breakpoint()
    for line in out:
        parse_line(line.strip())

    #print(list(map(lambda x: x[1], sorted(list(params.items())))))
    return list(map(lambda x: x[1], sorted(list(params.items()))))
def _fix_options(options: List[Option]) -> List[Option]:
    """Fixes for things that seem not to be true in the help."""

    def keep(option: Option) -> bool:
        # Ignore -flive-patching
        if isinstance(option, GccFlagEnumOption):
            if option.name == "live-patching":
                return False
        if isinstance(option, GccParamIntOption):
            if option.name == "parloops-schedule":
                return False
            if option.name == "lto-max-partition":
                return False
        return True

    options = [opt for opt in options if keep(opt)]

    for i, option in enumerate(options):
        if isinstance(option, GccParamIntOption):
            # Some things say they can have -1, but can't
            #print("=============option 1==============")

            #print("option.name = ",option.name)
            #print("=============option 2==============")
            if option.name in [
                "logical-op-non-short-circuit",
                "prefetch-minimum-stride",
                "sched-autopref-queue-depth",
                "vect-max-peeling-for-alignment",
            ]:
                option.min = 0

        elif isinstance(option, GccFlagOption):
            # -fhandle-exceptions renamed to -fexceptions
            if option.name == "handle-exceptions":
                option.name = "exceptions"

            # Some flags have no -fno- version
            if option.name in [
                "stack-protector-all",
                "stack-protector-explicit",
                "stack-protector-strong",
            ]:
                option.no_fno = True

            # -fno-threadsafe-statics should have the no- removed
            if option.name == "no-threadsafe-statics":
                option.name = "threadsafe-statics"

        elif isinstance(option, GccFlagIntOption):
            # -fpack-struct has to be a small positive power of two
            if option.name == "pack-struct":
                values = [str(1 << j) for j in range(5)]
                options[i] = GccFlagEnumOption("pack-struct", values)

    return options

def get_flag():
    optim_opts = _gcc_parse_optimize()
    param_opts = _gcc_parse_params()

    options = _fix_options(optim_opts + param_opts)

    #print("options = ",options)

    return options

if __name__ == "__main__":
    
    result = get_flag()
    #print(result)
