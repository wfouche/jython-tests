#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import base64
import pprint
import re
import tomllib

REGEX = r'(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$'

def readMetadata(script: str) -> dict | None:
    name = 'script'
    matches = list(
        filter(lambda m: m.group('type') == name, re.finditer(REGEX, script))
    )
    if len(matches) > 1:
        raise ValueError(f'Multiple {name} blocks found')
    elif len(matches) == 1:
        content = ''.join(
            line[2:] if line.startswith('# ') else line[1:]
            for line in matches[0].group('content').splitlines(keepends=True)
        )
        return tomllib.loads(content)
    else:
        return None

text = """
import org.python.util.PythonInterpreter;
import java.util.Base64;

public class __CLASSNAME__ {

    public static String mainScriptTextBase64 = "__MAIN_SCRIPT__";
    
    public static void main(String... args) {
        String mainScriptFilename = "__MAIN_SCRIPT_FILENAME__";
        String mainScript = "";
        String jythonArgsScript = ""; 
        for (String arg: args) {
            if (jythonArgsScript.length() == 0) {
                if (!arg.equals(mainScriptFilename)) {
                    jythonArgsScript += "'" + mainScriptFilename + "', ";
                }
            } else {
                jythonArgsScript += ", ";
            }
            jythonArgsScript += "'" + arg + "'";
        }
        if (jythonArgsScript.length() == 0) {
            jythonArgsScript = "'" + mainScriptFilename + "'";
        }
        jythonArgsScript = "import sys; sys.argv = [" + jythonArgsScript + "]";
        {
            byte[] decodedBytes = Base64.getDecoder().decode(mainScriptTextBase64);
            String text = new String(decodedBytes);
            mainScript = text;
        }
        {
            // run script
            PythonInterpreter pyInterp = new PythonInterpreter();

            // initialize args
            pyInterp.exec(jythonArgsScript);

            // run script
            //pyInterp.exec("__name__=\"\"");
            pyInterp.exec(mainScript);
        }
    }
}

"""

#
# https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata
#

def main():
    scriptFilename = sys.argv[1]
    javaClassname = os.path.basename(scriptFilename)[:-3] + "_py"
    javaFilename = os.path.basename(scriptFilename).replace(".","_") + ".java"

    data = open(scriptFilename,"r").read()
    metadata = readMetadata(data)
    print("")
    pprint.pp(metadata)
    print("")
    deps = []
    jythonVersion = "2.7.4"
    javaVersion = "21"

    k = "requires-jython"
    if k in metadata.keys():
        jythonVersion = metadata["requires-jython"][2:]
    k = "requires-java"
    if k in metadata.keys():
        javaVersion = metadata["requires-java"][2:]
    k = "dependencies"
    if k in metadata.keys():
        for dep in metadata["dependencies"]:
            deps.append(dep)
    dep = "org.python:jython-standalone:" + jythonVersion
    deps.append(dep)

    data = open(scriptFilename,'rb').read()
    scriptFileTextB64 = base64.b64encode(data).decode('utf-8')

    jf = open(javaFilename,"w+")
    jf.write('///usr/bin/env jbang "$0" "$@" ; exit $?' + "\n\n")
    jf.write('// spotless:off\n')
    for dep in deps:
        jf.write("//DEPS " + dep + "\n")
        #print(dep)
    jf.write("//JAVA " + javaVersion + "\n")
    jf.write('// spotless:on\n')

    jtext = text.replace("__CLASSNAME__",javaClassname)
    jtext = jtext.replace("__MAIN_SCRIPT__", scriptFileTextB64)
    jtext = jtext.replace("__MAIN_SCRIPT_FILENAME__", scriptFilename)
    jf.write(jtext)
    jf.close()
    #print(sys.argv[1:])
    params = ""
    for e in sys.argv[1:]:
        if len(params) > 0:
            params += " "
        params += e
    os.system("jbang run " + javaFilename + " " + params)
    os.unlink(javaFilename)
main()
