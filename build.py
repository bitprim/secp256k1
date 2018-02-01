import os
from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(username="bitprim", channel="testing",
                                 remotes="https://api.bintray.com/conan/bitprim/bitprim",
                                 archs=["x86_64"])

    builder.add_common_builds(shared_option_name="secp256k1:shared", pure_c=True)

    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:

        # if settings["build_type"] == "Release" \
        #         and not("secp256k1:shared" in options and options["secp256k1:shared"]) \
        #         and (not "compiler.runtime" in settings or not settings["compiler.runtime"] == "MT"):

        if settings["build_type"] == "Release" \
                and not("secp256k1:shared" in options and options["secp256k1:shared"]):

            env_vars["BITPRIM_BUILD_NUMBER"] = os.getenv('BITPRIM_BUILD_NUMBER', '-')
                
            filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
