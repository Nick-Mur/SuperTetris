package utils

// Config represents the configuration for the development tools
type Config struct {
	// General settings
	WorkingDirectory string `json:"workingDirectory"`
	LogLevel         string `json:"logLevel"`
	AutoSave         bool   `json:"autoSave"`
	AutoSaveInterval int    `json:"autoSaveInterval"` // in seconds

	// Editor settings
	EditorTheme      string `json:"editorTheme"`
	GridSize         int    `json:"gridSize"`
	ShowGrid         bool   `json:"showGrid"`
	SnapToGrid       bool   `json:"snapToGrid"`
	MaxUndoSteps     int    `json:"maxUndoSteps"`
	DefaultBlockSize int    `json:"defaultBlockSize"`

	// Generator settings
	GeneratorSeed        int64   `json:"generatorSeed"`
	DifficultyLevel      int     `json:"difficultyLevel"`
	MinBlocks            int     `json:"minBlocks"`
	MaxBlocks            int     `json:"maxBlocks"`
	SymmetryProbability  float64 `json:"symmetryProbability"`
	SpecialBlockChance   float64 `json:"specialBlockChance"`
	GenerateSpellPickups bool    `json:"generateSpellPickups"`

	// Analyzer settings
	AnalysisDepth        int  `json:"analysisDepth"`
	GenerateHeatmaps     bool `json:"generateHeatmaps"`
	AnalyzeBlockPatterns bool `json:"analyzeBlockPatterns"`
	AnalyzePlayerStats   bool `json:"analyzePlayerStats"`
	AnalyzeGameBalance   bool `json:"analyzeGameBalance"`

	// Profiler settings
	ProfilerSamplingRate int    `json:"profilerSamplingRate"` // in milliseconds
	ProfilerOutputFormat string `json:"profilerOutputFormat"`
	ProfileMemory        bool   `json:"profileMemory"`
	ProfileCPU           bool   `json:"profileCPU"`
	ProfileNetwork       bool   `json:"profileNetwork"`
	ProfilePhysics       bool   `json:"profilePhysics"`
}

// DefaultConfig returns a default configuration
func DefaultConfig() Config {
	return Config{
		// General settings
		WorkingDirectory: ".",
		LogLevel:         "info",
		AutoSave:         true,
		AutoSaveInterval: 300, // 5 minutes

		// Editor settings
		EditorTheme:      "dark",
		GridSize:         32,
		ShowGrid:         true,
		SnapToGrid:       true,
		MaxUndoSteps:     50,
		DefaultBlockSize: 32,

		// Generator settings
		GeneratorSeed:        0, // 0 means use current time
		DifficultyLevel:      2, // Medium difficulty
		MinBlocks:            10,
		MaxBlocks:            50,
		SymmetryProbability:  0.3,
		SpecialBlockChance:   0.1,
		GenerateSpellPickups: true,

		// Analyzer settings
		AnalysisDepth:        3,
		GenerateHeatmaps:     true,
		AnalyzeBlockPatterns: true,
		AnalyzePlayerStats:   true,
		AnalyzeGameBalance:   true,

		// Profiler settings
		ProfilerSamplingRate: 100,
		ProfilerOutputFormat: "json",
		ProfileMemory:        true,
		ProfileCPU:           true,
		ProfileNetwork:       true,
		ProfilePhysics:       true,
	}
}
