package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/tetris-towers/dev-tools/analyzer"
	"github.com/tetris-towers/dev-tools/editor"
	"github.com/tetris-towers/dev-tools/generator"
	"github.com/tetris-towers/dev-tools/profiler"
	"github.com/tetris-towers/dev-tools/utils"
)

// Version information
const (
	ToolName    = "Tetris Towers Development Tools"
	ToolVersion = "1.0.0"
)

// Command line flags
var (
	mode        = flag.String("mode", "", "Tool mode: editor, generator, analyzer, profiler")
	inputFile   = flag.String("input", "", "Input file path")
	outputFile  = flag.String("output", "", "Output file path")
	configFile  = flag.String("config", "", "Configuration file path")
	verbose     = flag.Bool("verbose", false, "Enable verbose output")
	interactive = flag.Bool("interactive", false, "Run in interactive mode")
	version     = flag.Bool("version", false, "Show version information")
)

func main() {
	flag.Parse()

	// Setup logging
	logFormat := log.Ldate | log.Ltime
	if *verbose {
		logFormat |= log.Lshortfile
	}
	log.SetFlags(logFormat)

	// Show version and exit if requested
	if *version {
		fmt.Printf("%s v%s\n", ToolName, ToolVersion)
		return
	}

	// Load configuration if provided
	var config utils.Config
	if *configFile != "" {
		if err := loadConfig(*configFile, &config); err != nil {
			log.Fatalf("Failed to load configuration: %v", err)
		}
	} else {
		config = utils.DefaultConfig()
	}

	// Execute the requested mode
	switch strings.ToLower(*mode) {
	case "editor":
		runEditor(config)
	case "generator":
		runGenerator(config)
	case "analyzer":
		runAnalyzer(config)
	case "profiler":
		runProfiler(config)
	case "":
		if *interactive {
			runInteractive(config)
		} else {
			flag.Usage()
			os.Exit(1)
		}
	default:
		log.Fatalf("Unknown mode: %s", *mode)
	}
}

// loadConfig loads the configuration from a JSON file
func loadConfig(path string, config *utils.Config) error {
	data, err := ioutil.ReadFile(path)
	if err != nil {
		return fmt.Errorf("failed to read config file: %w", err)
	}

	if err := json.Unmarshal(data, config); err != nil {
		return fmt.Errorf("failed to parse config file: %w", err)
	}

	return nil
}

// runEditor starts the level editor
func runEditor(config utils.Config) {
	log.Println("Starting level editor...")

	// Create editor instance
	ed := editor.NewEditor(config)

	// Load level if input file is provided
	if *inputFile != "" {
		if err := ed.LoadLevel(*inputFile); err != nil {
			log.Fatalf("Failed to load level: %v", err)
		}
		log.Printf("Loaded level from %s", *inputFile)
	}

	// Run the editor
	if err := ed.Run(); err != nil {
		log.Fatalf("Editor error: %v", err)
	}

	// Save level if output file is provided
	if *outputFile != "" {
		if err := ed.SaveLevel(*outputFile); err != nil {
			log.Fatalf("Failed to save level: %v", err)
		}
		log.Printf("Saved level to %s", *outputFile)
	}
}

// runGenerator starts the level generator
func runGenerator(config utils.Config) {
	log.Println("Starting level generator...")

	// Create generator instance
	gen := generator.NewGenerator(config)

	// Set generator parameters from input file if provided
	if *inputFile != "" {
		if err := gen.LoadParameters(*inputFile); err != nil {
			log.Fatalf("Failed to load generator parameters: %v", err)
		}
		log.Printf("Loaded generator parameters from %s", *inputFile)
	}

	// Generate level
	level, err := gen.Generate()
	if err != nil {
		log.Fatalf("Generator error: %v", err)
	}

	// Save generated level if output file is provided
	if *outputFile != "" {
		if err := gen.SaveLevel(level, *outputFile); err != nil {
			log.Fatalf("Failed to save generated level: %v", err)
		}
		log.Printf("Saved generated level to %s", *outputFile)
	}
}

// runAnalyzer starts the game analyzer
func runAnalyzer(config utils.Config) {
	log.Println("Starting game analyzer...")

	// Create analyzer instance
	a := analyzer.NewAnalyzer(config)

	// Load game data if input file is provided
	if *inputFile != "" {
		if err := a.LoadGameData(*inputFile); err != nil {
			log.Fatalf("Failed to load game data: %v", err)
		}
		log.Printf("Loaded game data from %s", *inputFile)
	}

	// Run analysis
	results, err := a.Analyze()
	if err != nil {
		log.Fatalf("Analyzer error: %v", err)
	}

	// Save analysis results if output file is provided
	if *outputFile != "" {
		if err := a.SaveResults(results, *outputFile); err != nil {
			log.Fatalf("Failed to save analysis results: %v", err)
		}
		log.Printf("Saved analysis results to %s", *outputFile)
	} else {
		// Print summary to console
		a.PrintSummary(results)
	}
}

// runProfiler starts the performance profiler
func runProfiler(config utils.Config) {
	log.Println("Starting performance profiler...")

	// Create profiler instance
	p := profiler.NewProfiler(config)

	// Load profiling configuration if input file is provided
	if *inputFile != "" {
		if err := p.LoadConfig(*inputFile); err != nil {
			log.Fatalf("Failed to load profiler configuration: %v", err)
		}
		log.Printf("Loaded profiler configuration from %s", *inputFile)
	}

	// Run profiling
	results, err := p.Run()
	if err != nil {
		log.Fatalf("Profiler error: %v", err)
	}

	// Save profiling results if output file is provided
	if *outputFile != "" {
		if err := p.SaveResults(results, *outputFile); err != nil {
			log.Fatalf("Failed to save profiling results: %v", err)
		}
		log.Printf("Saved profiling results to %s", *outputFile)
	} else {
		// Print summary to console
		p.PrintSummary(results)
	}
}

// runInteractive starts the interactive mode
func runInteractive(config utils.Config) {
	fmt.Printf("%s v%s\n\n", ToolName, ToolVersion)
	fmt.Println("Interactive mode. Type 'help' for available commands, 'exit' to quit.")

	for {
		fmt.Print("> ")
		var command string
		fmt.Scanln(&command)

		switch strings.ToLower(command) {
		case "exit", "quit":
			fmt.Println("Exiting...")
			return
		case "help":
			printHelp()
		case "editor":
			runEditor(config)
		case "generator":
			runGenerator(config)
		case "analyzer":
			runAnalyzer(config)
		case "profiler":
			runProfiler(config)
		case "version":
			fmt.Printf("%s v%s\n", ToolName, ToolVersion)
		default:
			fmt.Printf("Unknown command: %s\nType 'help' for available commands.\n", command)
		}
	}
}

// printHelp prints the help information for interactive mode
func printHelp() {
	fmt.Println("Available commands:")
	fmt.Println("  editor     - Start the level editor")
	fmt.Println("  generator  - Start the level generator")
	fmt.Println("  analyzer   - Start the game analyzer")
	fmt.Println("  profiler   - Start the performance profiler")
	fmt.Println("  version    - Show version information")
	fmt.Println("  help       - Show this help")
	fmt.Println("  exit       - Exit the program")
}
