#! /usr/bin/env python
"""Just a small little script to help manage Packer templates in this repo."""

import argparse
from datetime import datetime
import json
import logging
import os
import shutil
import subprocess
import sys
import requests
import git
from urlparse import urlparse
from difflib import get_close_matches
from multiprocessing import Pool, cpu_count, TimeoutError
from requests_toolbelt.multipart import encoder

__author__ = "Cody Bunch"
__email__ = "bunchc@gmail.com"
__maintainer__ = "Cody Bunch"
__status__ = "Development"
# http://everythingshouldbevirtual.com
# @mrlesmithjr

logging.basicConfig(level=logging.INFO)

API_URL = 'https://app.vagrantup.com/api/v1/'
BUILD_OLDER_THAN_DAYS = 0
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    """Main program execution."""
    args = parse_args()
    if args.action == 'cleanup_builds':
        cleanup_builds()
    else:
        username, vagrant_cloud_token = private_vars()
        decide_action(args, username, vagrant_cloud_token)


def private_vars():
    private_vars_file = os.path.join(SCRIPT_DIR, 'private_vars.json')
    if os.path.isfile(private_vars_file):
        with open(private_vars_file) as priv_vars:
            priv_data = json.load(priv_vars)
            username = priv_data.get('username')
            vagrant_cloud_token = priv_data.get('vagrant_cloud_token')
            if username is not None and vagrant_cloud_token is not None:
                pass
            else:
                print('Vagrant Cloud token/username missing...')
    else:
        print('private_vars.json missing...')
        sys.exit(1)

    return username, vagrant_cloud_token


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Packer template utils.")
    parser.add_argument(
        "action", help="Define action to take.", choices=[
            'build_all', 'gotta_go_fast', 'change_controller',
            'cleanup_builds', 'commit_manifests', 'get_boxes',
            'rename_templates', 'repo_info', 'upload_boxes',
            'view_manifests', 'create_all', 'check_iso',
            'update_templates'])
    parser.add_argument('--controller',
                        help='Define hard drive controller type',
                        choices=['ide', 'sata', 'scsi'])
    args = parser.parse_args()
    if args.action == 'change_controller' and args.controller is None:
        parser.error('--controller is REQUIRED!')
    return args


def decide_action(args, username, vagrant_cloud_token):
    """Make decision on what to do from arguments being passed."""
    if args.action == 'build_all':
        build_all(username, vagrant_cloud_token)
        #upload_boxes(vagrant_cloud_token)
    elif args.action == 'gotta_go_fast':
        gotta_go_fast(username, vagrant_cloud_token)
        #upload_boxes(vagrant_cloud_token)
    elif args.action == 'change_controller':
        change_controller(args)
    elif args.action == 'cleanup_builds':
        cleanup_builds()
    elif args.action == 'commit_manifests':
        repo_facts = dict()
        repo_info(repo_facts)
        commit_manifests(repo_facts)
    elif args.action == 'get_boxes':
        boxes = dict()
        get_boxes(boxes, vagrant_cloud_token)
        print(json.dumps(boxes, indent=4))
    elif args.action == 'rename_templates':
        rename_templates()
    elif args.action == 'repo_info':
        repo_facts = dict()
        repo_info(repo_facts)
        print(json.dumps(repo_facts, indent=4))
    elif args.action == 'upload_boxes':
        upload_boxes(vagrant_cloud_token)
    elif args.action == "create_all":
        create_all(username, vagrant_cloud_token)
    elif args.action == "check_iso":
        check_iso(username, vagrant_cloud_token)
    elif args.action == "update_templates":
        update_templates()
    elif args.action == 'view_manifests':
        view_manifests()


def get_boxes(boxes, vagrant_cloud_token):
    """Connect to Vagrant Cloud API and get boxes."""
    box_api_url = API_URL + 'box/'
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if 'box_info.json' in files:
            with open(os.path.join(root, 'box_info.json'),
                      'r') as box_info:
                data = json.load(box_info)
                box_tag = data['box_tag']
                url = '{0}{1}'.format(box_api_url, box_tag)
                headers = {'Authorization': 'Bearer {0}'.format(
                    vagrant_cloud_token)}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    json_data = response.json()
                    boxes[json_data['tag']] = json_data


def repo_info(repo_facts):
    """Collect important repo info and store as facts."""
    changed_files = []
    repo_remotes = []
    repo_path = os.getcwd()
    repo = git.Repo(repo_path)
    for item in repo.index.diff(None):
        changed_files.append(item.a_path)
    for item in repo.remotes:
        remote_info = dict()
        remote_info[item.name] = {"url": item.url}
        repo_remotes.append(remote_info)
    repo_facts['changed_files'] = changed_files
    repo_facts['remotes'] = repo_remotes
    repo_facts['untracked_files'] = repo.untracked_files


def build_all(username, vagrant_cloud_token):
    """Looks for build script in each directory and then executes it."""
    print('Building all images.')
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if 'build.sh' in files:
            with open(os.path.join(root, 'box_info.json'),
                      'r') as box_info_file:
                box_info = json.load(box_info_file)
                auto_build = box_info['auto_build']
                if auto_build is not None:
                    if auto_build.lower() == 'true':
                        auto_build = True
                    else:
                        auto_build = False
                else:
                    auto_build = True
                build_image = get_box(box_info, username, vagrant_cloud_token)
                if auto_build and build_image:
                    print('Executing build.sh in {0}'.format(root))
                    os.chdir(root)
                    process = subprocess.Popen(['./build.sh'])
                    process.wait()
                    if process.returncode != 0:
                        print('Build of {0} failed'.format(root))
#                        sys.exit(1)
                    os.chdir(SCRIPT_DIR)


def go_fast(build):
    """Wrapper function for subprocess.Popen used by gotta_go_fast"""
    os.chdir(os.path.dirname(build))
    process = subprocess.Popen(build)
    process.wait()
    if process.returncode != 0:
        print('Build of {0} failed'.format(root))


def gotta_go_fast(username, vagrant_cloud_token):
    """The same thing as build_all() but with a pool of worker processes."""
    print('Building all images.')
    builds = []
    pool = Pool(processes=2)
    #pool = Pool(processes=(cpu_count() / 2))
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if 'build.sh' in files:
            with open(os.path.join(root, 'box_info.json'),
                      'r') as box_info_file:
                box_info = json.load(box_info_file)
                auto_build = box_info['auto_build']
                if auto_build is not None:
                    if auto_build.lower() == 'true':
                        auto_build = True
                    else:
                        auto_build = False
                else:
                    auto_build = True
                build_image = get_box(box_info, username, vagrant_cloud_token)
                if auto_build and build_image:
                    builds.append(root + '/build.sh')
                    os.chdir(SCRIPT_DIR)
    
    pool.map(go_fast, builds, chunksize = 1)


def get_box(box_info, username, vagrant_cloud_token):
    """Attempt to read box from Vagrant Cloud API."""
    build_image = False
    box_api_url = API_URL + 'box'
    url = '{0}/{1}/{2}'.format(box_api_url,
                               username, box_info['box_name'])
    headers = {'Authorization': 'Bearer {0}'.format(
        vagrant_cloud_token)}
    response = requests.get(url, headers=headers)
    json_data = response.json()
    if response.status_code == 200:
        update_box(box_info, username, vagrant_cloud_token)
        current_time = datetime.now()
        current_version = json_data.get('current_version')
        if current_version is not None:
            last_updated_str = json_data['current_version'][
                'updated_at']
            last_updated_object = datetime.strptime(
                last_updated_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            since_updated_days = (
                current_time - last_updated_object).days
            if since_updated_days > BUILD_OLDER_THAN_DAYS:
                build_image = True
        else:
            build_image = True
    elif response.status_code == 404:
        print('Box missing')
        create_box(box_info, username, vagrant_cloud_token)
        build_image = True
    else:
        print(response.status_code)
    return build_image


def create_box(box_info, username, vagrant_cloud_token):
    """Create box if missing using Vagrant Cloud API."""
    boxes_api_url = API_URL + 'boxes'
    url = '{0}/'.format(boxes_api_url)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(vagrant_cloud_token)}
    payload = {
        'box':
        {
            'username': username,
            'name': box_info['box_name'],
            'is_private': box_info['private'],
            'short_description': box_info['short_description'],
            'description': box_info['description']}
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    json_response = response.json()
    if response.status_code == 200:
        pass
    else:
        print(response.status_code)
    print(json_response)


def create_all(username, vagrant_cloud_token):
    """Looks box_info.json  in each directory and then creates it."""
    print('Building all images.')
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if 'build.sh' in files:
            with open(os.path.join(root, 'box_info.json'),
                      'r') as box_info_file:
                box_info = json.load(box_info_file)
                auto_build = box_info['auto_build']
                if auto_build is not None:
                    if auto_build.lower() == 'true':
                        auto_build = True
                    else:
                        auto_build = False
                else:
                    auto_build = True
                build_image = get_box(box_info, username, vagrant_cloud_token)
                if auto_build:
                    get_box(box_info, username, vagrant_cloud_token)


def check_iso(boxes, vagrant_cloud_token):
    """Looks in template.json in each directory and validates the ISO is accessible."""
    box_api_url = API_URL + 'box/'
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if 'template.json' in files:
            with open(os.path.join(root, 'template.json'),
                      'r') as box_info:
                data = json.load(box_info)
                url = data['iso_url']
                response = requests.head(url)
                if response.status_code != 200:
                    print("Invalid URL: %s" %(url))
                else:
                    print("Valid URL: %s" %(url))


def check_sha(boxes, vagrant_cloud_token):
    """Looks in template.json in each directory and validates the ISO SHA listed matches the remote SHA."""
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if 'template.json' in files:
            with open(os.path.join(root, 'template.json'),
                      'r') as box_info:
                data = json.load(box_info)
                sha = data['iso_checksum']
                url = data['base_url'] + "SHA256SUMS"
                response = requests.get(url)
                if response.status_code != 200:
                    print("Invalid URL: %s" %(url))
                else:
                    if sha not in response.text:
                        print("SHA256 mismatch")


def update_templates():
    """Checks and updates the values in template.json."""
    print('Renaming templates to follow standard naming.')
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if 'template.json' in files:
            with open(os.path.join(root, 'template.json'),
                        'r') as template:
                data = json.load(template)
                checksum = data['iso_checksum']
                checksum_url = data['iso_checksum_url']
                url = data['iso_url']
                local_filename = os.path.basename(urlparse(url).path)
                remote_checksums = requests.get(checksum_url)
                update = False
                if remote_checksums.status_code != 200:
                    print("Invalid checksum url: %s" %(checksum_url))
                else:
                    # Check if the remote filename changed
                    if local_filename not in remote_checksums.text:
                        print("Filename mismatch: %s" %(local_filename))
                        remote_filename = get_close_matches(local_filename, remote_checksums.text.split(), 1, 0.9)
                        print("New filename: %s" %(remote_filename[0]))
                        url = url.replace(local_filename, remote_filename[0])
                        print("New URL: %s" %(url))
                        update = True
                    else:
                        remote_filename = local_filename

                    # Check if the local checksum matches the remote checksum                   
                    if checksum not in remote_checksums.text:
                        print("Checksum mismatch")
                        checksum = filter(lambda x: remote_filename[0] in x, remote_checksums.iter_lines())[0].split()[0]
                        print("New checksum: %s" %(checksum))
                        update = True

            if update:
                with open(os.path.join(root, 'template.json'),
                            'w') as template_update:
                    data['iso_checksum'] = checksum
                    data['iso_url'] = url
                    json.dump(data, template_update, indent = 2, sort_keys=True)

def update_box(box_info, username, vagrant_cloud_token):
    """Update box info using Vagrant Cloud API."""
    box_api_url = API_URL + 'box'
    url = '{0}/{1}/{2}'.format(box_api_url,
                               username, box_info['box_name'])
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(vagrant_cloud_token)}
    payload = {
        'box':
        {
            'name': box_info['box_name'],
            'is_private': box_info['private'],
            'short_description': box_info['short_description'],
            'description': box_info['description']}
    }
    print('Updating box: {0}/{1} info.'.format(username, box_info['box_name']))
    response = requests.put(url, headers=headers, data=json.dumps(payload))
    json_response = response.json()
    if response.status_code == 200:
        pass
    else:
        print(response.status_code)
        print(json_response)


def change_controller(args):
    """Change hard drive controller type for all templates."""
    controller_type = args.controller
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        for _index, item in enumerate(files):
            _filename, ext = os.path.splitext(item)
            if ext == '.json':
                try:
                    json_file = os.path.join(root, item)
                    with open(json_file, 'r') as stream:
                        data = json.load(stream)
                        try:
                            controller = data['variables'][
                                'vm_disk_adapter_type']
                            if controller != controller_type:
                                with open(json_file, 'r') as json_file_data:
                                    read_data = json_file_data.read()
                                    read_data = read_data.replace(
                                        controller, controller_type)
                                with open(json_file, 'w') as (json_file_data):
                                    json_file_data.write(read_data)
                        except KeyError:
                            pass
                except TypeError:
                    pass


def cleanup_builds():
    """Clean up lingering build data and artifacts."""
    print('Cleaning up any lingering build data.')
    for root, dirs, files in os.walk(SCRIPT_DIR):
        for item in dirs:
            if 'output-' in item:
                shutil.rmtree(os.path.join(root, item))
            if item == '.vagrant':
                shutil.rmtree(os.path.join(root, item))
            if item == 'packer_cache':
                shutil.rmtree(os.path.join(root, item))

        for item in files:
            filename, ext = os.path.splitext(item)
            if filename == 'Vagrantfile':
                os.remove(os.path.join(root, item))
            if ext == '.box':
                os.remove(os.path.join(root, item))
            if ext == '.iso':
                os.remove(os.path.join(root, item))


def rename_templates():
    """Renames legacy template names to more standardized template.json."""
    print('Renaming templates to follow standard naming.')
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        for _index, item in enumerate(files):
            _filename, ext = os.path.splitext(item)
            if ext == '.json':
                try:
                    json_file = os.path.join(root, item)
                    with open(json_file, 'r') as stream:
                        data = json.load(stream)
                        try:
                            _vm_name = data['vm_name']
                            json_template = os.path.join(root, 'template.json')
                            build_script = os.path.join(root, 'build.sh')
                            with open(build_script, 'r') as build_script_data:
                                read_data = build_script_data.read()
                                read_data = read_data.replace(
                                    item, 'template.json')
                            with open(build_script, 'w') as (
                                    build_script_data):
                                build_script_data.write(read_data)
                            process = subprocess.Popen(
                                ['git', 'add', build_script])
                            process.wait()
                            if item != 'template.json':
                                process = subprocess.Popen([
                                    'git', 'mv', json_file, json_template])
                                process.wait()
                        except KeyError:
                            pass
                except TypeError:
                    pass


def upload_boxes(vagrant_cloud_token):
    """Looks for upload_boxes script in each directory and then executes it."""
    print('Uploading all images.')
    boxes = dict()
    get_boxes(boxes, vagrant_cloud_token)
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if root != SCRIPT_DIR:
            if 'box_info.json' in files:
                with open(os.path.join(root, 'box_info.json'),
                          'r') as box_info:
                    data = json.load(box_info)
                    box_tag = data['box_tag']
                    existing_versions = boxes.get(box_tag)['versions']
                for file in files:
                    if file.endswith('.box'):
                        box_path = os.path.join(root, file)
                        box_provider_name = file.split('-')[4]
                        box_version = file.split('-')[5].split('.box')[0]
                        version_exists = False
                        provider_exists = False
                        for version in existing_versions:
                            if version['version'] == box_version:
                                version_exists = True
                                version_providers = version.get('providers')
                                if version_providers is not None:
                                    for provider in version_providers:
                                        if box_provider_name in provider[
                                                'name']:
                                            provider_exists = True
                                            break
                                break
                        # We convert vmware provider to vmware_desktop
                        if box_provider_name == 'vmware':
                            box_provider_name = 'vmware_desktop'
                        if not version_exists:
                            create_box_version(
                                box_tag, box_version, vagrant_cloud_token)
                            create_box_provider(
                                box_tag, box_version, box_provider_name,
                                vagrant_cloud_token)
                            upload_box(box_tag, box_path,
                                       box_version, box_provider_name,
                                       vagrant_cloud_token)
                        if version_exists and not provider_exists:
                            create_box_provider(
                                box_tag, box_version, box_provider_name,
                                vagrant_cloud_token)
                            upload_box(box_tag, box_path,
                                       box_version, box_provider_name,
                                       vagrant_cloud_token)


def create_box_version(box_tag, box_version, vagrant_cloud_token):
    """Create box version if missing using Vagrant Cloud API."""
    box_api_url = API_URL + 'box'
    url = '{0}/{1}/versions'.format(box_api_url, box_tag)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(vagrant_cloud_token)}
    payload = {'version': {'version': box_version}}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    json_response = response.json()
    if response.status_code == 200:
        pass
    else:
        print(json_response)
        print(response.status_code)
        sys.exit(1)
    print(json_response)


def create_box_provider(box_tag, box_version, box_provider_name,
                        vagrant_cloud_token):
    """Create box version provider if missing using Vagrant Cloud API."""
    box_api_url = API_URL + 'box'
    url = '{0}/{1}/version/{2}/providers'.format(
        box_api_url, box_tag, box_version)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(vagrant_cloud_token)}
    payload = {'provider': {'name': box_provider_name}}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    json_response = response.json()
    if response.status_code == 200:
        pass
    else:
        print(response.status_code)
        sys.exit(1)
    print(json_response)


def upload_box(box_tag, box_path, box_version, box_provider_name,
               vagrant_cloud_token):
    """Upload box to Vagrant Cloud."""
    box_api_url = API_URL + 'box'
    url = '{0}/{1}/version/{2}/provider/{3}/upload'.format(
        box_api_url, box_tag, box_version, box_provider_name)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(vagrant_cloud_token)}
    # Get upload path
    response = requests.get(url, headers=headers)
    json_response = response.json()
    upload_path = json_response.get('upload_path')
    box_size = str(os.path.getsize(box_path))
    files = {'file': open(box_path, 'rb')}
    upload_cmd = '/usr/bin/vagrant cloud publish --force {0} {1} {2} {3}'.format(box_tag, box_version, box_provider_name, box_path)
    print('Uploading box: {0} version: {1} provider: {2}'.format(
        box_tag, box_version, box_provider_name))
    print("""
    Local path: {0}
    Remote path: {1}
    Upload command: {2}
    """.format(box_path, upload_path, upload_cmd))
    
    process = subprocess.Popen(upload_cmd.split())
    process.wait()
    if process.returncode != 0:
        print('Upload of {0} failed'.format(box_tag))
        sys.exit(1)


def commit_manifests(repo_facts):
    """Auto commit manifests."""
    repo_path = os.getcwd()
    repo = git.Repo(repo_path)
    commit = False
    for item in repo_facts['changed_files']:
        if 'manifest.json' in item:
            repo.index.add([item])
            commit = True
    for item in repo_facts['untracked_files']:
        if 'manifest.json' in item:
            repo.index.add([item])
            commit = True
    if commit:
        commit_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        commit_msg = '{} - Manifest Updates'.format(commit_date)
        repo.git.commit('-m', '{}'.format(commit_msg))
        repo.git.push()


def view_manifests():
    """Find build manifests and display to stdout."""
    for root, _dirs, files in os.walk(SCRIPT_DIR):
        if 'manifest.json' in files:
            json_file = os.path.join(root, 'manifest.json')
            try:
                with open(json_file, 'r') as stream:
                    data = json.load(stream)
                    print(json.dumps(data, indent=4))
            except ValueError:
                pass

# def latest_build(root):
#     build_image = False
#     current_time_epoch = time.mktime(datetime.now().timetuple())
#     older_than_days_epoch = current_time_epoch - \
#         (86400 * BUILD_OLDER_THAN_DAYS)
#     older_than_days = int((older_than_days_epoch/86400) + 25569)
#     json_file = os.path.join(root, 'manifest.json')
#     if os.path.isfile(json_file):
#         with open(json_file, 'r') as stream:
#             data = json.load(stream)
#             last_run_uuid = data['last_run_uuid']
#             builds = data['builds']
#             for build in builds:
#                 if build['packer_run_uuid'] == last_run_uuid:
#                     last_build_time_epoch = build['build_time']
#                     last_build_time = int(
#                         (last_build_time_epoch/86400) + 25569)
#                     if last_build_time < older_than_days:
#                         build_image = True
#                     break
#     else:
#         build_image = True
#     return build_image


if __name__ == '__main__':
    main()
