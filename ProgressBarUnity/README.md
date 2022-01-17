# ProgressBarUnity
Show progress notifications on OHMDs (HoloLens2) during social interactions. This has the UI implementation using Unity.


## Contact person
- [Nuwan Janaka](https://www.nus-hci.org/team/nuwan-janaka/) ([In](https://www.linkedin.com/in/nuwan-janaka/))

## Project links
- See [architecture](https://docs.google.com/presentation/d/1PM6vqneAFQTyWqf7iwJGsualcYMQ_Krg9VtM4reVdrM/edit?usp=sharing)
- See [code introduction](https://drive.google.com/drive/folders/1ROBhivaV54AYaH4TrRMI-pO6aQM5NOys)
- [Project](https://drive.google.com/drive/folders/1T4qx_t7rxK0jX1LsGDBQuSTUcwmA7dpL)


## Installation
- create a `progress_config.json` file inside `Videos/ProgressApp` directory in HoloLens
- add the server address to the `progress_config.json` as follows
	- ```javascript
		{
			"server":"http://<IP_ADDRESS>:8080/data"
		}
	  ```
- NOTE: both the device (e.g., HoloLens2) and server computer should be connected via a PRIVATE network (e.g., phone hotspot)

## Eye-tracking recordings
- recorded data will be available in `Music/PROGRESS_DATA/<participant_id>` directory

## Face-tracking
- use [Windows.Media.FaceAnalysis](https://docs.microsoft.com/en-us/uwp/api/windows.media.faceanalysis) to track faces
- adjust the face size of conversation partner at [FaceTrackingController.cs#calculateFaceCenter](Assets/ProgressScripts/FaceTrackingController.cs)


