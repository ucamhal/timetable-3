'''
Created on May 9, 2012

@author: ieb
'''
import os

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _getGitRevision():
    if os.path.exists("%s/.git/HEAD" % ROOT_PATH):
        f = open("%s/.git/HEAD" % ROOT_PATH)
        ref = f.read().split(' ')[1].strip()
        f.close()
        branch = os.path.basename(ref)
        if os.path.exists("%s/.git/%s" % (ROOT_PATH, ref)):
            f = open("%s/.git/%s" % (ROOT_PATH, ref))
            revision = f.read().strip()
            f.close()
            return revision, branch
    if os.path.exists("%s/version.txt" % ROOT_PATH):
        f = open("%s/version.txt" % ROOT_PATH)
        revision = f.read()
        f.close()
        branch = "deployed"
        return revision, branch
    return "unknown-revision", "unknown-branch"



GIT_REVISION, GIT_BRANCH = _getGitRevision()

def git_revivion_contextprocessor(request):
    return {
            'GIT_REVISION' : GIT_REVISION,
            'GIT_BRANCH' : GIT_BRANCH,
            }
