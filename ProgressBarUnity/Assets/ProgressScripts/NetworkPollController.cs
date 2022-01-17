using UnityEngine;
using System;
using System.Collections;
using Proyecto26;
using Logger = Microsoft.MixedReality.Toolkit.Examples.Demos.EyeTracking.Logging.UserInputRecorder;
using Diagnose = System.Diagnostics;


// see: https://foxypanda.me/tcp-client-in-a-uwp-unity-app-on-hololens/,
// https://www.red-gate.com/simple-talk/dotnet/c-programming/calling-restful-apis-unity3d/


public class NetworkPollController : MonoBehaviour
{
    private const float MIN_POLL_GAP_SECONDS = 3f;

    private float elapsedTimeFromLastPoll = 0;

    public ProgressLoader progressLoader;
    public Logger userInputLogger;
    public ConfigLoader configLoader;


    // Start is called before the first frame update
    void Start()
    {
        elapsedTimeFromLastPoll = 0;
        // updateProgressFromNetwork();
        Debug.Log("Start NetworkPollController");
    }

    // Update is called once per frame
    void Update()
    {
        elapsedTimeFromLastPoll += Time.deltaTime;
        if (elapsedTimeFromLastPoll > MIN_POLL_GAP_SECONDS)
        {
            elapsedTimeFromLastPoll = 0;
            updateProgressFromNetwork();
        }
    }

    private void updateProgressFromNetwork()
    {
        RestClient.Get<ProgressData>(new RequestHelper
        {
            Uri = configLoader.GetServer(),
            Timeout = 3,
            Retries = 1,
            RetrySecondsDelay = 1,
            EnableDebug = true,
            IgnoreHttpException = true,
        }).Then(progressData =>
        {
            updateProgress(progressData);
        }).Catch(err =>
        {
            Debug.LogException(err);
            Diagnose.Debug.WriteLine(err.Message);
        });
    }


    private void updateProgress(ProgressData progressData)
    {
        string json = JsonUtility.ToJson(progressData, true);
        Debug.Log("Data: " + json);
        Diagnose.Debug.WriteLine("[C] Data: " + json);

        if (progressData != null)
        {
            Debug.Log("Progress: " + progressData.linearFill + ", " + progressData.circularFill + ", " + progressData.textFill);
            progressLoader.UpdateValues(progressData.circularFill, progressData.circularUnfill,
                progressData.linearFill, progressData.linearUnfill,
                progressData.textFill,
                progressData.progressText);

            string configData = progressData.config;
            if (!string.IsNullOrEmpty(configData))
            {
                updateConfig(configData);
            }
        }
    }

    private void updateConfig(string configData)
    {
        Diagnose.Debug.WriteLine("[C] Config data: " + configData);
        Debug.Log("Config data: " + configData);
        // Format: <EYE_TRACKING_START, EYE_TRACKING_STOP>|<participant>|<session>
        // Format: <CHANGE_SIZE>|<linear_size>|<circular_size>
        // Foramt: <CHANGE_DEPTH>|<depth>
        // Foramt: <CHANGE_CENTER>|<enter_x>|<center_y>
        // Format: <DISPLAY_DURATION>|<duration_millis>

        string[] configs = configData.Split('|');
        if (configs.Length >= 3)
        {
            string cmd = configs[0];
            string participant = configs[1];
            string session = configs[2];

            if (string.Equals("EYE_TRACKING_START", cmd) && !userInputLogger.IsLoggingActive())
            {
                userInputLogger.SetUserName(participant);
                userInputLogger.SetSessionDescr(session);
                userInputLogger.SetFileName($"{participant}_{session}_eyes");
                userInputLogger.StartLogging();
            }
            else if (string.Equals("EYE_TRACKING_STOP", cmd) && userInputLogger.IsLoggingActive())
            {
                userInputLogger.StopLoggingAndSave();
            }
            else if (string.Equals("CHANGE_SIZE", cmd) && isValidFloat(configs[1]) && isValidFloat(configs[2]))
            {
                progressLoader.UpdateSize(float.Parse(configs[1]), float.Parse(configs[2]));
            }
            else if (string.Equals("CHANGE_CENTER", cmd) && isValidFloat(configs[1]) && isValidFloat(configs[2]))
            {
                progressLoader.UpdateCenter(float.Parse(configs[1]), float.Parse(configs[2]));
            }
        }
        if (configs.Length >= 2)
        {
            string cmd = configs[0];
            string value = configs[1];

            if (string.Equals("CHANGE_DEPTH", cmd) && isValidFloat(value))
            {
                progressLoader.UpdateDepth(float.Parse(value));
            }
            else if (string.Equals("DISPLAY_DURATION", cmd) && isValidFloat(value))
            {
                StartCoroutine(resetProgressAfterMillis(float.Parse(value)));
            }
        }

    }

    private IEnumerator resetProgressAfterMillis(float millis)
    {
        yield return new WaitForSeconds(millis/1000);
        progressLoader.ResetValues();
    }

    private bool isValidFloat(string value)
    {
        float f = 0;
        return float.TryParse(value, out f);
    }
}

[Serializable]
public class ProgressData
{
    public float circularFill;
    public float circularUnfill;
    public float linearFill;
    public float linearUnfill;
    public float textFill;
    public string progressText;
    public string config;
}

