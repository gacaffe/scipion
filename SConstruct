#!/usr/bin/env python

# basic setup, import all environment and custom tools
import os
import platform 
import SCons.Script
if platform.system() == 'Windows':
    env = Environment(ENV=os.environ)
    env['ENV']['JAVA_HOME'] = "/c/Java/jdk1.6.0_34"
    env.PrependENVPath('PATH', 'C:\\MinGW\\bin')
    env.PrependENVPath('LIB', 'C:\\MinGW\\lib') 
else:
    env = Environment(ENV=os.environ,
          tools=['default', 'disttar'],
          toolpath=['external/scons/ToolsFromWiki'])

# avoid cruft in top dir
base_dir = 'build'
if not os.path.exists(base_dir):
    Execute(Mkdir(base_dir))
base_dir += '/'

# use only one signature file
env.SConsignFile(base_dir + 'SCons.dblite')

# read -or not- the cached -non default- options
if (ARGUMENTS['mode'] == 'configure'):
    opts = Variables(None, ARGUMENTS)
else:
    opts = Variables('.xmipp_scons.options', ARGUMENTS)

#print 'en opts', opts['MPI_LINKERFORPROGRAMS']

opts.Add('CC', 'The C compiler', 'gcc')
opts.Add('CXX', 'The C++ compiler', 'g++')

# Hack, some architectures required this (Coss?)
opts.Add('LINKERFORPROGRAMS', 'Linker for programs', 'g++')

# FIXME With ARGUMENTS these should be read... right?
#hope is OK roberto
if platform.system()=='Windows':
    opts.Add('CCFLAGS', 'The C compiler flags', '-fpermissive -I/c/MinGW/include')
    opts.Add('CXXFLAGS', 'The C++ compiler flags', '-fpermissive -I/c/MinGW/include')
    opts.Add(BoolVariable('release', 'Release mode', 'yes'))
else:
    opts.Add('CCFLAGS', 'The C compiler flags', None)
    opts.Add('CXXFLAGS', 'The C++ compiler flags', None)
    opts.Add(BoolVariable('release', 'Release mode', 'yes'))

opts.Add(BoolVariable('debug', 'Build debug version?', 'no'))
#Profile version implies debug and then it will be ignored
opts.Add(BoolVariable('profile', 'Build profile version?', 'no'))
opts.Add(BoolVariable('warn', 'Show warnings?', 'no'))
opts.Add(BoolVariable('fast', 'Fast?', 'no'))
opts.Add(BoolVariable('static', 'Prevent dynamic linking?', 'no'))

opts.Add('prepend', 'What to prepend to executable names', 'xmipp')
opts.Add(BoolVariable('quiet', 'Hide command line?', 'yes'))

opts.Add(BoolVariable('java', 'Build the java programs?', 'yes'))

opts.Add(BoolVariable('arpack', 'Build the arpack programs?', 'no'))

opts.Add(BoolVariable('gtest', 'Build tests?', 'yes'))

opts.Add(BoolVariable('mpi', 'Build the MPI programs?', 'yes'))

opts.Add('MPI_CC', 'MPI C compiler', 'mpicc')
opts.Add('MPI_CXX', 'MPI C++ compiler', 'mpiCC')
opts.Add('MPI_LINKERFORPROGRAMS', 'MPI Linker for programs', 'mpiCC')
opts.Add('MPI_INCLUDE', 'MPI headers dir ', '/usr/include')
opts.Add('MPI_LIBDIR', 'MPI libraries dir ', '/usr/lib')
opts.Add('MPI_LIB', 'MPI library', 'mpi')

#MINGW 
opts.Add('MINGW_PATHS', 'Include path for MinGW', '')

opts.Add('prefix', 'Base installation directory', Dir('.').abspath)

opts.Add(BoolVariable('matlab', 'Build the Matlab bindings?', 'no'))
opts.Add('MATLAB_DIR', 'Matlab installation dir', '/usr/local/matlab')

opts.Add(BoolVariable('cuda', 'Build GPU stuff?', 'no'))
opts.Add('CUDA_SDK_PATH', 'CUDA SDK dir', '/root/NVIDIA_GPU_Computing_SDK')
opts.Add('CUDA_LIB_PATH', 'CUDA RunTimeLib dir', '/usr/local/cuda/lib64')


#opts.Add(BoolVariable('verbose_fftw', 'Verbose configuring of FFTW libraries?', 'no'))
#opts.Add('FFTWFLAGS', 'Additional flags for FFTW configure', '--enable-threads')
#
#opts.Add(BoolVariable('verbose_tiff', 'Verbose configuring of TIFF libraries?', 'no'))
#opts.Add('TIFFFLAGS', 'Additional flags for TIFF configure', 'CPPFLAGS=-w')
#
#opts.Add(BoolVariable('verbose_arpack', 'Verbose configuring of ARPACK++ libraries?', 'no'))
#opts.Add('ARPACKFLAGS', 'Additional flags for ARPACK++ configure', '')
#
#opts.Add(BoolVariable('verbose_sqlite', 'Verbose configuring of SQLite libraries?', 'no'))
#opts.Add('SQLITEFLAGS', 'Additional flags for SQLite configure', 'CPPFLAGS=-w CFLAGS=-DSQLITE_ENABLE_UPDATE_DELETE_LIMIT=1')
#
#opts.Add(BoolVariable('verbose_python', 'Verbose configuring of Python compilation?', 'no'))
#opts.Add('PYTHONFLAGS', 'Additional flags for Python configure', '')

opts.Add('JAVAC', 'Java compiler', 'javac')
opts.Add('JAVA_HOME', 'Java installation directory', '')
opts.Add('JNI_CPPPATH', 'Directory of jni.h', '')
#print 'en opts-2', opts['MPI_LINKERFORPROGRAMS']

opts.Update(env)
# generate help for options
Help(opts.GenerateHelpText(env, sort=cmp))

# FIXME Hack, for several flags in command-line
env['CCFLAGS'] = Split(env['CCFLAGS'])
env['CXXFLAGS'] = Split(env['CXXFLAGS'])
env['JARFLAGS'] = '-Mcf'    # Default "cf". "M" = Do not add a manifest file.

# These defaults are needed for both the custom tests and the compilation
env.SetDefault(LIBS='')
env.SetDefault(LIBPATH='')
env.SetDefault(CPPPATH='')

def AppendIfNotExists(**args):
    append = True
    for k, v in args.iteritems():
        if v in env[k]:
            append = False
    if append:
        env.Append(**args)
    
# This is required for both modes
env['STATIC_FLAG'] = '-static'

if (ARGUMENTS['mode'] == 'configure'):
    # --- This is the configure mode

    # Custom tests
    def CheckMPI(context, mpi_inc, mpi_libpath, mpi_lib, mpi_cc, mpi_cxx, mpi_link):
        context.Message('* Checking for MPI ... ')

        lastLIBS = context.env['LIBS']
        lastLIBPATH = context.env['LIBPATH']
        lastCPPPATH = context.env['CPPPATH']
        lastCC = context.env['CC']
        lastCXX = context.env['CXX']

        # TODO Replace() also here?
        context.env.Append(LIBS=mpi_lib, LIBPATH=mpi_libpath,
                           CPPPATH=mpi_inc)
        context.env.Replace(LINK=mpi_link)
        context.env.Replace(CC=mpi_cc, CXX=mpi_cxx)

        # Test only C++ mpi compiler
        ret = context.TryLink('''
        #include <mpi.h>
        int main(int argc, char** argv)
        {
            MPI_Init(0, 0);
            MPI_Finalize();
            return 0;
        }
    ''', '.cpp')

        # NOTE: We don't want MPI flags for not-mpi programs (always revert)
        # env['mpi'] remains 1 so those can be enabled again when needed

        context.env.Replace(LIBS=lastLIBS)
        context.env.Replace(LIBPATH=lastLIBPATH)
        context.env.Replace(CPPPATH=lastCPPPATH)
        context.env.Replace(CC=lastCC)
        context.env.Replace(CXX=lastCXX)

        context.Result(ret)
        return ret

    # Configuration or cleaning
    if env.GetOption('clean'):
        print '* Cleaning  ...'
        if 'distclean' in COMMAND_LINE_TARGETS:
            print '* Deleting configuration ...'
            Execute(Delete(base_dir))
            Execute(Delete(env['prefix']))
    else:
        print '* Configuring  ...'
        config_dir = base_dir + 'config.tests'
        config_log = base_dir + 'config.log'

    # release?
    # This is done in compile mode
#    if int(env['release']):
#        AppendIfNotExists(CCFLAGS='-DRELEASE_MODE')
#        AppendIfNotExists(CXXFLAGS='-DRELEASE_MODE')

    # static?
    if int(env['static']):
        AppendIfNotExists(CCFLAGS='$STATIC_FLAG')
        AppendIfNotExists(LINKFLAGS='$STATIC_FLAG')

    # osx?
#    if env['PLATFORM'] == 'darwin':
#        AppendIfNotExists(CCFLAGS='-m64')
#        AppendIfNotExists(CXXFLAGS='-m64')
#        AppendIfNotExists(LINKFLAGS='-m64')

    # mingw?
    if platform.system() == 'Windows':
         AppendIfNotExists(CCFLAGS='-f permissive -Ilibraries/data -I/c/MinGW/include')
         AppendIfNotExists(CXXFLAGS='-f permissive -Ilibraries/data -I/c/MinGW/include')
#         AppendIfNotExists(LINKFLAGS='')

    # QT
    if int(env['qt']):
        if int(env['QT4']):
            print '* QT4 selected!'
            # FIXME /usr/lib/qt4
            env['QTDIR'] = ''
            env['QT_LIB'] = ''
        else:
            print '* QT3 selected!'

        # QT3 makes use of QTDIR
        if ARGUMENTS.get('QTDIR'):
            print '* Trying user-supplied QTDIR: ' + ARGUMENTS.get('QTDIR')
            env['QTDIR'] = ARGUMENTS.get('QTDIR')
        else:
            print '* Trying environment\'s $QTDIR'
            if os.environ.has_key('QTDIR'):
                env['QTDIR'] = os.environ['QTDIR']
            else:
                print '* QTDIR not in environment nor supplied' \
                     ' (default value won\'t probably work)'
                print '  Please set it correctly, i.e.: export ' \
                      'QTDIR=/path/to/qt'
                print '  or specify one directly in command line: '\
                      'QTDIR=/path/to/qt'
                print '* Trying default value: ' + env['QTDIR']

        # Create a new environment with Qt tool enabled to see if it works
        envQT = env.Clone()

        if int(env['QT4']):
            # DBG
            try:
                envQT.Tool('qt4')
                envQT.EnableQt4Modules(['QtCore', 'QtGui', 'Qt3Support'], debug=False)
            except:
                print "*QT4 not found! Disabling..."
                env['qt'] = 0
        else:
            envQT.Tool('qt')

        # FIXME Copy() does not work well (adds twice the library, 'qt' ...)
        # envQT.Replace(QT_LIB = env['QT_LIB'])
        envQT.Replace(LINK=env['LINKERFORPROGRAMS'])

        confQT = Configure(envQT, {}, config_dir, config_log)

        if not confQT.CheckLibWithHeader(env['QT_LIB'], 'qapplication.h',
                                         'c++', 'QApplication qapp(0,0);',
                                         0):
            print '* Did not find QT. Disabling ...'
            env['qt'] = 0

        envQT = confQT.Finish()

    # Non-GUI configuration environment
    conf = Configure(env, {'CheckMPI' : CheckMPI}, config_dir, config_log)

    # MPI
    if int(env['mpi']):
        if not conf.CheckMPI(env['MPI_INCLUDE'], env['MPI_LIBDIR'],
                             env['MPI_LIB'], env['MPI_CC'], env['MPI_CXX'], env['MPI_LINKERFORPROGRAMS']):
            print '* Did not find MPI library. Disabling ...'
            env['mpi'] = 0

    # Java
    if int(env['java']) == 1: 
        import sys
        sys.path.append("external/scons/ToolsFromWiki")
        import ConfigureJNI
        if not ConfigureJNI.ConfigureJNI(env):
            env['java'] = 0
            print '* Did not find JNI header. Disabling java support...'
        else:
            print '* JNI header found: ', env['JNI_CPPPATH']

    # MATLAB
    if int(env['matlab']):
        print '* Checking for Matlab ... ',
        if not os.path.exists(env['MATLAB_DIR'] + '/bin/matlab'):
            print 'no'
            print '* Did not find Matlab. Disabling ...'
            env['matlab'] = 0
        else:
            print 'yes'

#    def ConfigureExternalLibrary(libName, libFlags, libpath, verbose):
#            
#        libpath = os.path.join('external', libpath)
#        if not GetOption("help"):
#            if os.path.exists(os.path.join(libpath, 'Makefile')):
#                command = 'cd %s ; make distclean > /dev/null' % libpath
#                print command
#                os.system(command)
#    
#        if not int(env['static']):
#            libFlags += " --enable-shared"
#    
#        if env['PLATFORM'] == 'darwin':
#            libFlags += " CFLAGS='-m64'"
#        
#        msg = "* Configuring " + libName
#        cmd = "cd %s;./configure %s" % (libpath, libFlags)
#        
#        logFile = os.path.join("..", "..", "build", libName + "_configure.log")
#        if not verbose:
#            msg += "(see log file '%s' for details)" % logFile
#            cmd += " > " + logFile
#            
#        print msg, "..."
#        print "   command:  ", cmd
#        os.system(cmd)        
    
#    ConfigureExternalLibrary('sqlite', env['SQLITEFLAGS'], 
#                             'sqlite-3.6.23', int(env['verbose_sqlite']))
#    ConfigureExternalLibrary('python', env['PYTHONFLAGS'], 
#                             'Python-2.7.2', int(env['verbose_python']))
#    ConfigureExternalLibrary('fftw', env['FFTWFLAGS'], 
#                             'fftw-3.2.2', int(env['verbose_fftw']))
#    ConfigureExternalLibrary('tiff', env['TIFFFLAGS'], 
#                             'tiff-3.9.4', int(env['verbose_tiff']))
#    ConfigureExternalLibrary('arpack++', env['ARPACKFLAGS'], 
#                             'arpack++-2.3', int(env['verbose_arpack']))

    # Finish configuration
    env = conf.Finish()
    opts.Save('.xmipp_scons.options', env)


elif (ARGUMENTS['mode'] == 'compile'):
    # --- This is the compilation mode

    # add separator to prepend (not shown in help)
    env['prepend'] = env['prepend'] + '_'

    dp = False #debug or profile?
    dpFlags = ""
    if int(env['profile']):
        dp = True
        dpFlags = ['-g', '-pg']
    elif int(env['debug']):
        dp = True
        dpFlags = ['-g']
    # profile or debug?
    if dp:
        AppendIfNotExists(CXXFLAGS=['-D__XMIPP_DEBUG__'])
        AppendIfNotExists(CXXFLAGS=dpFlags)
        AppendIfNotExists(CCFLAGS=dpFlags)
        AppendIfNotExists(LINKFLAGS=dpFlags)
        #required for print stack trace
    
    # Activate release version when compiling
    if int(env['release']):
        AppendIfNotExists(CCFLAGS=['-DRELEASE_MODE'])
        AppendIfNotExists(CXXFLAGS=['-DRELEASE_MODE'])
        
    if not int(env['cuda']):
	if env['PLATFORM'] != 'cygwin' and env['PLATFORM'] != 'win32':
            AppendIfNotExists(CXXFLAGS=['-rdynamic'])
        AppendIfNotExists(CXXFLAGS=['-O0'])
    else:
        # "safe" optimization
        AppendIfNotExists(CXXFLAGS=['-O2'])
        AppendIfNotExists(CCFLAGS=['-O2'])
        AppendIfNotExists(LINKFLAGS=['-s'])

    if env['PLATFORM'] == 'darwin':
#        env.Append(CXXFLAGS=['-m64'])
#        env.Append(CCFLAGS=['-m64'])
#        env.Append(LINKFLAGS=['-m64'])
        AppendIfNotExists(CXXFLAGS=['-I/usr/include/malloc'])
        AppendIfNotExists(CCFLAGS=['-I/usr/include/malloc'])
#        AppendIfNotExists(LINKFLAGS=['-m64'])


# stdout_handle = os.popen('svnversion -n .')
#    svnver = stdout_handle.read()
#    env.Append(CXXFLAGS="-D'SVN_REV=\""+ svnver +"\"'")
#    env.Append(CCFLAGS="-D'SVN_REV=\""+ svnver +"\"'")

    # Add threads
    env.Append(LINKFLAGS=['-lpthread'])
    #env.Append(CXXFLAGS=['-lpthread'])
    #env.Append(CCFLAGS=['-lpthread'])

    # warnings?
    if int(env['warn']):
        env.Append(CXXFLAGS=['-Wall'])
    else:
        env.Append(CXXFLAGS=['-w'])
        # TODO suppress linker warnings too... what's the flag?
        # env.Append(LINKFLAGS = ['-Wl,???'])

    # fast?
    # COSS' work. I dont like this. Classic debug vs release (asolano)
    if int(env['fast']):
        env.Append(CXXFLAGS=['-O3', '-fomit-frame-pointer', '-ffast-math',
                   '-finline-functions', '-funroll-loops'])

    # verbosity (for $SCONS_VERSION < 0.96.2 option has no effect)
    if int(env['quiet']):
        env['CCCOMSTR'] = 'Compiling $SOURCE'
        env['CXXCOMSTR'] = 'Compiling $SOURCE'
        env['SHCXXCOMSTR'] = 'Compiling $SOURCE'
        env['SHCCCOMSTR'] = 'Compiling $SOURCE'
        env['LINKCOMSTR'] = 'Linking $SOURCE'
        env['ARCOMSTR'] = 'Archiving $TARGET'
        env['SHLINKCOMSTR'] = 'Linking $TARGET'
        env['RANLIBCOMSTR'] = 'Indexing $TARGET'
        env['TARCOMSTR'] = 'Archiving $TARGET'
        env['INSTALLSTR'] = 'Installing $TARGET'

    Export('env')
    env.SConscript('SConscript')

elif (ARGUMENTS['mode'] == 'docs'):
    action = env.Action("doxygen")
    env.Execute(action)

# TODO: make specific modes for generation of dist

# distribution
""" FIXME Testing, not ready for production
env['DISTTAR_FORMAT'] = 'bz2'
env.Append(DISTTAR_EXCLUDEEXTS = ['.o', '.os', '.so', '.a', '.dll', '.cc',
    '.cache', '.pyc', '.cvsignore', '.dblite', '.log', '.bz2'],
DISTTAR_EXCLUDEDIRS = ['CVS', '.svn', '.sconf_temp', 'dist']
)
disttar = env.DistTar(os.path.join(base_dir, 'Xmipp-1.1'), [env.Dir('#')])
env.Alias('dist', disttar)
"""

