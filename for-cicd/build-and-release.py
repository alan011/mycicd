#!/usr/bin/env python3

import os, sys, argparse, datetime, requests, json, yaml
sys.path.append(dirname(abspath(__file__)))
from .config import ENVS, APPS, DOCKER_REPO, PACKGE_SERVER

WORK_DIR   = "/data1/jenkins-build"

class BuildAll(object):
    def __init__(self):
        self.version = datetime.datetime.now().strftime("%Y.%m.%s.%H.%M.%S")

    def parse_args(self):
        ### common parameters.
        parent_parser = argparse.ArgumentParser(add_help=False)
        parent_parser.add_argument('-p', '--project', dest='project', metavar='project_name', required=True,help='project in gitlab')
        parent_parser.add_argument('-b', '--branch',  dest='branch',  metavar='branch_num',   required=True,help="branch for this project.")
        parent_parser.add_argument('-v', '--version', dest='version', metavar='version',      required=True,help="building output version.")

        self.parser = argparse.ArgumentParser(prog='build-all.py', description="ci/cd common used script.")
        subparsers = self.parser.add_subparsers(title='subcommands', dest='subcommand', metavar='')

        ### Subcommand: build
        build_parser = subparsers.add_parser('build', help="To fetch code, build it, make package, build docker image.", parents=[parent_parser])
        build_parser.set_defaults(func=self.build)

        ### Subcommand: release
        release_parser = subparsers.add_parser('release', help="release the building output into the specified env.", parents=[parent_parser])
        release_parser.add_argument('-e', '--env', dest='env', metavar='env', required=True, help=f"supported envs {', '.join(ENVS.keys())}")
        release_parser.set_defaults(func=self.release)

        ### parse args
        self.args = self.parser.parse_args()

    def push_package_to_package_server(self):
        print(f"===> To push package {self.package_name} to package server:")
        os.chdir(self.work_dir)
        cmd = f"rsync -av {self.package_name} root@{PACKGE_SERVER}:/data1/packages/{self.project}/"
        if os.system(cmd):
            SystemExit(f"\nERROR: To push package to package server failed. Project: {self.project}, Version: {self.version}")

    def push_image_to_docker_repo(self):
        print(f"===> To push docker image to docker repo:")
        os.chdir(self.work_dir)
        cmd = f"docker push {DOCKER_REPO}/{self.project}:{self.branch}-{self.version}"
        if os.system(cmd):
            SystemExit(f"\nERROR: To push docker image to docker repo failed. Project: {self.project}, Version: {self.version}")

    def build_docker_image(self):
        print(f"===> To build docker image:")
        os.chdir(self.docker_build_dir)
        cmd = f"docker build -t {self.docker_image}"
        if os.system(cmd):
            raise SystemExit(f"\nERROR:  package failed. Project: {self.project}, Version: {self.version}")

    def make_package(self, target_dir):
        print(f"===> To packge files into a {file_type} file:")
        os.chdir(target_dir)
        cmd = f'zip {self.package_name} *'
        if os.system(cmd):
            raise SystemExit(f"\nERROR: Compile code to package failed. Project: {self.project}, Version: {self.version}")

    def compile_java_proj(self):
        print(f"===> To compile java code:")
        os.chdir(self.src_dir)
        cmd = f"{self.app_config["build_command"]}"
        if os.system(cmd):
            raise SystemExit(f"\nERROR: Compile java code failed. Project: {self.project}, Version: {self.version}")

    def pull_code(self):
        print("\n===> To fetch branch and pull code:")

        git_url = self.project_config['git_url']
        get_code_cmd_list = [
            "git init",
            "git remote add origin %s" % (git_url,),
            "git fetch origin %s" % (self.branch,),
            "git checkout -b %s" % (self.branch,),
            "git pull origin %s" % (self.branch,),
        ]

        os.chdir(self.src_dir)
        for cmd in get_code_cmd_list:
            print("--> %s" % cmd)
            if os.system(cmd):
                raise SystemExit(f"ERROR: Pull code failed. {self.message}")

    def compile_to_package(self):
        print "\n===> To compile and package:"

        if self.app_config.get('app_type') == "static":
            self.compile_static_proj()
        elif self.app_config.get('app_type') == "java":
            self.compile_java_proj()
        else:
            raise SystemExit(f"\nERROR: App type '{}' is not supported to compile.".format(self.app_config.get('app_type')))

    def build(self):
        self.pull_code()
        self.compile_to_package()
        self.upload_package()

    def release(self):
        pass


    def dispatch(self):
        ### To parse arguments
        if self.args.subcommand is None:
            self.parser.print_help()
            sys.exit(1)

        self.project = self.args.project
        self.app_config = APPS.get(self.project)
        if not self.app_config:
            raise SystemExit(f"\nERROR: Unsupported project: {self.project}")
        self.branch  = self.app_config["release_branch"]

        ### To set workspace.
        self.work_dir = os.path.join(WORK_DIR, self.project, self.branch, self.version)
        self.src_dir  = os.path.join(self.work_dir, self.project)
        self.docker_build_dir = os.path.join(self.work_dir, 'docker_build')
        if not os.path.isdir(self.src_dir):
            os.makedirs(self.src_dir)

        ### To set build outputs.
        if self.app_config["app_type"] == "static":
            self.package_name = f"{self.project}-{self.branch}-{self.version}.zip"
        else self.app_config["app_type"] == "java":
            self.package_name = f"{self.project}-{self.branch}-{self.version}.war"
        else:
            raise SystemExit(f"\nERROR: Unsupported app_type: {self.app_config['app_type']}")
        self.docker_image = f"{DOCKER_REPO}/{self.project}:{self.branch}-{self.version}"
        self.message = f"Build information: Project: {self.project}, Branch: {self.branch}, Version: {self.version}"

        ### dispatch action.
        self.args.func()

    def run(self):
        self.parse_args()
        self.dispatch()


if __name__ == "__main__":
    builder = BuildAll()
    builder.run()
