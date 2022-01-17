using System;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;
using TMPro;
using Microsoft.MixedReality.Toolkit.Input;

public class ProgressLoader : MonoBehaviour
{
    private float circularFill = 0f;
    private float circularUnfill = 1f;
    private float linearFill = 0f;
    private float linearUnfill = 1f;
    private float textFill = 0f;
    private string progressText = "0%";
    private bool shouldUpdateValues = false;

    private float elementDepth = 1.6f;
    private bool shouldUpdateDepth = false;

    private float linearElementSize = 0.40f;
    private float circularElementSize = 0.32f;
    private bool shouldUpdateSize = false;

    private float centerX = 0f;
    private float centerY = 0f;
    private float prevCenterX = 0f;
    private float prevCenterY = 0f;
    private bool shouldUpdateCenter = false;

    public GameObject circularFillUI;
    public GameObject circularUnfillUI;
    public GameObject linearFillUI;
    public GameObject linearUnfillUI;
    public GameObject textFillUI;
    public GameObject progressTextUI;

    void Start()
    {
        Debug.Log("Start ProgressLoader");
        // see https://docs.microsoft.com/en-us/dotnet/api/microsoft.mixedreality.toolkit.input.pointerutils, 
        // https://docs.microsoft.com/en-us/windows/mixed-reality/mrtk-unity/features/input/eye-tracking/eye-tracking-eyes-and-hands
        PointerUtils.SetGazePointerBehavior(PointerBehavior.AlwaysOff);
    }

    public void UpdateValues(float cFill, float cUnfill, float lFill, float lUnfill, float tFill, string details)
    {
        circularFill = cFill;
        circularUnfill = cUnfill;
        linearFill = lFill;
        linearUnfill = lUnfill;
        textFill = tFill;
        progressText = details;

        shouldUpdateValues = true;
    }

    public void UpdateText(string details)
    {
        progressText = details;
        shouldUpdateValues = true;
    }

    public void ResetValues()
    {
        circularFill = 0f;
        circularUnfill = 0f;
        linearFill = 0f;
        linearUnfill = 0f;
        textFill = 0f;
        progressText = "";

        shouldUpdateValues = true;
    }

    public void UpdateDepth(float depth)
    {
        elementDepth = depth;
        shouldUpdateDepth = true;
    }

    public void UpdateSize(float linearSize, float circularSize)
    {
        linearElementSize = linearSize;
        circularElementSize = circularSize;
        shouldUpdateSize = true;
    }

    public void UpdateCenter(float x, float y)
    {
        centerX = x;
        centerY = y;
        shouldUpdateCenter = true;
    }

    private void changeDepth(GameObject gameObject, float depth)
    {
        Vector3 currentPosition = gameObject.transform.position;
        gameObject.transform.position = new Vector3(currentPosition.x, currentPosition.y, depth);
    }

    private void shiftCenterPosition(GameObject gameObject, float deltaX, float deltaY)
    {
        Vector3 currentPosition = gameObject.transform.position;
        gameObject.transform.position = new Vector3(currentPosition.x + deltaX, currentPosition.y + deltaY, currentPosition.z);
    }

    private void changeSize(GameObject gameObject, float size)
    {
        RectTransform currentTransformation = gameObject.GetComponent<RectTransform>();
        currentTransformation.SetSizeWithCurrentAnchors(RectTransform.Axis.Horizontal, size);
        currentTransformation.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical, size);
    }

    private void Update()
    {
        if (shouldUpdateDepth)
        {
            changeDepth(circularFillUI, elementDepth);
            changeDepth(circularUnfillUI, elementDepth);
            changeDepth(linearFillUI, elementDepth);
            changeDepth(linearUnfillUI, elementDepth);
            changeDepth(textFillUI, elementDepth);
            changeDepth(progressTextUI, elementDepth);

            shouldUpdateDepth = false;
            shouldUpdateValues = true;
        }

        if (shouldUpdateCenter)
        {
            float deltaX = centerX - prevCenterX;
            float deltaY = centerY - prevCenterY;
            prevCenterX = centerX;
            prevCenterY = centerY;

            shiftCenterPosition(circularFillUI, deltaX, deltaY);
            shiftCenterPosition(circularUnfillUI, deltaX, deltaY);
            shiftCenterPosition(linearFillUI, deltaX, deltaY);
            shiftCenterPosition(linearUnfillUI, deltaX, deltaY);
            shiftCenterPosition(textFillUI, deltaX, deltaY);
            shiftCenterPosition(progressTextUI, deltaX, deltaY);

            shouldUpdateCenter = false;
            shouldUpdateValues = true;
        }

        if (shouldUpdateSize)
        {
            changeSize(circularFillUI, circularElementSize);
            changeSize(circularUnfillUI, circularElementSize);
            changeSize(linearFillUI, linearElementSize);
            changeSize(linearUnfillUI, linearElementSize);

            shouldUpdateSize = false;
            shouldUpdateValues = true;
        }

        if (shouldUpdateValues)
        {
            circularFillUI.GetComponent<Image>().fillAmount = circularFill;
            circularUnfillUI.GetComponent<Image>().fillAmount = circularUnfill;
            linearFillUI.GetComponent<Image>().fillAmount = linearFill;
            linearUnfillUI.GetComponent<Image>().fillAmount = linearUnfill;
            if (textFill != 0)
            {
                textFillUI.GetComponent<TextMeshProUGUI>().text = ((int)Math.Round(textFill * 100) + "%");
            }
            else
            {
                textFillUI.GetComponent<TextMeshProUGUI>().text = "";
            }
            
            progressTextUI.GetComponent<TextMeshProUGUI>().text = progressText;

            shouldUpdateValues = false;
        }


    }
}
