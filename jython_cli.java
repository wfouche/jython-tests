///usr/bin/env jbang "$0" "$@" ; exit $?

//JAVA 21

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class jython_cli {
    private static final String text = """
            //import org.python.util.jython;
            import org.python.util.PythonInterpreter;
            import java.util.Base64;
            
            public class __CLASSNAME__ {
            
                public static String mainScriptTextBase64 = "__MAIN_SCRIPT__";
 
                public static void main(String... args) {
                    String mainScriptFilename = "__MAIN_SCRIPT_FILENAME__";
                    String mainScript = "";
                    String jythonArgsScript = "";
                    for (String arg: args) {
                        //System.out.println("Java: " + arg);
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
                        //System.out.println("===");
                        //System.out.println(text);
                        //System.out.println("===");
                        mainScript = text;
                    }
                    //System.out.println("args --> " + jythonArgsScript);
                    {
                        // run script
                        PythonInterpreter pyInterp = new PythonInterpreter();
                        // initialize args
                        pyInterp.exec(jythonArgsScript);
                        // run script
                        //pyInterp.exec("__name__=\\"\\"");
                        pyInterp.exec(mainScript);
                    }
                    //jython.main(args);
                }
            }            
            """;

    public static void main(String[] args) throws IOException {
        String scriptFilename = args[0];
        String javaClassname = new File(scriptFilename).getName().substring(0, scriptFilename.length() - 3) + "_py";
        String javaFilename = scriptFilename.replace(".", "_") + ".java";
        List<String> deps = new ArrayList<>();
        String jythonVersion = "2.7.4";
        String javaVersion = "21";

        List<String> lines = Files.readAllLines(Paths.get(scriptFilename));
        String tag1 = "##DEPS";
        String tag2 = "##JYTHON";
        String tag3 = "##JAVA";

        for (String line : lines) {
            if (line.length() > tag1.length() && line.startsWith(tag1)) {
                String[] list = line.split(" ");
                String dep = list[1];
                deps.add(dep);
            }
            if (line.length() > tag2.length() && line.startsWith(tag2)) {
                jythonVersion = line.split(" ")[1];
            }
            if (line.length() > tag3.length() && line.startsWith(tag3)) {
                javaVersion = line.split(" ")[1];
            }
        }

        String dep = "org.python:jython-standalone:" + jythonVersion;
        deps.add(dep);

        byte[] data = Files.readAllBytes(Paths.get(scriptFilename));
        String scriptFileTextB64 = Base64.getEncoder().encodeToString(data);

        try (BufferedWriter jf = new BufferedWriter(new FileWriter(javaFilename))) {
            jf.write("///usr/bin/env jbang \"$0\" \"$@\" ; exit $?" + System.lineSeparator() + System.lineSeparator());
            for (String dependency : deps) {
                jf.write("//DEPS " + dependency + System.lineSeparator());
            }
            jf.write("//JAVA " + javaVersion + System.lineSeparator());
            String jtext = text.replace("__CLASSNAME__", javaClassname)
                               .replace("__MAIN_SCRIPT__", scriptFileTextB64)
                               .replace("__MAIN_SCRIPT_FILENAME__", scriptFilename);
            jf.write(jtext);
        }

//        StringBuilder params = new StringBuilder();
//        for (int i = 1; i < args.length; i++) {
//            if (params.length() > 0) {
//                params.append(" ");
//            }
//            params.append(args[i]);
//        }
//        Runtime.getRuntime().exec("jbang run " + javaFilename + " " + params.toString());

        {
            List<String> commandList = new ArrayList<>();

            commandList.add("jbang");
            commandList.add("run");
            commandList.add(javaFilename);
            for (int i = 1; i < args.length; i++) {
                commandList.add(args[i]);
            }

            try {
                ProcessBuilder processBuilder = new ProcessBuilder(commandList);
                //processBuilder.directory(new java.io.File("."));

                Process process = processBuilder.start();

                // Read the output of the process
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }

                // Read any error output
//                BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
//                while ((line = errorReader.readLine()) != null) {
//                    System.err.println(line);
//                }

                // Wait for the process to complete
                int exitCode = process.waitFor();
                //System.out.println("\nProcess finished with exit code: " + exitCode);

            } catch (IOException e) {
                System.err.println("Error executing Gradle command: " + e.getMessage());
            } catch (InterruptedException e) {
                System.err.println("Process interrupted: " + e.getMessage());
            }
        }
    }
}
