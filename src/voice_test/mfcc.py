# extract_mfcc_only.py

import librosa
import numpy as np
import os

# ================= CONFIG =================
SR = 16000
N_MFCC = 40
MAX_LEN = 300

# ================= EXTRACT MFCC =================
def extract_mfcc(file_path):
    """Extract MFCC features from audio file"""
    print(f"Processing: {file_path}")
    
    # Load audio
    y, sr = librosa.load(file_path, sr=SR)
    print(f"✅ Audio loaded")
    print(f"   Duration: {len(y)/sr:.2f} seconds")
    print(f"   Sample rate: {sr} Hz")
    print(f"   Total samples: {len(y)}")
    
    # Extract MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    mfcc = mfcc.T  # Transpose to (time_frames, n_mfcc)
    
    print(f"\n✅ MFCC extracted")
    print(f"   Shape before padding: {mfcc.shape}")
    print(f"   (time_frames, n_mfcc_coefficients)")
    
    # Pad or trim to MAX_LEN
    if mfcc.shape[0] < MAX_LEN:
        pad_width = MAX_LEN - mfcc.shape[0]
        mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)), mode='constant')
        print(f"   Padded with {pad_width} zero frames")
    else:
        mfcc = mfcc[:MAX_LEN, :]
        print(f"   Trimmed to {MAX_LEN} frames")
    
    print(f"   Final shape: {mfcc.shape}")
    
    return mfcc

# ================= MAIN =================
if __name__ == "__main__":
    # Audio file path
    audio_file = os.path.join("uploads", "test_audio.wav")
    
    print("\n" + "="*60)
    print("MFCC FEATURE EXTRACTION")
    print("="*60 + "\n")
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        print(f"Current directory: {os.getcwd()}")
        
        uploads_dir = os.path.join("src", "uploads")
        if os.path.exists(uploads_dir):
            wav_files = [f for f in os.listdir(uploads_dir) if f.endswith('.wav')]
            if wav_files:
                print(f"\nFound WAV files:")
                for f in wav_files:
                    print(f"  - {f}")
                audio_file = os.path.join(uploads_dir, wav_files[0])
                print(f"\nUsing: {audio_file}\n")
            else:
                print("No WAV files found")
                exit(1)
        else:
            print(f"❌ Directory not found: {uploads_dir}")
            exit(1)
    
    try:
        # Extract MFCC
        mfcc_features = extract_mfcc(audio_file)
        
        # Display MFCC statistics
        print("\n" + "="*60)
        print("MFCC FEATURES")
        print("="*60)
        print(f"Shape:           {mfcc_features.shape}")
        print(f"Data type:       {mfcc_features.dtype}")
        print(f"Min value:       {mfcc_features.min():.4f}")
        print(f"Max value:       {mfcc_features.max():.4f}")
        print(f"Mean value:      {mfcc_features.mean():.4f}")
        print(f"Std deviation:   {mfcc_features.std():.4f}")
        
        # Show first few frames and coefficients
        print("\n" + "-"*60)
        print("SAMPLE DATA (First 5 frames, First 10 coefficients)")
        print("-"*60)
        print(mfcc_features[:5, :10])
        
        # Save to file (optional)
        save_option = input("\n💾 Save MFCC to file? (y/n): ").lower()
        if save_option == 'y':
            output_file = "mfcc_features.npy"
            np.save(output_file, mfcc_features)
            print(f"✅ Saved to: {output_file}")
            print(f"   Load with: mfcc = np.load('{output_file}')")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()