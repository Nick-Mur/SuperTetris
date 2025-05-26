package com.tetristowers.analytics

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.ml.feature.VectorAssembler
import org.apache.spark.ml.clustering.KMeans
import org.apache.spark.ml.evaluation.ClusteringEvaluator
import org.apache.spark.ml.regression.LinearRegression
import org.apache.spark.ml.classification.RandomForestClassifier
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator

import java.time.{Instant, LocalDateTime, ZoneId}
import java.time.format.DateTimeFormatter
import java.io.{File, PrintWriter}
import java.nio.file.{Files, Paths}

import scala.collection.mutable.ArrayBuffer
import scala.util.{Try, Success, Failure}
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.duration._

import play.api.libs.json._

/**
 * Main Analytics System for Tetris Towers
 *
 * This system collects, processes, and analyzes game data to provide insights
 * about player behavior, game balance, and system performance.
 */
class AnalyticsSystem(config: AnalyticsConfig) {
  
  // Initialize Spark session
  private val spark = SparkSession.builder()
    .appName("TetrisTowersAnalytics")
    .master(config.sparkMaster)
    .config("spark.sql.warehouse.dir", config.warehouseDir)
    .getOrCreate()
  
  import spark.implicits._
  
  // Initialize data collectors
  private val gameplayCollector = new GameplayDataCollector(config)
  private val playerCollector = new PlayerDataCollector(config)
  private val systemCollector = new SystemPerformanceCollector(config)
  
  // Initialize analyzers
  private val gameplayAnalyzer = new GameplayAnalyzer(spark, config)
  private val playerAnalyzer = new PlayerAnalyzer(spark, config)
  private val balanceAnalyzer = new GameBalanceAnalyzer(spark, config)
  private val performanceAnalyzer = new PerformanceAnalyzer(spark, config)
  
  // Initialize reporters
  private val dashboardReporter = new DashboardReporter(config)
  private val alertSystem = new AlertSystem(config)
  
  /**
   * Start the analytics system
   */
  def start(): Unit = {
    println(s"Starting Tetris Towers Analytics System with config: $config")
    
    // Start data collectors
    gameplayCollector.start()
    playerCollector.start()
    systemCollector.start()
    
    // Start reporters
    dashboardReporter.start()
    alertSystem.start()
    
    println("Analytics system started successfully")
  }
  
  /**
   * Stop the analytics system
   */
  def stop(): Unit = {
    println("Stopping Tetris Towers Analytics System")
    
    // Stop data collectors
    gameplayCollector.stop()
    playerCollector.stop()
    systemCollector.stop()
    
    // Stop reporters
    dashboardReporter.stop()
    alertSystem.stop()
    
    // Stop Spark session
    spark.stop()
    
    println("Analytics system stopped successfully")
  }
  
  /**
   * Record a game event
   *
   * @param event The game event to record
   */
  def recordGameEvent(event: GameEvent): Unit = {
    gameplayCollector.collectEvent(event)
  }
  
  /**
   * Record a player action
   *
   * @param action The player action to record
   */
  def recordPlayerAction(action: PlayerAction): Unit = {
    playerCollector.collectAction(action)
  }
  
  /**
   * Record system performance metrics
   *
   * @param metrics The system performance metrics to record
   */
  def recordPerformanceMetrics(metrics: PerformanceMetrics): Unit = {
    systemCollector.collectMetrics(metrics)
  }
  
  /**
   * Run analytics on collected data
   *
   * @return A Future containing the analytics results
   */
  def runAnalytics()(implicit ec: ExecutionContext): Future[AnalyticsResults] = {
    // Load data from collectors
    val gameplayDataFuture = Future { gameplayCollector.getData() }
    val playerDataFuture = Future { playerCollector.getData() }
    val systemDataFuture = Future { systemCollector.getData() }
    
    // Combine data and run analytics
    for {
      gameplayData <- gameplayDataFuture
      playerData <- playerDataFuture
      systemData <- systemDataFuture
      
      // Convert to DataFrames
      gameplayDF = spark.createDataFrame(gameplayData)
      playerDF = spark.createDataFrame(playerData)
      systemDF = spark.createDataFrame(systemData)
      
      // Run analyzers
      gameplayResults <- Future { gameplayAnalyzer.analyze(gameplayDF) }
      playerResults <- Future { playerAnalyzer.analyze(playerDF) }
      balanceResults <- Future { balanceAnalyzer.analyze(gameplayDF, playerDF) }
      performanceResults <- Future { performanceAnalyzer.analyze(systemDF) }
    } yield {
      // Combine results
      val results = AnalyticsResults(
        gameplayResults,
        playerResults,
        balanceResults,
        performanceResults,
        Instant.now()
      )
      
      // Generate reports
      dashboardReporter.generateReport(results)
      
      // Check for alerts
      alertSystem.checkAlerts(results)
      
      results
    }
  }
  
  /**
   * Generate a comprehensive analytics report
   *
   * @param outputPath Path to save the report
   * @return Success or Failure
   */
  def generateReport(outputPath: String): Try[String] = {
    Try {
      // Load the latest analytics results
      val results = runAnalytics()(ExecutionContext.global).await(5.minutes)
      
      // Generate report content
      val reportContent = ReportGenerator.generateHtmlReport(results)
      
      // Save report to file
      val reportFile = new File(outputPath)
      val writer = new PrintWriter(reportFile)
      writer.write(reportContent)
      writer.close()
      
      outputPath
    }
  }
  
  /**
   * Export analytics data to various formats
   *
   * @param dataType Type of data to export
   * @param format Export format (csv, json, parquet)
   * @param outputPath Path to save the exported data
   * @return Success or Failure
   */
  def exportData(dataType: String, format: String, outputPath: String): Try[String] = {
    Try {
      // Get the appropriate DataFrame based on data type
      val df = dataType match {
        case "gameplay" => spark.createDataFrame(gameplayCollector.getData())
        case "player" => spark.createDataFrame(playerCollector.getData())
        case "system" => spark.createDataFrame(systemCollector.getData())
        case _ => throw new IllegalArgumentException(s"Unknown data type: $dataType")
      }
      
      // Export data in the specified format
      format.toLowerCase match {
        case "csv" => df.write.option("header", "true").csv(outputPath)
        case "json" => df.write.json(outputPath)
        case "parquet" => df.write.parquet(outputPath)
        case _ => throw new IllegalArgumentException(s"Unsupported format: $format")
      }
      
      outputPath
    }
  }
}

/**
 * Configuration for the Analytics System
 *
 * @param dataStoragePath Path to store collected data
 * @param analysisInterval Interval between analysis runs (in seconds)
 * @param retentionPeriod How long to retain data (in days)
 * @param sparkMaster Spark master URL
 * @param warehouseDir Spark warehouse directory
 * @param enableRealTimeAnalytics Whether to enable real-time analytics
 * @param alertThresholds Thresholds for various alerts
 * @param dashboardConfig Configuration for the dashboard
 */
case class AnalyticsConfig(
  dataStoragePath: String,
  analysisInterval: Int,
  retentionPeriod: Int,
  sparkMaster: String,
  warehouseDir: String,
  enableRealTimeAnalytics: Boolean,
  alertThresholds: Map[String, Double],
  dashboardConfig: DashboardConfig
)

/**
 * Configuration for the dashboard
 *
 * @param port HTTP port for the dashboard
 * @param refreshInterval Refresh interval in seconds
 * @param enablePublicAccess Whether to allow public access
 */
case class DashboardConfig(
  port: Int,
  refreshInterval: Int,
  enablePublicAccess: Boolean
)

/**
 * Game event data
 *
 * @param eventId Unique identifier for the event
 * @param gameId Game session identifier
 * @param playerId Player identifier
 * @param eventType Type of event
 * @param eventData Event-specific data
 * @param timestamp Event timestamp
 */
case class GameEvent(
  eventId: String,
  gameId: String,
  playerId: String,
  eventType: String,
  eventData: JsValue,
  timestamp: Instant
)

/**
 * Player action data
 *
 * @param actionId Unique identifier for the action
 * @param gameId Game session identifier
 * @param playerId Player identifier
 * @param actionType Type of action
 * @param actionData Action-specific data
 * @param timestamp Action timestamp
 */
case class PlayerAction(
  actionId: String,
  gameId: String,
  playerId: String,
  actionType: String,
  actionData: JsValue,
  timestamp: Instant
)

/**
 * System performance metrics
 *
 * @param metricsId Unique identifier for the metrics
 * @param gameId Game session identifier (optional)
 * @param componentType Component being measured
 * @param metrics Performance metrics data
 * @param timestamp Metrics timestamp
 */
case class PerformanceMetrics(
  metricsId: String,
  gameId: Option[String],
  componentType: String,
  metrics: JsValue,
  timestamp: Instant
)

/**
 * Combined analytics results
 *
 * @param gameplayResults Results from gameplay analysis
 * @param playerResults Results from player analysis
 * @param balanceResults Results from game balance analysis
 * @param performanceResults Results from performance analysis
 * @param timestamp Timestamp when analysis was performed
 */
case class AnalyticsResults(
  gameplayResults: GameplayAnalysisResults,
  playerResults: PlayerAnalysisResults,
  balanceResults: GameBalanceAnalysisResults,
  performanceResults: PerformanceAnalysisResults,
  timestamp: Instant
)

/**
 * Results from gameplay analysis
 *
 * @param averageGameDuration Average game duration in seconds
 * @param averageScore Average player score
 * @param averageLinesCleared Average number of lines cleared per game
 * @param blockUsageDistribution Distribution of block type usage
 * @param spellUsageDistribution Distribution of spell usage
 * @param winRateByGameMode Win rate by game mode
 * @param difficultyDistribution Distribution of game difficulty
 */
case class GameplayAnalysisResults(
  averageGameDuration: Double,
  averageScore: Double,
  averageLinesCleared: Double,
  blockUsageDistribution: Map[String, Double],
  spellUsageDistribution: Map[String, Double],
  winRateByGameMode: Map[String, Double],
  difficultyDistribution: Map[String, Double]
)

/**
 * Results from player analysis
 *
 * @param playerSegments Player segments identified by clustering
 * @param playerSkillDistribution Distribution of player skill levels
 * @param playerRetention Player retention rates
 * @param playerProgressionCurve Player progression curve
 * @param playerBehaviorPatterns Common player behavior patterns
 * @param playerFeedbackSentiment Sentiment analysis of player feedback
 */
case class PlayerAnalysisResults(
  playerSegments: List[PlayerSegment],
  playerSkillDistribution: Map[String, Double],
  playerRetention: Map[String, Double],
  playerProgressionCurve: List[ProgressionPoint],
  playerBehaviorPatterns: List[BehaviorPattern],
  playerFeedbackSentiment: Map[String, Double]
)

/**
 * Player segment identified by clustering
 *
 * @param segmentId Unique identifier for the segment
 * @param segmentName Descriptive name for the segment
 * @param playerCount Number of players in the segment
 * @param characteristics Key characteristics of the segment
 */
case class PlayerSegment(
  segmentId: String,
  segmentName: String,
  playerCount: Int,
  characteristics: Map[String, Double]
)

/**
 * Point on the player progression curve
 *
 * @param level Player level
 * @param averageScore Average score at this level
 * @param averagePlayTime Average play time to reach this level
 * @param playerCount Number of players who reached this level
 */
case class ProgressionPoint(
  level: Int,
  averageScore: Double,
  averagePlayTime: Double,
  playerCount: Int
)

/**
 * Common player behavior pattern
 *
 * @param patternId Unique identifier for the pattern
 * @param patternName Descriptive name for the pattern
 * @param frequency Frequency of the pattern
 * @param actions Sequence of actions in the pattern
 */
case class BehaviorPattern(
  patternId: String,
  patternName: String,
  frequency: Double,
  actions: List[String]
)

/**
 * Results from game balance analysis
 *
 * @param blockBalanceMetrics Balance metrics for block types
 * @param spellBalanceMetrics Balance metrics for spells
 * @param difficultyBalanceMetrics Balance metrics for difficulty levels
 * @param gameModesBalanceMetrics Balance metrics for game modes
 * @param balanceRecommendations Recommendations for improving game balance
 */
case class GameBalanceAnalysisResults(
  blockBalanceMetrics: Map[String, Double],
  spellBalanceMetrics: Map[String, Double],
  difficultyBalanceMetrics: Map[String, Double],
  gameModesBalanceMetrics: Map[String, Double],
  balanceRecommendations: List[BalanceRecommendation]
)

/**
 * Recommendation for improving game balance
 *
 * @param targetElement Element to adjust
 * @param currentValue Current value
 * @param recommendedValue Recommended value
 * @param impact Expected impact of the change
 * @param confidence Confidence in the recommendation
 */
case class BalanceRecommendation(
  targetElement: String,
  currentValue: Double,
  recommendedValue: Double,
  impact: String,
  confidence: Double
)

/**
 * Results from performance analysis
 *
 * @param averageFPS Average frames per second
 * @param averageMemoryUsage Average memory usage in MB
 * @param averageCPUUsage Average CPU usage percentage
 * @param averageNetworkLatency Average network latency in ms
 * @param componentPerformance Performance metrics by component
 * @param performanceBottlenecks Identified performance bottlenecks
 * @param optimizationRecommendations Recommendations for performance optimization
 */
case class PerformanceAnalysisResults(
  averageFPS: Double,
  averageMemoryUsage: Double,
  averageCPUUsage: Double,
  averageNetworkLatency: Double,
  componentPerformance: Map[String, Double],
  performanceBottlenecks: List[PerformanceBottleneck],
  optimizationRecommendations: List[OptimizationRecommendation]
)

/**
 * Identified performance bottleneck
 *
 * @param componentId Component with the bottleneck
 * @param metricName Metric showing the bottleneck
 * @param severity Severity of the bottleneck
 * @param description Description of the bottleneck
 */
case class PerformanceBottleneck(
  componentId: String,
  metricName: String,
  severity: Double,
  description: String
)

/**
 * Recommendation for performance optimization
 *
 * @param targetComponent Component to optimize
 * @param recommendation Optimization recommendation
 * @param expectedImprovement Expected improvement percentage
 * @param implementationComplexity Complexity of implementing the recommendation
 */
case class OptimizationRecommendation(
  targetComponent: String,
  recommendation: String,
  expectedImprovement: Double,
  implementationComplexity: String
)

/**
 * Collector for gameplay data
 *
 * @param config Analytics configuration
 */
class GameplayDataCollector(config: AnalyticsConfig) {
  private val events = new ArrayBuffer[GameEvent]()
  private var running = false
  
  def start(): Unit = {
    running = true
    println("Gameplay data collector started")
  }
  
  def stop(): Unit = {
    running = false
    println("Gameplay data collector stopped")
  }
  
  def collectEvent(event: GameEvent): Unit = {
    if (running) {
      events.synchronized {
        events += event
        
        // Periodically save data to disk
        if (events.size % 1000 == 0) {
          saveData()
        }
      }
    }
  }
  
  def getData(): List[GameEvent] = {
    events.synchronized {
      events.toList
    }
  }
  
  private def saveData(): Unit = {
    val timestamp = DateTimeFormatter
      .ofPattern("yyyyMMdd_HHmmss")
      .format(LocalDateTime.now())
    
    val filePath = s"${config.dataStoragePath}/gameplay_data_$timestamp.json"
    
    // Ensure directory exists
    Files.createDirectories(Paths.get(config.dataStoragePath))
    
    // Convert events to JSON and save
    val json = Json.toJson(events.map { event =>
      Json.obj(
        "eventId" -> event.eventId,
        "gameId" -> event.gameId,
        "playerId" -> event.playerId,
        "eventType" -> event.eventType,
        "eventData" -> event.eventData,
        "timestamp" -> event.timestamp.toString
      )
    })
    
    val writer = new PrintWriter(filePath)
    writer.write(Json.prettyPrint(json))
    writer.close()
    
    println(s"Saved ${events.size} gameplay events to $filePath")
  }
}

/**
 * Collector for player action data
 *
 * @param config Analytics configuration
 */
class PlayerDataCollector(config: AnalyticsConfig) {
  private val actions = new ArrayBuffer[PlayerAction]()
  private var running = false
  
  def start(): Unit = {
    running = true
    println("Player data collector started")
  }
  
  def stop(): Unit = {
    running = false
    println("Player data collector stopped")
  }
  
  def collectAction(action: PlayerAction): Unit = {
    if (running) {
      actions.synchronized {
        actions += action
        
        // Periodically save data to disk
        if (actions.size % 1000 == 0) {
          saveData()
        }
      }
    }
  }
  
  def getData(): List[PlayerAction] = {
    actions.synchronized {
      actions.toList
    }
  }
  
  private def saveData(): Unit = {
    val timestamp = DateTimeFormatter
      .ofPattern("yyyyMMdd_HHmmss")
      .format(LocalDateTime.now())
    
    val filePath = s"${config.dataStoragePath}/player_data_$timestamp.json"
    
    // Ensure directory exists
    Files.createDirectories(Paths.get(config.dataStoragePath))
    
    // Convert actions to JSON and save
    val json = Json.toJson(actions.map { action =>
      Json.obj(
        "actionId" -> action.actionId,
        "gameId" -> action.gameId,
        "playerId" -> action.playerId,
        "actionType" -> action.actionType,
        "actionData" -> action.actionData,
        "timestamp" -> action.timestamp.toString
      )
    })
    
    val writer = new PrintWriter(filePath)
    writer.write(Json.prettyPrint(json))
    writer.close()
    
    println(s"Saved ${actions.size} player actions to $filePath")
  }
}

/**
 * Collector for system performance metrics
 *
 * @param config Analytics configuration
 */
class SystemPerformanceCollector(config: AnalyticsConfig) {
  private val metrics = new ArrayBuffer[PerformanceMetrics]()
  private var running = false
  
  def start(): Unit = {
    running = true
    println("System performance collector started")
  }
  
  def stop(): Unit = {
    running = false
    println("System performance collector stopped")
  }
  
  def collectMetrics(metric: PerformanceMetrics): Unit = {
    if (running) {
      metrics.synchronized {
        metrics += metric
        
        // Periodically save data to disk
        if (metrics.size % 1000 == 0) {
          saveData()
        }
      }
    }
  }
  
  def getData(): List[PerformanceMetrics] = {
    metrics.synchronized {
      metrics.toList
    }
  }
  
  private def saveData(): Unit = {
    val timestamp = DateTimeFormatter
      .ofPattern("yyyyMMdd_HHmmss")
      .format(LocalDateTime.now())
    
    val filePath = s"${config.dataStoragePath}/performance_data_$timestamp.json"
    
    // Ensure directory exists
    Files.createDirectories(Paths.get(config.dataStoragePath))
    
    // Convert metrics to JSON and save
    val json = Json.toJson(metrics.map { metric =>
      Json.obj(
        "metricsId" -> metric.metricsId,
        "gameId" -> metric.gameId,
        "componentType" -> metric.componentType,
        "metrics" -> metric.metrics,
        "timestamp" -> metric.timestamp.toString
      )
    })
    
    val writer = new PrintWriter(filePath)
    writer.write(Json.prettyPrint(json))
    writer.close()
    
    println(s"Saved ${metrics.size} performance metrics to $filePath")
  }
}

/**
 * Analyzer for gameplay data
 *
 * @param spark Spark session
 * @param config Analytics configuration
 */
class GameplayAnalyzer(spark: SparkSession, config: AnalyticsConfig) {
  import spark.implicits._
  
  /**
   * Analyze gameplay data
   *
   * @param gameplayDF DataFrame containing gameplay data
   * @return Results of the analysis
   */
  def analyze(gameplayDF: DataFrame): GameplayAnalysisResults = {
    println("Analyzing gameplay data...")
    
    // Register the DataFrame as a temporary view
    gameplayDF.createOrReplaceTempView("gameplay_events")
    
    // Calculate average game duration
    val durationDF = spark.sql("""
      SELECT 
        gameId,
        (MAX(CAST(timestamp AS LONG)) - MIN(CAST(timestamp AS LONG))) / 1000.0 AS duration
      FROM gameplay_events
      GROUP BY gameId
    """)
    
    val averageGameDuration = durationDF.agg(avg("duration")).first().getDouble(0)
    
    // Calculate average score
    val scoreDF = spark.sql("""
      SELECT 
        gameId,
        playerId,
        CAST(get_json_object(eventData, '$.score') AS DOUBLE) AS score
      FROM gameplay_events
      WHERE eventType = 'GAME_END'
    """)
    
    val averageScore = scoreDF.agg(avg("score")).first().getDouble(0)
    
    // Calculate average lines cleared
    val linesDF = spark.sql("""
      SELECT 
        gameId,
        playerId,
        CAST(get_json_object(eventData, '$.linesCleared') AS DOUBLE) AS linesCleared
      FROM gameplay_events
      WHERE eventType = 'GAME_END'
    """)
    
    val averageLinesCleared = linesDF.agg(avg("linesCleared")).first().getDouble(0)
    
    // Calculate block usage distribution
    val blockUsageDF = spark.sql("""
      SELECT 
        get_json_object(eventData, '$.blockType') AS blockType,
        COUNT(*) AS count
      FROM gameplay_events
      WHERE eventType = 'BLOCK_PLACED'
      GROUP BY get_json_object(eventData, '$.blockType')
    """)
    
    val totalBlocks = blockUsageDF.agg(sum("count")).first().getLong(0)
    
    val blockUsageDistribution = blockUsageDF.collect().map { row =>
      (row.getString(0), row.getLong(1).toDouble / totalBlocks)
    }.toMap
    
    // Calculate spell usage distribution
    val spellUsageDF = spark.sql("""
      SELECT 
        get_json_object(eventData, '$.spellType') AS spellType,
        COUNT(*) AS count
      FROM gameplay_events
      WHERE eventType = 'SPELL_CAST'
      GROUP BY get_json_object(eventData, '$.spellType')
    """)
    
    val totalSpells = spellUsageDF.agg(sum("count")).first().getLong(0)
    
    val spellUsageDistribution = if (totalSpells > 0) {
      spellUsageDF.collect().map { row =>
        (row.getString(0), row.getLong(1).toDouble / totalSpells)
      }.toMap
    } else {
      Map.empty[String, Double]
    }
    
    // Calculate win rate by game mode
    val winRateDF = spark.sql("""
      SELECT 
        get_json_object(eventData, '$.gameMode') AS gameMode,
        SUM(CASE WHEN get_json_object(eventData, '$.result') = 'WIN' THEN 1 ELSE 0 END) AS wins,
        COUNT(*) AS total
      FROM gameplay_events
      WHERE eventType = 'GAME_END'
      GROUP BY get_json_object(eventData, '$.gameMode')
    """)
    
    val winRateByGameMode = winRateDF.collect().map { row =>
      (row.getString(0), row.getLong(1).toDouble / row.getLong(2))
    }.toMap
    
    // Calculate difficulty distribution
    val difficultyDF = spark.sql("""
      SELECT 
        get_json_object(eventData, '$.difficulty') AS difficulty,
        COUNT(*) AS count
      FROM gameplay_events
      WHERE eventType = 'GAME_START'
      GROUP BY get_json_object(eventData, '$.difficulty')
    """)
    
    val totalGames = difficultyDF.agg(sum("count")).first().getLong(0)
    
    val difficultyDistribution = difficultyDF.collect().map { row =>
      (row.getString(0), row.getLong(1).toDouble / totalGames)
    }.toMap
    
    // Return the results
    GameplayAnalysisResults(
      averageGameDuration = averageGameDuration,
      averageScore = averageScore,
      averageLinesCleared = averageLinesCleared,
      blockUsageDistribution = blockUsageDistribution,
      spellUsageDistribution = spellUsageDistribution,
      winRateByGameMode = winRateByGameMode,
      difficultyDistribution = difficultyDistribution
    )
  }
}

/**
 * Analyzer for player data
 *
 * @param spark Spark session
 * @param config Analytics configuration
 */
class PlayerAnalyzer(spark: SparkSession, config: AnalyticsConfig) {
  import spark.implicits._
  
  /**
   * Analyze player data
   *
   * @param playerDF DataFrame containing player data
   * @return Results of the analysis
   */
  def analyze(playerDF: DataFrame): PlayerAnalysisResults = {
    println("Analyzing player data...")
    
    // Register the DataFrame as a temporary view
    playerDF.createOrReplaceTempView("player_actions")
    
    // Extract player features for clustering
    val playerFeaturesDF = spark.sql("""
      SELECT 
        playerId,
        COUNT(*) AS actionCount,
        COUNT(DISTINCT gameId) AS gameCount,
        AVG(CASE WHEN actionType = 'MOVE_LEFT' OR actionType = 'MOVE_RIGHT' THEN 1 ELSE 0 END) AS movementRatio,
        AVG(CASE WHEN actionType = 'ROTATE_CW' OR actionType = 'ROTATE_CCW' THEN 1 ELSE 0 END) AS rotationRatio,
        AVG(CASE WHEN actionType = 'HARD_DROP' THEN 1 ELSE 0 END) AS hardDropRatio,
        AVG(CASE WHEN actionType = 'CAST_SPELL' THEN 1 ELSE 0 END) AS spellCastRatio
      FROM player_actions
      GROUP BY playerId
    """)
    
    // Prepare data for clustering
    val assembler = new VectorAssembler()
      .setInputCols(Array("actionCount", "gameCount", "movementRatio", "rotationRatio", "hardDropRatio", "spellCastRatio"))
      .setOutputCol("features")
    
    val featuresDF = assembler.transform(playerFeaturesDF)
    
    // Perform k-means clustering
    val kmeans = new KMeans()
      .setK(4)  // Number of clusters
      .setSeed(42)
      .setFeaturesCol("features")
      .setPredictionCol("segment")
    
    val model = kmeans.fit(featuresDF)
    val predictions = model.transform(featuresDF)
    
    // Evaluate clustering
    val evaluator = new ClusteringEvaluator()
    val silhouette = evaluator.evaluate(predictions)
    println(s"Silhouette with squared euclidean distance: $silhouette")
    
    // Extract cluster centers
    val centers = model.clusterCenters
    
    // Create player segments
    val playerSegments = (0 until 4).map { i =>
      val center = centers(i)
      val segmentName = i match {
        case 0 => "Casual Players"
        case 1 => "Regular Players"
        case 2 => "Competitive Players"
        case 3 => "Expert Players"
      }
      
      val playerCount = predictions.filter($"segment" === i).count().toInt
      
      val characteristics = Map(
        "actionCount" -> center(0),
        "gameCount" -> center(1),
        "movementRatio" -> center(2),
        "rotationRatio" -> center(3),
        "hardDropRatio" -> center(4),
        "spellCastRatio" -> center(5)
      )
      
      PlayerSegment(
        segmentId = s"segment_$i",
        segmentName = segmentName,
        playerCount = playerCount,
        characteristics = characteristics
      )
    }.toList
    
    // Calculate player skill distribution
    val skillDF = spark.sql("""
      SELECT 
        CASE 
          WHEN get_json_object(actionData, '$.score') < 1000 THEN 'Beginner'
          WHEN get_json_object(actionData, '$.score') < 5000 THEN 'Intermediate'
          WHEN get_json_object(actionData, '$.score') < 10000 THEN 'Advanced'
          ELSE 'Expert'
        END AS skillLevel,
        COUNT(DISTINCT playerId) AS playerCount
      FROM player_actions
      WHERE actionType = 'GAME_END'
      GROUP BY 
        CASE 
          WHEN get_json_object(actionData, '$.score') < 1000 THEN 'Beginner'
          WHEN get_json_object(actionData, '$.score') < 5000 THEN 'Intermediate'
          WHEN get_json_object(actionData, '$.score') < 10000 THEN 'Advanced'
          ELSE 'Expert'
        END
    """)
    
    val totalPlayers = skillDF.agg(sum("playerCount")).first().getLong(0)
    
    val playerSkillDistribution = skillDF.collect().map { row =>
      (row.getString(0), row.getLong(1).toDouble / totalPlayers)
    }.toMap
    
    // Calculate player retention
    val retentionDF = spark.sql("""
      SELECT 
        daysActive,
        COUNT(DISTINCT playerId) AS playerCount
      FROM (
        SELECT 
          playerId,
          COUNT(DISTINCT DATE(timestamp)) AS daysActive
        FROM player_actions
        GROUP BY playerId
      )
      GROUP BY daysActive
      ORDER BY daysActive
    """)
    
    val playerRetention = retentionDF.collect().map { row =>
      (s"${row.getLong(0)} days", row.getLong(1).toDouble / totalPlayers)
    }.toMap
    
    // Calculate player progression curve
    val progressionDF = spark.sql("""
      SELECT 
        CAST(get_json_object(actionData, '$.level') AS INT) AS level,
        AVG(CAST(get_json_object(actionData, '$.score') AS DOUBLE)) AS averageScore,
        AVG(CAST(get_json_object(actionData, '$.playTime') AS DOUBLE)) AS averagePlayTime,
        COUNT(DISTINCT playerId) AS playerCount
      FROM player_actions
      WHERE actionType = 'LEVEL_UP'
      GROUP BY CAST(get_json_object(actionData, '$.level') AS INT)
      ORDER BY level
    """)
    
    val playerProgressionCurve = progressionDF.collect().map { row =>
      ProgressionPoint(
        level = row.getInt(0),
        averageScore = row.getDouble(1),
        averagePlayTime = row.getDouble(2),
        playerCount = row.getLong(3).toInt
      )
    }.toList
    
    // Identify common behavior patterns
    val behaviorPatternsDF = spark.sql("""
      SELECT 
        CONCAT(a1.actionType, ' -> ', a2.actionType, ' -> ', a3.actionType) AS pattern,
        COUNT(*) AS frequency
      FROM 
        player_actions a1
        JOIN player_actions a2 ON a1.playerId = a2.playerId AND a1.gameId = a2.gameId AND a2.timestamp > a1.timestamp
        JOIN player_actions a3 ON a2.playerId = a3.playerId AND a2.gameId = a3.gameId AND a3.timestamp > a2.timestamp
      WHERE 
        a3.timestamp <= CAST(a1.timestamp AS LONG) + 5000  -- Within 5 seconds
      GROUP BY CONCAT(a1.actionType, ' -> ', a2.actionType, ' -> ', a3.actionType)
      ORDER BY frequency DESC
      LIMIT 10
    """)
    
    val totalPatterns = behaviorPatternsDF.agg(sum("frequency")).first().getLong(0)
    
    val playerBehaviorPatterns = behaviorPatternsDF.collect().zipWithIndex.map { case (row, i) =>
      val pattern = row.getString(0)
      val frequency = row.getLong(1).toDouble / totalPatterns
      
      BehaviorPattern(
        patternId = s"pattern_$i",
        patternName = s"Pattern ${i + 1}: $pattern",
        frequency = frequency,
        actions = pattern.split(" -> ").toList
      )
    }.toList
    
    // Simulate sentiment analysis of player feedback
    // In a real implementation, this would use actual feedback data and NLP
    val playerFeedbackSentiment = Map(
      "Gameplay" -> 0.85,
      "Graphics" -> 0.78,
      "Difficulty" -> 0.65,
      "Spells" -> 0.92,
      "Controls" -> 0.73
    )
    
    // Return the results
    PlayerAnalysisResults(
      playerSegments = playerSegments,
      playerSkillDistribution = playerSkillDistribution,
      playerRetention = playerRetention,
      playerProgressionCurve = playerProgressionCurve,
      playerBehaviorPatterns = playerBehaviorPatterns,
      playerFeedbackSentiment = playerFeedbackSentiment
    )
  }
}

/**
 * Analyzer for game balance
 *
 * @param spark Spark session
 * @param config Analytics configuration
 */
class GameBalanceAnalyzer(spark: SparkSession, config: AnalyticsConfig) {
  import spark.implicits._
  
  /**
   * Analyze game balance
   *
   * @param gameplayDF DataFrame containing gameplay data
   * @param playerDF DataFrame containing player data
   * @return Results of the analysis
   */
  def analyze(gameplayDF: DataFrame, playerDF: DataFrame): GameBalanceAnalysisResults = {
    println("Analyzing game balance...")
    
    // Register the DataFrames as temporary views
    gameplayDF.createOrReplaceTempView("gameplay_events")
    playerDF.createOrReplaceTempView("player_actions")
    
    // Analyze block balance
    val blockBalanceDF = spark.sql("""
      SELECT 
        get_json_object(eventData, '$.blockType') AS blockType,
        AVG(CAST(get_json_object(eventData, '$.successRate') AS DOUBLE)) AS placementSuccessRate,
        AVG(CAST(get_json_object(eventData, '$.clearRate') AS DOUBLE)) AS lineClearRate
      FROM gameplay_events
      WHERE eventType = 'BLOCK_STATS'
      GROUP BY get_json_object(eventData, '$.blockType')
    """)
    
    val blockBalanceMetrics = blockBalanceDF.collect().flatMap { row =>
      val blockType = row.getString(0)
      val successRate = row.getDouble(1)
      val clearRate = row.getDouble(2)
      
      // Calculate balance score (higher is more balanced)
      val balanceScore = (successRate + clearRate) / 2
      
      if (blockType != null) {
        Some((blockType, balanceScore))
      } else {
        None
      }
    }.toMap
    
    // Analyze spell balance
    val spellBalanceDF = spark.sql("""
      SELECT 
        get_json_object(eventData, '$.spellType') AS spellType,
        AVG(CAST(get_json_object(eventData, '$.effectivenessScore') AS DOUBLE)) AS effectiveness,
        AVG(CAST(get_json_object(eventData, '$.usageRate') AS DOUBLE)) AS usageRate
      FROM gameplay_events
      WHERE eventType = 'SPELL_STATS'
      GROUP BY get_json_object(eventData, '$.spellType')
    """)
    
    val spellBalanceMetrics = spellBalanceDF.collect().flatMap { row =>
      val spellType = row.getString(0)
      val effectiveness = row.getDouble(1)
      val usageRate = row.getDouble(2)
      
      // Calculate balance score (higher is more balanced)
      val balanceScore = (effectiveness + usageRate) / 2
      
      if (spellType != null) {
        Some((spellType, balanceScore))
      } else {
        None
      }
    }.toMap
    
    // Analyze difficulty balance
    val difficultyBalanceDF = spark.sql("""
      SELECT 
        get_json_object(eventData, '$.difficulty') AS difficulty,
        AVG(CAST(get_json_object(eventData, '$.completionRate') AS DOUBLE)) AS completionRate,
        AVG(CAST(get_json_object(eventData, '$.averageScore') AS DOUBLE)) AS averageScore
      FROM gameplay_events
      WHERE eventType = 'DIFFICULTY_STATS'
      GROUP BY get_json_object(eventData, '$.difficulty')
    """)
    
    val difficultyBalanceMetrics = difficultyBalanceDF.collect().flatMap { row =>
      val difficulty = row.getString(0)
      val completionRate = row.getDouble(1)
      val averageScore = row.getDouble(2)
      
      // Calculate balance score (higher is more balanced)
      // For difficulty, we want completion rates to decrease as difficulty increases
      val balanceScore = if (difficulty != null) {
        difficulty match {
          case "EASY" => if (completionRate > 0.8) 1.0 else completionRate / 0.8
          case "MEDIUM" => if (completionRate > 0.6 && completionRate < 0.8) 1.0 else 1.0 - Math.abs(completionRate - 0.7) / 0.7
          case "HARD" => if (completionRate > 0.3 && completionRate < 0.5) 1.0 else 1.0 - Math.abs(completionRate - 0.4) / 0.4
          case "EXPERT" => if (completionRate < 0.3) 1.0 else 1.0 - (completionRate - 0.3) / 0.7
          case _ => 0.5
        }
      } else {
        0.5
      }
      
      if (difficulty != null) {
        Some((difficulty, balanceScore))
      } else {
        None
      }
    }.toMap
    
    // Analyze game modes balance
    val gameModesBalanceDF = spark.sql("""
      SELECT 
        get_json_object(eventData, '$.gameMode') AS gameMode,
        AVG(CAST(get_json_object(eventData, '$.popularityScore') AS DOUBLE)) AS popularity,
        AVG(CAST(get_json_object(eventData, '$.engagementScore') AS DOUBLE)) AS engagement
      FROM gameplay_events
      WHERE eventType = 'GAME_MODE_STATS'
      GROUP BY get_json_object(eventData, '$.gameMode')
    """)
    
    val gameModesBalanceMetrics = gameModesBalanceDF.collect().flatMap { row =>
      val gameMode = row.getString(0)
      val popularity = row.getDouble(1)
      val engagement = row.getDouble(2)
      
      // Calculate balance score (higher is more balanced)
      val balanceScore = (popularity + engagement) / 2
      
      if (gameMode != null) {
        Some((gameMode, balanceScore))
      } else {
        None
      }
    }.toMap
    
    // Generate balance recommendations
    val balanceRecommendations = new ArrayBuffer[BalanceRecommendation]()
    
    // Add recommendations for blocks
    blockBalanceMetrics.foreach { case (blockType, score) =>
      if (score < 0.6) {
        balanceRecommendations += BalanceRecommendation(
          targetElement = s"Block: $blockType",
          currentValue = score,
          recommendedValue = 0.7,
          impact = "Improve player experience with this block type",
          confidence = 0.8
        )
      }
    }
    
    // Add recommendations for spells
    spellBalanceMetrics.foreach { case (spellType, score) =>
      if (score < 0.6) {
        balanceRecommendations += BalanceRecommendation(
          targetElement = s"Spell: $spellType",
          currentValue = score,
          recommendedValue = 0.7,
          impact = "Increase spell usage and effectiveness",
          confidence = 0.75
        )
      }
    }
    
    // Add recommendations for difficulty levels
    difficultyBalanceMetrics.foreach { case (difficulty, score) =>
      if (score < 0.6) {
        balanceRecommendations += BalanceRecommendation(
          targetElement = s"Difficulty: $difficulty",
          currentValue = score,
          recommendedValue = 0.7,
          impact = "Better align difficulty with player expectations",
          confidence = 0.85
        )
      }
    }
    
    // Add recommendations for game modes
    gameModesBalanceMetrics.foreach { case (gameMode, score) =>
      if (score < 0.6) {
        balanceRecommendations += BalanceRecommendation(
          targetElement = s"Game Mode: $gameMode",
          currentValue = score,
          recommendedValue = 0.7,
          impact = "Increase popularity and engagement",
          confidence = 0.7
        )
      }
    }
    
    // Return the results
    GameBalanceAnalysisResults(
      blockBalanceMetrics = blockBalanceMetrics,
      spellBalanceMetrics = spellBalanceMetrics,
      difficultyBalanceMetrics = difficultyBalanceMetrics,
      gameModesBalanceMetrics = gameModesBalanceMetrics,
      balanceRecommendations = balanceRecommendations.toList
    )
  }
}

/**
 * Analyzer for system performance
 *
 * @param spark Spark session
 * @param config Analytics configuration
 */
class PerformanceAnalyzer(spark: SparkSession, config: AnalyticsConfig) {
  import spark.implicits._
  
  /**
   * Analyze system performance
   *
   * @param performanceDF DataFrame containing performance metrics
   * @return Results of the analysis
   */
  def analyze(performanceDF: DataFrame): PerformanceAnalysisResults = {
    println("Analyzing system performance...")
    
    // Register the DataFrame as a temporary view
    performanceDF.createOrReplaceTempView("performance_metrics")
    
    // Calculate average FPS
    val fpsDF = spark.sql("""
      SELECT AVG(CAST(get_json_object(metrics, '$.fps') AS DOUBLE)) AS averageFPS
      FROM performance_metrics
      WHERE componentType = 'RENDERER'
    """)
    
    val averageFPS = if (fpsDF.count() > 0) fpsDF.first().getDouble(0) else 60.0
    
    // Calculate average memory usage
    val memoryDF = spark.sql("""
      SELECT AVG(CAST(get_json_object(metrics, '$.memoryUsageMB') AS DOUBLE)) AS averageMemoryUsage
      FROM performance_metrics
      WHERE componentType = 'SYSTEM'
    """)
    
    val averageMemoryUsage = if (memoryDF.count() > 0) memoryDF.first().getDouble(0) else 500.0
    
    // Calculate average CPU usage
    val cpuDF = spark.sql("""
      SELECT AVG(CAST(get_json_object(metrics, '$.cpuUsagePercent') AS DOUBLE)) AS averageCPUUsage
      FROM performance_metrics
      WHERE componentType = 'SYSTEM'
    """)
    
    val averageCPUUsage = if (cpuDF.count() > 0) cpuDF.first().getDouble(0) else 30.0
    
    // Calculate average network latency
    val latencyDF = spark.sql("""
      SELECT AVG(CAST(get_json_object(metrics, '$.latencyMs') AS DOUBLE)) AS averageNetworkLatency
      FROM performance_metrics
      WHERE componentType = 'NETWORK'
    """)
    
    val averageNetworkLatency = if (latencyDF.count() > 0) latencyDF.first().getDouble(0) else 50.0
    
    // Calculate component performance
    val componentDF = spark.sql("""
      SELECT 
        componentType,
        AVG(CAST(get_json_object(metrics, '$.performanceScore') AS DOUBLE)) AS averagePerformance
      FROM performance_metrics
      GROUP BY componentType
    """)
    
    val componentPerformance = componentDF.collect().map { row =>
      (row.getString(0), row.getDouble(1))
    }.toMap
    
    // Identify performance bottlenecks
    val bottlenecksDF = spark.sql("""
      SELECT 
        componentType,
        get_json_object(metrics, '$.metricName') AS metricName,
        CAST(get_json_object(metrics, '$.value') AS DOUBLE) AS metricValue,
        CAST(get_json_object(metrics, '$.threshold') AS DOUBLE) AS threshold
      FROM performance_metrics
      WHERE get_json_object(metrics, '$.isBottleneck') = 'true'
    """)
    
    val performanceBottlenecks = bottlenecksDF.collect().zipWithIndex.map { case (row, i) =>
      val componentType = row.getString(0)
      val metricName = row.getString(1)
      val metricValue = row.getDouble(2)
      val threshold = row.getDouble(3)
      
      // Calculate severity (0-1, higher is more severe)
      val severity = if (threshold > 0) Math.min(1.0, metricValue / threshold) else 0.5
      
      // Generate description
      val description = s"$metricName is at $metricValue, which exceeds the threshold of $threshold"
      
      PerformanceBottleneck(
        componentId = componentType,
        metricName = metricName,
        severity = severity,
        description = description
      )
    }.toList
    
    // Generate optimization recommendations
    val optimizationRecommendations = new ArrayBuffer[OptimizationRecommendation]()
    
    // Add recommendations based on bottlenecks
    performanceBottlenecks.foreach { bottleneck =>
      val recommendation = bottleneck.componentId match {
        case "RENDERER" => 
          OptimizationRecommendation(
            targetComponent = "Renderer",
            recommendation = "Optimize rendering pipeline and reduce draw calls",
            expectedImprovement = 20.0,
            implementationComplexity = "Medium"
          )
        case "PHYSICS" =>
          OptimizationRecommendation(
            targetComponent = "Physics Engine",
            recommendation = "Implement spatial partitioning to reduce collision checks",
            expectedImprovement = 30.0,
            implementationComplexity = "High"
          )
        case "NETWORK" =>
          OptimizationRecommendation(
            targetComponent = "Network",
            recommendation = "Implement more efficient serialization and compression",
            expectedImprovement = 25.0,
            implementationComplexity = "Medium"
          )
        case "AI" =>
          OptimizationRecommendation(
            targetComponent = "AI System",
            recommendation = "Optimize decision-making algorithms and reduce computation frequency",
            expectedImprovement = 15.0,
            implementationComplexity = "Medium"
          )
        case _ =>
          OptimizationRecommendation(
            targetComponent = bottleneck.componentId,
            recommendation = "Review and optimize resource usage",
            expectedImprovement = 10.0,
            implementationComplexity = "Low"
          )
      }
      
      optimizationRecommendations += recommendation
    }
    
    // Add general recommendations if no specific bottlenecks
    if (performanceBottlenecks.isEmpty) {
      optimizationRecommendations += OptimizationRecommendation(
        targetComponent = "Memory Management",
        recommendation = "Implement object pooling for frequently created/destroyed objects",
        expectedImprovement = 15.0,
        implementationComplexity = "Medium"
      )
      
      optimizationRecommendations += OptimizationRecommendation(
        targetComponent = "Rendering",
        recommendation = "Implement level-of-detail system for complex scenes",
        expectedImprovement = 20.0,
        implementationComplexity = "Medium"
      )
    }
    
    // Return the results
    PerformanceAnalysisResults(
      averageFPS = averageFPS,
      averageMemoryUsage = averageMemoryUsage,
      averageCPUUsage = averageCPUUsage,
      averageNetworkLatency = averageNetworkLatency,
      componentPerformance = componentPerformance,
      performanceBottlenecks = performanceBottlenecks,
      optimizationRecommendations = optimizationRecommendations.toList
    )
  }
}

/**
 * Dashboard reporter for analytics results
 *
 * @param config Analytics configuration
 */
class DashboardReporter(config: AnalyticsConfig) {
  private var running = false
  
  def start(): Unit = {
    running = true
    println(s"Dashboard reporter started on port ${config.dashboardConfig.port}")
  }
  
  def stop(): Unit = {
    running = false
    println("Dashboard reporter stopped")
  }
  
  def generateReport(results: AnalyticsResults): Unit = {
    if (running) {
      println("Generating dashboard report...")
      
      // In a real implementation, this would update a web dashboard
      // For now, we'll just print a summary
      println(s"Dashboard updated with latest analytics results from ${results.timestamp}")
      
      // Save report to file
      val timestamp = DateTimeFormatter
        .ofPattern("yyyyMMdd_HHmmss")
        .format(LocalDateTime.ofInstant(results.timestamp, ZoneId.systemDefault()))
      
      val reportPath = s"${config.dataStoragePath}/reports/dashboard_report_$timestamp.html"
      
      // Ensure directory exists
      Files.createDirectories(Paths.get(s"${config.dataStoragePath}/reports"))
      
      // Generate HTML report
      val reportContent = ReportGenerator.generateHtmlReport(results)
      
      // Save report
      val writer = new PrintWriter(reportPath)
      writer.write(reportContent)
      writer.close()
      
      println(s"Dashboard report saved to $reportPath")
    }
  }
}

/**
 * Alert system for analytics results
 *
 * @param config Analytics configuration
 */
class AlertSystem(config: AnalyticsConfig) {
  private var running = false
  
  def start(): Unit = {
    running = true
    println("Alert system started")
  }
  
  def stop(): Unit = {
    running = false
    println("Alert system stopped")
  }
  
  def checkAlerts(results: AnalyticsResults): Unit = {
    if (running) {
      println("Checking for alerts...")
      
      // Check performance alerts
      if (results.performanceResults.averageFPS < config.alertThresholds.getOrElse("minFPS", 30.0)) {
        triggerAlert("Low FPS", s"Average FPS is ${results.performanceResults.averageFPS}, which is below the threshold")
      }
      
      if (results.performanceResults.averageCPUUsage > config.alertThresholds.getOrElse("maxCPU", 80.0)) {
        triggerAlert("High CPU Usage", s"Average CPU usage is ${results.performanceResults.averageCPUUsage}%, which is above the threshold")
      }
      
      if (results.performanceResults.averageMemoryUsage > config.alertThresholds.getOrElse("maxMemory", 1000.0)) {
        triggerAlert("High Memory Usage", s"Average memory usage is ${results.performanceResults.averageMemoryUsage} MB, which is above the threshold")
      }
      
      // Check game balance alerts
      results.balanceResults.balanceRecommendations.foreach { recommendation =>
        if (recommendation.confidence > 0.8 && recommendation.currentValue < 0.5) {
          triggerAlert("Game Balance Issue", s"${recommendation.targetElement} has a low balance score of ${recommendation.currentValue}")
        }
      }
      
      // Check player retention alerts
      val dayOneRetention = results.playerResults.playerRetention.getOrElse("1 days", 0.0)
      if (dayOneRetention < config.alertThresholds.getOrElse("minRetention", 0.4)) {
        triggerAlert("Low Player Retention", s"Day 1 retention is $dayOneRetention, which is below the threshold")
      }
    }
  }
  
  private def triggerAlert(title: String, message: String): Unit = {
    println(s"ALERT: $title - $message")
    
    // In a real implementation, this would send notifications via email, Slack, etc.
    val timestamp = DateTimeFormatter
      .ofPattern("yyyyMMdd_HHmmss")
      .format(LocalDateTime.now())
    
    val alertPath = s"${config.dataStoragePath}/alerts/alert_${timestamp}.txt"
    
    // Ensure directory exists
    Files.createDirectories(Paths.get(s"${config.dataStoragePath}/alerts"))
    
    // Save alert
    val writer = new PrintWriter(alertPath)
    writer.write(s"$timestamp - $title\n$message")
    writer.close()
    
    println(s"Alert saved to $alertPath")
  }
}

/**
 * Report generator for analytics results
 */
object ReportGenerator {
  /**
   * Generate an HTML report from analytics results
   *
   * @param results Analytics results
   * @return HTML report content
   */
  def generateHtmlReport(results: AnalyticsResults): String = {
    val timestamp = DateTimeFormatter
      .ofPattern("yyyy-MM-dd HH:mm:ss")
      .format(LocalDateTime.ofInstant(results.timestamp, ZoneId.systemDefault()))
    
    val html = new StringBuilder()
    
    // HTML header
    html.append("""
      <!DOCTYPE html>
      <html>
      <head>
        <title>Tetris Towers Analytics Report</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          h1 { color: #333; }
          h2 { color: #666; margin-top: 30px; }
          table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f2f2f2; }
          tr:nth-child(even) { background-color: #f9f9f9; }
          .chart { width: 100%; height: 300px; margin-bottom: 20px; }
          .alert { background-color: #ffdddd; border-left: 6px solid #f44336; padding: 10px; margin-bottom: 15px; }
          .recommendation { background-color: #e7f3fe; border-left: 6px solid #2196F3; padding: 10px; margin-bottom: 15px; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      </head>
      <body>
    """)
    
    // Report header
    html.append(s"""
      <h1>Tetris Towers Analytics Report</h1>
      <p>Generated on: $timestamp</p>
    """)
    
    // Gameplay Analysis
    html.append("""
      <h2>Gameplay Analysis</h2>
      <table>
        <tr>
          <th>Metric</th>
          <th>Value</th>
        </tr>
    """)
    
    html.append(s"""
      <tr><td>Average Game Duration</td><td>${results.gameplayResults.averageGameDuration} seconds</td></tr>
      <tr><td>Average Score</td><td>${results.gameplayResults.averageScore}</td></tr>
      <tr><td>Average Lines Cleared</td><td>${results.gameplayResults.averageLinesCleared}</td></tr>
    """)
    
    html.append("</table>")
    
    // Block Usage Distribution
    html.append("""
      <h3>Block Usage Distribution</h3>
      <div class="chart">
        <canvas id="blockChart"></canvas>
      </div>
      <script>
        var blockCtx = document.getElementById('blockChart').getContext('2d');
        var blockChart = new Chart(blockCtx, {
          type: 'pie',
          data: {
            labels: [
    """)
    
    html.append(results.gameplayResults.blockUsageDistribution.keys.map(k => s"'$k'").mkString(", "))
    
    html.append("""
            ],
            datasets: [{
              data: [
    """)
    
    html.append(results.gameplayResults.blockUsageDistribution.values.map(v => f"$v%.2f").mkString(", "))
    
    html.append("""
              ],
              backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
              ]
            }]
          },
          options: {
            responsive: true,
            title: {
              display: true,
              text: 'Block Usage Distribution'
            }
          }
        });
      </script>
    """)
    
    // Player Analysis
    html.append("""
      <h2>Player Analysis</h2>
      <h3>Player Segments</h3>
      <table>
        <tr>
          <th>Segment</th>
          <th>Player Count</th>
          <th>Key Characteristics</th>
        </tr>
    """)
    
    results.playerResults.playerSegments.foreach { segment =>
      val characteristics = segment.characteristics.map { case (k, v) => s"$k: ${f"$v%.2f"}" }.mkString(", ")
      html.append(s"""
        <tr>
          <td>${segment.segmentName}</td>
          <td>${segment.playerCount}</td>
          <td>${characteristics}</td>
        </tr>
      """)
    }
    
    html.append("</table>")
    
    // Player Skill Distribution
    html.append("""
      <h3>Player Skill Distribution</h3>
      <div class="chart">
        <canvas id="skillChart"></canvas>
      </div>
      <script>
        var skillCtx = document.getElementById('skillChart').getContext('2d');
        var skillChart = new Chart(skillCtx, {
          type: 'bar',
          data: {
            labels: [
    """)
    
    html.append(results.playerResults.playerSkillDistribution.keys.map(k => s"'$k'").mkString(", "))
    
    html.append("""
            ],
            datasets: [{
              label: 'Player Percentage',
              data: [
    """)
    
    html.append(results.playerResults.playerSkillDistribution.values.map(v => f"${v * 100}%.2f").mkString(", "))
    
    html.append("""
              ],
              backgroundColor: '#36A2EB'
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    return value + '%';
                  }
                }
              }
            }
          }
        });
      </script>
    """)
    
    // Game Balance Analysis
    html.append("""
      <h2>Game Balance Analysis</h2>
      <h3>Balance Recommendations</h3>
    """)
    
    results.balanceResults.balanceRecommendations.foreach { recommendation =>
      html.append(s"""
        <div class="recommendation">
          <h4>${recommendation.targetElement}</h4>
          <p>Current Value: ${f"${recommendation.currentValue}%.2f"}</p>
          <p>Recommended Value: ${f"${recommendation.recommendedValue}%.2f"}</p>
          <p>Expected Impact: ${recommendation.impact}</p>
          <p>Confidence: ${f"${recommendation.confidence * 100}%.0f"}%</p>
        </div>
      """)
    }
    
    // Performance Analysis
    html.append("""
      <h2>Performance Analysis</h2>
      <table>
        <tr>
          <th>Metric</th>
          <th>Value</th>
        </tr>
    """)
    
    html.append(s"""
      <tr><td>Average FPS</td><td>${f"${results.performanceResults.averageFPS}%.2f"}</td></tr>
      <tr><td>Average Memory Usage</td><td>${f"${results.performanceResults.averageMemoryUsage}%.2f"} MB</td></tr>
      <tr><td>Average CPU Usage</td><td>${f"${results.performanceResults.averageCPUUsage}%.2f"}%</td></tr>
      <tr><td>Average Network Latency</td><td>${f"${results.performanceResults.averageNetworkLatency}%.2f"} ms</td></tr>
    """)
    
    html.append("</table>")
    
    // Performance Bottlenecks
    html.append("<h3>Performance Bottlenecks</h3>")
    
    if (results.performanceResults.performanceBottlenecks.isEmpty) {
      html.append("<p>No significant performance bottlenecks detected.</p>")
    } else {
      results.performanceResults.performanceBottlenecks.foreach { bottleneck =>
        html.append(s"""
          <div class="alert">
            <h4>${bottleneck.componentId}: ${bottleneck.metricName}</h4>
            <p>Severity: ${f"${bottleneck.severity * 100}%.0f"}%</p>
            <p>${bottleneck.description}</p>
          </div>
        """)
      }
    }
    
    // Optimization Recommendations
    html.append("<h3>Optimization Recommendations</h3>")
    
    results.performanceResults.optimizationRecommendations.foreach { recommendation =>
      html.append(s"""
        <div class="recommendation">
          <h4>${recommendation.targetComponent}</h4>
          <p>${recommendation.recommendation}</p>
          <p>Expected Improvement: ${f"${recommendation.expectedImprovement}%.0f"}%</p>
          <p>Implementation Complexity: ${recommendation.implementationComplexity}</p>
        </div>
      """)
    }
    
    // HTML footer
    html.append("""
      </body>
      </html>
    """)
    
    html.toString()
  }
}

/**
 * Main entry point for the analytics system
 */
object AnalyticsMain {
  def main(args: Array[String]): Unit = {
    // Parse command line arguments
    if (args.length < 1) {
      println("Usage: AnalyticsMain <config_file>")
      System.exit(1)
    }
    
    val configFile = args(0)
    
    // Load configuration
    val configJson = new String(Files.readAllBytes(Paths.get(configFile)))
    val config = Json.parse(configJson).as[AnalyticsConfig]
    
    // Create and start analytics system
    val analytics = new AnalyticsSystem(config)
    analytics.start()
    
    // Add shutdown hook
    Runtime.getRuntime().addShutdownHook(new Thread() {
      override def run(): Unit = {
        println("Shutting down analytics system...")
        analytics.stop()
      }
    })
    
    // Keep running until terminated
    println("Analytics system running. Press Ctrl+C to stop.")
    while (true) {
      Thread.sleep(1000)
    }
  }
}
