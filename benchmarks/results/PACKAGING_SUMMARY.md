# Benchmark packaging results (2026-08-06)

Profile: `balanced`, transcript: off (packaging/bandwidth only).

## DeepSeek API status

Provider calls returned **HTTP 402 Insufficient Balance** for all 14 videos.
Key authenticates, but the DeepSeek account needs credits before Q&A evals can run.

## Compression table

| Source | Clip | Original MB | LVP KB | Ratio | Keyframes | Pack ms |
|--------|------|-------------|--------|-------|-----------|---------|
| uploads | `1_Minute_Outdoor_ASMR_No_dogs_no_roosters_no_cars_Peaceful.mp4` | 3.82 | 281.2 | **13.26×** | 13 | 1657.6 |
| uploads | `1_minute_funny_videos.mp4` | 2.31 | 140.7 | **16.06×** | 16 | 1047.8 |
| uploads | `A_one_minute_TEDx_Talk_for_the_digital_age_Woody_Roseland_TEDxMileHigh.mp4` | 2.63 | 102.9 | **24.97×** | 16 | 1042.3 |
| uploads | `test_audio_video.mp4` | 0.75 | 11.5 | **63.79×** | 1 | 210.2 |
| uploads | `test_video_longer.mp4` | 8.71 | 45.0 | **188.93×** | 8 | 818.3 |
| open_samples | `filesample_sample_960x400.mp4` | 17.52 | 258.2 | **66.27×** | 16 | 1220.2 |
| open_samples | `intel_face_demographics.mp4` | 9.41 | 63.7 | **144.19×** | 18 | 1150.5 |
| open_samples | `intel_person_detection.mp4` | 6.03 | 33.8 | **174.1×** | 10 | 701.5 |
| open_samples | `learningcontainer_small.mp4` | 10.55 | 289.1 | **35.63×** | 34 | 2001.1 |
| open_samples | `samplelib_10s.mp4` | 5.49 | 88.1 | **60.79×** | 2 | 632.5 |
| open_samples | `samplelib_20s.mp4` | 11.82 | 178.8 | **64.52×** | 4 | 1102.3 |
| open_samples | `samplelib_5s.mp4` | 2.85 | 48.4 | **57.43×** | 1 | 360.9 |
| open_samples | `test_videos_bunny.mp4` | 0.99 | 54.9 | **17.64×** | 2 | 313.5 |
| open_samples | `w3c_test_fragment.mp4` | 1.13 | 9.6 | **114.45×** | 1 | 201.8 |

**n=14** · avg **74.43×** · range **13.26–188.93×**

Raw JSON: [`batch_packaging_deepseek.json`](batch_packaging_deepseek.json)

## Next steps for solid LLM quality data

1. Top up DeepSeek balance (or use OpenAI/Gemini/Claude keys)
2. Re-run: `export DEEPSEEK_API_KEY=... && python benchmarks/run_batch_evals.py --providers deepseek --max-questions 4`
3. Optionally enable transcripts for speech clips (TEDx / learningcontainer)
