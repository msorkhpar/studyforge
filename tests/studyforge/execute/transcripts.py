"""Real build-tool output for `test_quiet.py`, and exactly where each line came from.

⭐ **Each transcript is what the runner would hand the filter**: already
relative to the source root and scrubbed (`execute.output`). ⛔ **The ONLY
edits are named here, per transcript.** No line was retyped. The runner's
own exit line is NOT part of any transcript; a test appends it, as the
runner does.

- `MAVEN_PASS`: ⭐ **the PINNED toolchain.** Maven 3.9.16 with the plugins
  its default bindings pick (resources 3.4.0, compiler 3.15.0, surefire 3.5.4)
  on the pinned Java (Temurin 25.0.4). It is `code-server-toolchain`'s own
  recording build (`build.py --record-maven`), which runs
  `mvn -B -C -ntp … test` on the component's Maven smoke project,
  `docker/minimal/smoke/maven`, unmodified. That build writes its log to the
  component's untracked work directory. Edits: the build log's step and
  timing prefix is removed, and the in-build root `/unpack/smoke` is made
  relative by `LineGate`, as the runner does with its own root.
- `MAVEN_OFFLINE`, `MAVEN_OFFLINE_TRACE`: Maven 3.9.16 (the pinned VERSION,
  from a local distribution) on Java 26.0.1. The command was `mvn -B -o test`,
  plus `-e` for the trace, run on an unmodified copy of the same smoke
  project with an empty local repository and an empty settings file.
  Edit: `Finished at:` normalised to UTC.
- `JVM_TRACE`: Java 26.0.1 running a short program that prints one line and
  then throws an exception with a cause. No edits.
- `JAVAC_ERROR`: javac 26.0.1 on one source file with an undefined name.
  No edits.
- `GRADLE_FAILURE`: a reader's own paste. Edit: the report path, as `scrub` rewrites it.

⚠️ **Not captured, and why.** A real `mvn test` run with a compile error or
a failing test needs the runner image or a Maven cache holding the pinned
plugins' jars (surefire's JUnit provider among them), so **none exists in this
module.** An offline Maven on an empty repository fails before any plugin
runs. That failure is real, and it is what `MAVEN_OFFLINE` and
`MAVEN_OFFLINE_TRACE` are. ⭐ `test_quiet_image.py` takes the missing
readings against the runner image once one is named. It needs no edit.
"""

from __future__ import annotations

MAVEN_PASS = (
    "[INFO] Scanning for projects...",
    "[INFO] ",
    "[INFO] ----------------------------< smoke:smoke >-----------------------------",
    "[INFO] Building smoke 1",
    "[INFO]   from pom.xml",
    "[INFO] --------------------------------[ jar ]---------------------------------",
    "[INFO] ",
    "[INFO] --- resources:3.4.0:resources (default-resources) @ smoke ---",
    "[INFO] skip non existing resourceDirectory src/main/resources",
    "[INFO] ",
    "[INFO] --- compiler:3.15.0:compile (default-compile) @ smoke ---",
    "[INFO] Recompiling the module because of changed source code.",
    "[INFO] Compiling 1 source file with javac [debug release 21] to target/classes",
    "[INFO] ",
    "[INFO] --- resources:3.4.0:testResources (default-testResources) @ smoke ---",
    "[INFO] skip non existing resourceDirectory src/test/resources",
    "[INFO] ",
    "[INFO] --- compiler:3.15.0:testCompile (default-testCompile) @ smoke ---",
    "[INFO] Recompiling the module because of changed dependency.",
    "[INFO] Compiling 1 source file with javac [debug release 21] to target/test-classes",
    "[INFO] ",
    "[INFO] --- surefire:3.5.4:test (default-test) @ smoke ---",
    (
        "[INFO] Using auto detected provider org.apache.maven.surefire.junitplatform.JUni"
        "tPlatformProvider"
    ),
    "[INFO] ",
    "[INFO] -------------------------------------------------------",
    "[INFO]  T E S T S",
    "[INFO] -------------------------------------------------------",
    "[INFO] Running smoke.AdderTest",
    (
        "[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.020 s "
        "-- in smoke.AdderTest"
    ),
    "[INFO] ",
    "[INFO] Results:",
    "[INFO] ",
    "[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0",
    "[INFO] ",
    "[INFO] ------------------------------------------------------------------------",
    "[INFO] BUILD SUCCESS",
    "[INFO] ------------------------------------------------------------------------",
    "[INFO] Total time:  8.863 s",
    "[INFO] Finished at: 2026-09-18T18:46:16Z",
    "[INFO] ------------------------------------------------------------------------",
)


MAVEN_OFFLINE = (
    "[INFO] Scanning for projects...",
    "[INFO] ",
    "[INFO] ----------------------------< smoke:smoke >-----------------------------",
    "[INFO] Building smoke 1",
    "[INFO]   from pom.xml",
    "[INFO] --------------------------------[ jar ]---------------------------------",
    (
        "[WARNING] The POM for org.apache.maven.plugins:maven-resources-plugin:jar:3.4.0 "
        "is missing, no dependency information available"
    ),
    "[INFO] ------------------------------------------------------------------------",
    "[INFO] BUILD FAILURE",
    "[INFO] ------------------------------------------------------------------------",
    "[INFO] Total time:  0.065 s",
    "[INFO] Finished at: 2026-09-19T02:41:39Z",
    "[INFO] ------------------------------------------------------------------------",
    (
        "[ERROR] Plugin org.apache.maven.plugins:maven-resources-plugin:3.4.0 or one of "
        "its dependencies could not be resolved:"
    ),
    (
        "[ERROR] \tCannot access central (https://repo.maven.apache.org/maven2) in "
        "offline mode and the artifact org.apache.maven.plugins:maven-resources-plugin:ja"
        "r:3.4.0 has not been downloaded from it before."
    ),
    "[ERROR] -> [Help 1]",
    "[ERROR] ",
    "[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.",
    "[ERROR] Re-run Maven using the -X switch to enable full debug logging.",
    "[ERROR] ",
    (
        "[ERROR] For more information about the errors and possible solutions, please "
        "read the following articles:"
    ),
    "[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/PluginResolutionException",
)


MAVEN_OFFLINE_TRACE = (
    "[INFO] Error stacktraces are turned on.",
    "[INFO] Scanning for projects...",
    "[INFO] ",
    "[INFO] ----------------------------< smoke:smoke >-----------------------------",
    "[INFO] Building smoke 1",
    "[INFO]   from pom.xml",
    "[INFO] --------------------------------[ jar ]---------------------------------",
    (
        "[WARNING] The POM for org.apache.maven.plugins:maven-resources-plugin:jar:3.4.0 "
        "is missing, no dependency information available"
    ),
    "[INFO] ------------------------------------------------------------------------",
    "[INFO] BUILD FAILURE",
    "[INFO] ------------------------------------------------------------------------",
    "[INFO] Total time:  0.052 s",
    "[INFO] Finished at: 2026-09-19T02:41:40Z",
    "[INFO] ------------------------------------------------------------------------",
    (
        "[ERROR] Plugin org.apache.maven.plugins:maven-resources-plugin:3.4.0 or one of "
        "its dependencies could not be resolved:"
    ),
    (
        "[ERROR] \tCannot access central (https://repo.maven.apache.org/maven2) in "
        "offline mode and the artifact org.apache.maven.plugins:maven-resources-plugin:ja"
        "r:3.4.0 has not been downloaded from it before."
    ),
    "[ERROR] -> [Help 1]",
    (
        "org.apache.maven.plugin.PluginResolutionException: Plugin "
        "org.apache.maven.plugins:maven-resources-plugin:3.4.0 or one of its "
        "dependencies could not be resolved:"
    ),
    (
        "\tCannot access central (https://repo.maven.apache.org/maven2) in offline mode "
        "and the artifact org.apache.maven.plugins:maven-resources-plugin:jar:3.4.0 has "
        "not been downloaded from it before."
    ),
    "",
    (
        "    at org.apache.maven.plugin.internal.DefaultPluginDependenciesResolver.resolv"
        "e (DefaultPluginDependenciesResolver.java:144)"
    ),
    (
        "    at org.apache.maven.plugin.internal.DefaultMavenPluginManager.lambda$getPlug"
        "inDescriptor$0 (DefaultMavenPluginManager.java:188)"
    ),
    (
        "    at org.apache.maven.plugin.DefaultPluginDescriptorCache.get "
        "(DefaultPluginDescriptorCache.java:77)"
    ),
    (
        "    at org.apache.maven.plugin.internal.DefaultMavenPluginManager.getPluginDescr"
        "iptor (DefaultMavenPluginManager.java:186)"
    ),
    (
        "    at org.apache.maven.plugin.internal.DefaultMavenPluginManager.getMojoDescrip"
        "tor (DefaultMavenPluginManager.java:276)"
    ),
    (
        "    at org.apache.maven.plugin.DefaultBuildPluginManager.getMojoDescriptor "
        "(DefaultBuildPluginManager.java:214)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.DefaultLifecycleExecutionPlanCalculat"
        "or.setupMojoExecution (DefaultLifecycleExecutionPlanCalculator.java:155)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.DefaultLifecycleExecutionPlanCalculat"
        "or.setupMojoExecutions (DefaultLifecycleExecutionPlanCalculator.java:143)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.DefaultLifecycleExecutionPlanCalculat"
        "or.calculateExecutionPlan (DefaultLifecycleExecutionPlanCalculator.java:122)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.DefaultLifecycleExecutionPlanCalculat"
        "or.calculateExecutionPlan (DefaultLifecycleExecutionPlanCalculator.java:135)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.builder.BuilderCommon.resolveBuildPla"
        "n (BuilderCommon.java:93)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.LifecycleModuleBuilder.buildProject "
        "(LifecycleModuleBuilder.java:100)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.LifecycleModuleBuilder.buildProject "
        "(LifecycleModuleBuilder.java:73)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.builder.singlethreaded.SingleThreaded"
        "Builder.build (SingleThreadedBuilder.java:53)"
    ),
    (
        "    at org.apache.maven.lifecycle.internal.LifecycleStarter.execute "
        "(LifecycleStarter.java:118)"
    ),
    "    at org.apache.maven.DefaultMaven.doExecute (DefaultMaven.java:261)",
    "    at org.apache.maven.DefaultMaven.doExecute (DefaultMaven.java:173)",
    "    at org.apache.maven.DefaultMaven.execute (DefaultMaven.java:101)",
    "    at org.apache.maven.cli.MavenCli.execute (MavenCli.java:919)",
    "    at org.apache.maven.cli.MavenCli.doMain (MavenCli.java:285)",
    "    at org.apache.maven.cli.MavenCli.main (MavenCli.java:207)",
    (
        "    at jdk.internal.reflect.DirectMethodHandleAccessor.invoke "
        "(DirectMethodHandleAccessor.java:104)"
    ),
    "    at java.lang.reflect.Method.invoke (Method.java:565)",
    "    at org.codehaus.plexus.classworlds.launcher.Launcher.launchEnhanced (Launcher.java:255)",
    "    at org.codehaus.plexus.classworlds.launcher.Launcher.launch (Launcher.java:201)",
    "    at org.codehaus.plexus.classworlds.launcher.Launcher.mainWithExitCode (Launcher.java:362)",
    "    at org.codehaus.plexus.classworlds.launcher.Launcher.main (Launcher.java:314)",
    "[ERROR] ",
    "[ERROR] Re-run Maven using the -X switch to enable full debug logging.",
    "[ERROR] ",
    (
        "[ERROR] For more information about the errors and possible solutions, please "
        "read the following articles:"
    ),
    "[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/PluginResolutionException",
)


JVM_TRACE = (
    "adding 1 and 2: 3",
    (
        'Exception in thread "main" java.lang.IllegalStateException: refusing to add a '
        "number to itself"
    ),
    "\tat smoke.Adder.add(Adder.java:6)",
    "\tat smoke.Adder.main(Adder.java:13)",
    "Caused by: java.lang.ArithmeticException: equal operands",
    "\t... 2 more",
)


JAVAC_ERROR = (
    "smoke/Broken.java:5: error: cannot find symbol",
    "        return a + c;",
    "                   ^",
    "  symbol:   variable c",
    "  location: class Broken",
    "1 error",
)


GRADLE_FAILURE = (
    "> Task :jvm:kotlin:checkKotlinGradlePluginConfigurationErrors SKIPPED",
    "> Task :jvm:kotlin:compileKotlin UP-TO-DATE",
    "> Task :jvm:kotlin:compileJava NO-SOURCE",
    "> Task :jvm:kotlin:processResources NO-SOURCE",
    "> Task :jvm:kotlin:classes UP-TO-DATE",
    "> Task :jvm:kotlin:jar UP-TO-DATE",
    "> Task :jvm:kotlin:testClasses UP-TO-DATE",
    "",
    "> Task :jvm:kotlin:test FAILED",
    "",
    "KitchenInventoryManagementTest > is implemented, and prints() STANDARD_OUT",
    "    --- output of Kitchen Inventory Management in Kotlin ---",
    "    --- end of output ---",
    "",
    "KitchenInventoryManagementTest > is implemented, and prints() FAILED",
    "    org.opentest4j.AssertionFailedError: KitchenInventoryManagement printed nothing.",
    "        at app//org.junit.jupiter.api.AssertionUtils.fail(AssertionUtils.java:38)",
    "        at app//org.junit.jupiter.api.Assertions.fail(Assertions.java:138)",
    "        at app//kotlin.test.junit5.JUnit5Asserter.fail(JUnitSupport.kt:56)",
    "        at app//kotlin.test.Asserter.assertTrue(Assertions.kt:767)",
    "        at app//kotlin.test.AssertionsKt.assertTrue(Unknown Source)",
    (
        "        at app//concepts.gs.unit02.KitchenInventoryManagementTest.isImplemented("
        "KitchenInventoryManagementTest.kt:57)"
    ),
    "",
    "9 tests completed, 3 failed",
    "",
    "FAILURE: Build failed with an exception.",
    "",
    "* What went wrong:",
    "Execution failed for task ':jvm:kotlin:test'.",
    (
        "> There were failing tests. See the report at: "
        "file:///path/to/project/repo/jvm/kotlin/build/reports/tests/test/index.html"
    ),
    "",
    "* Try:",
    "> Run with --scan to get full insights from a Build Scan (powered by Develocity).",
    "",
    "BUILD FAILED in 2s",
    "4 actionable tasks: 2 executed, 2 up-to-date",
)

#: Every transcript, by name, for the properties that hold of all of them.
ALL = {
    "MAVEN_PASS": MAVEN_PASS,
    "MAVEN_OFFLINE": MAVEN_OFFLINE,
    "MAVEN_OFFLINE_TRACE": MAVEN_OFFLINE_TRACE,
    "JVM_TRACE": JVM_TRACE,
    "JAVAC_ERROR": JAVAC_ERROR,
    "GRADLE_FAILURE": GRADLE_FAILURE,
}
