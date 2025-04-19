#!/usr/bin/env python3
import os
import sys
import base64
import pprint
import re
import tomllib

def readMetadata(script: str) -> dict | None:
    name = 'jbang'
    REGEX = r'(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$'
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

textJython = """
import org.python.util.PythonInterpreter;
import java.util.Base64;

public class __CLASSNAME__ {

    public static String mainScriptTextBase64 = "__MAIN_SCRIPT__";
    
    public static void main(String... args) {
        String mainScriptFilename = "__MAIN_SCRIPT_FILENAME__";
        String mainScript = "";
        String pythonArgsScript = "";
        for (String arg: args) {
            if (pythonArgsScript.length() == 0) {
                if (!arg.equals(mainScriptFilename)) {
                    pythonArgsScript += "'" + mainScriptFilename + "', ";
                }
            } else {
                pythonArgsScript += ", ";
            }
            pythonArgsScript += "'" + arg + "'";
        }
        if (pythonArgsScript.length() == 0) {
            pythonArgsScript = "'" + mainScriptFilename + "'";
        }
        pythonArgsScript = "import sys; sys.argv = [" + pythonArgsScript + "]";
        {
            byte[] decodedBytes = Base64.getDecoder().decode(mainScriptTextBase64);
            String text = new String(decodedBytes);
            mainScript = text;
        }
        {
            // run script
            PythonInterpreter pyInterp = new PythonInterpreter();

            // initialize args
            pyInterp.exec(pythonArgsScript);

            // run script
            //pyInterp.exec("__name__=\"\"");
            pyInterp.exec(mainScript);
        }
    }
}

"""

textGraalPython = """
import org.graalvm.polyglot.*;
import java.util.Base64;

public class __CLASSNAME__ {

    public static String mainScriptTextBase64 = "__MAIN_SCRIPT__";

    public static void main(String... args) {
        String mainScriptFilename = "__MAIN_SCRIPT_FILENAME__";
        String mainScript = "";
        String pythonArgsScript = "";
        for (String arg: args) {
            if (pythonArgsScript.length() == 0) {
                if (!arg.equals(mainScriptFilename)) {
                    pythonArgsScript += "'" + mainScriptFilename + "', ";
                }
            } else {
                pythonArgsScript += ", ";
            }
            pythonArgsScript += "'" + arg + "'";
        }
        if (pythonArgsScript.length() == 0) {
            pythonArgsScript = "'" + mainScriptFilename + "'";
        }
        pythonArgsScript = "import sys; sys.argv = [" + pythonArgsScript + "]";
        {
            byte[] decodedBytes = Base64.getDecoder().decode(mainScriptTextBase64);
            String text = new String(decodedBytes);
            mainScript = text;
        }
        {
            try (var context = Context.newBuilder().allowAllAccess(true).build()) {
                Source sourceArgs = Source.create("python", pythonArgsScript);
                Source sourceMain = Source.create("python", mainScript);
                Value result = context.eval(sourceArgs);
                result = context.eval(sourceMain);
                //System.out.println(context.eval("python", "'Hello Python!'").asString());
                //System.out.println(context.eval("python", "1+1"));
            }
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
    #print("")
    #pprint.pp(metadata)
    #print("")
    deps = []
    jythonVersion = "2.7.4"
    graalpyVersion = ""
    javaVersion = "21"

    k = "requires-jython"
    if k in metadata.keys():
        jythonVersion = metadata["requires-jython"][2:]
    k = "requires-graalpy"
    if k in metadata.keys():
        graalpyVersion = metadata["requires-graalpy"][2:]
    k = "requires-java"
    if k in metadata.keys():
        javaVersion = metadata["requires-java"][2:]
    k = "dependencies"
    if k in metadata.keys():
        for dep in metadata["dependencies"]:
            deps.append(dep)
    if len(graalpyVersion) > 0:
        dep = 'org.graalvm.python:jbang:' + graalpyVersion
    else:
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
    if len(graalpyVersion) > 0:
        jf.write('//RUNTIME_OPTIONS -XX:+UnlockExperimentalVMOptions -XX:+EnableJVMCI -Dpolyglot.engine.WarnInterpreterOnly=false\n')
    jf.write('// spotless:on\n')

    if len(graalpyVersion) > 0:
        jtext = textGraalPython
    else:
        jtext = textJython
    jtext = jtext.replace("__CLASSNAME__",javaClassname)
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
    #os.unlink(javaFilename)
main()
