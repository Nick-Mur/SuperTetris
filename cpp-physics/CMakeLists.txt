cmake_minimum_required(VERSION 3.10)
project(TetrisTowersPhysics)

# Установка стандарта C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Опции сборки
option(BUILD_SHARED_LIBS "Build shared libraries" ON)
option(BUILD_TESTS "Build tests" ON)

# Включаем поддержку экспорта компиляционной базы данных для инструментов
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Флаги компиляции
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -pedantic)
endif()

# Исходные файлы
set(SOURCES
    PhysicsEngine.cpp
)

# Заголовочные файлы
set(HEADERS
    include/PhysicsEngine.h
)

# Создание библиотеки
add_library(physics_engine ${SOURCES} ${HEADERS})
target_include_directories(physics_engine PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Создание исполняемого файла для тестирования
add_executable(physics_engine_test main.cpp)
target_link_libraries(physics_engine_test physics_engine)

# Установка
install(TARGETS physics_engine
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)
install(FILES ${HEADERS} DESTINATION include)

# Экспорт целей
export(TARGETS physics_engine FILE physics_engine-config.cmake)
