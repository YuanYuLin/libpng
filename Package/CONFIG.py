import ops
import iopc

TARBALL_FILE="libpng-1.6.34.tar.xz"
TARBALL_DIR="libpng-1.6.34"
INSTALL_DIR="libpng-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))

    '''
    ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    ops.exportEnv(ops.setEnv("LIBS", libs))
    '''

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    ops.copyto(ops.path_join(iopc.getSdkPath(), 'usr/include/libz/.'), tarball_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)
    cc_sysroot = ops.getEnv("CC_SYSROOT")

    cflags = iopc.get_includes()
    libs = iopc.get_libs()

    extra_conf = []
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("V=1")
    #extra_conf.append("--disable-silent-rules")
    extra_conf.append("--enable-hardware-optimizations")
    extra_conf.append("--disable-arm-neon")
    extra_conf.append("--disable-mips-msa")
    extra_conf.append("--disable-intel-sse")
    extra_conf.append("--disable-powerpc-vsx")
    extra_conf.append('FFI_CFLAGS=' + cflags)
    extra_conf.append('FFI_LIBS=' + libs)
    extra_conf.append('EXPAT_CFLAGS=' + cflags)
    extra_conf.append('EXPAT_LIBS=' + libs)
    extra_conf.append('LIBXML_CFLAGS=' + cflags)
    extra_conf.append('LIBXML_LIBS=' + libs)
    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(install_dir)
    ops.mkdir(dst_lib_dir)
    libpng = "libpng16.so.16.34.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libpng), dst_lib_dir)
    ops.ln(dst_lib_dir, libpng, "libpng16.so.16.34")
    ops.ln(dst_lib_dir, libpng, "libpng16.so.16")
    ops.ln(dst_lib_dir, libpng, "libpng16.so")
    ops.ln(dst_lib_dir, libpng, "libpng.so.16.34")
    ops.ln(dst_lib_dir, libpng, "libpng.so.16")
    ops.ln(dst_lib_dir, libpng, "libpng.so")

    ops.mkdir(tmp_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)
    return False

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)

    return False

def MAIN_SDKENV(args):
    set_global(args)

    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/' + args["pkg_name"])
    iopc.add_includes(cflags)

    libs = ""
    libs += " -lpng"
    iopc.add_libs(libs)

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

