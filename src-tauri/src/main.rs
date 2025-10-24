// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;

// Tauri commands that will be called from frontend
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to the CRM Meeting App.", name)
}

#[tauri::command]
async fn start_recording(device_index: Option<u32>) -> Result<String, String> {
    // TODO: Integrate with Python audio service
    // For now, return a placeholder
    Ok(format!("Recording started on device {:?}", device_index))
}

#[tauri::command]
async fn stop_recording() -> Result<String, String> {
    // TODO: Integrate with Python audio service
    // For now, return a placeholder path
    Ok("/path/to/recording.wav".to_string())
}

#[tauri::command]
async fn get_audio_devices() -> Result<Vec<String>, String> {
    // TODO: Integrate with Python audio service
    Ok(vec![
        "Default Microphone".to_string(),
        "System Audio".to_string(),
    ])
}

#[tauri::command]
async fn transcribe_audio(audio_path: String) -> Result<String, String> {
    // TODO: Integrate with Python transcription service
    Ok(format!("Transcription of {}", audio_path))
}

#[tauri::command]
async fn summarize_transcription(transcription: String) -> Result<String, String> {
    // TODO: Integrate with Python summarization agent
    Ok(format!("Summary of: {}", transcription))
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|_app| {
            // Auto-start embedded Python backend
            // In development, use current directory; in production, use resource directory
            let app_dir = std::env::current_dir().expect("Failed to get current directory");
            let backend_path = app_dir.join("src-tauri/python/backend.py");

            // Start Python backend in background
            if backend_path.exists() {
                println!("Starting Python backend at {:?}", backend_path);
                Command::new("python3")
                    .args(["-u", backend_path.to_str().unwrap()])
                    .spawn()
                    .expect("Failed to start Python backend");
            } else {
                println!("Backend not found at {:?}, assuming it's running separately", backend_path);
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            start_recording,
            stop_recording,
            get_audio_devices,
            transcribe_audio,
            summarize_transcription
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
