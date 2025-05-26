use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use anyhow::{Result, Context};

/// Чтение содержимого файла в строку
pub fn read_file_to_string(path: &Path) -> Result<String> {
    fs::read_to_string(path)
        .context(format!("Failed to read file: {}", path.display()))
}

/// Запись строки в файл
pub fn write_string_to_file(path: &Path, content: &str) -> Result<()> {
    fs::write(path, content)
        .context(format!("Failed to write file: {}", path.display()))
}

/// Создание директории и всех родительских директорий
pub fn create_dir_all(path: &Path) -> Result<()> {
    fs::create_dir_all(path)
        .context(format!("Failed to create directory: {}", path.display()))
}

/// Проверка существования файла
pub fn file_exists(path: &Path) -> bool {
    path.exists()
}

/// Получение размера файла
pub fn get_file_size(path: &Path) -> Result<u64> {
    fs::metadata(path)
        .context(format!("Failed to get file metadata: {}", path.display()))
        .map(|metadata| metadata.len())
}

/// Копирование файла
pub fn copy_file(src: &Path, dst: &Path) -> Result<()> {
    fs::copy(src, dst)
        .context(format!("Failed to copy file from {} to {}", src.display(), dst.display()))?;
    Ok(())
}

/// Перемещение файла
pub fn move_file(src: &Path, dst: &Path) -> Result<()> {
    fs::rename(src, dst)
        .context(format!("Failed to move file from {} to {}", src.display(), dst.display()))?;
    Ok(())
}

/// Удаление файла
pub fn remove_file(path: &Path) -> Result<()> {
    fs::remove_file(path)
        .context(format!("Failed to remove file: {}", path.display()))?;
    Ok(())
}

/// Получение расширения файла
pub fn get_file_extension(path: &Path) -> Option<&str> {
    path.extension()?.to_str()
}

/// Получение имени файла без расширения
pub fn get_file_stem(path: &Path) -> Option<&str> {
    path.file_stem()?.to_str()
}

/// Получение абсолютного пути
pub fn get_absolute_path(path: &Path) -> Result<PathBuf> {
    path.canonicalize()
        .context(format!("Failed to get absolute path: {}", path.display()))
} 