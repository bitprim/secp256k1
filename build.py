import os
import cpuid
from ci_utils.utils import get_builder, handle_microarchs, copy_env_vars

if __name__ == "__main__":

    # full_build_str = os.getenv('BITPRIM_FULL_BUILD', '0')
    # full_build = os.getenv('BITPRIM_FULL_BUILD', '0') == '1'
    full_build = True

    builder, name = get_builder()
    builder.add_common_builds(shared_option_name="%s:shared" % name, pure_c=True)

    filtered_builds = []
    for settings, options, env_vars, build_requires, reference in builder.items:

        if settings["build_type"] == "Release" \
                and not("%s:shared"  % name in options and options["%s:shared" % name]):

            copy_env_vars(env_vars)

            if os.getenv('BITPRIM_RUN_TESTS', 'false') == 'true':
                # options["%s:with_benchmark" % name] = "True"
                options["%s:with_tests" % name] = "True"
                # options["%s:with_openssl_tests" % name] = "True"
                marchs = ["x86_64"]
            else:
                if full_build:
                    # marchs = ["x86_64", ''.join(cpuid.cpu_microarchitecture()), "haswell", "skylake", "skylake-avx512"]
                    marchs = [''.join(cpuid.cpu_microarchitecture()), 'znver1', 'silvermont', 'westmere', 'goldmont', 'btver1', 'icelake-client', 'btver2', 'skylake', 'nano', 'haswell', 'nano-1000', 'broadwell', 'bdver1', 'bdver3', 'bdver2', 'bdver4', 'core2', 'k8', 'amdfam10', 'icelake-server', 'bonnell', 'cannonlake', 'k8-sse3', 'goldmont-plus', 'nano-x4', 'nehalem', 'ivybridge', 'eden-x4', 'x86-64', 'nano-3000', 'knl', 'knm', 'penryn', 'eden-x2', 'sandybridge', 'nano-2000', 'tremont', 'skylake-avx512', 'nano-x2']
                else:
                    marchs = ["x86_64"]

            handle_microarchs("%s:microarchitecture" % name, marchs, filtered_builds, settings, options, env_vars, build_requires)
            # filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
