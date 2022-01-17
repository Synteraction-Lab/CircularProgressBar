using System;
using UnityEngine;

using System.IO;

#if WINDOWS_UWP
using Windows.Storage;
using System.Linq;
using System.Threading.Tasks;
#endif

public class ConfigLoader : MonoBehaviour
{
    public const string SERVER = "http://192.168.43.97:8080/data";
    //public const string SERVER = "http://127.0.0.1:8080/data";
    public const string FILE_NAME = "progress_config.json";
    public const string FILE_DIRECTORY = "ProgressApp";

    private string server = SERVER;

    private bool configUpdated = false;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (!configUpdated)
        {
            updateConfigInfo();
            configUpdated = true;
        }
    }

    public string GetServer()
    {
        return server;
    }

    private async void updateConfigInfo()
    {
        ConfigData config;
//#if WINDOWS_UWP
//        config = await readConfigDataAsync();
//#else
        config = readConfigData();
//#endif
        server = config.server;
    }

    private string getConfigFilePath()
    {
        return (System.Environment.ExpandEnvironmentVariables("%userprofile%") + Path.DirectorySeparatorChar + "Videos" + Path.DirectorySeparatorChar + FILE_DIRECTORY + Path.DirectorySeparatorChar + FILE_NAME);
        //return Path.Combine(Application.persistentDataPath, FILE_NAME);
    }

    private void writeConfigData()
    {
        ConfigData config = new ConfigData();
        config.server = SERVER;

        string jsonString = JsonUtility.ToJson(config);
        string path = getConfigFilePath();
        try
        {
            Debug.Log("Write config file: " + path);
            File.WriteAllText(path, jsonString);
        }
        catch
        {
            Debug.Log("Failed to write config file: " + path);
        }
    }

    private ConfigData readConfigData()
    {
        string path = getConfigFilePath();

        if (!File.Exists(path))
        {
            writeConfigData();
        }


        ConfigData config = new ConfigData();
        try
        {
            Debug.Log("Read config file: " + path);
            System.Diagnostics.Debug.WriteLine("Read config file: " + path);
            string jsonString = File.ReadAllText(path);
            config = JsonUtility.FromJson<ConfigData>(jsonString);
        }
        catch
        {
            Debug.Log("Failed to read config file: " + path);
            System.Diagnostics.Debug.WriteLine("Failed to read config file: " + path);
        }
        return config;
    }

#if WINDOWS_UWP
    private async Task<ConfigData> readConfigDataAsync()
    {
        ConfigData config;

        try{
            System.Diagnostics.Debug.WriteLine("Reading config file [async] : " + FILE_NAME);
            StorageFolder docLib = await KnownFolders.VideosLibrary.GetFolderAsync(FILE_DIRECTORY);
            StorageFile docFile = await docLib.GetFileAsync(FILE_NAME);

            string jsonString;
            using (Stream fs = await docFile.OpenStreamForReadAsync())
            {
                byte[] byData = new byte[fs.Length];
                fs.Read(byData, 0, (int)fs.Length);
                jsonString = System.Text.Encoding.UTF8.GetString(byData);
            }
            config = JsonUtility.FromJson<ConfigData>(jsonString);
        }
        catch
        {
            System.Diagnostics.Debug.WriteLine("Failed to read config file [async] : " + FILE_NAME);
            config = new ConfigData();
            config.server = SERVER;
        }
        return config;
    }
#endif
}


[Serializable]
public class ConfigData
{
    public string server;
}

