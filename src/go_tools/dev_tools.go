package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

/**
 * DevTools - Инструменты разработки для игры Tetris с элементами Tricky Towers
 * Реализовано на Go с использованием Fyne для GUI
 */

// Типы тетромино
type TetrominoType string

const (
	TetrominoI TetrominoType = "I"
	TetrominoJ TetrominoType = "J"
	TetrominoL TetrominoType = "L"
	TetrominoO TetrominoType = "O"
	TetrominoS TetrominoType = "S"
	TetrominoT TetrominoType = "T"
	TetrominoZ TetrominoType = "Z"
)

// Типы заклинаний
type SpellType string

const (
	// Светлая магия
	SpellReinforce  SpellType = "REINFORCE"  // Укрепление блоков
	SpellStabilize  SpellType = "STABILIZE"  // Стабилизация башни
	SpellEnlarge    SpellType = "ENLARGE"    // Увеличение блока
	SpellShrink     SpellType = "SHRINK"     // Уменьшение блока
	SpellLevitate   SpellType = "LEVITATE"   // Левитация блока
	
	// Тёмная магия
	SpellEarthquake SpellType = "EARTHQUAKE" // Землетрясение
	SpellWind       SpellType = "WIND"       // Ветер
	SpellSlippery   SpellType = "SLIPPERY"   // Скользкие блоки
	SpellConfusion  SpellType = "CONFUSION"  // Путаница управления
	SpellAccelerate SpellType = "ACCELERATE" // Ускорение падения
)

// Режимы игры
type GameMode string

const (
	GameModeRace     GameMode = "RACE"
	GameModeSurvival GameMode = "SURVIVAL"
	GameModePuzzle   GameMode = "PUZZLE"
)

// Структура для представления блока
type Block struct {
	ID         int       `json:"id"`
	X          float64   `json:"x"`
	Y          float64   `json:"y"`
	Width      float64   `json:"width"`
	Height     float64   `json:"height"`
	Rotation   float64   `json:"rotation"`
	Color      string    `json:"color"`
	Density    float64   `json:"density"`
	Friction   float64   `json:"friction"`
	Restitution float64  `json:"restitution"`
	IsStatic   bool      `json:"is_static"`
}

// Структура для представления тетромино
type Tetromino struct {
	Type     TetrominoType `json:"type"`
	X        float64       `json:"x"`
	Y        float64       `json:"y"`
	Rotation float64       `json:"rotation"`
}

// Структура для представления игрока
type Player struct {
	ID              int         `json:"id"`
	Name            string      `json:"name"`
	TowerBlocks     []Block     `json:"tower_blocks"`
	CurrentTetromino *Tetromino  `json:"current_tetromino"`
	NextTetrominos  []Tetromino `json:"next_tetrominos"`
	HeldTetromino   *Tetromino  `json:"held_tetromino"`
	Spells          []SpellType `json:"spells"`
	Score           int         `json:"score"`
	Health          int         `json:"health"`
}

// Структура для представления состояния игры
type GameState struct {
	Players    map[string]Player `json:"players"`
	GameMode   GameMode          `json:"game_mode"`
	CurrentTurn int              `json:"current_turn"`
	GameStatus string            `json:"game_status"`
	Timer      float64           `json:"timer"`
}

// Структура для представления уровня
type Level struct {
	Name        string    `json:"name"`
	Description string    `json:"description"`
	GameMode    GameMode  `json:"game_mode"`
	Blocks      []Block   `json:"blocks"`
	WinCondition string   `json:"win_condition"`
}

// Структура для представления настроек игры
type GameSettings struct {
	DefaultGameMode GameMode `json:"default_game_mode"`
	GravityScale    float64  `json:"gravity_scale"`
	SpellFrequency  float64  `json:"spell_frequency"`
	AIEnabled       bool     `json:"ai_enabled"`
	AILevel         int      `json:"ai_level"`
}

// Главная структура для инструментов разработки
type DevTools struct {
	app          fyne.App
	mainWindow   fyne.Window
	levelEditor  *LevelEditor
	gameAnalyzer *GameAnalyzer
	settingsEditor *SettingsEditor
	assetManager *AssetManager
}

// Структура для редактора уровней
type LevelEditor struct {
	window       fyne.Window
	currentLevel *Level
	blocks       []Block
	grid         *canvas.Raster
	selectedBlock *Block
	blockProperties *widget.Form
}

// Структура для анализатора игры
type GameAnalyzer struct {
	window       fyne.Window
	gameState    *GameState
	playerStats  map[int]PlayerStats
	charts       map[string]*canvas.Raster
}

// Структура для статистики игрока
type PlayerStats struct {
	TowerHeight     []float64
	TowerStability  []float64
	Score           []int
	SpellsUsed      int
	BlocksPlaced    int
	TimeAlive       float64
}

// Структура для редактора настроек
type SettingsEditor struct {
	window       fyne.Window
	settings     *GameSettings
	form         *widget.Form
}

// Структура для менеджера ассетов
type AssetManager struct {
	window       fyne.Window
	assetList    *widget.List
	assetPreview *canvas.Image
	assetPath    string
}

// Создание нового экземпляра инструментов разработки
func NewDevTools() *DevTools {
	a := app.New()
	w := a.NewWindow("Tetris with Tricky Towers - Developer Tools")
	
	dt := &DevTools{
		app:        a,
		mainWindow: w,
	}
	
	dt.setupMainWindow()
	
	return dt
}

// Настройка главного окна
func (dt *DevTools) setupMainWindow() {
	// Создание кнопок для различных инструментов
	levelEditorBtn := widget.NewButton("Level Editor", func() {
		dt.openLevelEditor()
	})
	
	gameAnalyzerBtn := widget.NewButton("Game Analyzer", func() {
		dt.openGameAnalyzer()
	})
	
	settingsEditorBtn := widget.NewButton("Settings Editor", func() {
		dt.openSettingsEditor()
	})
	
	assetManagerBtn := widget.NewButton("Asset Manager", func() {
		dt.openAssetManager()
	})
	
	// Создание контейнера с кнопками
	content := container.NewVBox(
		widget.NewLabel("Tetris with Tricky Towers - Developer Tools"),
		widget.NewSeparator(),
		levelEditorBtn,
		gameAnalyzerBtn,
		settingsEditorBtn,
		assetManagerBtn,
	)
	
	dt.mainWindow.SetContent(content)
	dt.mainWindow.Resize(fyne.NewSize(400, 300))
}

// Открытие редактора уровней
func (dt *DevTools) openLevelEditor() {
	if dt.levelEditor == nil {
		w := dt.app.NewWindow("Level Editor")
		
		dt.levelEditor = &LevelEditor{
			window:       w,
			currentLevel: &Level{
				Name:        "New Level",
				Description: "A new level",
				GameMode:    GameModeRace,
				Blocks:      []Block{},
				WinCondition: "height >= 15",
			},
			blocks:       []Block{},
		}
		
		dt.levelEditor.setupUI()
	}
	
	dt.levelEditor.window.Show()
}

// Настройка UI для редактора уровней
func (le *LevelEditor) setupUI() {
	// Создание сетки для редактирования
	le.grid = canvas.NewRaster(func(w, h int) image.Image {
		img := image.NewRGBA(image.Rect(0, 0, w, h))
		
		// Рисование сетки
		for x := 0; x < w; x += 30 {
			for y := 0; y < h; y++ {
				img.Set(x, y, color.RGBA{200, 200, 200, 255})
			}
		}
		
		for y := 0; y < h; y += 30 {
			for x := 0; x < w; x++ {
				img.Set(x, y, color.RGBA{200, 200, 200, 255})
			}
		}
		
		// Рисование блоков
		for _, block := range le.blocks {
			x := int(block.X * 30)
			y := int(block.Y * 30)
			width := int(block.Width * 30)
			height := int(block.Height * 30)
			
			// Парсинг цвета
			var r, g, b uint8
			fmt.Sscanf(block.Color, "#%02x%02x%02x", &r, &g, &b)
			
			// Рисование блока
			for dx := 0; dx < width; dx++ {
				for dy := 0; dy < height; dy++ {
					if x+dx < w && y+dy < h {
						img.Set(x+dx, y+dy, color.RGBA{r, g, b, 255})
					}
				}
			}
		}
		
		return img
	})
	
	// Обработка кликов по сетке
	le.grid.SetMinSize(fyne.NewSize(300, 600))
	
	// Создание формы для свойств блока
	le.blockProperties = widget.NewForm(
		widget.NewFormItem("X", widget.NewEntry()),
		widget.NewFormItem("Y", widget.NewEntry()),
		widget.NewFormItem("Width", widget.NewEntry()),
		widget.NewFormItem("Height", widget.NewEntry()),
		widget.NewFormItem("Color", widget.NewEntry()),
		widget.NewFormItem("Is Static", widget.NewCheck("", nil)),
	)
	
	// Кнопки для управления уровнем
	newBtn := widget.NewButton("New Level", func() {
		le.newLevel()
	})
	
	saveBtn := widget.NewButton("Save Level", func() {
		le.saveLevel()
	})
	
	loadBtn := widget.NewButton("Load Level", func() {
		le.loadLevel()
	})
	
	addBlockBtn := widget.NewButton("Add Block", func() {
		le.addBlock()
	})
	
	removeBlockBtn := widget.NewButton("Remove Block", func() {
		le.removeBlock()
	})
	
	// Создание контейнера с кнопками
	buttonContainer := container.NewHBox(
		newBtn,
		saveBtn,
		loadBtn,
		addBlockBtn,
		removeBlockBtn,
	)
	
	// Создание контейнера с формой и сеткой
	gridContainer := container.NewHSplit(
		le.grid,
		le.blockProperties,
	)
	
	// Создание основного контейнера
	content := container.NewVBox(
		buttonContainer,
		gridContainer,
	)
	
	le.window.SetContent(content)
	le.window.Resize(fyne.NewSize(800, 600))
}

// Создание нового уровня
func (le *LevelEditor) newLevel() {
	le.currentLevel = &Level{
		Name:        "New Level",
		Description: "A new level",
		GameMode:    GameModeRace,
		Blocks:      []Block{},
		WinCondition: "height >= 15",
	}
	
	le.blocks = []Block{}
	le.grid.Refresh()
}

// Сохранение уровня
func (le *LevelEditor) saveLevel() {
	// Создание диалога для выбора файла
	dialog.ShowFileSave(func(writer fyne.URIWriteCloser, err error) {
		if err != nil {
			dialog.ShowError(err, le.window)
			return
		}
		
		if writer == nil {
			return
		}
		
		// Обновление блоков в уровне
		le.currentLevel.Blocks = le.blocks
		
		// Сериализация уровня в JSON
		data, err := json.MarshalIndent(le.currentLevel, "", "  ")
		if err != nil {
			dialog.ShowError(err, le.window)
			return
		}
		
		// Запись данных в файл
		_, err = writer.Write(data)
		if err != nil {
			dialog.ShowError(err, le.window)
			return
		}
		
		writer.Close()
		
		dialog.ShowInformation("Success", "Level saved successfully", le.window)
	}, le.window)
}

// Загрузка уровня
func (le *LevelEditor) loadLevel() {
	// Создание диалога для выбора файла
	dialog.ShowFileOpen(func(reader fyne.URIReadCloser, err error) {
		if err != nil {
			dialog.ShowError(err, le.window)
			return
		}
		
		if reader == nil {
			return
		}
		
		// Чтение данных из файла
		data, err := ioutil.ReadAll(reader)
		if err != nil {
			dialog.ShowError(err, le.window)
			return
		}
		
		reader.Close()
		
		// Десериализация уровня из JSON
		var level Level
		err = json.Unmarshal(data, &level)
		if err != nil {
			dialog.ShowError(err, le.window)
			return
		}
		
		// Обновление текущего уровня и блоков
		le.currentLevel = &level
		le.blocks = level.Blocks
		le.grid.Refresh()
		
		dialog.ShowInformation("Success", "Level loaded successfully", le.window)
	}, le.window)
}

// Добавление блока
func (le *LevelEditor) addBlock() {
	// Создание нового блока
	block := Block{
		ID:         len(le.blocks),
		X:          5,
		Y:          10,
		Width:      1,
		Height:     1,
		Rotation:   0,
		Color:      "#FF0000",
		Density:    1.0,
		Friction:   0.3,
		Restitution: 0.1,
		IsStatic:   true,
	}
	
	// Добавление блока в список
	le.blocks = append(le.blocks, block)
	le.grid.Refresh()
}

// Удаление блока
func (le *LevelEditor) removeBlock() {
	if le.selectedBlock != nil {
		// Поиск индекса выбранного блока
		index := -1
		for i, block := range le.blocks {
			if block.ID == le.selectedBlock.ID {
				index = i
				break
			}
		}
		
		// Удаление блока из списка
		if index >= 0 {
			le.blocks = append(le.blocks[:index], le.blocks[index+1:]...)
			le.selectedBlock = nil
			le.grid.Refresh()
		}
	}
}

// Открытие анализатора игры
func (dt *DevTools) openGameAnalyzer() {
	if dt.gameAnalyzer == nil {
		w := dt.app.NewWindow("Game Analyzer")
		
		dt.gameAnalyzer = &GameAnalyzer{
			window:      w,
			gameState:   nil,
			playerStats: make(map[int]PlayerStats),
			charts:      make(map[string]*canvas.Raster),
		}
		
		dt.gameAnalyzer.setupUI()
	}
	
	dt.gameAnalyzer.window.Show()
}

// Настройка UI для анализатора игры
func (ga *GameAnalyzer) setupUI() {
	// Кнопки для управления анализатором
	loadBtn := widget.NewButton("Load Game Data", func() {
		ga.loadGameData()
	})
	
	analyzeBtn := widget.NewButton("Analyze Game", func() {
		ga.analyzeGame()
	})
	
	exportBtn := widget.NewButton("Export Analysis", func() {
		ga.exportAnalysis()
	})
	
	// Создание контейнера с кнопками
	buttonContainer := container.NewHBox(
		loadBtn,
		analyzeBtn,
		exportBtn,
	)
	
	// Создание вкладок для различных графиков
	tabs := container.NewAppTabs(
		container.NewTabItem("Tower Height", canvas.NewRaster(func(w, h int) image.Image {
			return ga.drawTowerHeightChart(w, h)
		})),
		container.NewTabItem("Tower Stability", canvas.NewRaster(func(w, h int) image.Image {
			return ga.drawTowerStabilityChart(w, h)
		})),
		container.NewTabItem("Score", canvas.NewRaster(func(w, h int) image.Image {
			return ga.drawScoreChart(w, h)
		})),
	)
	
	// Создание основного контейнера
	content := container.NewBorder(
		buttonContainer,
		nil,
		nil,
		nil,
		tabs,
	)
	
	ga.window.SetContent(content)
	ga.window.Resize(fyne.NewSize(800, 600))
}

// Загрузка данных игры
func (ga *GameAnalyzer) loadGameData() {
	// Создание диалога для выбора файла
	dialog.ShowFileOpen(func(reader fyne.URIReadCloser, err error) {
		if err != nil {
			dialog.ShowError(err, ga.window)
			return
		}
		
		if reader == nil {
			return
		}
		
		// Чтение данных из файла
		data, err := ioutil.ReadAll(reader)
		if err != nil {
			dialog.ShowError(err, ga.window)
			return
		}
		
		reader.Close()
		
		// Десериализация состояния игры из JSON
		var gameState GameState
		err = json.Unmarshal(data, &gameState)
		if err != nil {
			dialog.ShowError(err, ga.window)
			return
		}
		
		// Обновление текущего состояния игры
		ga.gameState = &gameState
		
		dialog.ShowInformation("Success", "Game data loaded successfully", ga.window)
	}, ga.window)
}

// Анализ игры
func (ga *GameAnalyzer) analyzeGame() {
	if ga.gameState == nil {
		dialog.ShowInformation("Error", "No game data loaded", ga.window)
		return
	}
	
	// Очистка предыдущих статистик
	ga.playerStats = make(map[int]PlayerStats)
	
	// Анализ статистики для каждого игрока
	for idStr, player := range ga.gameState.Players {
		id, _ := strconv.Atoi(idStr)
		
		// Вычисление высоты башни
		towerHeight := 0.0
		for _, block := range player.TowerBlocks {
			towerHeight = math.Max(towerHeight, 20-block.Y)
		}
		
		// Вычисление стабильности башни
		towerStability := ga.calculateTowerStability(player.TowerBlocks)
		
		// Создание статистики игрока
		stats := PlayerStats{
			TowerHeight:    []float64{towerHeight},
			TowerStability: []float64{towerStability},
			Score:          []int{player.Score},
			SpellsUsed:     len(player.Spells),
			BlocksPlaced:   len(player.TowerBlocks),
			TimeAlive:      ga.gameState.Timer,
		}
		
		ga.playerStats[id] = stats
	}
	
	// Обновление графиков
	for _, chart := range ga.charts {
		chart.Refresh()
	}
	
	dialog.ShowInformation("Success", "Game analyzed successfully", ga.window)
}

// Вычисление стабильности башни
func (ga *GameAnalyzer) calculateTowerStability(blocks []Block) float64 {
	if len(blocks) == 0 {
		return 1.0
	}
	
	// Вычисление центра масс башни
	totalMass := 0.0
	weightedX := 0.0
	
	for _, block := range blocks {
		mass := block.Width * block.Height * block.Density
		totalMass += mass
		weightedX += block.X * mass
	}
	
	centerOfMassX := weightedX / totalMass
	
	// Вычисление отклонения от центра поля
	fieldCenterX := 5.0 // Центр поля по X
	deviation := math.Abs(centerOfMassX - fieldCenterX)
	
	// Нормализация отклонения (0 - максимальная стабильность, 1 - минимальная)
	maxDeviation := 5.0 // Максимально возможное отклонение
	stability := 1.0 - (deviation / maxDeviation)
	
	return math.Max(0.0, math.Min(1.0, stability))
}

// Рисование графика высоты башни
func (ga *GameAnalyzer) drawTowerHeightChart(w, h int) image.Image {
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	
	// Заполнение фона
	for x := 0; x < w; x++ {
		for y := 0; y < h; y++ {
			img.Set(x, y, color.RGBA{240, 240, 240, 255})
		}
	}
	
	// Рисование осей
	for x := 0; x < w; x++ {
		img.Set(x, h-50, color.RGBA{0, 0, 0, 255})
	}
	
	for y := 0; y < h; y++ {
		img.Set(50, y, color.RGBA{0, 0, 0, 255})
	}
	
	// Рисование данных для каждого игрока
	colors := []color.RGBA{
		{255, 0, 0, 255},
		{0, 255, 0, 255},
		{0, 0, 255, 255},
		{255, 255, 0, 255},
	}
	
	i := 0
	for _, stats := range ga.playerStats {
		if len(stats.TowerHeight) > 0 {
			// Нормализация данных
			maxHeight := 20.0
			normalizedHeight := stats.TowerHeight[0] / maxHeight
			
			// Рисование точки
			x := 50 + int(float64(w-100)*0.5)
			y := h - 50 - int(float64(h-100)*normalizedHeight)
			
			// Рисование круга
			radius := 5
			for dx := -radius; dx <= radius; dx++ {
				for dy := -radius; dy <= radius; dy++ {
					if dx*dx+dy*dy <= radius*radius {
						img.Set(x+dx, y+dy, colors[i%len(colors)])
					}
				}
			}
			
			i++
		}
	}
	
	return img
}

// Рисование графика стабильности башни
func (ga *GameAnalyzer) drawTowerStabilityChart(w, h int) image.Image {
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	
	// Заполнение фона
	for x := 0; x < w; x++ {
		for y := 0; y < h; y++ {
			img.Set(x, y, color.RGBA{240, 240, 240, 255})
		}
	}
	
	// Рисование осей
	for x := 0; x < w; x++ {
		img.Set(x, h-50, color.RGBA{0, 0, 0, 255})
	}
	
	for y := 0; y < h; y++ {
		img.Set(50, y, color.RGBA{0, 0, 0, 255})
	}
	
	// Рисование данных для каждого игрока
	colors := []color.RGBA{
		{255, 0, 0, 255},
		{0, 255, 0, 255},
		{0, 0, 255, 255},
		{255, 255, 0, 255},
	}
	
	i := 0
	for _, stats := range ga.playerStats {
		if len(stats.TowerStability) > 0 {
			// Нормализация данных
			normalizedStability := stats.TowerStability[0]
			
			// Рисование точки
			x := 50 + int(float64(w-100)*0.5)
			y := h - 50 - int(float64(h-100)*normalizedStability)
			
			// Рисование круга
			radius := 5
			for dx := -radius; dx <= radius; dx++ {
				for dy := -radius; dy <= radius; dy++ {
					if dx*dx+dy*dy <= radius*radius {
						img.Set(x+dx, y+dy, colors[i%len(colors)])
					}
				}
			}
			
			i++
		}
	}
	
	return img
}

// Рисование графика очков
func (ga *GameAnalyzer) drawScoreChart(w, h int) image.Image {
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	
	// Заполнение фона
	for x := 0; x < w; x++ {
		for y := 0; y < h; y++ {
			img.Set(x, y, color.RGBA{240, 240, 240, 255})
		}
	}
	
	// Рисование осей
	for x := 0; x < w; x++ {
		img.Set(x, h-50, color.RGBA{0, 0, 0, 255})
	}
	
	for y := 0; y < h; y++ {
		img.Set(50, y, color.RGBA{0, 0, 0, 255})
	}
	
	// Рисование данных для каждого игрока
	colors := []color.RGBA{
		{255, 0, 0, 255},
		{0, 255, 0, 255},
		{0, 0, 255, 255},
		{255, 255, 0, 255},
	}
	
	// Нахождение максимального значения очков
	maxScore := 1
	for _, stats := range ga.playerStats {
		if len(stats.Score) > 0 && stats.Score[0] > maxScore {
			maxScore = stats.Score[0]
		}
	}
	
	i := 0
	for _, stats := range ga.playerStats {
		if len(stats.Score) > 0 {
			// Нормализация данных
			normalizedScore := float64(stats.Score[0]) / float64(maxScore)
			
			// Рисование точки
			x := 50 + int(float64(w-100)*0.5)
			y := h - 50 - int(float64(h-100)*normalizedScore)
			
			// Рисование круга
			radius := 5
			for dx := -radius; dx <= radius; dx++ {
				for dy := -radius; dy <= radius; dy++ {
					if dx*dx+dy*dy <= radius*radius {
						img.Set(x+dx, y+dy, colors[i%len(colors)])
					}
				}
			}
			
			i++
		}
	}
	
	return img
}

// Экспорт анализа
func (ga *GameAnalyzer) exportAnalysis() {
	if ga.gameState == nil || len(ga.playerStats) == 0 {
		dialog.ShowInformation("Error", "No analysis data available", ga.window)
		return
	}
	
	// Создание диалога для выбора файла
	dialog.ShowFileSave(func(writer fyne.URIWriteCloser, err error) {
		if err != nil {
			dialog.ShowError(err, ga.window)
			return
		}
		
		if writer == nil {
			return
		}
		
		// Создание отчета
		report := "Game Analysis Report\n"
		report += "====================\n\n"
		report += fmt.Sprintf("Game Mode: %s\n", ga.gameState.GameMode)
		report += fmt.Sprintf("Game Duration: %.2f seconds\n", ga.gameState.Timer)
		report += fmt.Sprintf("Number of Players: %d\n\n", len(ga.gameState.Players))
		
		// Добавление статистики для каждого игрока
		for idStr, player := range ga.gameState.Players {
			id, _ := strconv.Atoi(idStr)
			stats := ga.playerStats[id]
			
			report += fmt.Sprintf("Player: %s (ID: %s)\n", player.Name, idStr)
			report += fmt.Sprintf("Score: %d\n", player.Score)
			
			if len(stats.TowerHeight) > 0 {
				report += fmt.Sprintf("Tower Height: %.2f\n", stats.TowerHeight[0])
			}
			
			if len(stats.TowerStability) > 0 {
				report += fmt.Sprintf("Tower Stability: %.2f\n", stats.TowerStability[0])
			}
			
			report += fmt.Sprintf("Blocks Placed: %d\n", stats.BlocksPlaced)
			report += fmt.Sprintf("Spells Used: %d\n", stats.SpellsUsed)
			report += fmt.Sprintf("Time Alive: %.2f seconds\n\n", stats.TimeAlive)
		}
		
		// Запись отчета в файл
		_, err = writer.Write([]byte(report))
		if err != nil {
			dialog.ShowError(err, ga.window)
			return
		}
		
		writer.Close()
		
		dialog.ShowInformation("Success", "Analysis exported successfully", ga.window)
	}, ga.window)
}

// Открытие редактора настроек
func (dt *DevTools) openSettingsEditor() {
	if dt.settingsEditor == nil {
		w := dt.app.NewWindow("Settings Editor")
		
		dt.settingsEditor = &SettingsEditor{
			window:   w,
			settings: &GameSettings{
				DefaultGameMode: GameModeRace,
				GravityScale:    1.0,
				SpellFrequency:  0.5,
				AIEnabled:       true,
				AILevel:         2,
			},
		}
		
		dt.settingsEditor.setupUI()
	}
	
	dt.settingsEditor.window.Show()
}

// Настройка UI для редактора настроек
func (se *SettingsEditor) setupUI() {
	// Создание выпадающего списка для режима игры
	gameModeSelect := widget.NewSelect([]string{"RACE", "SURVIVAL", "PUZZLE"}, func(value string) {
		se.settings.DefaultGameMode = GameMode(value)
	})
	gameModeSelect.SetSelected(string(se.settings.DefaultGameMode))
	
	// Создание слайдера для гравитации
	gravitySlider := widget.NewSlider(0.1, 2.0)
	gravitySlider.Value = se.settings.GravityScale
	gravitySlider.OnChanged = func(value float64) {
		se.settings.GravityScale = value
	}
	
	// Создание слайдера для частоты заклинаний
	spellSlider := widget.NewSlider(0.0, 1.0)
	spellSlider.Value = se.settings.SpellFrequency
	spellSlider.OnChanged = func(value float64) {
		se.settings.SpellFrequency = value
	}
	
	// Создание чекбокса для включения ИИ
	aiCheck := widget.NewCheck("", func(value bool) {
		se.settings.AIEnabled = value
	})
	aiCheck.Checked = se.settings.AIEnabled
	
	// Создание слайдера для уровня ИИ
	aiLevelSlider := widget.NewSlider(1, 5)
	aiLevelSlider.Value = float64(se.settings.AILevel)
	aiLevelSlider.OnChanged = func(value float64) {
		se.settings.AILevel = int(value)
	}
	
	// Создание формы с настройками
	se.form = widget.NewForm(
		widget.NewFormItem("Default Game Mode", gameModeSelect),
		widget.NewFormItem("Gravity Scale", gravitySlider),
		widget.NewFormItem("Spell Frequency", spellSlider),
		widget.NewFormItem("AI Enabled", aiCheck),
		widget.NewFormItem("AI Level", aiLevelSlider),
	)
	
	// Кнопки для управления настройками
	saveBtn := widget.NewButton("Save Settings", func() {
		se.saveSettings()
	})
	
	loadBtn := widget.NewButton("Load Settings", func() {
		se.loadSettings()
	})
	
	resetBtn := widget.NewButton("Reset to Defaults", func() {
		se.resetSettings()
	})
	
	// Создание контейнера с кнопками
	buttonContainer := container.NewHBox(
		saveBtn,
		loadBtn,
		resetBtn,
	)
	
	// Создание основного контейнера
	content := container.NewVBox(
		se.form,
		buttonContainer,
	)
	
	se.window.SetContent(content)
	se.window.Resize(fyne.NewSize(400, 300))
}

// Сохранение настроек
func (se *SettingsEditor) saveSettings() {
	// Создание диалога для выбора файла
	dialog.ShowFileSave(func(writer fyne.URIWriteCloser, err error) {
		if err != nil {
			dialog.ShowError(err, se.window)
			return
		}
		
		if writer == nil {
			return
		}
		
		// Сериализация настроек в JSON
		data, err := json.MarshalIndent(se.settings, "", "  ")
		if err != nil {
			dialog.ShowError(err, se.window)
			return
		}
		
		// Запись данных в файл
		_, err = writer.Write(data)
		if err != nil {
			dialog.ShowError(err, se.window)
			return
		}
		
		writer.Close()
		
		dialog.ShowInformation("Success", "Settings saved successfully", se.window)
	}, se.window)
}

// Загрузка настроек
func (se *SettingsEditor) loadSettings() {
	// Создание диалога для выбора файла
	dialog.ShowFileOpen(func(reader fyne.URIReadCloser, err error) {
		if err != nil {
			dialog.ShowError(err, se.window)
			return
		}
		
		if reader == nil {
			return
		}
		
		// Чтение данных из файла
		data, err := ioutil.ReadAll(reader)
		if err != nil {
			dialog.ShowError(err, se.window)
			return
		}
		
		reader.Close()
		
		// Десериализация настроек из JSON
		var settings GameSettings
		err = json.Unmarshal(data, &settings)
		if err != nil {
			dialog.ShowError(err, se.window)
			return
		}
		
		// Обновление текущих настроек
		se.settings = &settings
		
		// Обновление UI
		se.setupUI()
		
		dialog.ShowInformation("Success", "Settings loaded successfully", se.window)
	}, se.window)
}

// Сброс настроек
func (se *SettingsEditor) resetSettings() {
	// Сброс настроек к значениям по умолчанию
	se.settings = &GameSettings{
		DefaultGameMode: GameModeRace,
		GravityScale:    1.0,
		SpellFrequency:  0.5,
		AIEnabled:       true,
		AILevel:         2,
	}
	
	// Обновление UI
	se.setupUI()
	
	dialog.ShowInformation("Success", "Settings reset to defaults", se.window)
}

// Открытие менеджера ассетов
func (dt *DevTools) openAssetManager() {
	if dt.assetManager == nil {
		w := dt.app.NewWindow("Asset Manager")
		
		dt.assetManager = &AssetManager{
			window:    w,
			assetPath: "./assets",
		}
		
		dt.assetManager.setupUI()
	}
	
	dt.assetManager.window.Show()
}

// Настройка UI для менеджера ассетов
func (am *AssetManager) setupUI() {
	// Создание списка ассетов
	am.assetList = widget.NewList(
		func() int {
			return len(am.getAssetFiles())
		},
		func() fyne.CanvasObject {
			return widget.NewLabel("Template")
		},
		func(id widget.ListItemID, obj fyne.CanvasObject) {
			files := am.getAssetFiles()
			if id < len(files) {
				obj.(*widget.Label).SetText(files[id])
			}
		},
	)
	
	// Обработка выбора ассета
	am.assetList.OnSelected = func(id widget.ListItemID) {
		files := am.getAssetFiles()
		if id < len(files) {
			am.loadAssetPreview(files[id])
		}
	}
	
	// Создание предпросмотра ассета
	am.assetPreview = canvas.NewImageFromFile("")
	am.assetPreview.FillMode = canvas.ImageFillContain
	
	// Кнопки для управления ассетами
	importBtn := widget.NewButton("Import Asset", func() {
		am.importAsset()
	})
	
	exportBtn := widget.NewButton("Export Asset", func() {
		am.exportAsset()
	})
	
	deleteBtn := widget.NewButton("Delete Asset", func() {
		am.deleteAsset()
	})
	
	// Создание контейнера с кнопками
	buttonContainer := container.NewHBox(
		importBtn,
		exportBtn,
		deleteBtn,
	)
	
	// Создание контейнера с списком и предпросмотром
	splitContainer := container.NewHSplit(
		am.assetList,
		am.assetPreview,
	)
	
	// Создание основного контейнера
	content := container.NewBorder(
		nil,
		buttonContainer,
		nil,
		nil,
		splitContainer,
	)
	
	am.window.SetContent(content)
	am.window.Resize(fyne.NewSize(800, 600))
}

// Получение списка файлов ассетов
func (am *AssetManager) getAssetFiles() []string {
	// Создание директории ассетов, если она не существует
	if _, err := os.Stat(am.assetPath); os.IsNotExist(err) {
		os.MkdirAll(am.assetPath, 0755)
	}
	
	// Чтение файлов из директории
	files, err := ioutil.ReadDir(am.assetPath)
	if err != nil {
		return []string{}
	}
	
	// Фильтрация файлов
	var assetFiles []string
	for _, file := range files {
		if !file.IsDir() {
			assetFiles = append(assetFiles, file.Name())
		}
	}
	
	return assetFiles
}

// Загрузка предпросмотра ассета
func (am *AssetManager) loadAssetPreview(filename string) {
	// Полный путь к файлу
	filePath := filepath.Join(am.assetPath, filename)
	
	// Проверка расширения файла
	ext := strings.ToLower(filepath.Ext(filename))
	
	// Загрузка изображения для предпросмотра
	if ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".gif" {
		am.assetPreview.File = filePath
		am.assetPreview.Refresh()
	} else {
		// Для неизображений показываем заглушку
		am.assetPreview.File = ""
		am.assetPreview.Refresh()
	}
}

// Импорт ассета
func (am *AssetManager) importAsset() {
	// Создание диалога для выбора файла
	dialog.ShowFileOpen(func(reader fyne.URIReadCloser, err error) {
		if err != nil {
			dialog.ShowError(err, am.window)
			return
		}
		
		if reader == nil {
			return
		}
		
		// Получение имени файла
		filename := filepath.Base(reader.URI().String())
		
		// Создание директории ассетов, если она не существует
		if _, err := os.Stat(am.assetPath); os.IsNotExist(err) {
			os.MkdirAll(am.assetPath, 0755)
		}
		
		// Создание файла для записи
		file, err := os.Create(filepath.Join(am.assetPath, filename))
		if err != nil {
			dialog.ShowError(err, am.window)
			return
		}
		
		// Чтение данных из исходного файла
		data, err := ioutil.ReadAll(reader)
		if err != nil {
			dialog.ShowError(err, am.window)
			return
		}
		
		reader.Close()
		
		// Запись данных в новый файл
		_, err = file.Write(data)
		if err != nil {
			dialog.ShowError(err, am.window)
			return
		}
		
		file.Close()
		
		// Обновление списка ассетов
		am.assetList.Refresh()
		
		dialog.ShowInformation("Success", "Asset imported successfully", am.window)
	}, am.window)
}

// Экспорт ассета
func (am *AssetManager) exportAsset() {
	// Получение выбранного ассета
	if am.assetList.Selected() < 0 {
		dialog.ShowInformation("Error", "No asset selected", am.window)
		return
	}
	
	files := am.getAssetFiles()
	if am.assetList.Selected() >= len(files) {
		dialog.ShowInformation("Error", "Invalid asset selected", am.window)
		return
	}
	
	filename := files[am.assetList.Selected()]
	
	// Создание диалога для выбора файла
	dialog.ShowFileSave(func(writer fyne.URIWriteCloser, err error) {
		if err != nil {
			dialog.ShowError(err, am.window)
			return
		}
		
		if writer == nil {
			return
		}
		
		// Чтение данных из исходного файла
		data, err := ioutil.ReadFile(filepath.Join(am.assetPath, filename))
		if err != nil {
			dialog.ShowError(err, am.window)
			return
		}
		
		// Запись данных в новый файл
		_, err = writer.Write(data)
		if err != nil {
			dialog.ShowError(err, am.window)
			return
		}
		
		writer.Close()
		
		dialog.ShowInformation("Success", "Asset exported successfully", am.window)
	}, am.window)
}

// Удаление ассета
func (am *AssetManager) deleteAsset() {
	// Получение выбранного ассета
	if am.assetList.Selected() < 0 {
		dialog.ShowInformation("Error", "No asset selected", am.window)
		return
	}
	
	files := am.getAssetFiles()
	if am.assetList.Selected() >= len(files) {
		dialog.ShowInformation("Error", "Invalid asset selected", am.window)
		return
	}
	
	filename := files[am.assetList.Selected()]
	
	// Подтверждение удаления
	dialog.ShowConfirm("Confirm Delete", "Are you sure you want to delete this asset?", func(confirmed bool) {
		if confirmed {
			// Удаление файла
			err := os.Remove(filepath.Join(am.assetPath, filename))
			if err != nil {
				dialog.ShowError(err, am.window)
				return
			}
			
			// Обновление списка ассетов
			am.assetList.Refresh()
			
			// Очистка предпросмотра
			am.assetPreview.File = ""
			am.assetPreview.Refresh()
			
			dialog.ShowInformation("Success", "Asset deleted successfully", am.window)
		}
	}, am.window)
}

// Запуск инструментов разработки
func main() {
	dt := NewDevTools()
	dt.mainWindow.ShowAndRun()
}
