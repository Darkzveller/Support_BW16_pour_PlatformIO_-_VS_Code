"""PlatformIO build and upload pipeline for Realtek AmebaD."""

import os
import shutil
import subprocess
import sys

from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment


env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

toolchain_dir = platform.get_package_dir("toolchain-realtek-amebad")
uploader_dir = platform.get_package_dir("tool-realtek-amebad")
framework_dir = platform.get_package_dir("framework-arduinorealtek-amebad")

assert toolchain_dir and os.path.isdir(toolchain_dir), "Realtek toolchain is missing"
assert uploader_dir and os.path.isdir(uploader_dir), "Realtek upload tools are missing"
assert framework_dir and os.path.isdir(framework_dir), "AmebaD Arduino framework is missing"

toolchain_bin = os.path.join(toolchain_dir, "bin")
env.PrependENVPath("PATH", toolchain_bin)

common_libs_dir = os.path.join(framework_dir, "hardware", "variants", "common_libs")
ldscript = os.path.join(common_libs_dir, board.get("build.ldscript"))

env.Replace(
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-gcc",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    GDB="arm-none-eabi-gdb",
    LINK="arm-none-eabi-gcc",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",
    ARFLAGS=["rcs"],
    PROGNAME="firmware",
    PROGSUFFIX=".elf",
    SIZECHECKCMD="$SIZETOOL -B -d $SOURCES",
    SIZEPRINTCMD="$SIZETOOL -B -d $SOURCES",
    LDSCRIPT_PATH=ldscript,
)

link_flags = [
    "-O2",
    "-march=armv8-m.main+dsp",
    "-mcpu=%s" % board.get("build.cpu"),
    "-mthumb",
    "-mcmse",
    "-mfloat-abi=hard",
    "-mfpu=fpv5-sp-d16",
    "-nostartfiles",
    "--specs=nosys.specs",
    "-Wl,--gc-sections",
    "-Wl,--cref",
    "-Wl,--build-id=none",
    "-Wl,--no-enum-size-warning",
    "-Wl,--warn-common",
    "-Wl,-Map=%s" % os.path.join(env.subst("$BUILD_DIR"), "application.map"),
]

for symbol in (
    "strcat", "strchr", "strcmp", "strncmp", "strcpy", "strncpy", "strlen",
    "strnlen", "strncat", "strpbrk", "strstr", "strtok", "strsep", "strtoll",
    "strtoul", "strtoull", "atoi", "malloc", "free", "realloc", "memcmp",
    "memcpy", "memmove", "memset",
):
    link_flags.append("-Wl,-wrap,%s" % symbol)

env.Append(
    LIBPATH=[os.path.join(toolchain_dir, "lib"), common_libs_dir],
    LINKFLAGS=link_flags,
)

# Circular references occur between the Arduino core and Realtek prebuilt SDK.
env.Replace(
    LINKCOM="$LINK -o $TARGET $LINKFLAGS $SOURCES -Wl,--start-group $_LIBDIRFLAGS $_LIBFLAGS -Wl,--end-group"
)


def host_tool_name():
    if sys.platform.startswith("win"):
        return "postbuild_img2_arduino_windows.exe"
    if sys.platform == "darwin":
        return "postbuild_img2_arduino_macos"
    return "postbuild_img2_arduino_linux"


def uploader_name():
    if sys.platform.startswith("win"):
        return "upload_image_tool_windows.exe"
    if sys.platform == "darwin":
        return "upload_image_tool_macos"
    return "upload_image_tool_linux"


def build_ameba_image(target, source, env):
    output_path = str(target[0])
    elf_path = str(source[0])
    application_axf = os.path.join(env.subst("$BUILD_DIR"), "application.axf")
    shutil.copy2(elf_path, application_axf)

    variant = board.get("build.variant")
    symbol_blacklist = os.path.join(
        framework_dir, "hardware", "variants", variant, "symbol_blacklist.txt"
    )
    if not os.path.isfile(symbol_blacklist):
        symbol_blacklist = os.path.join(
            framework_dir, "hardware", "variants", variant, "symb_blacklist.txt"
        )

    postbuild = os.path.join(uploader_dir, host_tool_name())
    command = [
        postbuild,
        uploader_dir,
        application_axf,
        toolchain_bin + os.sep,
        symbol_blacklist,
    ]
    subprocess.check_call(command)

    generated_image = os.path.join(uploader_dir, "km0_km4_image2.bin")
    if not os.path.isfile(generated_image):
        raise RuntimeError("The Realtek post-build tool did not create km0_km4_image2.bin")
    shutil.copy2(generated_image, output_path)
    return 0


env.Append(
    BUILDERS={
        "AmebaImage": Builder(
            action=env.VerboseAction(build_ameba_image, "Building $TARGET"),
            suffix=".bin",
            src_suffix=".elf",
        )
    }
)

target_elf = env.BuildProgram()
target_bin = env.AmebaImage(os.path.join("$BUILD_DIR", "firmware"), target_elf)
env.Depends(target_bin, "checkprogsize")

size_target = env.Alias(
    "size",
    target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"),
)
AlwaysBuild(size_target)


def before_upload(target, source, env):
    env.AutodetectUploadPort()


upload_tool = os.path.join(uploader_dir, uploader_name())
def upload_ameba_image(target, source, env):
    command = [
        upload_tool,
        uploader_dir,
        env.subst("$UPLOAD_PORT"),
        "Ai-Thinker_BW16",
        board.get("upload.auto_mode", "Disable"),
        board.get("upload.erase_flash", "Disable"),
        env.subst("$UPLOAD_SPEED"),
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output_lines = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        output_lines.append(line)
    return_code = process.wait()
    output = "".join(output_lines).lower()
    failure_markers = (
        "error:",
        "flashloader download fail",
        "cannot access",
        "upload failed",
    )
    if return_code != 0 or any(marker in output for marker in failure_markers):
        return 1
    return 0

upload_actions = [
    env.VerboseAction(before_upload, "Looking for upload port..."),
    env.VerboseAction(upload_ameba_image, "Uploading $SOURCE"),
]
upload_target = env.Alias("upload", target_bin, upload_actions)
AlwaysBuild(upload_target)

Default(target_bin)
