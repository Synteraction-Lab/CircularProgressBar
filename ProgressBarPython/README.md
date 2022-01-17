# ProgressBarPython
Show progress notifications on OHMDs (HoloLens2) during social interactions. This has the notification triggering implementation using Python.


## Contact person
- [Nuwan Janaka](https://www.nus-hci.org/team/nuwan-janaka/) ([In](https://www.linkedin.com/in/nuwan-janaka/))

## Project links
- See [architecture](https://docs.google.com/presentation/d/1PM6vqneAFQTyWqf7iwJGsualcYMQ_Krg9VtM4reVdrM/edit?usp=sharing)
- See [code introduction](https://drive.google.com/drive/folders/1ROBhivaV54AYaH4TrRMI-pO6aQM5NOys)
- [Project](https://drive.google.com/drive/folders/1T4qx_t7rxK0jX1LsGDBQuSTUcwmA7dpL)

## Installation
- make sure python3 is installed
- install [flask ](https://pypi.org/project/Flask/)
- install [pynput](https://pypi.org/project/pynput/)

### HoloLens app
- install the corresponding mixed reality app in [ProgressBarUnity](https://github.com/NUS-HCILab/ProgressBarUnity)

## Logs
- all data will be logged to `data/<participant_id>`
- if you need to redo a same condition, change the name of the log file (`<participant_id>_<session_id>progress.csv`)


## Run the application (sever)
- connect the computer (server that runs this code) and HoloLens to the same PRIVATE network (e.g., your phone's hotspot)
- identify the IP address of the computer/server
- configure the HoloLens to support the IP address of the computer/server (see https://github.com/janakanuwan/ProgressBarUnity)
- to set the HoloLens app to initial state run `python trigger_sample.py` (it will auto-exit after 6 seconds)
- run the `python trigger_progress.py` and input the <participant_id> (default: p0) and <session_id> (default: 0) when prompts
- see the configurations at [participant_config.py](participant_config.py)

## See the content of HoloLens
- connect the HoloLens via Device Portal (USB or Web, see [Windows Device Portal overview](https://docs.microsoft.com/en-us/windows/uwp/debug-test-perf/device-portal))
- use *Mixed Reality Capture* window to see the content (disable audio and set the Preview to lowest bandwidth)



