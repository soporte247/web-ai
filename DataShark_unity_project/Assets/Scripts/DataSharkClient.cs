using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class DataSharkClient : MonoBehaviour
{
    [Header("Backend")]
    [SerializeField] private string baseUrl = "http://127.0.0.1:8000";

    [Header("Prompt")]
    [TextArea(3, 6)]
    [SerializeField] private string prompt = "Ciudad costera futurista con clima cambiante";
    [SerializeField] private string theme = "ciencia ficción";
    [SerializeField] private string multiplayerMode = "co-op";
    [SerializeField] private string playerSkillLevel = "intermedio";
    [SerializeField] private bool enableArVr = true;

    public void GenerateWorld()
    {
        StartCoroutine(GenerateWorldRoutine());
    }

    private IEnumerator GenerateWorldRoutine()
    {
        var request = new GenerationRequest
        {
            prompt = prompt,
            theme = theme,
            platforms = new string[] { "Windows", "Mac", "Linux", "Android", "iOS" },
            enable_ar_vr = enableArVr,
            multiplayer_mode = multiplayerMode,
            player_skill_level = playerSkillLevel
        };

        string json = JsonUtility.ToJson(request);
        byte[] payload = Encoding.UTF8.GetBytes(json);

        using (var webRequest = new UnityWebRequest($"{baseUrl}/generate", "POST"))
        {
            webRequest.uploadHandler = new UploadHandlerRaw(payload);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/json");

            yield return webRequest.SendWebRequest();

            if (webRequest.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"DataShark error: {webRequest.error}\n{webRequest.downloadHandler.text}");
                yield break;
            }

            Debug.Log($"DataShark response: {webRequest.downloadHandler.text}");
        }
    }

    [System.Serializable]
    private class GenerationRequest
    {
        public string prompt;
        public string theme;
        public string[] platforms;
        public bool enable_ar_vr;
        public string multiplayer_mode;
        public string player_skill_level;
    }
}
