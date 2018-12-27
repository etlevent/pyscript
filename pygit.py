"""

Usage:
    pygit.py (--checkout | --update) <branchName>...
    pygit.py --version <versionName>
    pygit.py --clone [<rootDir>]
    pygit.py --merge <from> <to>
    pygit.py --tag <tag_branch> <tagName>
    pygit.py <branchName>...

Options:
    -h --help     help
    --checkout    checkout only.
    --update      update branch and checkout back.
    --version     update project version
    --clone       clone remote repos
    --merge       merge branch
    --tag         tag in branch and push
"""
import os

from docopt import docopt

default_git_url = 'git@git.homelabs.cn'


def execute_cmd(command) -> str:
    """
    execute command line
    :param command:
    :return:
    """
    print('execute cmd [%s]' % command)
    return os.popen(command).read()


def current_branch() -> str:
    """
    get current branch
    :return:
    """
    return execute_cmd('git rev-parse --abbrev-ref HEAD').rstrip()


def checkout_branch(branch_name) -> str:
    """
    checkout branch if needed
    :param branch_name:
    :return:
    """
    return execute_cmd(
        'git checkout %s' % branch_name) if current_branch() != branch_name else 'Skip! Now is [%s]' % branch_name


def pull() -> str:
    """
    git pull
    :return:
    """
    return execute_cmd('git pull')


def push() -> str:
    """
    git push
    :return:
    """
    return execute_cmd('git push')


def tag(tag_name):
    """
    make tag
    :param tag_name:
    :return:
    """
    # push all local project tags
    # 'git push origin --tags'
    commands = [
        'git tag -a %s -m \"tag %s\"' % (tag_name, tag_name),
        'git push origin %s' % tag_name
    ]
    [print(execute_cmd(cmd)) for cmd in commands]


def merge(_from, _to):
    """
    merge two branch
    :param _from:
    :param _to:
    :return:
    """
    current = current_branch()
    update(_from)
    update(_to)
    command = 'git merge %s' % _from
    print(execute_cmd(command))
    print(push())
    print(checkout_branch(current))


def update(branch_name):
    print(checkout_branch(branch_name))
    print(pull())


def tag_branch(branch_name, tag_name):
    """
    update branch, tag, push
    :param branch_name:
    :param tag_name:
    :return:
    """
    current = current_branch()
    update(branch_name)
    tag(tag_name)
    print(checkout_branch(current))


def clone(project_name, dir_name=None, git_url=default_git_url) -> str:
    """
    git clone
    :param project_name:
    :param dir_name:
    :param git_url:
    :return:
    """
    format_git_url = '%s:{}.git' % git_url
    clone_cmd = 'git clone %s' % format_git_url.format(project_name)
    command = clone_cmd if not dir_name else ' '.join([clone_cmd, dir_name])
    print('clone workspace: ', os.getcwd())
    return execute_cmd(command)


def call_set_versions(versions):
    """
    modify versions
    :param versions:
    :return:
    """
    set_versions = 'setVersions.{}'
    bat_set_versions = set_versions.format('bat')
    sh_set_versions = set_versions.format('sh')
    is_windows = os.name == 'nt'
    if not os.path.exists(sh_set_versions) and not os.path.exists(bat_set_versions):
        print('Skip [%s]. Don\'t have %s or %s' % (os.getcwd(), bat_set_versions, sh_set_versions))
        return
    elif not is_windows and not os.path.exists(sh_set_versions):
        print('Current OS [%s]. But don\'t have %s' % (os.name, sh_set_versions))
        return
    cmd_set_versions = bat_set_versions if os.path.exists(
        bat_set_versions) else 'sh ./%s' % sh_set_versions if is_windows else './%s' % sh_set_versions
    commands = [
        'git checkout .',
        'git checkout develop',
        'git pull',
        ' '.join([cmd_set_versions, versions]),
        'git commit -a -m \"update version [%s]\"' % versions,
        'git push'
    ]
    [print(execute_cmd(cmd)) for cmd in commands]


def each_repos(func, root=os.getcwd()):
    if func is None:
        return
    workspaces = filter(lambda w: os.path.isdir(w) and os.path.exists(os.path.join(w, '.git')),
                        map(lambda f: os.path.join(root, f), os.listdir(root)))
    for workspace in workspaces:
        os.chdir(workspace)
        print('current workspace [%s]' % workspace)
        func()


def clone_repos(root_dir, git_url=default_git_url):
    def clone_from_git(project_name):
        _name = input('Input a new project name. Default is %s: ' % project_name)
        print('new_name=%s. project name=%s' % (_name, project_name))
        print(clone(project_name, _name))

    def select_project(max_len) -> int:
        while True:
            try:
                val = int(input('Please Select:'))
                if 0 <= val < max_len:
                    return val
            except ValueError:
                print('input a valid number.')

    if root_dir:
        os.chdir(root_dir)
    cmd_ssh = 'ssh -T %s' % git_url
    ret = execute_cmd(cmd_ssh)
    project_list = list(map(lambda x: x.split('\t')[1], filter(lambda x: x and '\t' in x, ret.split('\n'))))
    print('There is [%d] projects at git [%s]' % (len(project_list), git_url))
    if len(project_list):
        project_list.append('** All Projects.** ')
    print('all projects at server %s:\n' % git_url)
    for i in range(len(project_list)):
        print('%d.\t%s' % (i, project_list[i]))
    index = select_project(len(project_list))
    print('select [%s]' % project_list[index])
    len_real_project = len(project_list) - 1
    [clone_from_git(project_list[i]) for i in range(len_real_project)] if index == len_real_project else clone_from_git(
        project_list[index])


def update_checkout(branch_list):
    def func():
        current = current_branch()
        [update(branch) for branch in branch_list]
        checkout_branch(current)

    each_repos(func)


arguments = docopt(__doc__)
print(arguments)
if arguments['--version']:
    each_repos(lambda: call_set_versions(arguments['<versionName>']))
elif arguments['--checkout']:
    each_repos(lambda: [print(checkout_branch(branch)) for branch in arguments['<branchName>']])
elif arguments['--update']:
    each_repos(lambda: [update(branch) for branch in arguments['<branchName>']])
elif arguments['--clone']:
    clone_repos(arguments['<rootDir>'])
elif arguments['--merge']:
    each_repos(lambda: merge(arguments['<from>'], arguments['<to>']))
elif arguments['--tag']:
    each_repos(lambda: tag_branch(arguments['<tag_branch>'], arguments['<tagName>']))
else:
    update_checkout(arguments['<branchName>'])
