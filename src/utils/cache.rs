use std::collections::HashMap;
use std::time::{Duration, Instant};
use std::sync::{Arc, Mutex};

pub struct CacheEntry<T> {
    value: T,
    expires_at: Option<Instant>,
}

pub struct Cache<T> {
    entries: Arc<Mutex<HashMap<String, CacheEntry<T>>>>,
}

impl<T: Clone> Cache<T> {
    pub fn new() -> Self {
        Self {
            entries: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn set(&self, key: &str, value: T, ttl: Option<Duration>) {
        let expires_at = ttl.map(|duration| Instant::now() + duration);
        let entry = CacheEntry {
            value,
            expires_at,
        };
        let mut entries = self.entries.lock().unwrap();
        entries.insert(key.to_string(), entry);
    }

    pub fn get(&self, key: &str) -> Option<T> {
        let mut entries = self.entries.lock().unwrap();
        if let Some(entry) = entries.get(key) {
            if let Some(expires_at) = entry.expires_at {
                if Instant::now() > expires_at {
                    entries.remove(key);
                    return None;
                }
            }
            Some(entry.value.clone())
        } else {
            None
        }
    }

    pub fn remove(&self, key: &str) {
        let mut entries = self.entries.lock().unwrap();
        entries.remove(key);
    }

    pub fn clear(&self) {
        let mut entries = self.entries.lock().unwrap();
        entries.clear();
    }
} 