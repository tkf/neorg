import cog
from subprocess import Popen, PIPE


def genehelp(subcommand=''):
    cmd = 'python -m neorg.commands %s -h' % subcommand
    po = Popen(cmd.split(),
               cwd='../..', stdout=PIPE, stderr=PIPE)
    (stdoutdata, stderrdata) = po.communicate()
    stdoutdata = stdoutdata.replace('commands.py', 'neorg', 1)
    cog.out('\n::\n\n')
    lines = (l if l=='' else'    ' + l for l in stdoutdata.splitlines())
    cog.outl('\n'.join(lines))
    cog.out('\n')
