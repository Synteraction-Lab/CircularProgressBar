"# ARProgressBar" 


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

## Versions

### pilot1.7_eye_contact
- enable eye-cursor

### pilot1.7_conversation
- enable eye-tracking

### pilot1.5_conversation
- change sizes of linear bar to fit for the requirements

### pilot1.5
- add support for v1.5
- change update frequency to 3 seconds
- add text element to show progress (on top of head)

### pilot1.1
- add support for v1.1
- linear bar is shown in top of the circle bar

### pilot1
- initial pilot, v1
- linear bar is shown in between top and center of circle bar
