use rand::{Rng, thread_rng};
use rand::distributions::{Distribution, Standard, Uniform};

pub fn random_int(min: i32, max: i32) -> i32 {
    let mut rng = thread_rng();
    rng.gen_range(min..=max)
}

pub fn random_float(min: f32, max: f32) -> f32 {
    let mut rng = thread_rng();
    rng.gen_range(min..=max)
}

pub fn random_bool() -> bool {
    let mut rng = thread_rng();
    rng.gen_bool(0.5)
}

pub fn random_element<T: Clone>(items: &[T]) -> Option<T> {
    if items.is_empty() {
        None
    } else {
        let mut rng = thread_rng();
        let index = rng.gen_range(0..items.len());
        Some(items[index].clone())
    }
} 