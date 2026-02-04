using UnityEngine;
using UnityEngine.UI;

public class DataSharkDemoBootstrap : MonoBehaviour
{
    [SerializeField] private DataSharkClient client;
    [SerializeField] private Button generateButton;

    private void Awake()
    {
        if (client == null)
        {
            client = FindFirstObjectByType<DataSharkClient>();
        }

        if (generateButton == null)
        {
            var buttonObject = GameObject.Find("GenerateButton");
            if (buttonObject != null)
            {
                generateButton = buttonObject.GetComponent<Button>();
            }
        }

        if (generateButton != null && client != null)
        {
            generateButton.onClick.AddListener(client.GenerateWorld);
        }
    }
}
