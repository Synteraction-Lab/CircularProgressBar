using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using System;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

#if WINDOWS_UWP
using Windows.Graphics.Imaging;
using Windows.Media;
using Windows.Media.Capture;
using Windows.Media.Capture.Frames;
using Windows.Media.FaceAnalysis;
using Windows.Media.MediaProperties;
using Windows.System.Threading;

using Windows.Perception.Spatial;
using Windows.Graphics.Holographic;
#endif


// ref: https://docs.microsoft.com/en-us/windows/uwp/audio-video-camera/process-media-frames-with-mediaframereader
// ref: https://docs.microsoft.com/en-us/azure/cognitive-services/face/concepts/face-detection
// ref: https://docs.microsoft.com/en-us/samples/microsoft/windows-universal-samples/basicfacetracking/
// ref: https://docs.microsoft.com/en-us/windows/uwp/audio-video-camera/detect-and-track-faces-in-an-image#track-faces-in-a-sequence-of-frames
// ref: https://docs.microsoft.com/en-us/windows/mixed-reality/develop/unity/locatable-camera-in-unity



public class FaceTrackingController : MonoBehaviour
{
    private const int FACE_TRACKING_RATE = 10;
    private const int FACE_TRACKING_START_GAP_MILLIS = 1000;
    private const float FACE_TRACKING_TIME_GAP_SECONDS = 1f / FACE_TRACKING_RATE;

    private const float DISTANCE_TO_FACE_Z = 1.6f;


    // Holds the current scenario state value.
    private ScenarioState currentState = ScenarioState.Idle;

    private volatile  float elapsedTimeFromLastFaceTracking = 0;

    public ProgressLoader progressLoader;

#if WINDOWS_UWP
    // References a FaceTracker instance.
    private FaceTracker faceTracker;
    // References a MediaCapture instance; is null when not in Streaming state.
    private MediaCapture mediaCapture;
    // Cache of properties from the current MediaCapture device which is used for capturing the preview frame.
    private VideoEncodingProperties videoProperties;

    private MediaFrameSource mediaFrameSource;
    private MediaFrameReader mediaFrameReader;
#endif

    // Start is called before the first frame update
    void Start()
    {
        elapsedTimeFromLastFaceTracking = 0;
        StartFaceTracker();
    }

    // Update is called once per frame
    void Update()
    {
        elapsedTimeFromLastFaceTracking += Time.deltaTime;

        updateFaceCenter();
        changeProgressBarCenter();
    }

    void OnApplicationQuit()
    {
        StopFaceTracker();
    }

    // Holds the faceCenter w.r.t. world
    private Vector2 currentFaceCenter = Vector2.zero;
    private Vector2 previousFaceCenter = Vector2.zero;

    public Vector2 GetFaceCenter()
    {
        return Vector2.zero + currentFaceCenter;
    }

    private void setFaceCenter(Vector2 newFaceCenter)
    {
        //Debug.Log($"Update face center: {newFaceCenter.x}, { newFaceCenter.y}");
        this.currentFaceCenter = newFaceCenter;
    }

    private volatile bool faceLocationChanged = false;

    private const float FILTER_PARAM_ALPHA = 0.6f;
    private Vector2 filterFace = Vector2.zero;

    private void changeProgressBarCenter()
    {
        if(currentFaceCenter != previousFaceCenter || faceLocationChanged)
        {
            Debug.Log("Update progress bar center");

            filterFace = FILTER_PARAM_ALPHA * currentFaceCenter + (1 - FILTER_PARAM_ALPHA) * filterFace;

            progressLoader.UpdateCenter(filterFace.x, filterFace.y);

            previousFaceCenter = currentFaceCenter;
            faceLocationChanged = false;
        }
    }

    // Holds the (normalized) faceCenter w.r.t. image
    private Vector2 currentNormalizedImageFaceCenter = Vector2.zero;

    private void setNormalizedImageFaceCenter(Vector2 newImageFaceCenter)
    {
        this.currentNormalizedImageFaceCenter = newImageFaceCenter;
    }

    private Vector3 worldCenter = Vector3.zero;
    
    private void updateFaceCenter()
    {
        if(faceLocationChanged)
        {
            try
            {
                var newCenter = Camera.main.ViewportToWorldPoint(new Vector3(currentNormalizedImageFaceCenter.x, currentNormalizedImageFaceCenter.y, DISTANCE_TO_FACE_Z));
                Debug.Log($"New center: {newCenter.x}, { newCenter.y}, { newCenter.z}");
                setFaceCenter(new Vector2(newCenter.x, newCenter.y));
            }
            catch (Exception ex)
            {
                Debug.Log("Error in calculating world coordinates: " + ex.ToString());
            }
        }
    }


    // Values for identifying and controlling scenario states.
    private enum ScenarioState
    {
        Idle,
        Streaming
    }

    public void StartFaceTracker()
    {
        Debug.Log("StartFaceTracker");
#if WINDOWS_UWP
        Task.Run(async () => {
            await Task.Delay(FACE_TRACKING_START_GAP_MILLIS);
            ChangeScenarioStateAsync(ScenarioState.Streaming);  
        });
#endif
    }

    public void StopFaceTracker()
    {
        Debug.Log("StopFaceTracker");
#if WINDOWS_UWP
        Task.Run(() => ChangeScenarioStateAsync(ScenarioState.Idle));
#endif
    }


#if WINDOWS_UWP

    // Manages the scenario's internal state. Invokes the internal methods and updates the UI according to the
    // passed in state value. Handles failures and resets the state if necessary.
    /// param "newState" = State to switch to
    private async Task ChangeScenarioStateAsync(ScenarioState newState)
    {
        switch (newState)
        {
            case ScenarioState.Idle:

                this.currentState = newState;
                await this.ShutdownWebcamAsync();

                break;

            case ScenarioState.Streaming:

                if (!await this.StartWebcamStreamingAsync())
                {
                    await this.ChangeScenarioStateAsync(ScenarioState.Idle);
                    break;
                }

                this.currentState = newState;
                break;
        }
    }

    
    // Creates the FaceTracker object which we will use for face detection and tracking.
    // Initializes a new MediaCapture instance and starts the Preview streaming to the CamPreview UI element.
    // Returns Async Task object returning true if initialization and streaming were successful and false if an exception occurred.
    private async Task<bool> StartWebcamStreamingAsync()
    {
        Debug.Log("StartWebcamStreamingAsync");

        bool successful = false;

        var frameSourceGroups = await MediaFrameSourceGroup.FindAllAsync();

        // select the source with color camera
        MediaFrameSourceGroup selectedGroup = null;
        MediaFrameSourceInfo colorSourceInfo = null;
        foreach (var sourceGroup in frameSourceGroups)
        {
            foreach (var sourceInfo in sourceGroup.SourceInfos)
            {
                if (sourceInfo.MediaStreamType == MediaStreamType.VideoPreview
                    && sourceInfo.SourceKind == MediaFrameSourceKind.Color)
                {
                    colorSourceInfo = sourceInfo;
                    break;
                }
            }
            if (colorSourceInfo != null)
            {
                selectedGroup = sourceGroup;
                break;
            }
        }
        Debug.Log($"selectedGroup is null: {(selectedGroup == null)}, colorSourceInfo is null: {(colorSourceInfo == null)}");

        try
        {
            faceTracker = await FaceTracker.CreateAsync();

            this.mediaCapture = new MediaCapture();

            // For this scenario, we only need Video (not microphone) so specify this in the initializer.
            // NOTE: the appxmanifest only declares "webcam" under capabilities and if this is changed to include
            // microphone (default constructor) you must add "microphone" to the manifest or initialization will fail.
            MediaCaptureInitializationSettings settings = new MediaCaptureInitializationSettings();
            settings.SourceGroup = selectedGroup;
            settings.StreamingCaptureMode = StreamingCaptureMode.Video;
            settings.SharingMode = MediaCaptureSharingMode.SharedReadOnly;  // MediaCaptureSharingMode.ExclusiveControl
            settings.MemoryPreference = MediaCaptureMemoryPreference.Cpu;
            await this.mediaCapture.InitializeAsync(settings);
            this.mediaCapture.Failed += this.MediaCapture_CameraStreamFailed;

            // Cache the media properties as we'll need them later.
            var deviceController = this.mediaCapture.VideoDeviceController;
            this.videoProperties = deviceController.GetMediaStreamProperties(MediaStreamType.VideoPreview) as VideoEncodingProperties;

            // select a key which is not empty (hack)
            string frameSourceKey = colorSourceInfo.Id;
            foreach (KeyValuePair<string,MediaFrameSource> kvp  in this.mediaCapture.FrameSources)
            {
                frameSourceKey = kvp.Key;
                Debug.Log($"Sources, count: {this.mediaCapture.FrameSources.Count}, key = {frameSourceKey}, value = {kvp.Value}");
            }

            this.mediaFrameSource = this.mediaCapture.FrameSources[frameSourceKey];
            this.mediaFrameReader = await mediaCapture.CreateFrameReaderAsync(this.mediaFrameSource, MediaEncodingSubtypes.Nv12);
            this.mediaFrameReader.FrameArrived += ColorFrameReader_FrameArrived;
            await this.mediaFrameReader.StartAsync();

            successful = true;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine("Failed to start video : " +  ex.ToString());
            Debug.Log("Error in starting video: " + ex.ToString());
        }

        return successful;
    }

    // Safely stops webcam streaming (if running) and releases MediaCapture object.
    private async Task ShutdownWebcamAsync()
    {
        Debug.Log("ShutdownWebcamAsync");

        if (this.mediaCapture != null)
        {
            if (this.mediaCapture.CameraStreamState == Windows.Media.Devices.CameraStreamState.Streaming)
            {
                try
                {
                    await mediaFrameReader.StopAsync();
                    mediaFrameReader.FrameArrived -= ColorFrameReader_FrameArrived;
                }
                catch(Exception)
                {
                    ;   // Since we're going to destroy the MediaCapture object there's nothing to do here
                }
            }
            this.mediaCapture.Dispose();
        }

        this.mediaCapture = null;
        this.mediaFrameSource = null;
    }


    private void ColorFrameReader_FrameArrived(MediaFrameReader sender, MediaFrameArrivedEventArgs args)
    {
        var mediaFrameReference = sender?.TryAcquireLatestFrame();
        var videoMediaFrame = mediaFrameReference?.VideoMediaFrame;
        var softwareBitmap = videoMediaFrame?.SoftwareBitmap;
        var coordinateSystem = mediaFrameReference?.CoordinateSystem;

        if(softwareBitmap == null)
        {
            mediaFrameReference.Dispose();
            return;
        }

        // limit frame rate
        if(elapsedTimeFromLastFaceTracking < FACE_TRACKING_TIME_GAP_SECONDS)
        {
            softwareBitmap?.Dispose();
            mediaFrameReference.Dispose();
            return;
        }

        // reset tracking timing
        elapsedTimeFromLastFaceTracking = 0;

        //Debug.Log("Running face tracking");

        // track the image size
        int bitmapWidth = softwareBitmap.PixelWidth;
        int bitmapHeight = softwareBitmap.PixelHeight;


        // The returned VideoFrame should be in the supported NV12 format but we need to verify this.
        if (!FaceTracker.IsBitmapPixelFormatSupported(softwareBitmap.BitmapPixelFormat))
        {
            System.Diagnostics.Debug.WriteLine($"PixelFormat '{softwareBitmap.BitmapPixelFormat}' is not supported by FaceDetector");
            Debug.Log($"PixelFormat: {softwareBitmap.BitmapPixelFormat} is not supported");

            softwareBitmap?.Dispose();
            mediaFrameReference.Dispose();
            return;
        }
        //if (softwareBitmap.BitmapPixelFormat != BitmapPixelFormat.Nv12)
        //{
        //    softwareBitmap = SoftwareBitmap.Convert(softwareBitmap, BitmapPixelFormat.Nv12);
        //}

        
        Debug.Log($"Camera coordinateSystem is null: {coordinateSystem == null}");

        var currentFrame = videoMediaFrame?.GetVideoFrame();
        mediaFrameReference.Dispose();

        Task.Run( async () => {
            try
            {
                IList<DetectedFace> faces = await this.faceTracker.ProcessNextFrameAsync(currentFrame);
                // calculate the face center
                calculateFaceCenter(faces, bitmapWidth, bitmapHeight);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Error in tracking faces: " + ex.ToString());
                Debug.Log("Error in tracking face: " + ex.ToString());           
            }
            finally
            {
               currentFrame.Dispose();
            }
        });

               
    }

    
    private void AbandonStreaming()
    {
        Task.Run(() => ChangeScenarioStateAsync(ScenarioState.Idle));
    }

    // Handles MediaCapture stream failures by shutting down streaming and returning to Idle state.
    // param "sender" = The source of the event, i.e. our MediaCapture object
    // param "args" = Event data
    private void MediaCapture_CameraStreamFailed(MediaCapture sender, object args)
    {
        AbandonStreaming();
    }

    // ref: https://docs.microsoft.com/en-us/uwp/api/windows.media.faceanalysis.detectedface?view=winrt-20348
    private void calculateFaceCenter(IList<DetectedFace> detectedFaces, int imageWidth, int imageHeight)
    {
        Debug.Log("Faces detected: " + detectedFaces.Count);
        IList<Vector2> faceCenters = new List<Vector2>();
        foreach (DetectedFace face in detectedFaces)
        {
            
            // faceCenters.Add(rect);
            Debug.Log($"Face rectangle: x = {face.FaceBox.X}, y = {face.FaceBox.Y}, w = {face.FaceBox.Width}, h = {face.FaceBox.Height}");

            // normalized face w.r.t. image
            Vector2 normalizedImageFaceCenter = new Vector2();
            normalizedImageFaceCenter.x = (float)(face.FaceBox.X + face.FaceBox.Width / 2) / (float)imageWidth;
            //normalizedImageFaceCenter.y = 1 - ((float)(face.FaceBox.Y + face.FaceBox.Height / 2) / (float)imageHeight);
            normalizedImageFaceCenter.y = 1 - ((float)(face.FaceBox.Y + face.FaceBox.Height / 2 + face.FaceBox.Height / 12 ) / (float)imageHeight);
            setNormalizedImageFaceCenter(normalizedImageFaceCenter);

            faceLocationChanged = true;
            break;
        }

        if(detectedFaces.Count <= 0)
        {
             setFaceCenter(Vector2.zero);
        }
    }
#endif


}

