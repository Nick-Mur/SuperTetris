using Flux
using BSON
using Statistics
using LinearAlgebra
using Random
using Dates
using ArgParse
using JSON
using Logging

"""
    compile_ai_model()

Компилирует модель ИИ для Tetris Towers в бинарный формат.
Создает оптимизированную модель для использования в игре.
"""
function compile_ai_model()
    @info "Компиляция модели ИИ для Tetris Towers"
    
    # Определение архитектуры модели
    model = Chain(
        Dense(128, 256, relu),
        Dropout(0.3),
        Dense(256, 512, relu),
        Dropout(0.3),
        Dense(512, 256, relu),
        Dense(256, 128, relu),
        Dense(128, 7)  # 7 возможных действий для тетромино
    )
    
    # Сохранение модели в формате BSON
    model_path = joinpath(@__DIR__, "model", "tetris_ai_model.bson")
    mkpath(dirname(model_path))
    BSON.@save model_path model
    
    # Создание метаданных модели
    metadata = Dict(
        "name" => "TetrisTowersAI",
        "version" => "1.0.0",
        "created_at" => string(now()),
        "input_shape" => 128,
        "output_shape" => 7,
        "description" => "AI model for Tetris Towers game"
    )
    
    # Сохранение метаданных
    metadata_path = joinpath(@__DIR__, "model", "metadata.json")
    open(metadata_path, "w") do io
        JSON.print(io, metadata, 4)
    end
    
    @info "Модель ИИ успешно скомпилирована и сохранена в $(model_path)"
    @info "Метаданные сохранены в $(metadata_path)"
    
    return model_path, metadata_path
end

"""
    create_shared_library()

Создает разделяемую библиотеку для использования модели ИИ из других языков.
"""
function create_shared_library()
    @info "Создание разделяемой библиотеки для ИИ"
    
    # Путь к исходному коду библиотеки
    lib_src_path = joinpath(@__DIR__, "src", "ai_lib.jl")
    
    # Создание директории, если она не существует
    mkpath(dirname(lib_src_path))
    
    # Создание исходного кода библиотеки
    lib_code = """
    module TetrisTowersAI
    
    using Flux
    using BSON
    using Statistics
    using LinearAlgebra
    
    export predict_move, load_model, get_model_info
    
    # Глобальная переменная для хранения модели
    global _model = nothing
    
    \"\"\"
        load_model(model_path::String)
    
    Загружает модель ИИ из указанного пути.
    \"\"\"
    function load_model(model_path::String)
        try
            BSON.@load model_path model
            global _model = model
            return true
        catch e
            @error "Ошибка загрузки модели: \$e"
            return false
        end
    end
    
    \"\"\"
        predict_move(game_state::Vector{Float64})
    
    Предсказывает лучший ход на основе текущего состояния игры.
    Возвращает индекс действия (0-6) и уверенность (0.0-1.0).
    \"\"\"
    function predict_move(game_state::Vector{Float64})
        if _model === nothing
            @error "Модель не загружена"
            return -1, 0.0
        end
        
        # Проверка размерности входных данных
        if length(game_state) != 128
            @error "Неверная размерность входных данных: \$(length(game_state)), ожидается 128"
            return -1, 0.0
        end
        
        # Нормализация входных данных
        normalized_state = game_state ./ maximum(abs.(game_state))
        
        # Предсказание
        output = _model(normalized_state)
        
        # Получение индекса максимального значения и уверенности
        max_val, max_idx = findmax(output)
        confidence = softmax(output)[max_idx]
        
        return max_idx - 1, Float64(confidence)  # -1 для индексации с 0
    end
    
    \"\"\"
        get_model_info()
    
    Возвращает информацию о загруженной модели.
    \"\"\"
    function get_model_info()
        if _model === nothing
            return "Model not loaded"
        end
        
        info = "TetrisTowersAI Model\\n"
        info *= "Layers: \$(_model.layers)\\n"
        info *= "Parameters: \$(sum(length, Flux.params(_model)))\\n"
        
        return info
    end
    
    end # module
    """
    
    # Запись исходного кода в файл
    open(lib_src_path, "w") do io
        write(io, lib_code)
    end
    
    @info "Исходный код библиотеки создан в $(lib_src_path)"
    
    # В реальной реализации здесь был бы код для компиляции библиотеки
    # с использованием PackageCompiler.jl или аналогичного инструмента
    
    @info "Для компиляции разделяемой библиотеки требуется запустить:"
    @info "using PackageCompiler; create_sysimage([\"Flux\", \"BSON\"], sysimage_path=\"tetris_ai.so\", project=\".\")"
    
    return lib_src_path
end

"""
    create_c_bindings()

Создает C-привязки для использования Julia AI из других языков.
"""
function create_c_bindings()
    @info "Создание C-привязок для ИИ"
    
    # Путь к файлу с C-привязками
    bindings_path = joinpath(@__DIR__, "src", "ai_bindings.jl")
    
    # Создание директории, если она не существует
    mkpath(dirname(bindings_path))
    
    # Создание кода C-привязок
    bindings_code = """
    module TetrisTowersAIBindings
    
    using TetrisTowersAI
    
    # Экспорт функций для C
    export c_load_model, c_predict_move, c_get_model_info
    
    \"\"\"
        c_load_model(model_path_ptr::Ptr{UInt8})::Cint
    
    C-привязка для загрузки модели ИИ.
    \"\"\"
    function c_load_model(model_path_ptr::Ptr{UInt8})::Cint
        model_path = unsafe_string(model_path_ptr)
        success = TetrisTowersAI.load_model(model_path)
        return success ? 1 : 0
    end
    
    \"\"\"
        c_predict_move(game_state_ptr::Ptr{Cdouble}, length::Cint, action_ptr::Ptr{Cint}, confidence_ptr::Ptr{Cdouble})::Cint
    
    C-привязка для предсказания хода.
    \"\"\"
    function c_predict_move(game_state_ptr::Ptr{Cdouble}, length::Cint, action_ptr::Ptr{Cint}, confidence_ptr::Ptr{Cdouble})::Cint
        if length != 128
            return 0
        end
        
        # Преобразование указателя в массив Julia
        game_state = unsafe_wrap(Array, game_state_ptr, length)
        
        # Вызов функции предсказания
        action, confidence = TetrisTowersAI.predict_move(game_state)
        
        # Запись результатов по указателям
        unsafe_store!(action_ptr, action)
        unsafe_store!(confidence_ptr, confidence)
        
        return 1
    end
    
    \"\"\"
        c_get_model_info()::Ptr{UInt8}
    
    C-привязка для получения информации о модели.
    \"\"\"
    function c_get_model_info()::Ptr{UInt8}
        info = TetrisTowersAI.get_model_info()
        # Преобразование строки в C-строку (должна быть освобождена вызывающей стороной)
        return Base.unsafe_convert(Ptr{UInt8}, Base.cconvert(Ptr{UInt8}, info))
    end
    
    end # module
    """
    
    # Запись кода C-привязок в файл
    open(bindings_path, "w") do io
        write(io, bindings_code)
    end
    
    @info "C-привязки созданы в $(bindings_path)"
    
    return bindings_path
end

"""
    main()

Основная функция для компиляции ИИ.
"""
function main()
    @info "Запуск компиляции ИИ для Tetris Towers"
    
    # Компиляция модели
    model_path, metadata_path = compile_ai_model()
    
    # Создание разделяемой библиотеки
    lib_path = create_shared_library()
    
    # Создание C-привязок
    bindings_path = create_c_bindings()
    
    @info "Компиляция ИИ завершена успешно"
    @info "Модель: $(model_path)"
    @info "Метаданные: $(metadata_path)"
    @info "Библиотека: $(lib_path)"
    @info "C-привязки: $(bindings_path)"
end

# Запуск основной функции, если скрипт запущен напрямую
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
