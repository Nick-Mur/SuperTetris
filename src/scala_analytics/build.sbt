name := "tetris-towers-analytics"
organization := "com.tetristowers"
version := "0.1.0-SNAPSHOT"

scalaVersion := "2.13.10"

libraryDependencies ++= Seq(
  // Akka
  "com.typesafe.akka" %% "akka-actor-typed" % "2.7.0",
  "com.typesafe.akka" %% "akka-stream" % "2.7.0",
  "com.typesafe.akka" %% "akka-http" % "10.5.0",
  
  // JSON
  "io.circe" %% "circe-core" % "0.14.5",
  "io.circe" %% "circe-generic" % "0.14.5",
  "io.circe" %% "circe-parser" % "0.14.5",
  "de.heikoseeberger" %% "akka-http-circe" % "1.39.2",
  
  // Database
  "org.tpolecat" %% "doobie-core" % "1.0.0-RC2",
  "org.tpolecat" %% "doobie-postgres" % "1.0.0-RC2",
  "org.tpolecat" %% "doobie-hikari" % "1.0.0-RC2",
  "org.flywaydb" % "flyway-core" % "9.16.0",
  
  // Logging
  "ch.qos.logback" % "logback-classic" % "1.4.7",
  "com.typesafe.scala-logging" %% "scala-logging" % "3.9.5",
  
  // Config
  "com.typesafe" % "config" % "1.4.2",
  "com.github.pureconfig" %% "pureconfig" % "0.17.4",
  
  // Metrics
  "io.prometheus" % "simpleclient" % "0.16.0",
  "io.prometheus" % "simpleclient_hotspot" % "0.16.0",
  "io.prometheus" % "simpleclient_httpserver" % "0.16.0",
  
  // Data processing
  "org.apache.spark" %% "spark-core" % "3.4.0" % "provided",
  "org.apache.spark" %% "spark-sql" % "3.4.0" % "provided",
  "org.apache.spark" %% "spark-streaming" % "3.4.0" % "provided",
  "org.apache.spark" %% "spark-mllib" % "3.4.0" % "provided",
  
  // JNI/FFI
  "net.java.dev.jna" % "jna" % "5.13.0",
  "net.java.dev.jna" % "jna-platform" % "5.13.0",
  
  // Testing
  "org.scalatest" %% "scalatest" % "3.2.15" % Test,
  "org.scalamock" %% "scalamock" % "5.2.0" % Test,
  "com.typesafe.akka" %% "akka-actor-testkit-typed" % "2.7.0" % Test,
  "com.typesafe.akka" %% "akka-stream-testkit" % "2.7.0" % Test,
  "com.typesafe.akka" %% "akka-http-testkit" % "10.5.0" % Test
)

// Assembly settings for creating a fat JAR
assembly / assemblyJarName := s"${name}-assembly-${version}.jar"
assembly / assemblyMergeStrategy := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case "reference.conf" => MergeStrategy.concat
  case x => MergeStrategy.first
}

// Scala compiler options
scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Xlint",
  "-Ywarn-dead-code",
  "-Ywarn-unused:imports",
  "-Ywarn-value-discard"
)

// Java compiler options
javacOptions ++= Seq(
  "-source", "11",
  "-target", "11"
)

// Enable forking in run
fork := true

// JVM options
javaOptions ++= Seq(
  "-Xms512m",
  "-Xmx2g",
  "-XX:+UseG1GC",
  "-XX:MaxGCPauseMillis=200"
)

// Publish settings
publishMavenStyle := true
publishTo := {
  val nexus = "https://maven.example.com/"
  if (isSnapshot.value)
    Some("snapshots" at nexus + "content/repositories/snapshots")
  else
    Some("releases" at nexus + "content/repositories/releases")
}

// Additional repositories
resolvers ++= Seq(
  "Sonatype OSS Snapshots" at "https://oss.sonatype.org/content/repositories/snapshots",
  "Sonatype OSS Releases" at "https://oss.sonatype.org/content/repositories/releases"
)
