#
# Copyright (c) 2017-2018 Bitprim Inc.
#
# This file is part of Bitprim.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
# import sys
from conans import ConanFile, CMake
from conans import __version__ as conan_version
from conans.model.version import Version
from ci_utils.utils import option_on_off, get_version, get_conan_req_version, get_cpu_microarchitecture, get_cpuid
from ci_utils.marchs import get_march, march_exists_in, march_exists_full, march_close_name, marchs_full_list

class Secp256k1Conan(ConanFile):
    name = "secp256k1"
    version = get_version()
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/bitprim/secp256k1"
    description = "Optimized C library for EC operations on curve secp256k1"
    settings = "os", "compiler", "build_type", "arch"

    if Version(conan_version) < Version(get_conan_req_version()):
        raise Exception ("Conan version should be greater or equal than %s. Detected: %s." % (get_conan_req_version(), conan_version))

    #TODO(fernando): See what to do with shared/static option... (not supported yet in Cmake)
    
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "enable_experimental": [True, False],
               "enable_endomorphism": [True, False],
               "enable_ecmult_static_precomputation": [True, False],
               "enable_module_ecdh": [True, False],
               "enable_module_schnorr": [True, False],
               "enable_module_recovery": [True, False],
               "with_benchmark": [True, False],
               "with_tests": [True, False],
               "with_openssl_tests": [True, False],
               "with_bignum_lib": [True, False],
               "microarchitecture": "ANY", #["x86_64", "haswell", "ivybridge", "sandybridge", "bulldozer", ...]
               "fix_march": [True, False],
               "verbose": [True, False],

               
            #    "with_bignum": ["conan", "auto", "system", "no"]

            #TODO(fernando): check what to do with with_asm, with_field and with_scalar 
            # Check CMake files and libbitcoin and bitcoin core makefiles

            #    "with_asm": ['x86_64', 'arm', 'no', 'auto'],
            #    "with_field": ['64bit', '32bit', 'auto'],
            #    "with_scalar": ['64bit', '32bit', 'auto'],
            #    "with_bignum": ['gmp', 'no', 'auto'],
    }

    # default_options = make_default_options_method()
    default_options = "shared=False", \
        "fPIC=True", \
        "enable_experimental=False", \
        "enable_endomorphism=False", \
        "enable_ecmult_static_precomputation=False", \
        "enable_module_ecdh=False", \
        "enable_module_schnorr=False", \
        "enable_module_recovery=True", \
        "with_benchmark=False", \
        "with_tests=False", \
        "with_openssl_tests=False", \
        "with_bignum_lib=True", \
        "microarchitecture=_DUMMY_",  \
        "fix_march=False", \
        "verbose=True"

        # "with_bignum=conan"
        # "with_asm='auto'", \
        # "with_field='auto'", \
        # "with_scalar='auto'"
        # "with_bignum='auto'"

    generators = "cmake"
    build_policy = "missing"

    exports = "conan_*", "ci_utils/*"      #"conan_channel", "conan_user", "conan_version", "conan_req_version"
    exports_sources = "src/*", "include/*", "CMakeLists.txt", "cmake/*", "secp256k1Config.cmake.in", "contrib/*", "test/*"
    #, "bitprimbuildinfo.cmake"

    # with_benchmark = False
    # with_tests = True
    # with_openssl_tests = False

    @property
    def msvc_mt_build(self):
        return "MT" in str(self.settings.compiler.runtime)

    @property
    def fPIC_enabled(self):
        if self.settings.compiler == "Visual Studio":
            return False
        else:
            return self.options.fPIC

    @property
    def is_shared(self):
        if self.options.shared and self.msvc_mt_build:
            return False
        else:
            return self.options.shared

    @property
    def bignum_lib_name(self):
        if self.options.with_bignum_lib:
            if self.settings.os == "Windows":
                return "mpir"
            else:
                return "gmp"
        else:
            return "no"

    # def fix_march(self, march):
        # marchs = ["x86_64", ''.join(cpuid.cpu_microarchitecture()), "haswell", "skylake", "skylake-avx512"]
        

    def requirements(self):
        # self.output.info("********************* BITPRIM_BUILD_NUMBER:  %s" % (os.getenv('BITPRIM_BUILD_NUMBER', '-'),))
        # self.output.info("********************* BITPRIM_BRANCH      :  %s" % (os.getenv('BITPRIM_BRANCH', '-'),))
        # self.output.info("********************* BITPRIM_CONAN_CHANNEL: %s" % (os.getenv('BITPRIM_CONAN_CHANNEL', '-'),))
        # self.output.info("********************* BITPRIM_FULL_BUILD:    %s" % (os.getenv('BITPRIM_FULL_BUILD', '-'),))
        # self.output.info("********************* BITPRIM_CONAN_VERSION: %s" % (os.getenv('BITPRIM_CONAN_VERSION', '-'),))
        # self.output.info("********************* get_version():         %s" % (get_version(),))
        # self.output.info("********************* self.channel: %s" % (self.channel,))

        # self.requires("Say/0.1@%s/%s" % (self.user, self.channel))

        if self.options.with_bignum_lib:
            if self.settings.os == "Windows":
                self.requires("mpir/3.0.0@bitprim/stable")
            else:
                self.requires("gmp/6.1.2@bitprim/stable")

    def config_options(self):
        if self.settings.arch != "x86_64":
            self.output.info("microarchitecture is disabled for architectures other than x86_64, your architecture: %s" % (self.settings.arch,))
            self.options.remove("microarchitecture")
            self.options.remove("fix_march")

        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")
            if self.options.shared and self.msvc_mt_build:
                self.options.remove("shared")

    def configure(self):
        del self.settings.compiler.libcxx       #Pure-C Library

        if self.settings.arch == "x86_64":
            if self.options.microarchitecture == "_DUMMY_":
                self.options.microarchitecture = get_cpu_microarchitecture().replace('_', '-')
                if get_cpuid() == None:
                    march_from = 'default'
                else:
                    march_from = 'taken from cpuid'
            else:
                march_from = 'user defined'

                # self.output.error("%s" % (marchs_full_list(),))

                if not march_exists_full(self.options.microarchitecture):
                    close = march_close_name(str(self.options.microarchitecture))
                    if not self.options.fix_march:
                        # self.output.error("fixed_march: %s" % (fixed_march,))

                        if len(close) > 0:
                            raise Exception ("Microarchitecture '%s' is not recognized. Did you mean '%s'?." % (self.options.microarchitecture, close[0]))
                            # self.output.error("Microarchitecture '%s' is not recognized. Did you mean '%s'?." % (self.options.microarchitecture, close[0]))
                            # sys.exit
                        else:
                            raise Exception ("Microarchitecture '%s' is not recognized." % (self.options.microarchitecture,))
                            # self.output.error("Microarchitecture '%s' is not recognized." % (self.options.microarchitecture,))
                            # sys.exit
                    else:
                        if len(close) > 0:
                            fixed_march = get_march(close[0], str(self.settings.compiler), float(str(self.settings.compiler.version)))
                        else:
                            fixed_march = get_march(self.options.microarchitecture, str(self.settings.compiler), float(str(self.settings.compiler.version)))

                        self.output.warn("Microarchitecture '%s' is not recognized, but it will be automatically fixed to '%s'." % (self.options.microarchitecture, fixed_march))
                        self.options.microarchitecture = fixed_march

                if not march_exists_in(self.options.microarchitecture, str(self.settings.compiler), float(str(self.settings.compiler.version))):
                    fixed_march = get_march(self.options.microarchitecture, str(self.settings.compiler), float(str(self.settings.compiler.version)))
                    if not self.options.fix_march:
                        raise Exception ("Microarchitecture '%s' is not supported by your compiler, you could use '%s'." % (self.options.microarchitecture,fixed_march))
                        # self.output.error("Microarchitecture '%s' is not supported by your compiler, you could use '%s'." % (self.options.microarchitecture,fixed_march))
                        # sys.exit
                    else:
                        self.output.warn("Microarchitecture '%s' is not supported by your compiler, but it will be automatically fixed to '%s'." % (self.options.microarchitecture, fixed_march))


            fixed_march = get_march(self.options.microarchitecture, str(self.settings.compiler), float(str(self.settings.compiler.version)))
    
            if march_from != 'user defined':
                self.output.info("Compiling for microarchitecture (%s): %s" % (march_from, self.options.microarchitecture))

            if self.options.microarchitecture != fixed_march:
                self.options.microarchitecture = fixed_march
                self.output.info("Corrected microarchitecture for compiler: %s" % (self.options.microarchitecture,))

            # self.options["*"].microarchitecture = self.options.microarchitecture

        # self.output.info("********* Compiler: %s" % (str(self.settings.compiler)))
        # self.output.info("********* Compiler Version: %s" % (str(self.settings.compiler.version)))

        # if self.settings.compiler.version == 9.1:
        #     self.output.info("************************************ IF")
        # else:
        #     self.output.info("************************************ ELSE")


        # # MinGW
        # if self.options.microarchitecture == 'skylake-avx512' and self.settings.os == "Windows" and self.settings.compiler == "gcc":
        #     self.output.info("'skylake-avx512' microarchitecture is not supported by this compiler, fall back to 'skylake'")
        #     self.options.microarchitecture = 'skylake'

        # # if self.options.microarchitecture == 'skylake' and self.settings.os == "Windows" and self.settings.compiler == "gcc":
        # #     self.output.info("'skylake' microarchitecture is not supported by this compiler, fall back to 'haswell'")
        # #     self.options.microarchitecture = 'haswell'

        # if self.options.microarchitecture == 'skylake-avx512' and self.settings.compiler == "apple-clang" and float(str(self.settings.compiler.version)) < 8:
        #     self.output.info("'skylake-avx512' microarchitecture is not supported by this compiler, fall back to 'skylake'")
        #     self.options.microarchitecture = 'skylake'

        # if self.options.microarchitecture == 'skylake' and self.settings.compiler == "apple-clang" and float(str(self.settings.compiler.version)) < 8:
        #     self.output.info("'skylake' microarchitecture is not supported by this compiler, fall back to 'haswell'")
        #     self.options.microarchitecture = 'haswell'

        # if self.options.microarchitecture == 'skylake-avx512' and self.settings.compiler == "gcc" and float(str(self.settings.compiler.version)) < 6:
        #     self.output.info("'skylake-avx512' microarchitecture is not supported by this compiler, fall back to 'skylake'")
        #     self.options.microarchitecture = 'skylake'

        # if self.options.microarchitecture == 'skylake' and self.settings.compiler == "gcc" and float(str(self.settings.compiler.version)) < 6:
        #     self.output.info("'skylake' microarchitecture is not supported by this compiler, fall back to 'haswell'")
        #     self.options.microarchitecture = 'haswell'

        # # if self.options.microarchitecture == 'skylake-avx512' and self.settings.compiler == "gcc" and float(str(self.settings.compiler.version)) < 5:
        # #     self.options.microarchitecture = 'haswell'

        

    def package_id(self):
        self.info.options.with_benchmark = "ANY"
        self.info.options.with_tests = "ANY"
        self.info.options.with_openssl_tests = "ANY"
        self.info.options.verbose = "ANY"

        # if self.settings.compiler == "Visual Studio":
        #     self.info.options.microarchitecture = "ANY"

    def build(self):
        cmake = CMake(self)

        cmake.definitions["USE_CONAN"] = option_on_off(True)
        cmake.definitions["NO_CONAN_AT_ALL"] = option_on_off(False)
        # cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = option_on_off(False)
        cmake.verbose = self.options.verbose

        cmake.definitions["ENABLE_SHARED"] = option_on_off(self.is_shared)
        cmake.definitions["ENABLE_POSITION_INDEPENDENT_CODE"] = option_on_off(self.fPIC_enabled)

        cmake.definitions["ENABLE_BENCHMARK"] = option_on_off(self.options.with_benchmark)
        cmake.definitions["ENABLE_TESTS"] = option_on_off(self.options.with_tests)
        cmake.definitions["ENABLE_OPENSSL_TESTS"] = option_on_off(self.options.with_openssl_tests)
        # cmake.definitions["ENABLE_BENCHMARK"] = option_on_off(self.with_benchmark)
        # cmake.definitions["ENABLE_TESTS"] = option_on_off(self.with_tests)
        # cmake.definitions["ENABLE_OPENSSL_TESTS"] = option_on_off(self.with_openssl_tests)

        cmake.definitions["ENABLE_EXPERIMENTAL"] = option_on_off(self.options.enable_experimental)
        cmake.definitions["ENABLE_ENDOMORPHISM"] = option_on_off(self.options.enable_endomorphism)
        cmake.definitions["ENABLE_ECMULT_STATIC_PRECOMPUTATION"] = option_on_off(self.options.enable_ecmult_static_precomputation)
        cmake.definitions["ENABLE_MODULE_ECDH"] = option_on_off(self.options.enable_module_ecdh)
        cmake.definitions["ENABLE_MODULE_SCHNORR"] = option_on_off(self.options.enable_module_schnorr)
        cmake.definitions["ENABLE_MODULE_RECOVERY"] = option_on_off(self.options.enable_module_recovery)

        # if self.settings.os == "Windows":
        #     cmake.definitions["WITH_BIGNUM"] = "mpir"
        # else:
        #     cmake.definitions["WITH_BIGNUM"] = "gmp"

        cmake.definitions["WITH_BIGNUM"] = self.bignum_lib_name

        cmake.definitions["MICROARCHITECTURE"] = self.options.microarchitecture

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio" and (self.settings.compiler.version != 12):
                cmake.definitions["ENABLE_TESTS"] = option_on_off(False)   #Workaround. test broke MSVC

        # Pure-C Library, No CXX11 ABI
        # if self.settings.compiler == "gcc":
        #     if float(str(self.settings.compiler.version)) >= 5:
        #         cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(False)
        #     else:
        #         cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(True)
        # elif self.settings.compiler == "clang":
        #     if str(self.settings.compiler.libcxx) == "libstdc++" or str(self.settings.compiler.libcxx) == "libstdc++11":
        #         cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(False)




        # cmake.definitions["WITH_ASM"] = option_on_off(self.options.with_asm)
        # cmake.definitions["WITH_FIELD"] = option_on_off(self.options.with_field)
        # cmake.definitions["WITH_SCALAR"] = option_on_off(self.options.with_scalar)
        # cmake.definitions["WITH_BIGNUM"] = option_on_off(self.options.with_bignum)

        if self.settings.compiler != "Visual Studio":
            # gcc_march = str(self.options.microarchitecture).replace('_', '-')
            gcc_march = str(self.options.microarchitecture)
            cmake.definitions["CONAN_CXX_FLAGS"] = cmake.definitions.get("CONAN_CXX_FLAGS", "") + " -march=" + gcc_march
            cmake.definitions["CONAN_C_FLAGS"] = cmake.definitions.get("CONAN_C_FLAGS", "") + " -march=" + gcc_march

        # microarchitecture_default

        cmake.definitions["BITPRIM_BUILD_NUMBER"] = os.getenv('BITPRIM_BUILD_NUMBER', '-')
        cmake.configure(source_dir=self.source_folder)
        cmake.build()


        #TODO(fernando): Cmake Tests and Visual Studio doesn't work
        #TODO(fernando): Secp256k1 segfaults al least on Windows
        # if self.options.with_tests:
        #     cmake.test()
        #     # cmake.test(target="tests")

    def package(self):
        self.copy("*.h", dst="include", src="include", keep_path=True)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["secp256k1"]
        if self.package_folder:
            self.env_info.CPATH = os.path.join(self.package_folder, "include")
            self.env_info.C_INCLUDE_PATH = os.path.join(self.package_folder, "include")
            self.env_info.CPLUS_INCLUDE_PATH = os.path.join(self.package_folder, "include")
