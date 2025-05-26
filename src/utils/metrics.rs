use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

pub struct Metric {
    count: u64,
    total: f64,
    min: f64,
    max: f64,
    last_update: Instant,
}

impl Metric {
    pub fn new() -> Self {
        Self {
            count: 0,
            total: 0.0,
            min: f64::MAX,
            max: f64::MIN,
            last_update: Instant::now(),
        }
    }

    pub fn record(&mut self, value: f64) {
        self.count += 1;
        self.total += value;
        self.min = self.min.min(value);
        self.max = self.max.max(value);
        self.last_update = Instant::now();
    }

    pub fn average(&self) -> f64 {
        if self.count == 0 {
            0.0
        } else {
            self.total / self.count as f64
        }
    }

    pub fn count(&self) -> u64 {
        self.count
    }

    pub fn min(&self) -> f64 {
        if self.count == 0 {
            0.0
        } else {
            self.min
        }
    }

    pub fn max(&self) -> f64 {
        if self.count == 0 {
            0.0
        } else {
            self.max
        }
    }

    pub fn last_update(&self) -> Instant {
        self.last_update
    }
}

pub struct Metrics {
    metrics: Arc<Mutex<HashMap<String, Metric>>>,
}

impl Metrics {
    pub fn new() -> Self {
        Self {
            metrics: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn record(&self, name: &str, value: f64) {
        let mut metrics = self.metrics.lock().unwrap();
        let metric = metrics.entry(name.to_string()).or_insert_with(Metric::new);
        metric.record(value);
    }

    pub fn get_metric(&self, name: &str) -> Option<Metric> {
        let metrics = self.metrics.lock().unwrap();
        metrics.get(name).cloned()
    }

    pub fn get_all_metrics(&self) -> HashMap<String, Metric> {
        let metrics = self.metrics.lock().unwrap();
        metrics.clone()
    }
} 