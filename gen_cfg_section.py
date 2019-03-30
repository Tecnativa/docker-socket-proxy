import argparse
import os
import re
from urllib.request import urlopen

import yaml


def parse_cli_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'api_versions',
        nargs='+',
        help=(
            'Docker API version(s) to support. ' +
            'If exactly two versions are passed, ' +
            'it will act as a range.'
        )
    )
    parser.add_argument(
        '--yaml-dir',
        help='Save and load Swagger YAML files from this directory'
    )
    parser.add_argument(
        '--add-comments',
        action='store_true',
        help='Add comments to the haproxy.cfg output'
    )
    return parser.parse_args()


def parse_api_versions(api_versions):
    if len(api_versions) == 2:
        min_ver = int(float(api_versions[0]) * 100)
        max_ver = int(float(api_versions[1]) * 100)
        assert min_ver < max_ver
        return [f'{ver / 100.0:.2f}' for ver in range(min_ver, max_ver + 1)]
    return api_versions


def create_cfg_line(endpoint):
    return r'    http-request allow if {{ path,url_dec -m reg -i ^(/v[\d\.]+)?/{} }} {{ env({}) -m bool }}'.format(
        endpoint, re.sub(r'[^A-Z]', '', endpoint.upper())
    )


def create_cfg_comment(endpoint, api_versions):
    version_nums = [float(ver) for ver in api_versions]
    return '    # /{} first seen: v{:.2f}, last seen: v{:.2f}'.format(
        endpoint,
        min(version_nums),
        max(version_nums),
    )


def get_base_endpoints(swagger):
    return set(
        path_name.split('/')[1]
        for path_name in swagger['paths'].keys()
    )


def load_swagger_yaml(api_version, yaml_dir=None):

    if yaml_dir:
        yaml_path = os.path.join(
            cli_args.yaml_dir,
            f"docker_v{api_version.replace('.', '_')}.yaml"
        )

        if os.path.isfile(yaml_path):
            print(f'Reading file {yaml_path!r}...')
            with open(yaml_path) as fd:
                return yaml.safe_load(fd)

    swagger_url = 'https://docs.docker.com/engine/api/v{}/swagger.yaml'.format(
        api_version
    )

    print(f'Downloading Docker API version {api_version}...')
    with urlopen(swagger_url) as fd:
        swagger = yaml.safe_load(fd)

    if yaml_dir:
        print(f'Writing file {yaml_path!r}...')
        with open(yaml_path, 'w') as fd:
            yaml.dump(swagger, fd)

    return swagger


if __name__ == '__main__':

    cli_args = parse_cli_args()

    api_versions = parse_api_versions(cli_args.api_versions)

    if cli_args.yaml_dir:
        os.makedirs(cli_args.yaml_dir, exist_ok=True)

    swaggers = {}
    for api_version in api_versions:
        swaggers[api_version] = load_swagger_yaml(
            api_version,
            yaml_dir=cli_args.yaml_dir
        )

    all_base_endpoints = {}
    for api_version, swagger in swaggers.items():
        for endpoint in get_base_endpoints(swagger):
            if endpoint in all_base_endpoints:
                all_base_endpoints[endpoint].append(api_version)
            else:
                all_base_endpoints[endpoint] = [api_version]

    for base_endpoint, api_versions in sorted(all_base_endpoints.items()):
        if cli_args.add_comments:
            print()
            print(create_cfg_comment(base_endpoint, api_versions))
        print(create_cfg_line(base_endpoint))
