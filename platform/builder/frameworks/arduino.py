"""Arduino framework integration for Realtek AmebaD."""

import os
import shlex

from SCons.Script import DefaultEnvironment


env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

framework_dir = platform.get_package_dir("framework-arduinorealtek-amebad")
assert framework_dir and os.path.isdir(framework_dir), "AmebaD Arduino framework is missing"

hardware_dir = os.path.join(framework_dir, "hardware")
core_dir = os.path.join(hardware_dir, "cores", board.get("build.core"))
variant_dir = os.path.join(hardware_dir, "variants", board.get("build.variant"))
common_libs_dir = os.path.join(hardware_dir, "variants", "common_libs")
sdk_dir = os.path.join(hardware_dir, "system")


def read_properties(path):
    result = {}
    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


properties = read_properties(os.path.join(hardware_dir, "platform.txt"))
ameba_project = properties.get("ameba.project", "realtek_amebaD_va0_example")

include_paths = [core_dir, variant_dir]
for token in shlex.split(properties.get("compiler.ameba.c.include", "")):
    token = token.replace("{ameba.sdkpath}", sdk_dir)
    token = token.replace("{ameba.project}", ameba_project)
    token = token.replace("{build.core.path}", core_dir)
    if token.startswith("-I"):
        include_paths.append(token[2:])

machine_flags = [
    "-mcpu=%s" % board.get("build.cpu"),
    "-march=armv8-m.main+dsp",
    "-mthumb",
    "-mcmse",
    "-mfloat-abi=hard",
    "-mfpu=fpv5-sp-d16",
]

common_compile_flags = machine_flags + [
    "-O2",
    "-ffunction-sections",
    "-fdata-sections",
    "-fstack-usage",
    "-nostartfiles",
    "-nodefaultlibs",
    "-nostdlib",
    "-Wall",
    "-Wpointer-arith",
    "-Wundef",
    "-Wno-write-strings",
    "-Wno-maybe-uninitialized",
    "-Wextra",
]

env.Append(
    ASFLAGS=machine_flags,
    ASPPFLAGS=["-x", "assembler-with-cpp"],
    CCFLAGS=common_compile_flags,
    CFLAGS=["-Wstrict-prototypes"],
    CXXFLAGS=["-std=c++11", "-fno-use-cxa-atexit"],
    CPPDEFINES=[
        ("ARDUINO", 10819),
        ("F_CPU", "$BOARD_F_CPU"),
        "ARDUINO_AMEBA",
        "ARDUINO_ARCH_AMEBAD",
        "ARDUINO_SDK",
        "ARDUINO_AMBD",
        "CORE_RTL8720DN",
        "BOARD_AITHINKER_BW16",
        "Arduino_STD_PRINTF",
        "__FPU_PRESENT",
        "CONFIG_PLATFORM_8721D",
        "CONFIG_USE_MBEDTLS_ROM_ALG",
        "CONFIG_FUNCION_O0_OPTIMIZE",
        ("DM_ODM_SUPPORT_TYPE", 32),
    ],
    CPPPATH=include_paths,
    LIBSOURCE_DIRS=[os.path.join(hardware_dir, "libraries")],
)

prebuilt_libraries = []
library_recipe = properties.get("compiler.ameba.ar.list", "")
for token in shlex.split(library_recipe):
    path = token.replace("{runtime.platform.path}", hardware_dir)
    path = path.replace("{build.variant.path}", variant_dir)
    if os.path.isfile(path):
        prebuilt_libraries.append(env.File(path))

variant_library = env.BuildLibrary(
    os.path.join("$BUILD_DIR", "FrameworkArduinoVariant"), variant_dir
)
core_library = env.BuildLibrary(
    os.path.join("$BUILD_DIR", "FrameworkArduino"), core_dir
)

# A linker group is required because the Realtek SDK consists of mutually
# dependent static archives.
env.Prepend(LIBS=[variant_library, core_library])
env.Append(LIBS=prebuilt_libraries + ["m", "stdc++"])
